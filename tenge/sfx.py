"""Synthesised effects (sfx.wav: whooshes on cuts, pops on pop-ins, a ding on the keyword) and a light music bed
(music.wav: soft pad + pluck arpeggio + kick, 100 bpm). Cue times (video seconds) come from cues.json: {dur, whoosh, pop, ding}."""
import json, wave, numpy as np
C = json.load(open('cues.json')); SR = 48000; DUR = C['dur']
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
def whoosh(L=.9):
    n = int(SR * L); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 200, 300 + 3500 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 1.8
def pop():
    t = tt(.25); f = 500 + 900 * np.exp(-t * 30); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16))
def ding(f=880):
    t = tt(1.5); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + h)) / h for h in (1, 2.01, 3.02)))
s = np.zeros(int(SR * DUR))
for c in C['whoosh']: add(s, c - .35, whoosh(), .22)
for c in C['pop']: add(s, c, pop(), .22)
for c in C['ding']: add(s, c, ding(), .4)
def boom():
    t = tt(1.2); f = 40 + 90 * np.exp(-t * 9); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5) + band(rng.standard_normal(len(t)), 60, 900) * np.exp(-t * 14) * .6)
def clang():
    t = tt(1.4); x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((1180, 3), (1730, 4.5), (2690, 6), (3410, 8)))
    return norm(x + band(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 40) * 2)
def tick():
    t = tt(.06); return norm(band(rng.standard_normal(len(t)), 2500, 7000) * np.exp(-t * 120))
def drum(L):   # rising tom roll
    out = np.zeros(int(SR * L)); n = int(L * 6)
    for i in range(n):
        u = i / n; tk = tt(.25); hit = np.sin(2 * np.pi * np.cumsum(110 * (1 + np.exp(-tk * 25))) / SR) * np.exp(-tk * 14)
        add(out, L * (u ** .8), hit, .25 + .75 * u)
    return out
for c in C.get('boom', []): add(s, c, boom(), .2)
for c in C.get('clang', []): add(s, c, clang(), .35)
for c in C.get('tick', []): add(s, c, tick(), .5)
for c0, c1 in C.get('drum', []): add(s, c0, drum(c1 - c0), .14)
write('sfx.wav', norm(s) * .9)
bpm = 92; beat = 60 / bpm; m = np.zeros(int(SR * DUR))
prog = [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]]   # Am F Dm E: minor, «detective»
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
write('music.wav', norm(m * fade) * .9); print('sfx + music ok', DUR)
