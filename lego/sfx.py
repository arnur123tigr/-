"""Synthesise the script's sound effects (sfx.wav) and a playful ticking-clock music bed (music.wav)."""
import json, wave, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
rng = np.random.default_rng(7)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())

# ---------- effects ----------
def snap(bright=1.0):            # plastic brick click
    t = tt(0.12)
    x = band(rng.standard_normal(len(t)), 1800, 9000) * np.exp(-t * 90)
    x += 0.6 * np.sin(2 * np.pi * (2600 * bright) * t) * np.exp(-t * 70)
    x += 0.4 * np.sin(2 * np.pi * 520 * t) * np.exp(-t * 45)
    return norm(x)
def shutter():
    s = np.zeros(int(SR * 0.3))
    for k, g in [(0, 1), (0.085, 0.8)]:
        t = tt(0.05); x = band(rng.standard_normal(len(t)), 1500, 10000) * np.exp(-t * 120)
        x += 0.5 * np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 150)
        add(s, k, norm(x), g)
    return s
def whoosh(L, lo=300, hi=4000):
    n = int(SR * L); x = rng.standard_normal(n); t = np.arange(n) / n
    y = np.zeros(n); blk = 1024
    for k in range(0, n, blk):
        c = np.sin(np.pi * t[k])
        y[k:k + blk] = band(x[k:k + blk], lo, lo + (hi - lo) * c)[:len(y[k:k + blk])]
    return norm(y) * np.sin(np.pi * t) ** 1.6
def whistle(L=1.3):              # cartoon slide whistle going up then settling
    t = tt(L); u = t / L
    f = 700 + 900 * np.sin(np.pi * np.minimum(u * 1.1, 1)) ** 0.7
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 + 0.04 * np.sin(2 * np.pi * 7 * t))
    x += 0.12 * band(rng.standard_normal(len(t)), 1500, 5000)
    return norm(x) * np.sin(np.pi * u) ** 0.8
def ding():                      # two-note phone notification
    s = np.zeros(int(SR * 1.0))
    for k, fr in [(0, 1568), (0.11, 2093)]:
        t = tt(0.8)
        x = sum(a * np.sin(2 * np.pi * fr * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 5), (2, .25, 8), (3, .08, 12)])
        add(s, k, x * np.minimum(1, t / 0.003))
    return norm(s)
def pop():
    t = tt(0.22); f = 260 + 1000 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)
    x += 0.3 * band(rng.standard_normal(len(t)), 500, 4000) * np.exp(-t * 80)
    return norm(x)
def clap():
    s = np.zeros(int(SR * 0.3))
    for k in [0, 0.012, 0.024]:
        t = tt(0.2); add(s, k, band(rng.standard_normal(len(t)), 800, 6000) * np.exp(-t * 35))
    return norm(s)
def roar(L=1.5):                 # elephant-like trumpet
    t = tt(L); u = t / L
    f = 330 + 260 * np.sin(np.pi * np.minimum(u * 1.4, 1)) + 25 * np.sin(2 * np.pi * 9 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = sum(np.sin(k * ph) / k for k in range(1, 18))
    x = band(saw, 250, 3800) + 0.25 * band(rng.standard_normal(len(t)), 600, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t))
    x = np.tanh(2.5 * norm(x))
    env = np.minimum(1, t / 0.08) * np.minimum(1, (L - t) / 0.35)
    return norm(x) * env
def thud():
    t = tt(0.3); f = 55 + 40 * np.exp(-t * 20)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) + 0.2 * band(rng.standard_normal(len(t)), 80, 400) * np.exp(-t * 30))

