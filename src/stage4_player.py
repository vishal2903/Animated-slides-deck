import json
import pathlib
import base64


def _embed_file_as_b64(file_path: pathlib.Path) -> str | None:
    """Return base64 data URL for embedding binary files. Returns None if file missing/empty."""
    if not file_path.exists() or file_path.stat().st_size == 0:
        return None
    data = base64.b64encode(file_path.read_bytes()).decode()
    suffix = file_path.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "mp4": "video/mp4"}.get(suffix[1:], "application/octet-stream")
    return f"data:{mime};base64,{data}"


def build_player(deck_dir: pathlib.Path, output_path: pathlib.Path) -> None:
    """Build self-contained player.html embedding all images and videos as base64."""
    slides = json.loads((deck_dir / "slides.json").read_text())

    # Embed images and videos into slide data
    for slide in slides:
        img_path = deck_dir / slide["image"]
        slide["_image_data"] = _embed_file_as_b64(img_path)

        if slide["transition_out"]:
            vid_path = deck_dir / slide["transition_out"]
            slide["_video_data"] = _embed_file_as_b64(vid_path)
        else:
            slide["_video_data"] = None

    slides_js = json.dumps(slides, indent=2)
    total_slides = len(slides)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cinematic Presentation</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --navy: #0a1628;
    --teal: #00d4c8;
    --teal-dim: rgba(0, 212, 200, 0.4);
    --orange: #ff6b35;
    --text: #e8f4f8;
  }}

  body {{
    background: var(--navy);
    color: var(--text);
    font-family: 'Courier New', monospace;
    height: 100vh;
    overflow: hidden;
    cursor: none;
  }}

  #cursor {{
    position: fixed;
    width: 8px; height: 8px;
    background: var(--teal);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-50%, -50%);
    transition: transform 0.1s;
  }}
  #cursor-ring {{
    position: fixed;
    width: 28px; height: 28px;
    border: 1.5px solid var(--teal-dim);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9998;
    transform: translate(-50%, -50%);
    transition: all 0.15s;
  }}

  #stage {{
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--navy);
  }}

  #slide-image {{
    max-height: 100vh;
    max-width: 100vw;
    object-fit: contain;
    display: block;
  }}

  #slide-fallback {{
    display: none;
    width: min(100vw, 177.78vh);
    height: min(100vh, 56.25vw);
    background: linear-gradient(160deg, #0d1f3c 0%, #061020 100%);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 32px;
    text-align: center;
    border: 1px solid var(--teal-dim);
  }}
  #slide-fallback .fb-title {{
    font-size: clamp(20px, 3.5vh, 36px);
    font-weight: 700;
    color: var(--text);
    margin-bottom: 16px;
    line-height: 1.2;
  }}
  #slide-fallback .fb-subtitle {{
    font-size: clamp(13px, 2vh, 20px);
    color: var(--teal);
    line-height: 1.4;
  }}

  #transition-video {{
    position: fixed;
    inset: 0;
    width: 100%; height: 100%;
    object-fit: contain;
    background: var(--navy);
    z-index: 100;
    display: none;
  }}

  #hud-top {{
    position: fixed;
    top: 0; left: 0; right: 0;
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(to bottom, rgba(10,22,40,0.95), transparent);
    z-index: 50;
    letter-spacing: 0.15em;
    font-size: 11px;
    text-transform: uppercase;
  }}
  #deck-title {{ color: var(--teal); }}
  #slide-counter {{ color: var(--text); opacity: 0.7; }}

  #hud-bottom {{
    position: fixed;
    bottom: 0; left: 0; right: 0;
    padding: 0 24px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(to top, rgba(10,22,40,0.95), transparent);
    z-index: 50;
  }}

  #dot-track {{
    display: flex;
    gap: 6px;
    align-items: center;
  }}
  .dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    cursor: pointer;
    transition: all 0.25s;
  }}
  .dot.visited {{ background: var(--teal-dim); }}
  .dot.current {{ background: var(--teal); width: 18px; border-radius: 3px; }}

  #nav-buttons {{ display: flex; gap: 10px; align-items: center; }}
  .hud-btn {{
    background: rgba(0,212,200,0.08);
    border: 1px solid var(--teal-dim);
    color: var(--teal);
    padding: 6px 14px;
    font-family: inherit;
    font-size: 10px;
    letter-spacing: 0.1em;
    cursor: pointer;
    text-transform: uppercase;
    transition: all 0.2s;
  }}
  .hud-btn:hover {{ background: rgba(0,212,200,0.18); }}

  #progress-bar {{
    position: fixed;
    bottom: 0; left: 0;
    height: 2px;
    background: var(--teal);
    transition: width 0.4s ease;
    z-index: 60;
    box-shadow: 0 0 8px var(--teal);
  }}

  .corner {{
    position: fixed;
    width: 20px; height: 20px;
    border-color: var(--teal-dim);
    border-style: solid;
    z-index: 50;
    opacity: 0.6;
  }}
  .corner.tl {{ top: 8px; left: 8px; border-width: 1.5px 0 0 1.5px; }}
  .corner.tr {{ top: 8px; right: 8px; border-width: 1.5px 1.5px 0 0; }}
  .corner.bl {{ bottom: 8px; left: 8px; border-width: 0 0 1.5px 1.5px; }}
  .corner.br {{ bottom: 8px; right: 8px; border-width: 0 1.5px 1.5px 0; }}

  #overview {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(10,22,40,0.97);
    z-index: 200;
    padding: 40px;
    overflow-y: auto;
  }}
  #overview.visible {{ display: block; }}
  #overview-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 16px;
    max-width: 1200px;
    margin: 0 auto;
  }}
  .overview-card {{
    border: 1px solid var(--teal-dim);
    cursor: pointer;
    overflow: hidden;
    aspect-ratio: 16/9;
    background: #061020;
    position: relative;
    transition: border-color 0.2s;
  }}
  .overview-card:hover {{ border-color: var(--teal); }}
  .overview-card img {{ width: 100%; height: 100%; object-fit: cover; }}
  .overview-card .card-num {{
    position: absolute;
    bottom: 6px; left: 8px;
    font-size: 10px;
    color: var(--teal);
    letter-spacing: 0.1em;
  }}

  #prompt-panel {{
    display: none;
    position: fixed;
    top: 0; right: 0;
    width: min(400px, 90vw);
    height: 100vh;
    background: rgba(10,22,40,0.97);
    border-left: 1px solid var(--teal-dim);
    z-index: 200;
    overflow-y: auto;
    padding: 24px;
  }}
  #prompt-panel.visible {{ display: block; }}
  .panel-label {{
    font-size: 9px;
    letter-spacing: 0.2em;
    color: var(--teal);
    text-transform: uppercase;
    margin-bottom: 6px;
    margin-top: 16px;
  }}
  .panel-text {{
    font-size: 11px;
    color: rgba(232,244,248,0.8);
    line-height: 1.6;
    background: rgba(0,212,200,0.04);
    border: 1px solid var(--teal-dim);
    padding: 10px;
    white-space: pre-wrap;
  }}
  .copy-btn {{
    font-size: 9px;
    color: var(--teal);
    background: none;
    border: 1px solid var(--teal-dim);
    padding: 3px 8px;
    cursor: pointer;
    letter-spacing: 0.1em;
    margin-top: 6px;
    font-family: inherit;
  }}

  #key-hints {{
    position: fixed;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 9px;
    color: rgba(0,212,200,0.4);
    letter-spacing: 0.1em;
    line-height: 2;
    text-align: right;
    z-index: 50;
    animation: fade-hints 4s ease forwards;
  }}
  @keyframes fade-hints {{
    0%, 60% {{ opacity: 1; }}
    100% {{ opacity: 0; pointer-events: none; }}
  }}

  @keyframes fade-in {{
    from {{ opacity: 0; }} to {{ opacity: 1; }}
  }}
  .fade-in {{ animation: fade-in 0.7s ease; }}
