#!/usr/bin/env python3
"""goot27 — Ctrl+C to exit"""
import os, sys, time, random, signal, shutil, math

# ── Windows ANSI ─────────────────────────────────────────────────────────────
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
HOME  = '\033[H'
CLEAR = '\033[2J\033[H'

# ── Colour palettes ──────────────────────────────────────────────────────────
PINK_NC = ['\033[2m\033[35m', '\033[35m']
GREY_NC = ['\033[90m', '\033[2m\033[37m']

G_WAVE  = '\033[38;5;213m\033[1m'   # hot pink   — particle arrival
G_LOGO  = '\033[97m\033[1m'         # white       — goot27 settled
W_WAVE  = '\033[38;5;208m\033[1m'   # orange      — particle arrival
W_LOGO  = '\033[38;5;214m\033[1m'   # gold        — WokSpec settled
CD_WAVE = '\033[38;5;219m\033[1m'   # pink-purple — countdown arrival
CD_LOGO = '\033[38;5;225m\033[1m'   # pale white  — countdown settled

PINK_RINGS = [
    '\033[97m\033[1m',           # white  — leading edge
    '\033[38;5;213m\033[1m',     # hot pink
    '\033[38;5;207m\033[1m',     # pink
    '\033[35m',                  # medium
    '\033[2m\033[35m',           # dim  ×4 (gap between rings)
    '\033[2m\033[35m',
    '\033[2m\033[35m',
    '\033[2m\033[35m',
]
GOLD_RINGS = [
    '\033[97m\033[1m',           # white  — leading edge
    '\033[38;5;214m\033[1m',     # gold
    '\033[38;5;208m\033[1m',     # orange
    '\033[38;5;196m\033[1m',     # red-orange
    '\033[2m\033[90m',           # dim grey ×4
    '\033[2m\033[90m',
    '\033[2m\033[90m',
    '\033[2m\033[90m',
]
NRP = 8

