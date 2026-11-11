"""Synthesise SFX (sfx.wav: whooshes on camera moves, blips on country names, pops on region labels)
and a light electronic music bed (music.wav: soft pad + pluck arpeggio, A minor, 96 bpm)."""
import json, re, wave, numpy as np
import os, sys
SR = 48000; OFF = 0.3; DUR = float(os.environ.get('VDUR', 112))
LANG = os.environ.get('VLANG', 'ru')
WP = json.load(open(f'warp_{LANG}.json')) if LANG != 'ru' else None
def inv(t):   # Russian timeline time -> this language's voice time
    if not WP: return t
    xs = [b for a, b in WP]; ys = [a for a, b in WP]
    return float(np.interp(t, xs, ys, left=None, right=None)) if xs[0] <= t <= xs[-1] else t + (ys[-1] - xs[-1] if t > xs[-1] else 0)
rng = np.random.default_rng(3)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0, raw=False):
    if not raw and WP is not None: t = inv(t - OFF) + OFF
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
N = lambda n: 440 * 2 ** ((n - 69) / 12)
src = open('scene.html', encoding='utf-8').read()
cams = [float(m) for m in re.findall(r'\[(-?[\d.]+), -?[\d.]+, -?[\d.]+, [\d.]+\]', src.split('const CAM =')[1].split(';')[0])]
names = [float(m.group(1)) for m in re.finditer(r"[A-Z]{3}: \[[-\d.]+, [-\d.]+, ([\d.]+)", src.split('const LBL =')[1].split('};')[0])]

def whoosh(L=1.2):
    n = int(SR * L); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 200, 300 + 3500 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 1.8
def blip(f=1320):
    t = tt(.18); return norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 28) + .3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 40))
def pop():
    t = tt(.25); f = 500 + 900 * np.exp(-t * 30); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16))
def ding(f=880):
    t = tt(1.5); x = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + h)) / h for h in (1, 2.01, 3.02)); return norm(x)

s = np.zeros(int(SR * DUR))
for c in cams[1:]: add(s, c + OFF - .25, whoosh(1.4), .55)
for i, c in enumerate(sorted(names)): add(s, c + OFF, blip(1100 + 140 * (i % 5)), .35)
for c in [103.8, 3.5, 5.9, 8.12, 8.88, 9.66, 23.0, 41.5, 46.0, 53.4, 71.2, 73.4, 82.6, 84.7, 92.1, 94.0, 96.2]: add(s, c + OFF, pop(), .5)
for c in [0.0, 12.6, 17.8, 35.3, 65.9, 99.3, 101.0, 108.9]: add(s, c + OFF, ding(), .4)
write('sfx.wav', norm(s) * .9)

# music bed
bpm = 96; beat = 60 / bpm; m = np.zeros(int(SR * DUR))
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
bar = 4 * beat; t_bar = tt(bar)
for b in range(int(DUR / bar) + 1):
    ch = prog[b % 4]; t0 = b * bar
    pad = sum(band(np.sign(np.sin(2 * np.pi * N(n) * t_bar)) * .3 + np.sin(2 * np.pi * N(n) * 1.003 * t_bar), 80, 1800) for n in ch)
    add(m, t0, raw=True, sig=pad * np.minimum(1, t_bar / .3) * np.minimum(1, (bar - t_bar) / .3) * .12)
    bass = np.sin(2 * np.pi * N(ch[0] - 12) * t_bar) * np.minimum(1, t_bar / .05) * np.minimum(1, (bar - t_bar) / .1)
    add(m, t0, bass * .25, raw=True)
    arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
    for k in range(8):
        tp = tt(beat * 1.5); n = arp[k % 4]
        pl = (np.sin(2 * np.pi * N(n) * tp) + .4 * np.sin(2 * np.pi * N(n) * 2 * tp)) * np.exp(-tp * 7)
        add(m, t0 + k * beat / 2, pl * .16, raw=True)
    for k in range(4):   # soft kick + hat
        tk = tt(.3); add(m, t0 + k * beat, raw=True, sig=np.sin(2 * np.pi * np.cumsum(55 * (1 + 2 * np.exp(-tk * 30))) / SR) * np.exp(-tk * 10) * .35)
        th = tt(.05); add(m, t0 + k * beat + beat / 2, raw=True, sig=band(rng.standard_normal(len(th)), 6000, 12000) * np.exp(-th * 80) * .08)
fade = np.ones(len(m)); n0 = int(SR * 1.5); fade[:n0] = np.linspace(0, 1, n0); n1 = int(SR * 2.5); fade[-n1:] = np.linspace(1, 0, n1)
write('music.wav', norm(m * fade) * .9)
print('ok', len(cams), len(names))
