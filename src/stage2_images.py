import os
import pathlib
import time
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Available image generation backends
BACKEND_IMAGEN = "imagen"    # Imagen 4 - dedicated image gen, native 16:9, high quality (default)
BACKEND_GEMINI = "gemini"    # Gemini native image gen (nano-banana), no aspect ratio control


def generate_single_image(prompt: str, output_path: pathlib.Path, backend: str = BACKEND_IMAGEN) -> bool:
    """Generate one 16:9 image. Returns True on success.

    backend: "imagen" (default, Imagen 4, native 16:9)
             "gemini" (Gemini native image gen / nano-banana)
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    if backend == BACKEND_IMAGEN:
        return _generate_imagen(client, prompt, output_path)
    elif backend == BACKEND_GEMINI:
        return _generate_gemini(client, prompt, output_path)
    else:
        print(f"[ERROR] Unknown backend: {backend}. Use 'imagen' or 'gemini'.")
        return False


def _generate_imagen(client, prompt: str, output_path: pathlib.Path) -> bool:
    """Imagen 4 - native 16:9, high quality, dedicated image model."""
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            aspect_ratio="16:9",
            number_of_images=1,
        )
    )

    if response.generated_images:
        img_bytes = response.generated_images[0].image.image_bytes
        output_path.write_bytes(img_bytes)
        print(f"[OK] Image saved (Imagen4 16:9): {output_path} ({len(img_bytes)//1024}KB)")
        return True

    print(f"[ERROR] No image returned for {output_path.name}")
    return False


def _generate_gemini(client, prompt: str, output_path: pathlib.Path) -> bool:
    """Gemini native image gen (nano-banana) - no native aspect ratio control."""
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt + " Wide 16:9 landscape widescreen orientation.",
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        )
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            output_path.write_bytes(part.inline_data.data)
            print(f"[OK] Image saved (Gemini native): {output_path} ({len(part.inline_data.data)//1024}KB)")
            return True

    print(f"[ERROR] No image returned for {output_path.name}")
    return False


def generate_all_images(slides: list[dict], output_dir: pathlib.Path, backend: str = BACKEND_IMAGEN) -> None:
    """Generate all slide images sequentially."""
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Image backend: {backend.upper()}")

    for slide in slides:
        slide_id = slide["id"]
        filename = f"slide_{slide_id:02d}.png"
        out_path = images_dir / filename

        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"[SKIP] {filename} already exists (checkpoint)")
            continue

        print(f"[*] Generating image {slide_id}/10: {slide['title']}")
        success = generate_single_image(slide["image_prompt"], out_path, backend=backend)

        if not success:
            print(f"[WARN] Failed to generate {filename}, creating placeholder")
            out_path.write_bytes(b"")

        if slide_id < len(slides):
            time.sleep(2)

    print(f"[OK] Stage 2 complete: images in {images_dir}")


if __name__ == "__main__":
    import sys
    slides_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("output/test-deck/slides.json")
    backend = sys.argv[2] if len(sys.argv) > 2 else BACKEND_IMAGEN
    slides = json.loads(slides_path.read_text())
    out_dir = slides_path.parent
    generate_all_images(slides, out_dir, backend=backend)
