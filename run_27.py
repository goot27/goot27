import random, time, signal, sys

try:
    signal.signal(signal.SIGINT, lambda s, f: (print('\n\033[0m^C'), sys.exit(0)))
except Exception:
    pass

p = ['\033[95m', '\033[35m', '\033[91m', '\033[97m']

while True:
    n = random.randint(40, 80)
    print(''.join(random.choice(p) + random.choice('27') + '\033[0m' for _ in range(n)), flush=True)
    time.sleep(random.uniform(0.008, 0.03))
