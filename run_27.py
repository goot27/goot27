#!/usr/bin/env python3
"""goot27 — Ctrl+C to exit"""
import os, sys, time, random, signal, shutil

if sys.platform == 'win32':
    os.system('')
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

PINK  = '\033[38;5;211m'
WHITE = '\033[97m\033[1m'
RESET = '\033[0m'
HIDE  = '\033[?25l'
SHOW  = '\033[?25h'

ART = [
    r" ██████╗  ██████╗  ██████╗ ████████╗██████╗  ███████╗",
    r"██╔════╝ ██╔═══██╗██╔═══██╗╚══██╔══╝╚════██╗ ╚════██║",
    r"██║  ███╗██║   ██║██║   ██║   ██║    █████╔╝     ██╔╝",
    r"██║   ██║██║   ██║██║   ██║   ██║   ██╔═══╝     ██╔╝ ",
    r"╚██████╔╝╚██████╔╝╚██████╔╝   ██║   ███████╗    ██║  ",
    r" ╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝    ╚═╝  ",
]
AW = max(len(l) for l in ART)

def noise(n):
    return ''.join(PINK + c + RESET for c in random.choices('27', k=n))

def frame(reveal):
    W, H = shutil.get_terminal_size((80, 24))
    lp = max(0, (W - AW) // 2)
    rp = max(0, W - lp - AW)
    mid = max(0, (H - len(ART)) // 2)
    lines = []
    for row in range(H):
        rel = row - mid
        if 0 <= rel < len(ART):
            parts = [noise(lp)]
            for ch in ART[rel]:
                if random.random() < reveal and ch != ' ':
                    parts.append(WHITE + ch + RESET)
                else:
                    parts.append(' ' if ch == ' ' and random.random() < reveal
                                 else PINK + random.choice('27') + RESET)
            parts.append(noise(rp))
            lines.append(''.join(parts))
        else:
            lines.append(noise(W))
    return '\n'.join(lines)

def flood(secs):
    W, _ = shutil.get_terminal_size((80, 24))
    end = time.time() + secs
    while time.time() < end:
        sys.stdout.write(noise(W) + '\n')
        sys.stdout.flush()
        time.sleep(0.010)

def animate(steps, r0, r1, fps=0.05):
    sys.stdout.write('\033[2J\033[H')
    for i in range(steps):
        r = r0 + (r1 - r0) * i / max(steps - 1, 1)
        sys.stdout.write('\033[H' + frame(r) + '\n')
        sys.stdout.flush()
        time.sleep(fps)

def hold(secs):
    end = time.time() + secs
    while time.time() < end:
        sys.stdout.write('\033[H' + frame(1.0) + '\n')
        sys.stdout.flush()
        time.sleep(0.07)

signal.signal(signal.SIGINT, lambda *_: (sys.stdout.write(SHOW + RESET + '\n'), sys.exit(0)))
sys.stdout.write(HIDE)

while True:
    flood(2.5)
    animate(30, 0.0, 1.0)   # form from noise
    hold(2.0)                # logo floats in live noise
    animate(20, 1.0, 0.0)   # dissolve back
