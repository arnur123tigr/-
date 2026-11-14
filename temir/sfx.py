"""Temir reel: synthesise SFX bed (sfx_<lang>.wav) and a soft steppe music bed (music_<lang>.wav).
Cue times are read from scene.html (CFG.<lang>.S / .c), so SFX follow the same voice timing as the picture."""
import re, sys, wave, numpy as np
LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
SR = 48000; OFF = 0.3
src = open('scene.html', encoding='utf-8').read()
blk = src.split(f'  {LANG}: {{')[1]
S = [float(x) for x in re.search(r'S: \[([^\]]+)\]', blk).group(1).split(',')]
C = {k: float(v) for k, v in re.findall(r'(\w+): ([\d.]+)', re.search(r'c: \{([^}]+)\}', blk).group(1))}
DUR = S[-1] + OFF + .5
rng = np.random.default_rng(5)
tt = lambda L: np.arange(int(SR * L)) / SR
norm = lambda x: x / (np.abs(x).max() + 1e-9)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def add(buf, t, sig, g=1.0):
    i = int((t + OFF) * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def env(n, a, r):
    e = np.ones(n); a = int(a * SR); r = int(r * SR); e[:a] = np.linspace(0, 1, a); e[n - r:] = np.linspace(1, 0, r); return e
def wind(L, lo=150, hi=900):
    n = int(SR * L); x = band(rng.standard_normal(n), lo, hi); m = 0.6 + 0.4 * np.sin(2 * np.pi * tt(L) * .23) * np.sin(2 * np.pi * tt(L) * .11 + 1)
    return norm(x * m) * env(n, .8, 1.0)
def drone(L, f=55):
    t = tt(L); return norm(np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.5 * t) + .3 * np.sin(2 * np.pi * f * 2.01 * t)) * env(len(t), 1, 1.2)
def boom():
    t = tt(1.6); f = 70 * np.exp(-t * 2) + 35; return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) + .3 * band(rng.standard_normal(len(t)), 40, 400) * np.exp(-t * 8))
def whoosh(L=.8):
    n = int(SR * L); u = np.arange(n) / n; x = rng.standard_normal(n); y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 300, 600 + 4000 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 2
def scratch(L):  # quill on paper: filtered noise bursts
    n = int(SR * L); x = band(rng.standard_normal(n), 2500, 9000); m = np.zeros(n); i = 0
    while i < n:
        d = int(SR * rng.uniform(.06, .22)); g = int(SR * rng.uniform(.02, .08)); m[i:i + d] = np.sin(np.linspace(0, np.pi, len(m[i:i + d]))) * rng.uniform(.5, 1); i += d + g
    return norm(x * m) * env(n, .05, .1)
def thud():
    t = tt(.5); return norm(np.sin(2 * np.pi * (90 * np.exp(-t * 8) + 50) * t) * np.exp(-t * 10) + .4 * band(rng.standard_normal(len(t)), 100, 1500) * np.exp(-t * 30))
def hit():
    t = tt(1.2); return norm(np.sin(2 * np.pi * np.cumsum(60 * np.exp(-t * 4) + 45) / SR) * np.exp(-t * 4) + .5 * band(rng.standard_normal(len(t)), 80, 3000) * np.exp(-t * 18))
def click():
    t = tt(.08); return norm(band(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 120))
def tick():
    t = tt(.05); return norm(band(rng.standard_normal(len(t)), 2000, 7000) * np.exp(-t * 160))

s = np.zeros(int(SR * DUR))
add(s, -OFF, wind(S[1] + OFF + 1.2), .35); add(s, -OFF, drone(S[1] + OFF + 1.0), .5)
add(s, S[1] - .5, whoosh(.6), .5); add(s, S[1], boom(), .6)
add(s, C['maver'] - .3, scratch(1.6), .35); add(s, C['samar'], thud(), .4)
add(s, C['tree'], scratch(2.6), .32); add(s, C['notHe'] + .5, scratch(.5), .3); add(s, C['emir'], thud(), .7)
for k in ['ar1', 'ar2', 'ar3']: add(s, C[k] - .1, whoosh(.7), .35); add(s, C[k] + .9, hit(), .6)
add(s, C['ank'], whoosh(1.4), .4); add(s, C['ankHit'], hit(), .8)
add(s, C['maus'], scratch(2.6), .32)
add(s, S[5] - .2, wind(S[6] - S[5] + .6, 300, 2500), .3)   # blizzard
add(s, C['card'], click(), .5); add(s, C['und'], scratch(.6), .35); add(s, C['und'] + .5, click(), .6)
for i in range(5): add(s, C['tarih'] - .1 + i * .12, tick(), .5)
add(s, C['link'], click(), .5)
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
write(f'sfx_{LANG}.wav', norm(s) * .9)

# music: low D drone pad + slow plucked dombyra-like figure (D dorian), 76 bpm
beat = 60 / 76; m = np.zeros(int(SR * DUR)); N = lambda n: 440 * 2 ** ((n - 69) / 12)
def pluck(f, L=1.4):
    n = int(SR * L); p = int(SR / f); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n): out[i] = buf[i % p]; buf[i % p] = .5 * (buf[i % p] + buf[(i + 1) % p]) * .996
    return out
OFFSAVE = OFF
def addm(t, sig, g): i = int(t * SR); j = min(len(m), i + len(sig)); m[i:j] += g * sig[:j - i] if i < j else 0
t = tt(DUR); m += (np.sin(2 * np.pi * N(38) * t) + .5 * np.sin(2 * np.pi * N(45) * t) + .25 * np.sin(2 * np.pi * N(50) * 1.002 * t)) * .12 * (0.8 + .2 * np.sin(2 * np.pi * t / 9))
fig = [62, 69, 67, 65, 64, 65, 62, 60]
pl = {n: pluck(N(n)) for n in set(fig + [50, 57])}
for b in range(int(DUR / beat)):
    n = fig[b % len(fig)]; addm(b * beat, pl[n], .22)
    if b % 4 == 0: addm(b * beat, pl[50], .25)
    if b % 8 == 6: addm(b * beat + beat / 2, pl[57], .15)
m *= env(len(m), 2.0, 2.0)
write(f'music_{LANG}.wav', norm(m) * .8)
print(LANG, 'DUR', DUR, S, C)