# ── Glyphs (7-wide × 6-tall box-draw) ────────────────────────────────────────
GLYPHS = {
    '1': ['   ╔═══','   ║   ','   ║   ','   ║   ','   ║   ','═══╩═══'],
    '2': ['╔═════╗','      ║','╔═════╝','║      ','║      ','╚══════'],
    '3': ['╔═════╗','      ║','╠═════╣','      ║','      ║','╚═════╝'],
    '7': ['══════╗','      ║','   ╔══╝','   ║   ','   ║   ','   ╩   '],
    'g': ['╔═════╗','║     ║','║      ','║ ════╣','║     ║','╚═════╝'],
    'o': ['╔═════╗','║     ║','║     ║','║     ║','║     ║','╚═════╝'],
    't': ['═══╦═══','   ║   ','   ║   ','   ║   ','   ║   ','   ╩   '],
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
        g = GLYPHS.get(ch)
        if not g: continue
        for r in range(NROWS): rows[r] += g[r]
        if i < len(word) - 1:
            for r in range(NROWS): rows[r] += SEP
    w = max(len(r) for r in rows)
    return [r.ljust(w) for r in rows]

GOOT27  = make_art('goot27')
WOKSPEC = make_art('WokSpec')

# ── Core helpers ─────────────────────────────────────────────────────────────
def noise(n, nc):
    return ''.join(random.choice(nc) + random.choice('27') + RESET
                   for _ in range(max(n, 0)))

def birth_times(art):
    """Randomly order every non-space char, map to 0→1."""
    pos = [(r, c) for r, row in enumerate(art)
           for c, ch in enumerate(row) if ch.strip()]
    random.shuffle(pos)
    n = max(len(pos) - 1, 1)
    return {(r, c): i / n for i, (r, c) in enumerate(pos)}

def full_bt(art):
    """All birth times 0 → everything visible at t=0."""
    return {(r, c): 0.0
            for r, row in enumerate(art) for c in range(len(row))}

def render(t, art, bt, wc, lc, nc):
    """Build one full-screen frame. t=0 → all noise; t=1 → all logo."""
    TW, TH = shutil.get_terminal_size((80, 24))
    aw  = max(len(l) for l in art)
    lp  = max(0, (TW - aw) // 2)
    rp  = max(0, TW - lp - aw)
    mid = max(0, (TH - NROWS) // 2)
    out = []
    for row in range(TH):
        rel = row - mid
        if 0 <= rel < NROWS:
            parts = [noise(lp, nc)]
            for col, ch in enumerate(art[rel]):
                b = bt.get((rel, col), 0.0)
                if not ch.strip():
                    parts.append(' ' if t > b else noise(1, nc))
                elif t >= b + 0.08:
                    parts.append(lc + ch + RESET)   # settled
                elif t >= b:
                    parts.append(wc + ch + RESET)   # arriving flash
                else:
                    parts.append(noise(1, nc))       # not yet
            parts.append(noise(rp, nc))
            out.append(''.join(parts))
        else:
            out.append(noise(TW, nc))
    return HOME + '\n'.join(out)

# ── Primitive display ops ────────────────────────────────────────────────────
def flood(secs, nc):
    TW, _ = shutil.get_terminal_size((80, 24))
    end   = time.time() + secs
    while time.time() < end:
        sys.stdout.write(noise(TW, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.010)

def transition(secs, a, b):
    """Stochastic crossfade between two noise palettes."""
    TW, _ = shutil.get_terminal_size((80, 24))
    end   = time.time() + secs
    while time.time() < end:
        frac = 1.0 - (end - time.time()) / secs
        sys.stdout.write(noise(TW, b if random.random() < frac else a) + '\n')
        sys.stdout.flush()
        time.sleep(0.010)

def hold_logo(secs, art, bt, wc, lc, nc):
    """Freeze logo at full reveal (t=1.0), live noise around it."""
    fbt = full_bt(art) if bt is None else bt
    end = time.time() + secs
    while time.time() < end:
        sys.stdout.write(render(1.0, art, fbt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.07)

# ── Particle reveal / dissolve ───────────────────────────────────────────────
def particle_in(art, wc, lc, nc, steps=40, fps=0.045):
    bt = birth_times(art)
    sys.stdout.write(CLEAR)
    for i in range(steps):
        sys.stdout.write(render(i / (steps - 1), art, bt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(fps)
    return bt

def particle_out(art, bt, wc, lc, nc, steps=28, fps=0.045):
    for i in range(steps):
        sys.stdout.write(render(1.0 - i / (steps - 1), art, bt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(fps)

# ── Scan-line reveal / erase ─────────────────────────────────────────────────
def _scan_frame(art, sx, wc, lc, nc, erase=False):
    """Build one frame for a left↔right scan sweep."""
    TW, TH = shutil.get_terminal_size((80, 24))
    aw  = max(len(l) for l in art)
    lp  = max(0, (TW - aw) // 2)
    rp  = max(0, TW - lp - aw)
    mid = max(0, (TH - NROWS) // 2)
    GW  = 4
    out = []
    for row in range(TH):
        rel = row - mid
        if 0 <= rel < NROWS:
            parts = [noise(lp, nc)]
            for col, ch in enumerate(art[rel]):
                d = (col - sx) if erase else (sx - col)
                if not ch.strip():
                    parts.append(noise(1, nc) if (0 <= d <= GW) else
                                 ('  '[erase]))
                elif d > GW:
                    # behind glow: noise if erasing, settled if revealing
                    parts.append(noise(1, nc) if erase else lc + ch + RESET)
                elif d >= 0:
                    parts.append(wc + ch + RESET)   # inside glow
                else:
                    # ahead of glow: settled if erasing, noise if revealing
                    parts.append(lc + ch + RESET if erase else noise(1, nc))
            parts.append(noise(rp, nc))
            out.append(''.join(parts))
        else:
            out.append(noise(TW, nc))
    return HOME + '\n'.join(out)

def scan_in(art, wc, lc, nc, fps=0.025):
    """Glowing line sweeps left → right, burning chars into view."""
    aw = max(len(l) for l in art)
    sys.stdout.write(CLEAR)
    for sx in range(aw + 5):
        sys.stdout.write(_scan_frame(art, sx, wc, lc, nc, erase=False) + '\n')
        sys.stdout.flush()
        time.sleep(fps)

def scan_out(art, wc, lc, nc, fps=0.025):
    """Glowing line sweeps right → left, erasing chars."""
    aw = max(len(l) for l in art)
    for sx in range(aw + 5):
        sys.stdout.write(_scan_frame(art, sx, wc, lc, nc, erase=True) + '\n')
        sys.stdout.flush()
        time.sleep(fps)

# ── Ring effects ─────────────────────────────────────────────────────────────
def rings(secs, palette, inward=False, v0=2.5, accel=2.2, fps=0.033):
    """Concentric Chebyshev rings expanding or collapsing from centre."""
    TW, TH = shutil.get_terminal_size((80, 24))
    cx, cy = TW // 2, TH // 2
    start  = time.time()
    end    = start + secs
    sys.stdout.write(CLEAR)
    while time.time() < end:
        elapsed = time.time() - start
        speed   = v0 + elapsed * accel
        out     = []
        for row in range(TH):
            parts = []
            for col in range(TW):
                dx   = abs(col - cx)
                dy   = abs(row - cy) * 2
                dist = max(dx, dy)
                phase = (elapsed * speed - dist) if inward else (dist - elapsed * speed)
                idx   = int(phase) % NRP
                parts.append(palette[idx] + ('7' if (col+row+dist) % 3 == 0 else '2') + RESET)
            out.append(''.join(parts))
        sys.stdout.write(HOME + '\n'.join(out) + '\n')
        sys.stdout.flush()
        time.sleep(fps)

def shockwave():
    """Single expanding ring pulse — calls attention between sections."""
    TW, TH = shutil.get_terminal_size((80, 24))
    cx, cy = TW // 2, TH // 2
    max_d  = max(cx, cy * 2) + 4
    sys.stdout.write(CLEAR)
    d = 0.0
    while d < max_d:
        out = []
        for row in range(TH):
            parts = []
            for col in range(TW):
                dx   = abs(col - cx)
                dy   = abs(row - cy) * 2
                dist = max(dx, dy)
                diff = dist - d
                if -1 <= diff <= 1:
                    parts.append('\033[97m\033[1m' + ('7' if (col+row) % 2 else '2') + RESET)
                elif -3 <= diff <= 3:
                    parts.append(G_WAVE + ('2' if (col+row) % 2 else '7') + RESET)
                else:
                    parts.append(random.choice(PINK_NC) + random.choice('27') + RESET)
            out.append(''.join(parts))
        sys.stdout.write(HOME + '\n'.join(out) + '\n')
        sys.stdout.flush()
        d += 2.8
        time.sleep(0.017)

def white_flash(secs=0.3):
    """Full-screen white-hot climax flash."""
    TW, TH = shutil.get_terminal_size((80, 24))
    line   = '\033[97m\033[1m' + '2' * TW + RESET
    block  = '\n'.join([line] * TH)
    end    = time.time() + secs
    while time.time() < end:
        sys.stdout.write(HOME + block + '\n')
        sys.stdout.flush()
        time.sleep(0.04)

# ── Cascade (matrix-rain style) ──────────────────────────────────────────────
def cascade(secs, nc):
    """Columns of 2/7 falling at random speeds — neon rain curtain."""
    TW, TH = shutil.get_terminal_size((80, 24))
    heads  = [random.uniform(-TH, 0)  for _ in range(TW)]
    speeds = [random.uniform(1.0, 3.2) for _ in range(TW)]
    trails = [random.randint(5, 14)   for _ in range(TW)]
    end    = time.time() + secs
    sys.stdout.write(CLEAR)
    while time.time() < end:
        out = []
        for row in range(TH):
            parts = []
            for col in range(TW):
                d = row - int(heads[col])
                if d == 0:
                    parts.append('\033[97m\033[1m' + random.choice('27') + RESET)
                elif 1 <= d <= 2:
                    parts.append(nc[0] + random.choice('27') + RESET)
                elif 3 <= d <= trails[col]:
                    parts.append(nc[-1] + random.choice('27') + RESET)
                else:
                    parts.append(' ')
            out.append(''.join(parts))
        sys.stdout.write(HOME + '\n'.join(out) + '\n')
        sys.stdout.flush()
        dt = 0.038
        for i in range(TW):
            heads[i] += speeds[i] * dt
            if heads[i] > TH + trails[i] + 5:
                heads[i]  = random.uniform(-TH // 2, -2)
                speeds[i] = random.uniform(1.0, 3.2)
                trails[i] = random.randint(5, 14)
        time.sleep(dt)

# ── Glitch burst ──────────────────────────────────────────────────────────────
def glitch(art, wc, lc, nc, frames=18):
    """Strobing corruption overlay — logo breaks apart on exit."""
    fbt = full_bt(art)
    for f in range(frames):
        frac = 1.0 - f / frames          # corruption intensifies then fades
        t    = 0.9 if f % 3 else random.uniform(0.2, 0.65)
        sys.stdout.write(render(t * frac + (1.0 - frac) * random.uniform(0.05, 0.3),
                                art, fbt, wc, lc, nc) + '\n')
        sys.stdout.flush()
        time.sleep(0.022)

# ── Countdown ────────────────────────────────────────────────────────────────
def countdown():
    """3 … 2 … 1 — each digit crystallises from pink noise then dissolves."""
    for digit in ('3', '2', '1'):
        art = make_art(digit)
        bt  = particle_in(art, CD_WAVE, CD_LOGO, PINK_NC, steps=20, fps=0.034)
        hold_logo(0.55, art, bt, CD_WAVE, CD_LOGO, PINK_NC)
        particle_out(art, bt, CD_WAVE, CD_LOGO, PINK_NC, steps=14, fps=0.030)

# ── Starfield / warp speed ───────────────────────────────────────────────────
def starfield(secs, nc):
    """Stars accelerate outward from centre — warp-speed hyperdrive effect."""
    TW, TH = shutil.get_terminal_size((80, 24))
    cx, cy  = TW / 2.0, TH / 2.0
    MAX_D   = math.hypot(cx, cy * 2.0)
    N       = 200
    stars   = [(random.uniform(0, 2 * math.pi),
                random.uniform(0.3, MAX_D * 0.25),
                random.uniform(0.4, 1.8)) for _ in range(N)]
    start   = time.time()
    end     = start + secs
    sys.stdout.write(CLEAR)
    while time.time() < end:
        elapsed = time.time() - start
        warp    = 1.0 + elapsed * 3.2
        grid    = [[' '] * TW for _ in range(TH)]
        new     = []
        for angle, dist, spd in stars:
            nd = dist + spd * warp * 0.55
            if nd >= MAX_D:
                nd    = random.uniform(0.2, 1.5)
                angle = random.uniform(0, 2 * math.pi)
                spd   = random.uniform(0.4, 1.8)
            x = int(cx + math.cos(angle) * nd)
            y = int(cy + math.sin(angle) * nd * 0.5)
            if 0 <= x < TW and 0 <= y < TH:
                ratio = nd / MAX_D
                if ratio < 0.12:
                    col = nc[-1]; ch = '\xb7'          # dim centre dot
                elif ratio < 0.55:
                    col = nc[0];  ch = random.choice('27')
                else:
                    col = '\033[97m\033[1m'; ch = random.choice('27')  # hot edge
                grid[y][x] = col + ch + RESET
            new.append((angle, nd, spd))
        stars = new
        sys.stdout.write(HOME + '\n'.join(''.join(r) for r in grid) + '\n')
        sys.stdout.flush()
        time.sleep(0.038)

# ── DNA double helix ──────────────────────────────────────────────────────────
def dna_helix(secs):
    """Two interweaving phosphate strands — double helix of 2 and 7."""
    TW, TH   = shutil.get_terminal_size((80, 24))
    STRAND_A = '\033[38;5;213m\033[1m'   # hot pink  — strand A
    STRAND_B = '\033[38;5;51m\033[1m'    # cyan      — strand B
    RUNG     = '\033[38;5;225m\033[2m'   # pale      — rungs
    end      = time.time() + secs
    offset   = 0.0
    sys.stdout.write(CLEAR)
    while time.time() < end:
        out = []
        for row in range(TH):
            line  = [' '] * TW
            phase = row * 0.40 + offset
            xa    = int((TW / 2) + (TW / 3.2) * math.sin(phase))
            xb    = int((TW / 2) + (TW / 3.2) * math.sin(phase + math.pi))
            lo, hi = min(xa, xb), max(xa, xb)
            for c in range(lo + 1, hi):       # rungs between strands
                if 0 <= c < TW:
                    line[c] = RUNG + ('2' if (c + row) % 2 == 0 else '7') + RESET
            if 0 <= xa < TW:
                line[xa] = STRAND_A + ('2' if row % 2 == 0 else '7') + RESET
            if 0 <= xb < TW:
                line[xb] = STRAND_B + ('7' if row % 2 == 0 else '2') + RESET
            out.append(''.join(line))
        sys.stdout.write(HOME + '\n'.join(out) + '\n')
        sys.stdout.flush()
        offset += 0.14
        time.sleep(0.033)

# ── Fireworks ─────────────────────────────────────────────────────────────────
def fireworks(bursts=5):
    """Radial particle explosions from random launch points — celebration burst."""
    TW, TH = shutil.get_terminal_size((80, 24))
    BURST_COLS = [
        '\033[97m\033[1m',
        '\033[38;5;213m\033[1m',
        '\033[38;5;214m\033[1m',
        '\033[38;5;226m\033[1m',
        '\033[38;5;51m\033[1m',
        '\033[38;5;207m\033[1m',
        '\033[38;5;196m\033[1m',
    ]
    N = 36
    for _ in range(bursts):
        cx    = random.randint(TW // 5, 4 * TW // 5)
        cy    = random.randint(TH // 4, 3 * TH // 4)
        col   = random.choice(BURST_COLS)
        angs  = [2 * math.pi * i / N for i in range(N)]
        max_r = min(cx, TW - cx, cy * 2, (TH - cy) * 2, 28)
        for r in range(1, max_r + 8):
            grid = [[' '] * TW for _ in range(TH)]
            for a in angs:
                x = int(cx + r * math.cos(a))
                y = int(cy + r * math.sin(a) * 0.5)
                if 0 <= x < TW and 0 <= y < TH:
                    fade = col if r <= max_r else '\033[2m\033[90m'
                    grid[y][x] = fade + random.choice('27') + RESET
                tr = r - 4
                if tr > 0:
                    tx = int(cx + tr * math.cos(a))
                    ty = int(cy + tr * math.sin(a) * 0.5)
                    if 0 <= tx < TW and 0 <= ty < TH:
                        grid[ty][tx] = '\033[2m\033[35m' + random.choice('27') + RESET
            sys.stdout.write(HOME + '\n'.join(''.join(row) for row in grid) + '\n')
            sys.stdout.flush()
            time.sleep(0.020)
        time.sleep(0.06)

# ── Signal + main loop ───────────────────────────────────────────────────────
signal.signal(signal.SIGINT,
              lambda *_: (sys.stdout.write(SHOW + RESET + '\n'), sys.exit(0)))
sys.stdout.write(HIDE)

while True:
    # ── I · APPROACH ─────────────────────────────────────────────────────────
    # Particles converge from deep space → sequence lock → signal fires
    starfield(2.5, PINK_NC)
    countdown()
    shockwave()

    # ── II · IDENTITY ────────────────────────────────────────────────────────
    # Logo scorches left → right, holds, then dissolves back to particles
    scan_in(GOOT27, G_WAVE, G_LOGO, PINK_NC)
    hold_logo(3.0, GOOT27, None, G_WAVE, G_LOGO, PINK_NC)
    particle_out(GOOT27, birth_times(GOOT27), G_WAVE, G_LOGO, PINK_NC)

    # ── III · ECHO ───────────────────────────────────────────────────────────
    # Pulse ring expands → WokSpec rises from the noise → dissolves
    rings(2.5, PINK_RINGS, inward=False, v0=2.0, accel=1.8)
    wbt = particle_in(WOKSPEC, W_WAVE, W_LOGO, PINK_NC)
    hold_logo(2.5, WOKSPEC, wbt, W_WAVE, W_LOGO, PINK_NC)
    particle_out(WOKSPEC, wbt, W_WAVE, W_LOGO, PINK_NC)

    # ── IV · SURGE & RESOLVE ─────────────────────────────────────────────────
    # Reactor builds → peak flash → gold implosion → goot27 crystallises
    rings(3.5, PINK_RINGS, inward=False, v0=3.0, accel=3.0)
    white_flash(0.3)
    rings(2.0, GOLD_RINGS, inward=True, v0=8.0, accel=3.0)
    gbt = particle_in(GOOT27, G_WAVE, G_LOGO, PINK_NC)
    hold_logo(2.0, GOOT27, gbt, G_WAVE, G_LOGO, PINK_NC)
    flood(0.6, PINK_NC)
