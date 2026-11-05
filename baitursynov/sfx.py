"""Synthesise the script's sound effects into sfx.wav, timed from timeline.json."""
import json, wave, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
out = np.zeros(int(SR * (dur + 1)))
rng = np.random.default_rng(3)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def add(t, sig, g=1.0):
    i = int(t * SR); j = min(len(out), i + len(sig)); out[i:j] += g * sig[:j - i]
def chalk(L=0.3):
    n = int(SR * L); x = band(rng.standard_normal(n), 1800, 7000)
    env = np.abs(band(rng.standard_normal(n), 5, 40)); env /= env.max() + 1e-9
    env *= np.sin(np.linspace(0, np.pi, n)) ** 0.5
    return x / (np.abs(x).max() + 1e-9) * env
def hmm(L=0.9):
    n = int(SR * L); t = np.arange(n) / SR
    f = 118 + 40 * (t / L) ** 2                     # rising, questioning
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k ** 1.3 for k in range(1, 12))
    x = band(x, 80, 1200)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (L - t) / 0.25)
    return x / np.abs(x).max() * env
def chime(freq, L=1.6):
    t = np.arange(int(SR * L)) / SR
    x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 2.2), (2.01, .35, 3.5), (3.02, .15, 5)])
    return x * np.minimum(1, t / 0.005) / 1.5
def rustle(L=0.8):
    n = int(SR * L); x = band(rng.standard_normal(n), 1200, 9000)
    env = np.zeros(n)
    for _ in range(14):
        c = rng.integers(0, n - 2000); w = rng.integers(800, 4000)
        env[c:c + w] += np.hanning(w)[:len(env[c:c + w])] * rng.uniform(.3, 1)
    return x / np.abs(x).max() * np.clip(env, 0, 1)
def drum(L=1.6):
    t = np.arange(int(SR * L)) / SR
    f = 42 + 50 * np.exp(-t * 18)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    x += 0.25 * band(rng.standard_normal(len(t)), 60, 400) * np.exp(-t * 25)
    return np.tanh(1.6 * x) * 0.9
def swell(L):
    t = np.arange(int(SR * L)) / SR
    x = sum(np.sin(2 * np.pi * f * t + i) * (1 + 0.003 * np.sin(2 * np.pi * 5 * t)) for i, f in enumerate([130.8, 196, 261.6, 329.6, 392, 587.3]))
    env = (t / L) ** 1.6 * np.minimum(1, (L - t) / 0.6)
    return x / 6 * env

s = sc['s1']['start']
for i in range(7): add(s + 0.15 + i * 0.36, chalk(0.28), 0.35)
add(sc['s3']['start'] + 1.1, hmm(), 0.45)
pent = [880, 988, 1175, 1319, 1480, 1760]
for i in range(6): add(sc['s4']['start'] + 0.5 + i * 0.42 + 0.35, chime(pent[i]), 0.22)
add(sc['s5']['start'] + 0.65, rustle(0.9), 0.3)
add(sc['s6']['start'] + sc['s6'].get('drum', 3.0), drum(), 0.8)
d7 = sc['s7']['end'] - sc['s7']['start']
add(sc['s7']['start'], swell(d7), 0.35)
for k in range(3): add(sc['end']['start'] + 0.7 + k * 0.45, chalk(0.35), 0.25)

out = out[:int(SR * dur)]
out = np.clip(out, -1, 1)
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32000).astype(np.int16).tobytes())
print('sfx.wav', dur, 's')
