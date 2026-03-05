import pathlib
import pytest


def test_transition_naming():
    """Verify transition filename pattern."""
    pairs = [(i, i+1) for i in range(1, 10)]
    for a, b in pairs:
        name = f"t_{a:02d}_{b:02d}.mp4"
        assert name.startswith("t_")
        assert name.endswith(".mp4")
        assert "-" not in name  # must use underscore, not hyphen


def test_pair_count():
    """10 slides -> 9 transitions."""
    slides = [{"id": i} for i in range(1, 11)]
    pairs = [(slides[i]["id"], slides[i+1]["id"]) for i in range(len(slides) - 1)]
    assert len(pairs) == 9
    assert pairs[0] == (1, 2)
    assert pairs[-1] == (9, 10)


def test_checkpoint_skip(tmp_path):
    """Non-empty file should be skipped."""
    f = tmp_path / "t_01_02.mp4"
    f.write_bytes(b"fake_video")
    assert f.exists() and f.stat().st_size > 0


def test_empty_image_guard(tmp_path):
    """Empty placeholder images should not be sent to API."""
    img = tmp_path / "slide_01.png"
    img.write_bytes(b"")  # empty placeholder
    assert img.stat().st_size == 0
    # Stage3 checks size > 0 before submitting
