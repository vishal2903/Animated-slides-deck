"""
Cinematic Presenter Pipeline
============================
INPUT:  TOPIC string
OUTPUT: output/<deck-name>/player.html  (open in browser, works offline)

Usage:
  python main.py "How to Build AI Agents" my-deck
  python main.py "Introduction to Python" python-deck --slides-only
  python main.py "Deep Learning" dl-deck --skip-transitions
"""

import argparse
import pathlib
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from src.stage1_slides import generate_slides
from src.stage2_images import generate_all_images
from src.stage3_transitions import generate_all_transitions
from src.stage4_player import build_player


def validate_env(skip_transitions: bool = False):
    missing = []
    if not os.getenv("GEMINI_API_KEY"):
        missing.append("GEMINI_API_KEY")
    if not skip_transitions and not os.getenv("KLING_API_KEY"):
        missing.append("KLING_API_KEY")
    if missing:
        print(f"[ERROR] Missing API keys in .env: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your keys.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Cinematic Presenter Pipeline")
    parser.add_argument("topic", help="Presentation topic, e.g. 'How to Build AI Agents'")
    parser.add_argument("deck_name", nargs="?", default="my-deck", help="Output folder name under output/")
    parser.add_argument("--slides-only", action="store_true", help="Run Stage 1 only (no images or video)")
    parser.add_argument("--skip-transitions", action="store_true", help="Skip Stage 3 (images but no videos)")
    parser.add_argument("--image-backend", choices=["imagen", "gemini"], default="imagen",
                        help="Image gen backend: 'imagen' (Imagen 4, native 16:9, default) or 'gemini' (Gemini native/nano-banana)")
    args = parser.parse_args()

    validate_env(skip_transitions=args.slides_only or args.skip_transitions)

    out_dir = pathlib.Path("output") / args.deck_name
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    (out_dir / "transitions").mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Topic: {args.topic}")
    print(f"[*] Output: {out_dir}\n")

    # Stage 1: Gemini LLM -> slides.json
    print("=" * 50)
    print("STAGE 1: Generating slide content...")
    print("=" * 50)
    slides = generate_slides(args.topic, out_dir / "slides.json")

    if args.slides_only:
        print("\n[OK] --slides-only flag set. Done.")
        return

    # Stage 2: Gemini Image Gen -> images/slide_01.png ... slide_10.png
    print("\n" + "=" * 50)
    print("STAGE 2: Generating slide images...")
    print("=" * 50)
    generate_all_images(slides, out_dir, backend=args.image_backend)

    if not args.skip_transitions:
        # Stage 3: Kling 2.1 Pro -> transitions/t_01_02.mp4 ... t_09_10.mp4
        print("\n" + "=" * 50)
        print("STAGE 3: Generating transition videos...")
        print("=" * 50)
        generate_all_transitions(slides, out_dir)

    # Stage 4: Pure Python -> player.html (self-contained, base64-embedded)
    print("\n" + "=" * 50)
    print("STAGE 4: Building player.html...")
    print("=" * 50)
    build_player(out_dir, out_dir / "player.html")

    print(f"\n[OK] Done! Open: {out_dir / 'player.html'}")


if __name__ == "__main__":
    main()