</style>
</head>
<body>

<div id="cursor"></div>
<div id="cursor-ring"></div>

<div class="corner tl"></div>
<div class="corner tr"></div>
<div class="corner bl"></div>
<div class="corner br"></div>

<div id="stage">
  <img id="slide-image" src="" alt="">
  <div id="slide-fallback">
    <div class="fb-title" id="fallback-title"></div>
    <div class="fb-subtitle" id="fallback-subtitle"></div>
  </div>
</div>

<video id="transition-video" playsinline></video>

<div id="hud-top">
  <span id="deck-title">CINEMATIC DECK</span>
  <span id="slide-counter">SLIDE 01 / {total_slides:02d}</span>
</div>

<div id="hud-bottom">
  <div id="dot-track"></div>
  <div id="nav-buttons">
    <button class="hud-btn" onclick="togglePromptPanel()">P - PROMPTS</button>
    <button class="hud-btn" onclick="toggleOverview()">G - GRID</button>
    <button class="hud-btn" onclick="prevSlide()">PREV</button>
    <button class="hud-btn" onclick="nextSlide()">NEXT</button>
  </div>
</div>

<div id="progress-bar"></div>

<div id="overview">
  <div id="overview-grid"></div>
</div>

<div id="prompt-panel">
  <div class="panel-label">IMAGE PROMPT</div>
  <div class="panel-text" id="pp-image-prompt"></div>
  <button class="copy-btn" onclick="copyText('pp-image-prompt')">COPY</button>
  <div class="panel-label">TRANSITION PROMPT</div>
  <div class="panel-text" id="pp-trans-prompt"></div>
  <button class="copy-btn" onclick="copyText('pp-trans-prompt')">COPY</button>
  <div style="margin-top:24px;">
    <button class="hud-btn" onclick="togglePromptPanel()">CLOSE</button>
  </div>
