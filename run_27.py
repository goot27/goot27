#!/usr/bin/env python3
"""goot27 — Ctrl+C to exit"""
import os, sys, time, random, signal, shutil

# Windows ANSI
if sys.platform == 'win32':
    os.system('')
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

R    = '\033[0m'
HIDE = '\033[?25l'
SHOW = '\033[?25h'
BOLD = '\033[1m'
HP   = '\033[38;5;199m'   # hot pink — logo

_NC = ['\033[97m',          # white
       '\033[38;5;205m',    # hot pink
       '\033[38;5;211m',    # pink
       '\033[38;5;213m',    # light pink
       '\033[38;5;218m']    # blush

W, H = shutil.get_terminal_size((80, 24))
W = max(W, 64)

LOGO = [
    r" ██████╗  ██████╗  ██████╗ ████████╗██████╗  ███████╗",
    r"██╔════╝ ██╔═══██╗██╔═══██╗╚══██╔══╝╚════██╗ ╚════██║",
    r"██║  ███╗██║   ██║██║   ██║   ██║    █████╔╝     ██╔╝",
    r"██║   ██║██║   ██║██║   ██║   ██║   ██╔═══╝     ██╔╝ ",
    r"╚██████╔╝╚██████╔╝╚██████╔╝   ██║   ███████╗    ██║  ",
    r" ╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝    ╚═╝  ",
]
LOGO_W = max(len(l) for l in LOGO)
lpad = max(0, (W - LOGO_W) // 2)
rpad = max(0, W - lpad - LOGO_W)
LOGO_CENTER = [HP + BOLD + l + R for l in LOGO]

def nr(w=None):
    n = w or W
    return ''.join(c + d + R
                   for c, d in zip(random.choices(_NC, k=n),
                                   random.choices('27', k=n)))

def logo_line(i):
    return nr(lpad) + LOGO_CENTER[i] + nr(rpad)

def cleanup(*_):
    sys.stdout.write(SHOW + R + '\n')
    sys.stdout.flush()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
sys.stdout.write(HIDE)

# Pre-built noise pool so generation stays fast
POOL = [nr().encode() for _ in range(80)]
NL   = b'\n'
GAP  = max(H - len(LOGO), 6)   # noise rows between logo passes
out  = sys.stdout.buffer

row = 0
while True:
    pos = row % (GAP + len(LOGO))
    if pos < len(LOGO):
        # Logo row — regenerate sides each time so noise around it stays live
        out.write(logo_line(pos).encode() + NL)
        out.flush()
        time.sleep(0.018)
    else:
        # Batch 3 noise rows per write to reduce syscall overhead
        chunk = (random.choice(POOL) + NL +
                 random.choice(POOL) + NL +
                 random.choice(POOL) + NL)
        out.write(chunk)
        out.flush()
        time.sleep(0.022)
        row += 2  # account for extra rows in batch
    row += 1
