#!/usr/bin/env python3
"""goot27 / WokSpec — Ctrl+C to exit"""
import os, sys, time, random, signal, shutil, math

if sys.platform == 'win32':
    os.system('')
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

RESET = '\033[0m'
HIDE  = '\033[?25l'
SHOW  = '\033[?25h'

PINK_NC  = ['\033[2m\033[35m', '\033[35m']
GREY_NC  = ['\033[90m', '\033[2m\033[37m']
G_WAVE   = '\033[38;5;213m\033[1m'
G_LOGO   = '\033[97m\033[1m'
W_WAVE   = '\033[38;5;208m\033[1m'
W_LOGO   = '\033[38;5;214m\033[1m'
CD_WAVE  = '\033[38;5;219m\033[1m'   # soft pink flash for countdown
CD_LOGO  = '\033[38;5;225m\033[1m'   # pale white-pink for countdown digits

GLYPHS = {
    'g': ['╔═════╗','║     ║','║      ','║ ════╣','║     ║','╚═════╝'],
    'o': ['╔═════╗','║     ║','║     ║','║     ║','║     ║','╚═════╝'],
    't': ['═══╦═══','   ║   ','   ║   ','   ║   ','   ║   ','   ╩   '],
    '2': ['╔═════╗','      ║','╔═════╝','║      ','║      ','╚══════'],
    '7': ['══════╗','      ║','   ╔══╝','   ║   ','   ║   ','   ╩   '],
    '1': ['   ╔═══','   ║   ','   ║   ','   ║   ','   ║   ','═══╩═══'],
    '3': ['╔═════╗','      ║','╠═════╣','      ║','      ║','╚═════╝'],
    'W': ['╗   ╔╗   ╔','║   ║║   ║','╚╗  ║║  ╔╝',' ╚══╝╚══╝ ','          ','          '],
    'k': ['║     ╔','║    ╔╝','║   ╔╝ ','╠═══╝  ','║   ╚╗ ','║    ╚═'],
    'S': ['╔═════╗','║      ','║      ','╚═════╗','      ║','╚═════╝'],
    'p': ['╔═════╗','║     ║','║     ║','╠═════╝','║      ','╩      '],
    'e': ['╔═════╗','║     ║','╠══════','║      ','║      ','╚═════╗'],
    'c': ['╔═════╗','║      ','║      ','║      ','║      ','╚═════╝'],
}
NROWS = 6
SEP   = '  '

def make_art(word):
    rows = ['' for _ in range(NROWS)]
    for i, ch in enumerate(word):
        if ch not in GLYPHS: continue
        for r in range(NROWS): rows[r] += GLYPHS[ch][r]
        if i < len(word) - 1:
            for r in range(NROWS): rows[r] += SEP
    w = max(len(r) for r in rows)
    return [r.ljust(w) for r in rows]

GOOT27  = make_art('goot27')
WOKSPEC = make_art('WokSpec')

def birth_times(art):
    positions = [(r, c) for r, row in enumerate(art)
                 for c, ch in enumerate(row) if ch != ' ']
    random.shuffle(positions)
    n = len(positions)
    bt = {}
    for i, (r, c) in enumerate(positions):
        bt[(r, c)] = i / max(n - 1, 1)
    return bt

def noise(n, nc):
    return ''.join(random.choice(nc) + random.choice('27') + RESET
                   for _ in range(max(n, 0)))

