"""Atlakh 751: synthesised SFX (sfx_<lang>.wav) and a calm steppe music bed (music_<lang>.wav), timed from beats.json."""
import json, wave, sys, numpy as np
SR = 48000; OFF = 0.3
LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
b = json.load(open('beats.json'))[LANG]
DUR = b['end'] + OFF + 1.6
rng = np.random.default_rng(5)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int((t + OFF) * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
def whoosh(L=1.0):
    n = int(SR * L); u = np.arange(n) / n; y = np.zeros(n); x = rng.standard_normal(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 150, 300 + 2500 * np.sin(np.pi * u[k]))
    return norm(y) * np.sin(np.pi * u) ** 1.8
def thud(f0=55, L=1.2, g=1):
    t = tt(L); f = f0 * (1 + 1.5 * np.exp(-t * 25)); body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    click = band(rng.standard_normal(len(t)), 80, 2500) * np.exp(-t * 40) * .5
    return norm(body + click)
def crackle(L=2.8):
    t = tt(L); x = np.zeros(len(t))
    for _ in range(int(L * 60)):
        i = rng.integers(0, len(t) - 600); x[i:i + 600] += rng.standard_normal(600) * np.exp(-np.arange(600) / 60) * rng.random()
    roar = band(rng.standard_normal(len(t)), 100, 900) * .25
    env = np.minimum(1, t / .2) * np.minimum(1, (L - t) / .8)
    return norm((band(x, 800, 7000) + roar) * env)
def drum(f0=80):
    t = tt(.6); return norm(np.sin(2 * np.pi * np.cumsum(f0 * (1 + .6 * np.exp(-t * 30))) / SR) * np.exp(-t * 7) + band(rng.standard_normal(len(t)), 100, 1500) * np.exp(-t * 30) * .3)
def click():
    t = tt(.08); return norm(band(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 90) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 70) * .6)
def rustle(L=.5):
    t = tt(L); return norm(band(rng.standard_normal(len(t)), 1500, 9000) * np.sin(np.pi * t / L) ** 2 * (.6 + .4 * np.sin(t * 60)))
def chime(f=660):
    t = tt(2.2); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (1.6 + h)) / h for h in (1, 2.0, 3.01)))
def march(L):
    t = tt(L); x = np.zeros(len(t))
    for k in np.arange(0, L, .32): i = int(k * SR); seg = band(rng.standard_normal(4000), 60, 400) * np.exp(-np.arange(4000) / 700); x[i:i + 4000] += seg[:len(x) - i]
    return norm(x) * np.minimum(1, t / .5) * np.minimum(1, (L - t) / .6)

s = np.zeros(int(SR * DUR))
add(s, .1, whoosh(1.4), .5)                      # arrow launch
add(s, b['hit'] - .02, thud(48, 1.6), 1.0)        # dull impact
add(s, b['hit'] + .05, whoosh(.9), .4)            # fast zoom
for c in ['s2', 's3', 's4', 's6', 's7']: add(s, b[c] - .15, rustle(), .35)
add(s, b['cn_in'] - .3, march(b['y748'] - b['cn_in'] + 1.5), .45)
add(s, b['raze'] - .05, crackle(min(3.0, b['s3'] - b['raze'] + .6)), .6)
add(s, b['raze'] - .05, thud(70, .8), .4)
t = b['s3'] + .2; k = 0
while t < b['s4'] - .2:                           # war drums
    add(s, t, drum(70 if k % 4 == 0 else 95), .55 if k % 4 == 0 else .35); t += .42; k += 1
days = [b['s4'] + .15 + i * (b['turks'] - b['s4'] - .15) / 4 for i in range(5)]
for d in days: add(s, d, thud(60, 1.0), .8)
add(s, b['karluk'] + 1.1, thud(45, 1.6), 1.0); add(s, b['karluk'] - .1, whoosh(1.3), .45)
add(s, b['rout'] - .1, whoosh(1.2), .4)
add(s, b['s5'] - .1, whoosh(1.0), .5)
add(s, b['leave'] - .2, whoosh(1.8), .35)
add(s, b['islam'] - .1, chime(587), .35)
for c in [b['d751'] - .1, b['d748'] - .1, b['d748'] + .25]: add(s, c, click(), .7)
for i in range(5): add(s, b['s7'] + .5 + i * .2, click(), .45)
add(s, b['link'], chime(880), .3)
write(f'sfx_{LANG}.wav', norm(s) * .9)

# calm steppe music: drone + slow dombra-like plucks, D minor (phrygian colour), 76 bpm
N = lambda n: 440 * 2 ** ((n - 69) / 12)
m = np.zeros(len(s)); beat = 60 / 76
tD = tt(DUR); m += (np.sin(2 * np.pi * N(38) * tD) + .5 * np.sin(2 * np.pi * N(45) * tD * 1.001) + .3 * np.sin(2 * np.pi * N(50) * tD * .999)) * .10 * (1 + .25 * np.sin(tD * .7))
pat = [62, 65, 64, 62, 60, 62, 69, 67, 65, 64, 62, 63, 62, 60, 57, 62]
def pluck(f, L=1.4):
    t = tt(L); return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4) + .25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 7)) * np.exp(-t * 3.2) * np.minimum(1, t / .004)
k = 0; t0 = 0.0
while t0 < DUR - 1:
    n = pat[k % len(pat)]
    i = int(t0 * SR); p = pluck(N(n)); j = min(len(m), i + len(p)); m[i:j] += .22 * p[:j - i]
    if k % 2 == 0: p2 = pluck(N(n - 12) * 1.0, 1.0); j = min(len(m), i + len(p2)); m[i:j] += .10 * p2[:j - i]
    t0 += beat / 2 if k % 4 != 3 else beat; k += 1
fade = np.ones(len(m)); n0 = int(SR * 1.0); fade[:n0] = np.linspace(0, 1, n0); n1 = int(SR * 2.5); fade[-n1:] = np.linspace(1, 0, n1)
write(f'music_{LANG}.wav', norm(m * fade) * .9)
print('ok', LANG, round(DUR, 2))
