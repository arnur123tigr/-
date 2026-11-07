"""Earth-in-one-year reel. Synthesised SFX (sfx.wav: whooshes on scene changes, page flips, pops, booms, ticks, fireworks)
and a light playful music bed (music.wav: pluck + pad + soft drums, C major, 104 bpm). Times are voice seconds (+OFF)."""
import wave, numpy as np
import sys, json
SR = 48000; OFF = 0.3; DUR = 96
LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
TM = json.load(open('tmap_kk.json'))['map'] if LANG == 'kk' else None
if TM: DUR = 104
def R2K(t):   # russian voice time -> kazakh voice time
    if not TM: return t
    for (k0, r0), (k1, r1) in zip(TM, TM[1:]):
        if t <= r1 or [k1, r1] == TM[-1]: return k0 + (t - r0) * (k1 - k0) / (r1 - r0)
rng = np.random.default_rng(5)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int((R2K(t) + OFF) * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
N = lambda n: 440 * 2 ** ((n - 69) / 12)
def whoosh(L=.8):
    n = int(SR * L); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 200, 300 + 3000 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 1.8
def pop():
    t = tt(.2); f = 500 + 900 * np.exp(-t * 30); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18))
def flip():
    t = tt(.25); return norm(band(rng.standard_normal(len(t)), 1500, 7000) * np.exp(-t * 22) * (1 - np.exp(-t * 300)))
def boom(L=2.2):
    t = tt(L); low = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t * 6)) / SR) * np.exp(-t * 2.2)
    return norm(low + .5 * band(rng.standard_normal(len(t)), 30, 700) * np.exp(-t * 3))
def tick():
    t = tt(.05); return norm(band(rng.standard_normal(len(t)), 2000, 6000) * np.exp(-t * 120))
def ding(f=880):
    t = tt(1.2); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (3 + h)) / h for h in (1, 2.01, 3.02)))
def crackle():
    t = tt(1.2); x = np.zeros(len(t))
    for _ in range(40): i = rng.integers(0, len(t) - 400); x[i:i + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 40)
    return norm(band(x, 800, 9000)) * np.exp(-t * 1.5)
s = np.zeros(int(SR * DUR))
for c in [3.0, 6.4, 14.1, 18.0, 27.68, 35.26, 38.82, 43.62, 52.78, 55.02, 60.12, 63.02, 67.86, 70.42, 76.98, 84.46]: add(s, c - .3, whoosh(), .35)
for c in [4.56, 18.06, 19.32, 20.3, 21.72, 22.48, 22.9, 23.34, 23.9, 25.3, 26.6, 56.32]: add(s, c, flip(), .45)
for c in [3.0, 15.4, 16.2, 16.45, 16.7, 25.32, 26.6, 37.3, 40.16, 45.8, 52.8, 53.5, 53.8, 58.3, 60.6, 61.2, 61.4, 63.1, 72.3, 74.6, 75.8, 77.0, 78.2, 81.6, 82.0, 85.4, 88.9, 90.7]: add(s, c, pop(), .4)
for i in range(10): add(s, 38.9 + i * .07, pop(), .25); add(s, 65.6 + (i % 5) * .18, pop(), .15 if i < 5 else 0)
for i in range(9): add(s, 41.44 + i * .14, tick(), .5)
for c in [10.7, 29.68, 49.2]: add(s, c, boom(), .7)
add(s, 6.4, boom(1.5), .35)
for c in [69.1, 69.5, 69.9, 83.1, 83.4, 83.7, 84.0]: add(s, c, crackle(), .25)
for i in range(16): add(s, 70.6 + i * .0625, tick(), .25)
for c in [37.22, 42.9, 53.8, 72.3, 81.5, 89.0]: add(s, c, ding(1046), .3)
for i in range(3): add(s, 91.5 + i * .17, tick(), .5)
add(s, 48.0, whoosh(1.3), .5)
write('sfx.wav' if LANG == 'ru' else 'sfx_kk.wav', norm(s) * .9)
# music bed
bpm = 104; beat = 60 / bpm; m = np.zeros(int(SR * DUR))
def addm(t, sig, g=1.0):
    i = int(t * SR); j = min(len(m), i + len(sig))
    if 0 <= i < j: m[i:j] += g * sig[:j - i]
prog = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]   # C G Am F
bar = 4 * beat; t_bar = tt(bar)
for b in range(int(DUR / bar) + 1):
    ch = prog[b % 4]; t0 = b * bar
    pad = sum(band(np.sin(2 * np.pi * N(n) * t_bar) + .3 * np.sin(2 * np.pi * N(n) * 1.004 * t_bar), 80, 2000) for n in ch)
    addm(t0, pad * np.minimum(1, t_bar / .3) * np.minimum(1, (bar - t_bar) / .3) * .08)
    addm(t0, np.sin(2 * np.pi * N(ch[0] - 24) * t_bar) * np.minimum(1, t_bar / .05) * np.minimum(1, (bar - t_bar) / .1) * .22)
    arp = [ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24, ch[2] + 12, ch[1] + 12, ch[2]]
    for k in range(8):
        tp = tt(beat * 1.2); n = arp[k]
        addm(t0 + k * beat / 2, (np.sin(2 * np.pi * N(n) * tp) + .5 * np.sin(2 * np.pi * N(n) * 2 * tp) + .2 * np.sin(2 * np.pi * N(n) * 3 * tp)) * np.exp(-tp * 9) * .13)
    for k in range(4):
        tk = tt(.3); addm(t0 + k * beat, np.sin(2 * np.pi * np.cumsum(55 * (1 + 2 * np.exp(-tk * 30))) / SR) * np.exp(-tk * 10) * .3)
        th = tt(.05); addm(t0 + k * beat + beat / 2, band(rng.standard_normal(len(th)), 6000, 12000) * np.exp(-th * 80) * .07)
        if k % 2: tc = tt(.15); addm(t0 + k * beat, band(rng.standard_normal(len(tc)), 900, 5000) * np.exp(-tc * 30) * .1)
fade = np.ones(len(m)); n0 = int(SR * 1.0); fade[:n0] = np.linspace(0, 1, n0); n1 = int(SR * 2.5); fade[-n1:] = np.linspace(1, 0, n1)
write('music.wav' if LANG == 'ru' else 'music_kk.wav', norm(m * fade) * .9)
print('ok')
