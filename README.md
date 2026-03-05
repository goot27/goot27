<img src="assets/rain.svg" width="100%"/>

<div align="center">

[![Profile Views](https://komarev.com/ghpvc/?username=goot27&style=flat-square&color=ff79c6&label=visitors&labelColor=0d0d1a)](https://github.com/goot27)
&nbsp;
[![X](https://img.shields.io/badge/@goot27-0d0d1a?style=flat-square&logo=x&logoColor=ffffff)](https://twitter.com/goot27)
&nbsp;
[![WokSpec](https://img.shields.io/badge/WokSpec-2d2d2d?style=flat-square&logo=github&logoColor=d4612a)](https://github.com/WokSpec)

# goot27 terminal show
### zero deps • pure python • full-screen ANSI art + snake

</div>

<div align="center">
<img src="https://raw.githubusercontent.com/goot27/goot27/output/github-contribution-grid-snake-dark.svg" width="100%"/>
</div>

<div align="center">
<img src="assets/terminal.svg" width="100%"/>
</div>

## What this is
`run_27.py` is a self-contained terminal experience made from Python standard library only.

It runs a cinematic sequence built from animated `2` and `7` glyphs:
- starfield warp
- 3-2-1 countdown
- shockwave pulse
- ASCII logo reveals (`goot27`, `WokSpec`)
- expanding/collapsing ring systems
- white flash + glitchy transitions
- interactive menu that can launch Snake

No external packages, no assets required at runtime, no install step.

## Quick start
### Local (recommended)
```bash
git clone https://github.com/goot27/goot27.git
cd goot27
python3 run_27.py
```

### One-liner (Linux / macOS / WSL)
```bash
curl -fsSL https://raw.githubusercontent.com/goot27/goot27/main/run_27.py | python3
```

### One-liner (Windows PowerShell)
```powershell
python -c "import urllib.request as r; exec(r.urlopen('https://raw.githubusercontent.com/goot27/goot27/main/run_27.py').read().decode())"
```

## Controls
### During intro/menu
- `s`: launch snake
- `Enter`: replay animation loop
- `Ctrl+C`: quit

### In snake
- move: `WASD` or arrow keys
- `r`: restart
- `q`: quit

## Requirements
- Python `3.8+`
- A terminal with ANSI color support
- UTF-8 capable font/terminal (box drawing glyphs look best in modern terminals)

Works on:
- Linux
- macOS
- WSL
- Windows Terminal / PowerShell (with ANSI enabled)

## Repo layout
- `run_27.py`: animation engine + snake game
- `assets/`: profile graphics used by this README
- `.github/workflows/snake.yml`: regenerates contribution snake SVG to `output` branch

## Tweak it
Everything is in one file by design. Easy places to customize:
- colors: `PINK_NC`, `PINK_RINGS`, `GOLD_RINGS`, `G_WAVE`, `W_WAVE`
- timings: function args in the main loop at bottom of `run_27.py`
- glyph art: `GLYPHS` map + `make_art(...)`
- snake speed/feel: `speed` calculation inside `snake_game()`

## Troubleshooting
- Garbled characters:
  - switch terminal encoding to UTF-8
  - use a font with box-drawing support (JetBrains Mono, Cascadia Mono, Fira Code)
- No color on Windows:
  - run inside Windows Terminal or recent PowerShell
- Controls not responding:
  - run in a real terminal, not a limited IDE output pane
- Very small terminal:
  - maximize window for cleaner framing and gameplay space

<div align="center">

# 🍚 I LOVE CHICKEN RICE 🍗

</div>

<img src="assets/ticker.svg" width="100%"/>
<img src="assets/tiles.svg" width="100%" alt="2 7"/>
