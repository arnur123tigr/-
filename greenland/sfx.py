"""Greenland reel: synthesise SFX (sfx.wav: whooshes on cuts, pops on pop-ins, tape rewind, mosquito buzz, dings)
and a light music bed (music.wav: soft pad + pluck arpeggio + kick, D minor, 100 bpm)."""
import wave, numpy as np
SR = 48000; OFF = 0.3; DUR = 73
rng = np.random.default_rng(3)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
N = lambda n: 440 * 2 ** ((n - 69) / 12)
def whoosh(L=1.0):
    n = int(SR * L); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 200, 300 + 3500 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 1.8
def pop():
    t = tt(.25); f = 500 + 900 * np.exp(-t * 30); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16))
def ding(f=880):
    t = tt(1.5); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + h)) / h for h in (1, 2.01, 3.02)))
def rewind(L=2.0):
    t = tt(L); f = 300 + 1800 * (t / L) ** .7 + 60 * np.sin(2 * np.pi * 9 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .4 + band(rng.standard_normal(len(t)), 1500, 6000) * .6
    return norm(band(x, 200, 7000)) * np.minimum(1, t / .1) * np.minimum(1, (L - t) / .15)
def buzz(L):
    t = tt(L); f = 520 + 40 * np.sin(2 * np.pi * 3 * t) + 25 * np.sin(2 * np.pi * 7.3 * t)
    return norm(band(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 300, 4000)) * (.6 + .4 * np.sin(2 * np.pi * .8 * t) ** 2) * np.minimum(1, t / .4) * np.minimum(1, (L - t) / .4)
s = np.zeros(int(SR * DUR))
for c in [7.2, 12.3, 17.0, 27.2, 31.8, 37.9, 44.2, 52.9, 61.75]: add(s, c + OFF - .3, whoosh(.9), .45)
for c in [0.0, 0.9, 7.5, 8.7, 9.0, 9.9, 11.0, 14.7, 15.5, 17.8, 25.2, 29.0, 30.5, 33.0, 34.6, 38.8, 39.4, 40.4, 41.5, 49.5, 50.3, 53.4, 53.9, 54.7, 55.9, 58.9, 61.85, 63.6, 66.2]: add(s, c + OFF, pop(), .45)
for c in [42.55]: add(s, c + OFF, whoosh(.5), .5)
wl = int(SR * 6.2); add(s, 21.0 + OFF, band(rng.standard_normal(wl), 200, 900) / 4 * np.minimum(1, np.arange(wl) / SR / 1.0) * np.minimum(1, (wl / SR - np.arange(wl) / SR) / 1.0), .25)
for c in [49.5, 68.9]: add(s, c + OFF, ding(), .4)
write('sfx.wav', norm(s) * .9)
bpm = 100; beat = 60 / bpm; m = np.zeros(int(SR * DUR))
prog = [[62, 65, 69], [58, 62, 65], [60, 64, 67], [57, 61, 64]]   # Dm Bb C A
bar = 4 * beat; t_bar = tt(bar)
for b in range(int(DUR / bar) + 1):
    ch = prog[b % 4]; t0 = b * bar
    pad = sum(band(np.sign(np.sin(2 * np.pi * N(n) * t_bar)) * .3 + np.sin(2 * np.pi * N(n) * 1.003 * t_bar), 80, 1800) for n in ch)
    add(m, t0, pad * np.minimum(1, t_bar / .3) * np.minimum(1, (bar - t_bar) / .3) * .12)
    add(m, t0, np.sin(2 * np.pi * N(ch[0] - 24) * t_bar) * np.minimum(1, t_bar / .05) * np.minimum(1, (bar - t_bar) / .1) * .25)
    arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
    for k in range(8):
        tp = tt(beat * 1.5); n = arp[k % 4]
        add(m, t0 + k * beat / 2, (np.sin(2 * np.pi * N(n) * tp) + .4 * np.sin(2 * np.pi * N(n) * 2 * tp)) * np.exp(-tp * 7) * .15)
    for k in range(4):
        tk = tt(.3); add(m, t0 + k * beat, np.sin(2 * np.pi * np.cumsum(55 * (1 + 2 * np.exp(-tk * 30))) / SR) * np.exp(-tk * 10) * .35)
        th = tt(.05); add(m, t0 + k * beat + beat / 2, band(rng.standard_normal(len(th)), 6000, 12000) * np.exp(-th * 80) * .08)
fade = np.ones(len(m)); n0 = int(SR * 1.5); fade[:n0] = np.linspace(0, 1, n0); n1 = int(SR * 2.5); fade[-n1:] = np.linspace(1, 0, n1)
write('music.wav', norm(m * fade) * .9)
print('ok')
