# Synth SFX bed (whooshes on scene changes, glitch, boom, camera click) + soft ambient music bed.
import numpy as np, wave
import json, os, sys
SR = 48000; DUR = 165.4
TM = json.load(open('tmap_kk.json')) if os.environ.get('LANG_Q') == 'kk' else None
if TM: DUR = TM['dur'] + 0.5
N = int(SR * DUR)
def M(t):  # RU timeline time -> output time
    if not TM: return t
    for A, B, a, b in TM['map']:
        if t < b: return A + (t - a) / (b - a) * (B - A)
    return t
rng = np.random.default_rng(7)
sfx = np.zeros(N); mus = np.zeros(N)

def put(buf, t, sig, g=1.0, raw=False):
    i = int((t if raw else M(t)) * SR); j = min(N, i + len(sig)); buf[i:j] += sig[:j - i] * g

def env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * np.exp(-t / r); return e

def whoosh(d=0.5):
    n = int(SR * d); w = rng.standard_normal(n); t = np.arange(n) / n
    # sweep a simple one-pole low-pass
    out = np.zeros(n); y = 0
    for k in range(n):
        a = 0.02 + 0.25 * np.sin(np.pi * t[k]); y += a * (w[k] - y); out[k] = y
    return out * np.sin(np.pi * t) ** 2 * 2.5

def click():
    n = int(SR * 0.12); return rng.standard_normal(n) * env(n, 0.001, 0.015) * 0.8

def boom():
    n = int(SR * 1.6); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (55 * np.exp(-t * 2)) * t) * np.exp(-t * 2.5)
    s += rng.standard_normal(n) * np.exp(-t * 6) * 0.3
    return s

def glitch(d=2.6):
    n = int(SR * d); s = np.zeros(n)
    for k in range(0, n, 1200):
        if rng.random() < 0.5: s[k:k + 1200] = np.sign(np.sin(2 * np.pi * rng.uniform(200, 1500) * np.arange(min(1200, n - k)) / SR)) * 0.15
    return s * np.linspace(0.3, 1, n)

W = whoosh()
for t in [9.5, 12.5, 33.2, 38.2, 48.6, 57.8, 68.4, 74.1, 81.3, 87.6, 94.9, 112.4, 120.3, 125.7, 128.5, 131.9, 135.0, 138.7, 151.0]:
    put(sfx, t - 0.25, W, 0.35)
put(sfx, 9.6, glitch(), 0.5)
put(sfx, 65.6, boom(), 0.8)
put(sfx, 126.7, click(), 1.0)
for t in [24.9, 101.9]: put(sfx, t, W, 0.25)

# music: slow minor pad (Am - F - C - G), soft pulse, fades out for CTA tail
def tone(f, d):
    n = int(SR * d); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * h * t) / h ** 1.6 for h in (1, 2, 3)) + 0.3 * np.sin(2 * np.pi * f * 1.003 * t)
    a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.2)
    return s * a
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 261.6, 329.6], [196, 246.9, 293.7]]
bar = 4.0
t = 0; k = 0
while t < DUR:
    for f in chords[k % 4]: put(mus, t, tone(f / 2, bar + 1.2), 0.12, True)
    put(mus, t, tone(chords[k % 4][0] / 4, bar + 1.2), 0.18, True)
    for b in range(4):  # soft pluck
        f = chords[k % 4][b % 3]; n = int(SR * 0.6); tt = np.arange(n) / SR
        put(mus, t + b, np.sin(2 * np.pi * f * tt) * np.exp(-tt * 6), 0.12, True)
    t += bar; k += 1
fo = np.ones(N); i0, i1 = int(M(158) * SR), int(min(DUR, M(165.3)) * SR); fo[i0:i1] = np.linspace(1, 0, i1 - i0); fo[i1:] = 0
mus *= fo

def save(name, a):
    a = a / (np.abs(a).max() + 1e-9) * 0.8
    s = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())
sx = '_kk' if TM else ''
save(f'sfx{sx}.wav', sfx); save(f'music{sx}.wav', mus)
print('ok')
