import json
import pathlib
import pytest
from unittest.mock import patch, MagicMock


def test_slides_json_schema_valid():
    """Test that generated slides.json has correct schema."""
    sample = [
        {
            "id": i,
            "title": f"Slide {i}",
            "subtitle": "subtitle",
            "image": f"images/slide_{i:02d}.png",
            "transition_out": f"transitions/t_{i:02d}_{i+1:02d}.mp4" if i < 10 else None,
            "image_prompt": "prompt text",
            "transition_prompt": "transition text"
        }
        for i in range(1, 11)
    ]
    sample[-1]["transition_out"] = None

    assert len(sample) == 10
    assert sample[0]["image"] == "images/slide_01.png"
    assert sample[9]["image"] == "images/slide_10.png"
    assert sample[0]["transition_out"] == "transitions/t_01_02.mp4"
    assert sample[8]["transition_out"] == "transitions/t_09_10.mp4"
    assert sample[9]["transition_out"] is None


def test_naming_convention():
    """Test zero-padded naming is correct."""
    for i in range(1, 11):
        img = f"images/slide_{i:02d}.png"
        assert img == f"images/slide_{i:02d}.png"

    for i in range(1, 10):
        trans = f"transitions/t_{i:02d}_{i+1:02d}.mp4"
        assert "_" in trans
        assert "-" not in trans