</div>

<div id="key-hints">
  SPACE / &rarr; &mdash; NEXT<br>
  &larr; &mdash; PREV<br>
  G &mdash; GRID<br>
  P &mdash; PROMPTS<br>
  F &mdash; FULLSCREEN<br>
  ESC &mdash; CLOSE
</div>

<script>
// ---- DATA (all images and videos embedded as base64) ----
const SLIDES = {slides_js};

// ---- STATE ----
let current = 0;
let transitioning = false;
const TOTAL = SLIDES.length;

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {{
  buildDots();
  buildOverviewGrid();
  showSlide(0, false);
  setupCursor();
  setupKeys();
}});

// ---- SLIDE DISPLAY ----
function showSlide(index, animate) {{
  if (animate === undefined) animate = true;
  if (index < 0 || index >= TOTAL) return;
  current = index;
  const slide = SLIDES[current];

  const img = document.getElementById('slide-image');
  const fallback = document.getElementById('slide-fallback');

  if (slide._image_data) {{
    img.src = slide._image_data;
    img.style.display = 'block';
    fallback.style.display = 'none';
  }} else {{
    img.style.display = 'none';
    fallback.style.display = 'flex';
    document.getElementById('fallback-title').textContent = slide.title;
    document.getElementById('fallback-subtitle').textContent = slide.subtitle;
  }}

  if (animate) img.classList.add('fade-in');
  setTimeout(() => img.classList.remove('fade-in'), 800);

  updateHUD();
  updatePromptPanel();
}}

// ---- NAVIGATION ----
function nextSlide() {{
  if (transitioning || current >= TOTAL - 1) return;
  const slide = SLIDES[current];

  if (slide._video_data) {{
    playTransition(slide._video_data, () => showSlide(current + 1));
  }} else {{
    showSlide(current + 1);
  }}
}}

function prevSlide() {{
  if (transitioning || current <= 0) return;
  showSlide(current - 1);
}}

function jumpTo(index) {{
  if (index === current) return;
  showSlide(index);
  toggleOverview();
}}

