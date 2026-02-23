#!/usr/bin/env python3
"""goot27 — press Ctrl+C to exit"""
import os, sys, time, random, signal, shutil

# ── Enable ANSI on Windows ─────────────────────────────────────────────────
if sys.platform == 'win32':
    os.system('')
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# ── ANSI ───────────────────────────────────────────────────────────────────
R    = '\033[0m'
HIDE = '\033[?25l'
SHOW = '\033[?25h'
HOME = '\033[H'
CLR  = '\033[2J\033[H'
BOLD = '\033[1m'

DP  = '\033[38;5;175m'   # dim pink    — background noise
MP  = '\033[38;5;205m'   # mid pink
HP  = '\033[38;5;199m'   # hot pink    — logo
WH  = '\033[97m'          # white
CY  = '\033[96m'          # cyan        — Chopsticks
GD  = '\033[93m'          # gold        — WokGen

# ── Terminal size ──────────────────────────────────────────────────────────
W, H = shutil.get_terminal_size((80, 24))
W = max(W, 64); H = max(H, 20)

# ── ASCII art ──────────────────────────────────────────────────────────────
LOGO = [
    r" ██████╗  ██████╗  ██████╗ ████████╗██████╗  ███████╗",
    r"██╔════╝ ██╔═══██╗██╔═══██╗╚══██╔══╝╚════██╗ ╚════██║",
    r"██║  ███╗██║   ██║██║   ██║   ██║    █████╔╝     ██╔╝",
    r"██║   ██║██║   ██║██║   ██║   ██║   ██╔═══╝     ██╔╝ ",
    r"╚██████╔╝╚██████╔╝╚██████╔╝   ██║   ███████╗    ██║  ",
    r" ╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝    ╚═╝  ",
    r"              ·  2  ·  7  ·  2  ·  7  ·              ",
]
LOGO_W = max(len(l) for l in LOGO)

# ── Noise ──────────────────────────────────────────────────────────────────
_NC = [DP, MP, '\033[38;5;211m', '\033[38;5;213m', '\033[38;5;218m']
_CH = list('2272777272272727')

def nr(w=None):
    return ''.join(random.choice(_NC) + random.choice(_CH) + R
                   for _ in range(w or W))

def np_(n):
    if n <= 0:
        return ''
    return ''.join(random.choice(_NC) + random.choice(_CH) + R
                   for _ in range(n))

# ── I/O ────────────────────────────────────────────────────────────────────
def put(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def cleanup(*_):
    put(SHOW + R + '\n')
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
put(HIDE)

# ── Phase: FLOOD ───────────────────────────────────────────────────────────
def phase_flood(secs=2.0):
    end = time.time() + secs
    while time.time() < end:
        put(nr() + '\n')
        time.sleep(random.uniform(0.004, 0.010))

# ── Phase: LOGO emerge from noise ──────────────────────────────────────────
def phase_logo(frames=30):
    lpad = max(0, (W - LOGO_W) // 2)
    rpad = max(0, W - lpad - LOGO_W)
    logo_row = max(0, (H - len(LOGO)) // 2)

    for f in range(frames):
        reveal = f / (frames - 1)
        buf = [CLR if f == 0 else HOME]
        for row in range(H):
            rel = row - logo_row
            if 0 <= rel < len(LOGO):
                line = LOGO[rel]
                out = [np_(lpad)]
                for ch in line:
                    if ch == ' ':
                        if random.random() < reveal * 0.7:
                            out.append(' ')
                        else:
                            out.append(random.choice(_NC) + random.choice(_CH) + R)
                    else:
                        if random.random() < reveal:
                            out.append(HP + BOLD + ch + R)
                        else:
                            out.append(random.choice(_NC) + random.choice(_CH) + R)
                out.append(np_(rpad))
                buf.append(''.join(out))
            else:
                buf.append(nr())
            buf.append('\n')
        put(''.join(buf))
        time.sleep(0.055)

    # Hold final clean frame
    buf = [HOME]
    for row in range(H):
        rel = row - logo_row
        if 0 <= rel < len(LOGO):
            lp = ' ' * lpad
            rp = ' ' * max(0, rpad)
            buf.append(lp + HP + BOLD + LOGO[rel] + R + rp)
        else:
            buf.append(nr())
        buf.append('\n')
    put(''.join(buf))
    time.sleep(1.4)

# ── Phase: SLIDE ───────────────────────────────────────────────────────────
def phase_slide(title, lines, accent, hold=2.4):
    inner_w = max(len(title), max(len(l) for l in lines)) + 4
    bx = max(0, (W - inner_w) // 2)
    by = max(0, (H - len(lines) - 4) // 2)
    rx = max(0, W - bx - inner_w)
    total_box = len(lines) + 4

    def box_row(rel):
        if rel == 0:
            return np_(bx) + accent + BOLD + '╔' + '═' * (inner_w - 2) + '╗' + R + np_(rx)
        if rel == 1:
            label = (' ' + title).ljust(inner_w - 2)
            return np_(bx) + accent + BOLD + '║' + WH + BOLD + label + accent + '║' + R + np_(rx)
        if rel == 2:
            return np_(bx) + accent + '╠' + '═' * (inner_w - 2) + '╣' + R + np_(rx)
        if 3 <= rel < 3 + len(lines):
            txt = (' ' + lines[rel - 3]).ljust(inner_w - 2)
            return np_(bx) + accent + '║' + WH + txt + accent + '║' + R + np_(rx)
        if rel == 3 + len(lines):
            return np_(bx) + accent + BOLD + '╚' + '═' * (inner_w - 2) + '╝' + R + np_(rx)
        return nr()

    end = time.time() + hold
    first = True
    while time.time() < end:
        buf = [CLR if first else HOME]
        first = False
        for row in range(H):
            rel = row - by
            buf.append(box_row(rel) if 0 <= rel <= total_box else nr())
            buf.append('\n')
        put(''.join(buf))
        time.sleep(0.09)

# ── Slides ─────────────────────────────────────────────────────────────────
SLIDES = [
    (
        '  goot27  ',
        ['  code  ·  sleep  ·  repeat  ',
         '  2  7  2  7  2  7  2  7     ',
         '  github.com/goot27          '],
        HP,
    ),
    (
        '  Chopsticks  ',
        ['  WokSpec workflow toolkit   ',
         '  2  7  2  7  2  7  2  7     ',
         '  github.com/goot27          '],
        CY,
    ),
    (
        '  WokGen  ',
        ['  code generation engine     ',
         '  2  7  2  7  2  7  2  7     ',
         '  github.com/WokSpec          '],
        GD,
    ),
]

# ── Main loop ──────────────────────────────────────────────────────────────
idx = 0
while True:
    phase_flood(2.0)
    phase_logo(frames=30)
    phase_flood(0.8)
    phase_slide(*SLIDES[idx % len(SLIDES)])
    idx += 1
