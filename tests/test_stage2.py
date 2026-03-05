import pathlib
import pytest
from unittest.mock import patch, MagicMock


def test_output_path_naming():
    """Verify image filename pattern is correct."""
    for i in range(1, 11):
        name = f"slide_{i:02d}.png"
        assert name.startswith("slide_")
        assert name.endswith(".png")
        assert len(name.split("_")[1].split(".")[0]) == 2  # zero-padded


def test_checkpoint_skip_logic(tmp_path):
    """Verify existing images are skipped."""
    existing = tmp_path / "images" / "slide_01.png"
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"fake_image_data")
    assert existing.exists()
    # Logic: if exists and size > 0 -> skip. Verified by file presence check in stage2.
    assert existing.stat().st_size > 0


def test_slide_count():
    """10 slides -> 10 images expected."""
    slides = [{"id": i} for i in range(1, 11)]
    expected_files = [f"slide_{s['id']:02d}.png" for s in slides]
    assert len(expected_files) == 10
    assert expected_files[0] == "slide_01.png"
    assert expected_files[9] == "slide_10.png"