// ---- TRANSITION VIDEO ----
function playTransition(dataUrl, onEnd) {{
  transitioning = true;
  const video = document.getElementById('transition-video');
  video.src = dataUrl;
  video.style.display = 'block';
  video.play().catch(() => {{
    video.style.display = 'none';
    transitioning = false;
    onEnd();
  }});
  video.onended = () => {{
    video.style.display = 'none';
    video.src = '';
    transitioning = false;
    onEnd();
  }};
  // Safety timeout 7s
  setTimeout(() => {{
    if (transitioning) {{
      video.style.display = 'none';
      video.src = '';
      transitioning = false;
      onEnd();
    }}
  }}, 7000);
}}

// ---- HUD ----
function updateHUD() {{
  document.getElementById('slide-counter').textContent =
    'SLIDE ' + String(current+1).padStart(2,'0') + ' / ' + String(TOTAL).padStart(2,'0');

  const dots = document.querySelectorAll('.dot');
  dots.forEach((dot, i) => {{
    dot.classList.remove('current', 'visited');
    if (i === current) dot.classList.add('current');
    else if (i < current) dot.classList.add('visited');
  }});

  const pct = ((current + 1) / TOTAL) * 100;
  document.getElementById('progress-bar').style.width = pct + '%';
}}

function buildDots() {{
  const track = document.getElementById('dot-track');
  for (let i = 0; i < TOTAL; i++) {{
    const dot = document.createElement('div');
    dot.className = 'dot';
    dot.title = SLIDES[i].title;
    dot.onclick = () => jumpTo(i);
    track.appendChild(dot);
  }}
}}

// ---- OVERVIEW GRID ----
function buildOverviewGrid() {{
  const grid = document.getElementById('overview-grid');
  SLIDES.forEach((slide, i) => {{
    const card = document.createElement('div');
    card.className = 'overview-card';
    card.onclick = () => jumpTo(i);
    if (slide._image_data) {{
      const img = document.createElement('img');
      img.src = slide._image_data;
      card.appendChild(img);
    }}
    const num = document.createElement('div');
    num.className = 'card-num';
    num.textContent = String(i+1).padStart(2,'0');
    card.appendChild(num);
    grid.appendChild(card);
  }});
}}

function toggleOverview() {{
  document.getElementById('overview').classList.toggle('visible');
}}

// ---- PROMPT PANEL ----
function updatePromptPanel() {{
  const slide = SLIDES[current];
  document.getElementById('pp-image-prompt').textContent = slide.image_prompt || '(none)';
  document.getElementById('pp-trans-prompt').textContent = slide.transition_prompt || '(none)';
}}

function togglePromptPanel() {{
  document.getElementById('prompt-panel').classList.toggle('visible');
  updatePromptPanel();
}}

function copyText(id) {{
  const text = document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).catch(() => {{}});
}}

// ---- KEYBOARD ----
function setupKeys() {{
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); nextSlide(); }}
    else if (e.key === 'ArrowLeft') prevSlide();
    else if (e.key.toLowerCase() === 'g') toggleOverview();
    else if (e.key.toLowerCase() === 'p') togglePromptPanel();
    else if (e.key.toLowerCase() === 'f') document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
    else if (e.key === 'Escape') {{
      document.getElementById('overview').classList.remove('visible');
      document.getElementById('prompt-panel').classList.remove('visible');
      document.exitFullscreen && document.exitFullscreen();
    }}
  }});
}}

// ---- CURSOR ----
function setupCursor() {{
  const cur = document.getElementById('cursor');
  const ring = document.getElementById('cursor-ring');
  document.addEventListener('mousemove', (e) => {{
    cur.style.left = e.clientX + 'px';
    cur.style.top = e.clientY + 'px';
    ring.style.left = e.clientX + 'px';
    ring.style.top = e.clientY + 'px';
  }});
  document.addEventListener('mousedown', () => {{
    cur.style.transform = 'translate(-50%,-50%) scale(1.8)';
  }});
  document.addEventListener('mouseup', () => {{
    cur.style.transform = 'translate(-50%,-50%) scale(1)';
  }});
}}
</script>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    print(f"[OK] Stage 4 complete: {output_path} ({len(slides)} slides embedded)")


if __name__ == "__main__":
    import sys
    deck_dir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("output/test-deck")
    build_player(deck_dir, deck_dir / "player.html")
