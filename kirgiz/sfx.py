"""Synthesise the script's sound effects into sfx.wav, timed from timeline.json."""
import json, wave, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
out = np.zeros(int(SR * (dur + 2)))
rng = np.random.default_rng(5)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def add(t, sig, g=1.0):
    i = int(t * SR); j = min(len(out), i + len(sig)); out[i:j] += g * sig[:j - i]
def tt(L): return np.arange(int(SR * L)) / SR

def stamp():                      # heavy rubber stamp thud
    t = tt(0.5)
    f = 70 + 120 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12)
    click = band(rng.standard_normal(len(t)), 300, 4000) * np.exp(-t * 60)
    return np.tanh(2.2 * norm(body + 0.6 * click)) * 0.9
def pen(L):                       # quill scratching
    n = int(SR * L); x = band(rng.standard_normal(n), 2500, 9000)
    env = np.abs(np.sin(np.arange(n) / SR * 2 * np.pi * 7)) ** 2
    env *= 0.6 + 0.4 * np.abs(band(rng.standard_normal(n), 2, 20)) / 0.05
    env = np.clip(env, 0, 1) * np.minimum(1, np.arange(n) / (0.05 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.1 * SR))
    return norm(x) * env
def whoosh(L, lo=300, hi=3000, up=True):
    n = int(SR * L); x = rng.standard_normal(n); t = np.arange(n) / n
    y = np.zeros(n); blk = 1024
    for k in range(0, n, blk):
        c = t[k] if up else 1 - t[k]
        y[k:k + blk] = band(x[k:k + blk], lo, lo + (hi - lo) * c)[:len(y[k:k + blk])]
    env = np.sin(np.pi * t) ** 1.5 if not up else t ** 2 * np.minimum(1, (1 - t) / 0.08)
    return norm(y) * env
def boing():                      # confused cartoon spring
    t = tt(0.9)
    f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 3) + 60 * t
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return norm(x) * np.exp(-t * 3.2) * np.minimum(1, t / 0.01)
def rustle(L):                    # unrolling map paper
    n = int(SR * L); x = band(rng.standard_normal(n), 1000, 9000)
    env = np.zeros(n)
    for _ in range(18):
        c = rng.integers(0, n - 3000); w = rng.integers(900, 4500)
        env[c:c + w] += np.hanning(w)[:len(env[c:c + w])] * rng.uniform(.3, 1)
    return norm(x) * np.clip(env, 0, 1)
def flip():                       # card flip: two quick flaps
    s = np.zeros(int(SR * 0.4))
    for k, d in [(0, 0.06), (0.14, 0.05)]:
        t = tt(d); x = band(rng.standard_normal(len(t)), 600, 5000) * np.exp(-t * 60)
        i = int(k * SR); s[i:i + len(x)] += norm(x)
    return s
def whistle():                    # soft rising-falling whistle
    t = tt(0.75)
    f = 900 + 700 * np.sin(np.pi * t / 0.75)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
    x += 0.15 * band(rng.standard_normal(len(t)), 1500, 4000)
    return norm(x) * np.sin(np.pi * t / 0.75) ** 2
def pop():
    t = tt(0.2); f = 300 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 25)
def chime(freq, L=1.2):
    t = tt(L)
    x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 3), (2.01, .3, 4.5), (3.02, .12, 6)])
    return x * np.minimum(1, t / 0.004) / 1.4

s1, s2, s3, s4, s5, s6, s7, se = (sc[k] for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'end'])
add(s1['start'] + s1['stamp'] - 0.01, stamp(), 0.9)
w0, w1 = s2['write']
add(s2['start'] + w0, pen(w1 - w0), 0.22)
add(s3['start'] - 0.05, whoosh(0.45, 400, 2600, up=False), 0.35)          # swipe
add(s3['start'] + 0.75, pop(), 0.35)                                        # paper appears
add(s3['start'] + s3['stamp'] - 0.01, stamp(), 0.9)
add(s4['start'] + 0.55, pop(), 0.3); add(s4['start'] + 1.05, pop(), 0.3)    # labels
add(s4['start'] + s4['q'], boing(), 0.45)
add(s4['end'] - s4['fly'], whoosh(s4['fly'] + 0.15, 300, 5000), 0.45)        # fly through "?"
add(s5['start'] + 0.1, rustle(0.75), 0.35)
add(s5['start'] + s5['banner'], pop(), 0.35)
add(s6['start'] + s6['flip'] + 0.05, flip(), 0.6)
add(s6['start'] + s6['flip'] + 0.5, chime(1318), 0.18)
add(s7['start'] + s7['morph'] - 0.15, whistle(), 0.22)
add(se['start'] + se['plus'], pop(), 0.45); add(se['start'] + se['plus'] + 0.05, chime(1568), 0.15)

out = np.clip(out[:int(SR * dur)], -1, 1)
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32000).astype(np.int16).tobytes())
print('sfx.wav', dur, 's')
