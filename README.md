<div align="center">

#  Animated Slides Pipeline

**Type a topic. Get a cinematic AI presentation. Open it in your browser.**



---

## What Is This?

This is a fully automated pipeline that turns a **single topic string** into a **cinematic AI presentation** — complete with AI-generated slide images and smooth morphing video transitions between each slide.

No PowerPoint. No Canva. No manual design work.

You run one command. The pipeline calls 3 AI APIs in sequence, generates all the assets, and bundles everything into a single `player.html` file you can double-click to present. The output file works **completely offline** — all images and videos are embedded inside it. No server, no internet, no `npm install`.

---

## Input → Output

**You provide:**
```
python main.py "How to Build AI Agents" my-deck
```

**You get:**
```
output/my-deck/
  ├── slides.json          ← 10 structured slides (titles, subtitles, prompts)
  ├── images/
  │     ├── slide_01.png   ← 16:9 cinematic AI-generated image
  │     ├── slide_02.png
  │     └── ...slide_10.png
  ├── transitions/
  │     ├── t_01_02.mp4    ← morphing video from slide 1 → 2
  │     ├── t_02_03.mp4
  │     └── ...t_09_10.mp4
  └── player.html          ← double-click to present. works offline.
```

---

## How It Works

```
TOPIC STRING
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  Stage 1  │  Gemini 2.5 Flash   │  → slides.json     │
│  Stage 2  │  Imagen 4           │  → slide images    │
│  Stage 3  │  Kling 2.1 Pro      │  → transition MP4s │
│  Stage 4  │  Pure Python        │  → player.html ✓   │
└──────────────────────────────────────────────────────┘
```

- **Stage 1** — Gemini LLM generates 10 slides with titles, subtitles, and detailed image prompts
- **Stage 2** — Imagen 4 generates a cinematic 16:9 image for every slide natively (no cropping)
- **Stage 3** — Kling 2.1 Pro takes the start and end frame of each pair and generates a cinematic morph video between them
- **Stage 4** — Pure Python bundles everything into one self-contained HTML file with all assets base64-embedded

---

## 🚀 Setup

```bash
git clone https://github.com/100x-Engineers100/animated-slides-pipeline.git
cd animated-slides-pipeline

python -m venv venv && venv\Scripts\activate   # Windows
# OR: source venv/bin/activate                 # Mac/Linux

pip install -r requirements.txt
cp .env.example .env   # then add your API keys
```

**Keys needed:**
| Key | Where to get it |
|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) ← needs billing enabled |
| `KLING_API_KEY` | [fal.ai/dashboard](https://fal.ai/dashboard) |

---

## 🎮 Usage

```bash
# Full pipeline — all 4 stages
python main.py "The Future of AI" my-deck

# No transitions (faster + cheaper, skips Kling)
python main.py "Deep Learning" ml-deck --skip-transitions

# Slides + structure only (completely free)
python main.py "Blockchain" crypto-deck --slides-only

# Use Gemini image gen instead of Imagen 4
python main.py "Web3" web3-deck --image-backend gemini
```

---

## 🎥 Player Controls

Once you open `player.html`:

| Key | Action |
|---|---|
| `SPACE` / `→` | Next slide + plays morph transition |
| `←` | Previous slide |
| `G` | Grid overview of all slides |
| `P` | View the exact AI prompts used per slide |
| `F` | Fullscreen |
| `ESC` | Close any panel |

---

## 💰 Cost Per Deck

| Stage | Service | Cost |
|---|---|---|
| Slide content | Gemini 2.5 Flash | ~$0.00 |
| 10 images | Imagen 4 | ~$0.10–0.20 |
| 9 transitions | Kling 2.1 Pro via fal.ai | ~$1.25–2.50 |
| **Total** | | **~$1.35–2.70** |

> Use `--skip-transitions` to keep total cost under $0.25.

---

## 🔁 Checkpoint & Resume

Stages 2 and 3 are expensive. If the pipeline crashes halfway, just re-run the same command — already-generated files are detected and skipped automatically. You only pay for what hasn't been generated yet.

---

<div align="center">

Built by [@vishal2903](https://github.com/vishal2903) &nbsp;|&nbsp; Part of [100xEngineers](https://100xengineers.com)

</div>
