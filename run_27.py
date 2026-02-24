#!/usr/bin/env python3
"""goot27 / WokSpec — Ctrl+C to exit"""
import os, sys, time, random, signal, shutil

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

PINK_NC = ['\033[2m\033[35m', '\033[35m']
GREY_NC = ['\033[90m', '\033[2m\033[37m']
G_WAVE  = '\033[38;5;213m\033[1m'   # bright pink  — flash as char arrives
G_LOGO  = '\033[97m\033[1m'         # white        — settled logo
W_WAVE  = '\033[38;5;208m\033[1m'   # orange       — flash as char arrives
W_LOGO  = '\033[38;5;214m\033[1m'   # gold         — settled logo

GLYPHS = {
    'g': ['╔═════╗','║     ║','║      ','║ ════╣','║     ║','╚═════╝'],
    'o': ['╔═════╗','║     ║','║     ║','║     ║','║     ║','╚═════╝'],
    't': ['═══╦═══','   ║   ','   ║   ','   ║   ','   ║   ','   ╩   '],
    '2': ['╔═════╗','      ║','╔═════╝','║      ','║      ','╚══════'],
    '7': ['══════╗','      ║','   ╔══╝','   ║   ','   ║   ','   ╩   '],
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
    """Random reveal order: evenly spaced 0→1 shuffled across all logo chars."""
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
    """
    t = 0.0 → all noise
    t = 1.0 → all logo chars fully revealed
    Each char has a birth time; within 0.08 window it flashes wc then settles to lc.
    """
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
                    parts.append(lc + ch + RESET)   # settled
                elif t >= b:
                    parts.append(wc + ch + RESET)   # arriving flash
                else:
                    parts.append(noise(1, nc))       # not yet
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
    return bt   # reuse for hold + out

def hold(secs, art, bt, wc, lc, nc):
    end = time.time() + secs
    while time.time() < end:
        # t=1.0 → all chars settled to lc, noise churns around
        sys.stdout.write('\033[H' + build(1.0, art, bt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.07)

def animate_out(art, bt, wc, lc, nc, steps=28, fps=0.045):
    for i in range(steps):
        t = 1.0 - i / (steps - 1)
        sys.stdout.write('\033[H' + build(t, art, bt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(fps)

signal.signal(signal.SIGINT,
              lambda *_: (sys.stdout.write(SHOW + RESET + '\n'), sys.exit(0)))
sys.stdout.write(HIDE)

while True:
    flood(2.5, PINK_NC)
    bt = animate_in(GOOT27,  G_WAVE, G_LOGO, PINK_NC)
    hold(2.5,   GOOT27,  bt, G_WAVE, G_LOGO, PINK_NC)
    animate_out(GOOT27,  bt, G_WAVE, G_LOGO, PINK_NC)
    transition(1.5, PINK_NC, GREY_NC)
    flood(1.0, GREY_NC)
    bt = animate_in(WOKSPEC, W_WAVE, W_LOGO, GREY_NC)
    hold(2.5,   WOKSPEC, bt, W_WAVE, W_LOGO, GREY_NC)
    animate_out(WOKSPEC, bt, W_WAVE, W_LOGO, GREY_NC)
    transition(1.5, GREY_NC, PINK_NC)
