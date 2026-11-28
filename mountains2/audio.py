"""Music bed + deep rumble/cracks for the 10 s plates clip -> mix.wav (48 kHz, about -14 LUFS)."""
import sys, wave, numpy as np
SR = 48000; DUR = float(sys.argv[1]); rng = np.random.default_rng(7); n = int(SR * DUR); t = np.arange(n) / SR
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
N = lambda m: 440 * 2 ** ((m - 69) / 12)
# epic pad: low drones in D minor, swelling
m = np.zeros(n)
for k, ch in enumerate([[50, 57, 62], [46, 53, 58], [48, 55, 60], [45, 52, 57]]):
    a, b = int(k * n / 4), int((k + 1) * n / 4); tt = t[:b - a]
    seg = sum(np.sin(2 * np.pi * N(c) * tt) + .3 * np.sin(2 * np.pi * N(c) * 2.003 * tt) for c in ch) + .8 * np.sin(2 * np.pi * N(ch[0] - 12) * tt)
    env = np.minimum(1, tt / .4) * np.minimum(1, (tt[-1] - tt + 1e-3) / .4); m[a:b] += seg * env
for bt in np.arange(0, DUR, 60 / 80):   # slow drum hits
    i = int(bt * SR); L = min(n - i, int(.6 * SR)); tk = np.arange(L) / SR
    m[i:i + L] += 2.5 * np.sin(2 * np.pi * np.cumsum(45 * (1 + 1.5 * np.exp(-tk * 25))) / SR) * np.exp(-tk * 6)
m *= np.minimum(1, t / 1.0) * np.minimum(1, (DUR - t) / 1.2) * (.6 + .4 * t / DUR)
r = band(rng.standard_normal(n), 25, 140) * (.3 + .7 * np.sin(np.pi * np.clip(t / DUR, 0, 1)))   # earth rumble
for c in rng.uniform(1.5, DUR - 1, 9):   # rock cracks
    i = int(c * SR); L = int(.35 * SR); r[i:i + L] += band(rng.standard_normal(L), 300, 5000) * np.exp(-np.arange(L) / SR * 18) * 1.5
x = m / np.abs(m).max() * .55 + r / np.abs(r).max() * .45; x = x / np.abs(x).max() * .89
with wave.open('mix.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
print('ok')
