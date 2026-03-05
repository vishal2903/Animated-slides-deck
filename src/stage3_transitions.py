import base64
import json
import os
import pathlib
import httpx
import fal_client
from dotenv import load_dotenv

load_dotenv()

TRANSITION_PROMPT = (
    "Cinematic morphing transition between two dark sci-fi holographic slides. "
    "Smooth camera motion. Teal and cyan particle effects. "
    "Robot character remains visually consistent. Deep navy background. "
    "Photorealistic. Epic cinematic quality. No abrupt cuts. 4 seconds duration."
)

MODEL = "fal-ai/kling-video/v2.1/pro/image-to-video"

# Set fal.ai key once at module load
os.environ["FAL_KEY"] = os.getenv("KLING_API_KEY", "")


def _image_to_data_url(image_path: pathlib.Path) -> str:
    """Convert image file to base64 data URL for API submission."""
    data = image_path.read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:image/png;base64,{b64}"


def generate_single_transition(
    slide_a: int,
    slide_b: int,
    images_dir: pathlib.Path,
    output_path: pathlib.Path,
) -> bool:
    """Generate one transition video using Kling 2.1 Pro via fal.ai."""
    img_a = images_dir / f"slide_{slide_a:02d}.png"
    img_b = images_dir / f"slide_{slide_b:02d}.png"

    if not img_a.exists() or not img_b.exists():
        print(f"[ERROR] Missing images for transition t_{slide_a:02d}_{slide_b:02d}")
        return False

    if img_a.stat().st_size == 0 or img_b.stat().st_size == 0:
        print(f"[ERROR] Empty placeholder image - skipping transition t_{slide_a:02d}_{slide_b:02d}")
        return False

    print(f"[*] Submitting t_{slide_a:02d}_{slide_b:02d} to Kling 2.1 Pro...")

    result = fal_client.run(
        MODEL,
        arguments={
            "prompt": TRANSITION_PROMPT,
            "image_url": _image_to_data_url(img_a),
            "tail_image_url": _image_to_data_url(img_b),
            "duration": "5",
            "aspect_ratio": "16:9",
        },
        timeout=300,
    )

    video_url = result["video"]["url"]
    print(f"[*] Downloading video from {video_url[:60]}...")

    with httpx.Client(timeout=120) as dl:
        video_resp = dl.get(video_url)
        output_path.write_bytes(video_resp.content)

    print(f"[OK] Transition saved: {output_path.name} ({output_path.stat().st_size // 1024}KB)")
    return True


def generate_all_transitions(slides: list[dict], output_dir: pathlib.Path) -> None:
    """Generate all N-1 transition videos."""
    images_dir = output_dir / "images"
    trans_dir = output_dir / "transitions"
    trans_dir.mkdir(parents=True, exist_ok=True)

    pairs = [(slides[i]["id"], slides[i + 1]["id"]) for i in range(len(slides) - 1)]

    for idx, (a, b) in enumerate(pairs):
        filename = f"t_{a:02d}_{b:02d}.mp4"
        out_path = trans_dir / filename

        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"[SKIP] {filename} already exists (checkpoint)")
            continue

        print(f"[*] Generating transition {a} -> {b} ({idx+1}/{len(pairs)})")
        generate_single_transition(a, b, images_dir, out_path)

    print(f"[OK] Stage 3 complete: transitions in {trans_dir}")


if __name__ == "__main__":
    import sys
    slides_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("output/test-deck/slides.json")
    slides = json.loads(slides_path.read_text())
    out_dir = slides_path.parent
    generate_all_transitions(slides, out_dir)
