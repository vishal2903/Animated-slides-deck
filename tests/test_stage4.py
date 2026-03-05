import json
import pathlib
import pytest


def test_player_contains_slides_data(tmp_path):
    """player.html must contain embedded SLIDES const."""
    slides = [
        {
            "id": i,
            "title": f"Slide {i}",
            "subtitle": "sub",
            "image": f"images/slide_{i:02d}.png",
            "transition_out": None,
            "image_prompt": "prompt",
            "transition_prompt": "trans"
        }
        for i in range(1, 3)
    ]
    (tmp_path / "slides.json").write_text(json.dumps(slides))
    (tmp_path / "images").mkdir()

    from src.stage4_player import build_player
    out = tmp_path / "player.html"
    build_player(tmp_path, out)

    content = out.read_text()
    assert "const SLIDES" in content
    assert "Slide 1" in content
    assert "<!DOCTYPE html>" in content
    assert "fetch(" not in content  # no fetch calls - must be self-contained


def test_player_no_server_required(tmp_path):
    """player.html must not use fetch() or XMLHttpRequest."""
    slides = [{"id": 1, "title": "T", "subtitle": "S", "image": "images/slide_01.png",
               "transition_out": None, "image_prompt": "p", "transition_prompt": "t"}]
    (tmp_path / "slides.json").write_text(json.dumps(slides))
    (tmp_path / "images").mkdir()

    from src.stage4_player import build_player
    out = tmp_path / "player.html"
    build_player(tmp_path, out)

    content = out.read_text()
    assert "fetch(" not in content
    assert "XMLHttpRequest" not in content


def test_player_embeds_image_as_base64(tmp_path):
    """When image file exists, it must be base64-embedded in HTML."""
    slides = [{"id": 1, "title": "T", "subtitle": "S", "image": "images/slide_01.png",
               "transition_out": None, "image_prompt": "p", "transition_prompt": "t"}]
    (tmp_path / "slides.json").write_text(json.dumps(slides))
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    # Write a minimal valid PNG (1x1 pixel)
    import base64
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    (img_dir / "slide_01.png").write_bytes(png_bytes)

    from src.stage4_player import build_player
    out = tmp_path / "player.html"
    build_player(tmp_path, out)

    content = out.read_text()
    assert "data:image/png;base64," in content


def test_player_fallback_when_no_image(tmp_path):
    """When image missing, _image_data must be null so fallback card shows."""
    slides = [{"id": 1, "title": "FallbackTest", "subtitle": "S", "image": "images/slide_01.png",
               "transition_out": None, "image_prompt": "p", "transition_prompt": "t"}]
    (tmp_path / "slides.json").write_text(json.dumps(slides))
    (tmp_path / "images").mkdir()
    # Do NOT create slide_01.png

    from src.stage4_player import build_player
    out = tmp_path / "player.html"
    build_player(tmp_path, out)

    content = out.read_text()
    assert '"_image_data": null' in content
    assert "FallbackTest" in content
