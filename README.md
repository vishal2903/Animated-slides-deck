# Animated Slides Pipeline

> You type a topic. You get a cinematic AI presentation. That's it.

No PowerPoint. No Canva. No "let me just tweak this font for 45 minutes."
Just pure automated glory — AI-generated slides, AI-generated images, and cinematic morph transitions between them. All wrapped in a self-contained HTML player that works by double-clicking a file.

---

## What Does It Actually Do?

```
YOU TYPE:    "How to Build AI Agents"

YOU GET:     output/ai-agents-deck/
               slides.json          <- 10 slides, fully structured
               images/
                 slide_01.png       <- 16:9 cinematic AI image
                 slide_02.png
                 ...slide_10.png
               transitions/
                 t_01_02.mp4        <- morphing video between slides
                 t_02_03.mp4
                 ...t_09_10.mp4
               player.html          <- double-click. present. done.
```

The `player.html` has **everything embedded inside it** — images, videos, all of it. No internet needed. No server. No `npm install`. Just open it in a browser.

---

## The Pipeline (4 Stages, Fully Automated)

```
STAGE 1   Gemini 2.5 Flash LLM
          Generates 10 slides with titles, subtitles, and detailed image prompts

STAGE 2   Imagen 4 (Google)
          Generates cinematic 16:9 images for each slide
          (or switch to Gemini native image gen if you prefer)

STAGE 3   Kling 2.1 Pro via fal.ai
          Creates smooth morphing transition videos between consecutive slides
          Uses start-frame + end-frame for true cinematic morphs

STAGE 4   Pure Python
          Bundles everything into a single player.html
          All assets base64-embedded. Works fully offline.
```

---

## The Player Features

Once you open `player.html`:

| Key / Action | What it does |
|---|---|
| `SPACE` or `-->` | Next slide (plays transition video if available) |
| `<--` | Previous slide |
| `G` | Toggle grid overview of all slides |
| `P` | Toggle prompts panel (see the exact AI prompts used) |
| `F` | Fullscreen |
| `ESC` | Close any panel |
| Click dots | Jump to any slide |

Custom cursor, progress bar, slide counter, copy-prompt buttons — all included.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/100x-Engineers100/animated-slides-pipeline.git
cd animated-slides-pipeline
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

```bash
cp .env.example .env
```

Open `.env` and fill in:

```
GEMINI_API_KEY=your_google_gemini_api_key
KLING_API_KEY=your_fal_ai_key
```

**Where to get them:**
- `GEMINI_API_KEY` -> [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (needs billing enabled for Imagen 4)
- `KLING_API_KEY` -> [fal.ai/dashboard](https://fal.ai/dashboard) (this is your fal.ai key, used for Kling)

---

## Usage

### Full pipeline (recommended)

```bash
python main.py "How to Build AI Agents" ai-agents-deck
```

Opens `output/ai-agents-deck/player.html` when done.

### Skip transitions (faster, no Kling cost)

```bash
python main.py "Machine Learning Basics" ml-deck --skip-transitions
```

### Only generate slides.json (free, instant)

```bash
python main.py "The Future of Work" future-deck --slides-only
```

### Switch image backend to Gemini (instead of Imagen 4)

```bash
python main.py "Blockchain Explained" crypto-deck --image-backend gemini
```

---

## Image Backends

Two options for image generation:

| Backend | Flag | Model | Aspect Ratio | Quality |
|---|---|---|---|---|
| **Imagen 4** (default) | `--image-backend imagen` | `imagen-4.0-generate-001` | Native 16:9 | High |
| **Gemini Native** | `--image-backend gemini` | `gemini-2.5-flash-image` | Prompt-guided | Medium |

Imagen 4 is recommended — it generates true 16:9 images natively with no cropping needed.

---

## Cost Per Deck (10 slides)

| Stage | Service | Approx Cost |
|---|---|---|
| Slide JSON | Gemini 2.5 Flash | ~$0.00 |
| 10 images | Imagen 4 | ~$0.10 - $0.20 |
| 9 transitions | Kling 2.1 Pro via fal.ai | ~$1.25 - $2.50 |
| **TOTAL** | | **~$1.35 - $2.70** |

Want it cheaper? Use `--skip-transitions` to skip Stage 3 entirely. You still get a beautiful image deck with fade transitions.

---

## Checkpoint / Resume

Expensive stages (images and transitions) have built-in checkpoint logic.

If the pipeline crashes halfway through, just run the same command again. Already-generated files are detected and skipped automatically. You only pay for what hasn't been generated yet.

---

## Project Structure

```
animated-slides-pipeline/
  main.py                  <- run this
  .env.example             <- copy to .env, add your keys
  requirements.txt
  prompts/
    slide_system_prompt.txt  <- the LLM prompt that generates slide structure
  src/
    stage1_slides.py       <- Gemini LLM -> slides.json
    stage2_images.py       <- Imagen 4 / Gemini -> slide images
    stage3_transitions.py  <- Kling 2.1 Pro -> transition videos
    stage4_player.py       <- builds player.html
  tests/
    test_stage1.py
    test_stage2.py
    test_stage3.py
    test_stage4.py
  output/                  <- your generated decks land here (gitignored)
```

---

## Run Tests

```bash
pytest tests/ -v
```

All 13 tests should pass. Tests cover schema validation, naming conventions, checkpoint logic, and player HTML correctness — without making any real API calls.

---

## Requirements

- Python 3.11+
- Google Cloud project with billing enabled (for Imagen 4)
- fal.ai account (for Kling transitions)

---

## FAQ

**Q: Why does player.html work offline?**
Everything — images, videos, JSON data — is base64-encoded and embedded directly into the HTML file. There are zero external requests. You can email it, put it on a USB drive, or open it on a plane.

**Q: What if an image fails to generate?**
The pipeline creates a styled fallback card with the slide title and subtitle. The rest of the deck continues generating normally.

**Q: What if a transition video fails?**
The player gracefully falls back to a fade transition. Your presentation still works.

**Q: Can I customise the visual style?**
Yes — edit `prompts/slide_system_prompt.txt` to change the robot character, color palette, and visual style. The prompt controls everything the AI generates.

**Q: Why Kling 2.1 Pro specifically?**
It's one of the few models that accepts both a start frame AND an end frame for video generation. This gives you true morphing transitions rather than just animating from a single image.

---

Built by [@vishal2903](https://github.com/vishal2903)