def build(t, art, bt, wc, lc, nc):
    TW, TH = shutil.get_terminal_size((80, 24))
    aw  = max(len(l) for l in art)
    lp  = max(0, (TW - aw) // 2)
    rp  = max(0, TW - lp - aw)
    mid = max(0, (TH - NROWS) // 2)
    lines = []
    for row in range(TH):
        rel = row - mid
        if 0 <= rel < NROWS:
            parts = [noise(lp, nc)]
            for col, ch in enumerate(art[rel]):
                b = bt.get((rel, col), 1.0)
                if ch == ' ':
                    parts.append(' ' if t > b else noise(1, nc))
                elif t >= b + 0.08:
                    parts.append(lc + ch + RESET)
                elif t >= b:
                    parts.append(wc + ch + RESET)
                else:
                    parts.append(noise(1, nc))
            parts.append(noise(rp, nc))
            lines.append(''.join(parts))
        else:
            lines.append(noise(TW, nc))
    return '\n'.join(lines)

def flood(secs, nc):
    TW, _ = shutil.get_terminal_size((80, 24))
    end   = time.time() + secs
    while time.time() < end:
        sys.stdout.write(noise(TW, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.010)

def transition(secs, a, b):
    TW, _ = shutil.get_terminal_size((80, 24))
    end   = time.time() + secs
    while time.time() < end:
        frac = 1.0 - (end - time.time()) / secs
        sys.stdout.write(noise(TW, b if random.random() < frac else a) + '\n')
        sys.stdout.flush()
        time.sleep(0.010)

def animate_in(art, wc, lc, nc, steps=40, fps=0.045):
    bt = birth_times(art)
    sys.stdout.write('\033[2J\033[H')
    for i in range(steps):
        t = i / (steps - 1)
        sys.stdout.write('\033[H' + build(t, art, bt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(fps)
    return bt

def hold(secs, art, bt, wc, lc, nc):
    end = time.time() + secs
    while time.time() < end:
        sys.stdout.write('\033[H' + build(1.0, art, bt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.07)

def animate_out(art, bt, wc, lc, nc, steps=28, fps=0.045):
    for i in range(steps):
        t = 1.0 - i / (steps - 1)
        sys.stdout.write('\033[H' + build(t, art, bt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(fps)

# ── Countdown ──────────────────────────────────────────────────────────────
def countdown():
    """3 … 2 … 1 — each digit crystallises then dissolves."""
    for digit in ('3', '2', '1'):
        art = make_art(digit)
        bt  = animate_in(art, CD_WAVE, CD_LOGO, PINK_NC, steps=22, fps=0.038)
        hold(0.55, art, bt, CD_WAVE, CD_LOGO, PINK_NC)
        animate_out(art, bt, CD_WAVE, CD_LOGO, PINK_NC, steps=14, fps=0.035)

# ── Reactor wild animation ─────────────────────────────────────────────────
REACTOR_PALETTE = [
    '\033[97m\033[1m',           # white   — leading edge
    '\033[38;5;213m\033[1m',     # hot pink
    '\033[38;5;207m\033[1m',     # pink
    '\033[35m',                  # medium pink
    '\033[2m\033[35m',           # dim pink
    '\033[2m\033[35m',           # dim  (gap)
    '\033[2m\033[35m',           # dim  (gap)
    '\033[2m\033[35m',           # dim  (gap)
]
NP = len(REACTOR_PALETTE)

def reactor(secs):
    """Expanding rings of 2/7 radiate from centre; speed ramps up to climax."""
    TW, TH = shutil.get_terminal_size((80, 24))
    cx, cy  = TW // 2, TH // 2
    start   = time.time()
    end     = start + secs
    frame   = 0
    while time.time() < end:
        elapsed = time.time() - start
        speed   = 2.5 + elapsed * 2.2          # accelerate over time
        lines   = []
        for row in range(TH):
            parts = []
            for col in range(TW):
                dx   = abs(col - cx)
                dy   = abs(row - cy) * 2        # compensate char aspect ratio
                dist = max(dx, dy)              # Chebyshev → rectangular rings
                idx  = int(dist - elapsed * speed) % NP
                color = REACTOR_PALETTE[idx]
                ch    = '7' if (col + row + dist) % 3 == 0 else '2'
                parts.append(color + ch + RESET)
            lines.append(''.join(parts))
        sys.stdout.write('\033[2J\033[H' + '\n'.join(lines) + '\n')
        sys.stdout.flush()
        time.sleep(0.033)
        frame += 1

def white_flash(secs=0.28):
    """Full-screen white-hot flash."""
    TW, TH = shutil.get_terminal_size((80, 24))
    line   = '\033[97m\033[1m' + '2' * TW + RESET
    block  = '\n'.join([line] * TH)
    end    = time.time() + secs
    while time.time() < end:
        sys.stdout.write('\033[H' + block + '\n')
        sys.stdout.flush()
        time.sleep(0.045)

# ── Signal / main loop ─────────────────────────────────────────────────────
signal.signal(signal.SIGINT,
              lambda *_: (sys.stdout.write(SHOW + RESET + '\n'), sys.exit(0)))
sys.stdout.write(HIDE)

while True:
    flood(1.5, PINK_NC)
    countdown()
    flood(0.4, PINK_NC)
    bt = animate_in(GOOT27,  G_WAVE, G_LOGO, PINK_NC)
    hold(2.5,   GOOT27,  bt, G_WAVE, G_LOGO, PINK_NC)
    animate_out(GOOT27,  bt, G_WAVE, G_LOGO, PINK_NC)
    transition(1.5, PINK_NC, GREY_NC)
    flood(0.8, GREY_NC)
    bt = animate_in(WOKSPEC, W_WAVE, W_LOGO, GREY_NC)
    hold(2.5,   WOKSPEC, bt, W_WAVE, W_LOGO, GREY_NC)
    animate_out(WOKSPEC, bt, W_WAVE, W_LOGO, GREY_NC)
    transition(1.0, GREY_NC, PINK_NC)
    reactor(4.5)
    white_flash(0.28)
    flood(1.0, PINK_NC)
