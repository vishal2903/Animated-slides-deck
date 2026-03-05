import json
import os
import pathlib
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_ROOT = pathlib.Path(__file__).parent.parent
SYSTEM_PROMPT = (_ROOT / "prompts" / "slide_system_prompt.txt").read_text()


def generate_slides(topic: str, output_path: pathlib.Path) -> list[dict]:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Create a 10-slide deck on: {topic}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        )
    )
    raw = response.text.strip()

    # Strip markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    slides = json.loads(raw)

    # Validate structure
    if not isinstance(slides, list):
        raise ValueError("Expected a JSON array from LLM")
    if len(slides) != 10:
        raise ValueError(f"Expected 10 slides, got {len(slides)}")
    for s in slides:
        for field in ["id", "title", "subtitle", "image", "transition_out", "image_prompt"]:
            if field not in s:
                raise ValueError(f"Slide {s.get('id')} missing field: {field}")
    if slides[-1]["transition_out"] is not None:
        raise ValueError("Last slide must have null transition_out")

    output_path.write_text(json.dumps(slides, indent=2))
    print(f"[OK] Stage 1 complete: {len(slides)} slides -> {output_path}")
    return slides


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "How to Build AI Agents"
    out = pathlib.Path("output/test-deck")
    out.mkdir(parents=True, exist_ok=True)
    generate_slides(topic, out / "slides.json")
