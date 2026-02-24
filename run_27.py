#!/usr/bin/env python3
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

W, H  = shutil.get_terminal_size((80, 24))

ART = [
    r" ██████╗  ██████╗  ██████╗ ████████╗██████╗  ███████╗",
    r"██╔════╝ ██╔═══██╗██╔═══██╗╚══██╔══╝╚════██╗ ╚════██║",
    r"██║  ███╗██║   ██║██║   ██║   ██║    █████╔╝     ██╔╝",
    r"██║   ██║██║   ██║██║   ██║   ██║   ██╔═══╝     ██╔╝ ",
    r"╚██████╔╝╚██████╔╝╚██████╔╝   ██║   ███████╗    ██║  ",
    r" ╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝    ╚═╝  ",
]
AW   = max(len(l) for l in ART)
lpad = max(0, (W - AW) // 2)
rpad = max(0, W - lpad - AW)

def noise(n):
    return ''.join(PINK + c + RESET for c in random.choices('27', k=n))

def art_line(i):
    return noise(lpad) + WHITE + ART[i] + RESET + noise(rpad)

signal.signal(signal.SIGINT, lambda *_: (sys.stdout.write(SHOW + RESET + '\n'), sys.exit(0)))
sys.stdout.write(HIDE)

GAP = max(H, 8)
row = 0
while True:
    pos = row % (GAP + len(ART))
    sys.stdout.write((art_line(pos) if pos < len(ART) else noise(W)) + '\n')
    sys.stdout.flush()
    time.sleep(0.012)
    row += 1
