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

# ── noise palettes ─────────────────────────────────────────────────────────
PINK_NC = ['\033[2m\033[35m', '\033[2m\033[95m', '\033[35m']
GREY_NC = ['\033[90m', '\033[2m\033[37m', '\033[37m']

# ── logo colors ────────────────────────────────────────────────────────────
G_WAVE = '\033[95m\033[1m'          # goot27 wave front  — bright magenta
G_LOGO = '\033[97m\033[1m'          # goot27 revealed    — bright white

W_WAVE = '\033[38;5;208m\033[1m'    # WokSpec wave front — orange
W_LOGO = '\033[38;5;214m\033[1m'    # WokSpec revealed   — gold/orange

# ── art ────────────────────────────────────────────────────────────────────
GOOT27 = [
    r" ██████╗  ██████╗  ██████╗ ████████╗██████╗  ███████╗",
    r"██╔════╝ ██╔═══██╗██╔═══██╗╚══██╔══╝╚════██╗ ╚════██║",
    r"██║  ███╗██║   ██║██║   ██║   ██║    █████╔╝     ██╔╝",
    r"██║   ██║██║   ██║██║   ██║   ██║   ██╔═══╝     ██╔╝ ",
    r"╚██████╔╝╚██████╔╝╚██████╔╝   ██║   ███████╗    ██║  ",
    r" ╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝    ╚═╝  ",
]

WOKSPEC = [
    r" ██╗    ██╗ ██████╗ ██╗  ██╗███████╗██████╗ ███████╗ ██████╗ ",
    r" ██║    ██║██╔═══██╗██║ ██╔╝██╔════╝██╔══██╗██╔════╝██╔════╝ ",
    r" ██║ █╗ ██║██║   ██║█████╔╝ ███████╗██████╔╝█████╗  ██║      ",
    r" ██║███╗██║██║   ██║██╔═██╗ ╚════██║██╔═══╝ ██╔══╝  ██║      ",
    r" ╚███╔███╔╝╚██████╔╝██║  ██╗███████║██║     ███████╗╚██████╗ ",
    r"  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝ ",
]

# ── helpers ────────────────────────────────────────────────────────────────
def noise(n, nc):
    return ''.join(random.choice(nc) + random.choice('27') + RESET
                   for _ in range(n))

def build(reveal, art, wc, lc, nc):
    W, H = shutil.get_terminal_size((80, 24))
    aw   = max(len(l) for l in art)
    lp   = max(0, (W - aw) // 2)
    rp   = max(0, W - lp - aw)
    mid  = max(0, (H - len(art)) // 2)
    lines = []
    for row in range(H):
        rel = row - mid
        if 0 <= rel < len(art):
            rr   = max(0.0, min(1.0, reveal - rel * 0.07))
            wave = rr * aw
            parts = [noise(lp, nc)]
            for col, ch in enumerate(art[rel]):
                dist = wave - col
                if ch == ' ':
                    parts.append(' ' if dist > 0
                                 else random.choice(nc) + random.choice('27') + RESET)
                elif dist > 6:
                    parts.append(lc + ch + RESET)
                elif dist > 0:
                    parts.append(wc + ch + RESET)
                else:
                    parts.append(random.choice(nc) + random.choice('27') + RESET)
            parts.append(noise(rp, nc))
            lines.append(''.join(parts))
        else:
            lines.append(noise(W, nc))
    return '\n'.join(lines)

def flood(secs, nc):
    W, _ = shutil.get_terminal_size((80, 24))
    end  = time.time() + secs
    while time.time() < end:
        sys.stdout.write(noise(W, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.010)

def transition(secs, from_nc, to_nc):
    W, _ = shutil.get_terminal_size((80, 24))
    end  = time.time() + secs
    while time.time() < end:
        t  = 1.0 - (end - time.time()) / secs
        nc = to_nc if random.random() < t else from_nc
        sys.stdout.write(noise(W, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.010)

def animate(steps, r0, r1, art, wc, lc, nc):
    sys.stdout.write('\033[2J\033[H')
    for i in range(steps):
        r = r0 + (r1 - r0) * i / max(steps - 1, 1)
        sys.stdout.write('\033[H' + build(r, art, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.055)

def hold(secs, art, wc, lc, nc):
    end = time.time() + secs
    while time.time() < end:
        sys.stdout.write('\033[H' + build(1.0, art, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.07)

signal.signal(signal.SIGINT,
              lambda *_: (sys.stdout.write(SHOW + RESET + '\n'), sys.exit(0)))
sys.stdout.write(HIDE)

while True:
    # ── goot27 ── pink 27 flood → white logo forms → dissolves
    flood(2.5,  PINK_NC)
    animate(32, 0.0, 1.0, GOOT27, G_WAVE, G_LOGO, PINK_NC)
    hold(2.5,              GOOT27, G_WAVE, G_LOGO, PINK_NC)
    animate(22, 1.0, 0.0, GOOT27, G_WAVE, G_LOGO, PINK_NC)

    # ── gradient pink → grey ──
    transition(1.5, PINK_NC, GREY_NC)

    # ── WokSpec ── grey 27 flood → orange logo forms → dissolves
    flood(1.0,  GREY_NC)
    animate(32, 0.0, 1.0, WOKSPEC, W_WAVE, W_LOGO, GREY_NC)
    hold(2.5,               WOKSPEC, W_WAVE, W_LOGO, GREY_NC)
    animate(22, 1.0, 0.0, WOKSPEC, W_WAVE, W_LOGO, GREY_NC)

    # ── gradient grey → pink ──
    transition(1.5, GREY_NC, PINK_NC)