fx = np.zeros(int(SR * (dur + 1)))
s1, s2, s3, s4, s5, s6, se = (sc[k] for k in ['s1', 's2', 's3', 's4', 's5', 's6', 'end'])
add(fx, s1['start'] + s1['click'] - 0.02, shutter(), 0.75)
add(fx, s1['start'] + 0.35, pop(), 0.25)                                  # title pops
add(fx, s2['start'] + 0.3, pop(), 0.22)
for k in (0.25, 0.55, 0.85): add(fx, s2['start'] + k, snap(0.8), 0.18)     # carried bricks rattle
add(fx, s2['start'] + s2['place'] - 0.01, snap(1.0), 0.9)
add(fx, s2['start'] + s2['place'] + 0.07, snap(1.15), 0.5)
add(fx, s3['start'] - 0.12, whoosh(0.5, 400, 5000), 0.45)                 # swipe
add(fx, s3['start'] + 0.1, whistle(s3['travel']), 0.28)
add(fx, s3['start'] + s3['travel'] + 0.05, pop(), 0.22)
add(fx, s4['start'] - 0.1, whoosh(0.6, 300, 4500), 0.4)
add(fx, s4['start'] + s4['raise'] - 0.05, ding(), 0.45)
add(fx, s4['end'] - 0.55, whoosh(1.1, 200, 3000), 0.4)                    # pull back
a0, a1 = s5['barA']; b0, b1 = s5['barB']
for k in np.arange(a0, a1, 0.07): add(fx, s5['start'] + k, snap(0.9 + 0.3 * (k - a0)), 0.22)
for k in np.arange(b0, b1, 0.07): add(fx, s5['start'] + k, snap(1.1 + 0.3 * (k - b0)), 0.22)
add(fx, s5['start'] + b1 + 0.05, clap(), 0.75)
add(fx, s5['start'] + b1 + 0.05, pop(), 0.35)
add(fx, s6['start'] + 0.35, pop(), 0.22)
for k in np.arange(0.2, s6['end'] - s6['start'], 0.75): add(fx, s6['start'] + k, thud(), 0.45)
add(fx, s6['start'] + s6['roar'] - 0.15, roar(1.4), 0.55)
add(fx, se['start'] + se['click'] - 0.02, shutter(), 0.75)
add(fx, se['start'] + 1.45, pop(), 0.25)
add(fx, se['start'] + se['plus'], pop(), 0.5); add(fx, se['start'] + se['plus'] + 0.03, snap(1.2), 0.5)
write('sfx.wav', fx[:int(SR * dur)])

# ---------- music: ticking clock + playful pizzicato ----------
BPM = 120; beat = 60 / BPM
mu = np.zeros(int(SR * (dur + 2)))
def tick(hi):
    t = tt(0.06); f = 3800 if hi else 2900
    return norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + 0.4 * band(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-t * 200))
def pluck(freq, L=0.35):
    t = tt(L)
    x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 9), (2, .5, 14), (3, .25, 20), (4, .1, 26)])
    return x * np.minimum(1, t / 0.003)
def bass(freq, L=0.45):
    t = tt(L); return np.sin(2 * np.pi * freq * t) * np.exp(-t * 5) * np.minimum(1, t / 0.005) + 0.3 * np.sin(4 * np.pi * freq * t) * np.exp(-t * 8)
N = lambda n: 440 * 2 ** ((n - 69) / 12)
# 2-bar loop in C major (8th notes, 0 = rest)
mel = [72, 0, 76, 79, 0, 76, 74, 0,   72, 0, 67, 0, 69, 71, 72, 0,
       74, 0, 77, 81, 0, 77, 76, 0,   74, 71, 67, 0, 71, 0, 72, 0]
bas = [48, 55, 48, 55, 50, 57, 43, 50]     # one per half note... per beat pair
nbeats = int(dur / beat) + 1
for b in range(nbeats):
    t0 = b * beat
    add(mu, t0, tick(b % 2 == 0), 0.35)
    add(mu, t0 + beat / 2, tick(False), 0.12)
    add(mu, t0, bass(N(bas[(b // 2) % len(bas)] - 12 + 12)), 0.30)
    for h in range(2):
        n = mel[(b * 2 + h) % len(mel)]
        if n and t0 + h * beat / 2 < dur - 1.0: add(mu, t0 + h * beat / 2, pluck(N(n)), 0.16)
# soft final chord
for n in (60, 64, 67, 72): add(mu, dur - 1.6, pluck(N(n), 1.6), 0.12)
mu = mu[:int(SR * dur)]
fade = np.ones(len(mu)); k = int(SR * 0.8); fade[-k:] = np.linspace(1, 0, k)
write('music.wav', norm(mu) * 0.8 * fade)
print('sfx.wav + music.wav', dur, 's')
