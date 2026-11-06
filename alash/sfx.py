"""Synthesise the script's sound effects (sfx.wav) and a minimal piano + strings music bed (music.wav):
anxious D minor for the history part, silence after 1937, bright D major for the final."""
import json, math, wave, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
rng = np.random.default_rng(7)

def jhash(n):  # same as hash() in scene.html
    s = math.sin(n * 127.1 + 311.7) * 43758.5453
    return s - math.floor(s)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    if j > i: buf[i:j] += g * sig[:j - i]
def reverb(x, L=2.2, mix=0.3, damp=3.0):
    t = tt(L); ir = rng.standard_normal(len(t)) * np.exp(-t * damp); ir = band(ir, 200, 7000); ir /= np.sqrt((ir ** 2).sum())
    n = len(x) + len(ir); F = 1 << int(np.ceil(np.log2(n)))
    wet = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
    return (1 - mix) * x + mix * wet
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())

# ---------- effects ----------
def drone(L):
    t = tt(L)
    x = np.sin(2 * np.pi * 49 * t) + .6 * np.sin(2 * np.pi * 73.5 * t) + .3 * np.sin(2 * np.pi * 98.3 * t)
    x *= (.8 + .2 * np.sin(2 * np.pi * .7 * t))
    x += .5 * norm(band(rng.standard_normal(len(t)), 30, 180))
    env = np.minimum(1, t / .8) * np.minimum(1, (L - t) / .6)
    return norm(x) * env
def clatter(L=1.0, n=60):
    s = np.zeros(int(SR * L))
    for k in range(n):
        tk = rng.random() * L * .85; t = tt(.05)
        f = 1800 + rng.random() * 3000
        add(s, tk, (np.sin(2 * np.pi * f * t) * .5 + band(rng.standard_normal(len(t)), 2000, 9000)) * np.exp(-t * 120), .3 + .7 * rng.random())
    return norm(s)
def crack():
    s = np.zeros(int(SR * .9))
    t = tt(.12); add(s, 0, band(rng.standard_normal(len(t)), 300, 9000) * np.exp(-t * 40), 1)
    for k in range(40):
        tk = .05 + rng.random() * .7; t = tt(.02)
        add(s, tk, band(rng.standard_normal(len(t)), 1500, 9000) * np.exp(-t * 300), .5 * np.exp(-tk * 3))
    return norm(s)
def thud(f0=60, L=.8, noise=.4):
    t = tt(L); f = f0 + 70 * np.exp(-t * 18)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) + noise * band(rng.standard_normal(len(t)), 40, 400) * np.exp(-t * 14)
    return norm(np.tanh(1.8 * x) * np.minimum(1, t / .004))
def shot():
    t = tt(1.0)
    x = band(rng.standard_normal(len(t)), 60, 900) * np.exp(-t * 9) + .5 * np.sin(2 * np.pi * 55 * t) * np.exp(-t * 12)
    return norm(reverb(x, 1.6, .6, 2.5))
def zap(L=.18):
    t = tt(L); return norm(band(rng.standard_normal(len(t)), 2500, 11000) * np.exp(-t * 25) * (rng.random(len(t)) > .6))
def scratch(L=.35):
    t = tt(L); x = band(rng.standard_normal(len(t)), 2500, 8000) * (0.55 + 0.45 * np.sin(2 * np.pi * 31 * t))
    x += .3 * np.sin(2 * np.pi * (2600 + 500 * np.sin(2 * np.pi * 7 * t)) * t)
    return norm(x * np.sin(np.pi * t / L))
def rustle(L=0.4):
    t = tt(L); x = band(rng.standard_normal(len(t)), 1500, 9000)
    am = np.abs(band(rng.standard_normal(len(t)), 5, 40)); am = am / (am.max() + 1e-9)
    return norm(x * (0.3 + am) * np.sin(np.pi * t / L) ** 0.7)
def whoosh(L=0.5, lo=400, hi=3500):
    t = tt(L); x = band(rng.standard_normal(len(t)), lo, hi)
    return norm(x) * np.sin(np.pi * t / L) ** 1.5
def pop():
    t = tt(0.2); f = 300 + 900 * np.exp(-t * 35)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22))
def chime(fr=1760, L=1.2):
    t = tt(L)
    x = sum(a * np.sin(2 * np.pi * fr * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 4), (2.76, .3, 7), (5.4, .1, 12)])
    return norm(x * np.minimum(1, t / 0.002))
def clap():
    t = tt(.06); return band(rng.standard_normal(len(t)), 700, 6000) * np.exp(-t * 90)
def applause(L):
    s = np.zeros(int(SR * L))
    for k in range(int(L * 90)):
        add(s, rng.random() * L, clap(), .4 + .6 * rng.random())
    t = tt(L); env = np.minimum(1, t / .3) * np.minimum(1, (L - t) / 1.0) ** 1.5
    return norm(s) * env
def shimmer(L=1.2):
    t = tt(L); x = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) for f in (1760, 2217, 2637, 3520)) * np.sin(np.pi * t / L) ** 2
    return norm(x * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)))

N = lambda n: 440 * 2 ** ((n - 69) / 12)
def piano(freq, L=2.5, vel=1.0):
    t = tt(L); x = np.zeros(len(t))
    for m, a in [(1, 1), (2, .45), (3, .22), (4, .12), (5, .06), (6, .03)]:
        fm = freq * m * (1 + 0.0004 * m * m)
        x += a * np.sin(2 * np.pi * fm * t) * np.exp(-t * (1.1 + 0.9 * m) * (freq / 440) ** 0.3)
    x += 0.02 * band(rng.standard_normal(len(t)), 1000, 6000) * np.exp(-t * 80)
    return x * np.minimum(1, t / 0.004) * vel
def strings(notes, L, att=1.0, rel=1.2, vel=1.0):
    t = tt(L); x = np.zeros(len(t))
    for n in notes:
        f = N(n)
        for d in (-.12, 0, .13):                       # three slightly detuned voices
            ph = 2 * np.pi * f * (1 + d / 100) * t + .0025 * f * np.sin(2 * np.pi * 5.2 * t + rng.random() * 6) / 5.2
            x += sum((1 / m) * np.sin(m * ph) for m in range(1, 7))
    env = np.minimum(1, t / att) * np.minimum(1, np.maximum(0, (L - t) / rel))
    return x * env * vel / (3 * len(notes))

s1, s2, s3, s4, s5, s6, s7, se = (sc[k] for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'end'])
fx = np.zeros(int(SR * (dur + 2)))
# S1: low hum, the army crumbles
add(fx, 0, drone(s1['end'] + .4), .55)
add(fx, s1['crumble'], clatter(1.1, 90), .3)
add(fx, s1['crumble'], whoosh(1.0, 100, 900), .25)
# S2: crack, falling crown, zigzags and distant shots (same timings as the picture)
a = s2['start']
add(fx, a + s2['crack'], crack(), .6)
add(fx, a + s2['fall'] + .9, thud(48, 1.2), .7)
for k in range(14):
    add(fx, a + s2['fall'] + .3 + k * .16 + jhash(k) * .1, zap(), .14)
for k in range(10):
    add(fx, a + s2['fall'] + .4 + k * .22 + jhash(k + 40) * .12, shot(), .28)
# S3: quill squeaks, icons pop in
a = s3['start']
for i in range(3): add(fx, a + .35 + i * .22, scratch(.4), .2)
for tk in s3['icons']: add(fx, a + tk - .1, pop(), .25); add(fx, a + tk - .05, scratch(.25), .12)
# S4: writing, paper rustle for every sheet, soft landing chimes
a = s4['start']
add(fx, a, scratch(1.4), .12)
YURTS = [900, 1250, 1600, 1950, 2300, 2650]
for i, x in enumerate(YURTS):
    t0 = .3 + i * .24; T = .75 + (x - 330) / 2100
    add(fx, a + t0, rustle(.45), .25)
    add(fx, a + t0 + T, chime(1320 + i * 90, .7), .06)
# S5: hands go up, applause (rolls into S6)
a = s5['start']
add(fx, a + s5['hands'], whoosh(.6, 300, 2500), .12)
add(fx, a + s5['clap'] - .1, applause(2.4), .45)
# S6: soft chord + shimmer as "Алаш Орда" lights up
a = s6['start']
add(fx, a + s6['sign'], shimmer(1.4), .08)
for n in (50, 57, 62, 66, 69): add(fx, a + s6['sign'] + .02, piano(N(n), 3.0, .4), .5)
# S7: dull blows, then silence
a = s7['start']
add(fx, a + s7['strike'] + .1, thud(55, .9), .6)
add(fx, a + s7['y37'], thud(45, 1.1), .7)
for e in s7['erase']: add(fx, a + e, thud(40, 1.0, .6), .45)
# END: lines gather, flag colours in, "25" pops
a = se['start']
add(fx, a + .05, shimmer(1.2), .07)
add(fx, a + .1, whoosh(1.0, 800, 6000), .1)
add(fx, a + 2.05, chime(1568, 1.5), .12); add(fx, a + 2.15, chime(2093, 1.5), .08)
add(fx, a + se['cta'] + .1, pop(), .18)
add(fx, a + se['plus'], pop(), .45); add(fx, a + se['plus'] + .02, chime(2093, 0.8), .18)
write('sfx.wav', fx[:int(SR * dur)])

# ---------- music ----------
mu = np.zeros(int(SR * (dur + 4)))
dark_end = s7['start'] + 3.4            # music gone by the 1937 blows -> silence
# anxious part: Dm - Bb - Gm - A, 4 s per chord, low strings + piano ostinato
prog = [(38, [62, 65, 69]), (34, [62, 65, 70]), (31, [62, 67, 70]), (33, [61, 64, 69])]
b = 0.0
while b < dark_end:
    k = int(b // 4) % 4; root, ch = prog[k]
    L = min(4.4, dark_end - b + 1.5)
    add(mu, b, strings([root + 12, ch[0], ch[2]], L, 1.2, 1.4, 1.0))
    b += 4
for i in range(int(dark_end / .5)):
    tk = i * .5; k = int(tk // 4) % 4; root, ch = prog[k]
    note = [ch[0], ch[2], ch[1] + 12, ch[2]][i % 4]
    add(mu, tk, piano(N(note), 1.6, .30 if i % 2 else .38))
    if i % 8 == 0: add(mu, tk, piano(N(root + 12), 3.0, .45))
fade = np.ones(len(mu)); i0, i1 = int((dark_end - 1.6) * SR), int(dark_end * SR)
fade[i0:i1] = np.linspace(1, 0, i1 - i0) ** 2; fade[i1:] = 0
mu *= fade
# bright final: D - G - Bm - A - D, from the start of the end scene
a = se['start'] + .1
bright = [(50, [62, 66, 69], 1.2), (43, [62, 67, 71], 1.2), (47, [62, 66, 71], 1.0), (45, [61, 64, 69], .9), (50, [62, 66, 69, 74], 2.0)]
tk = a
for root, ch, L in bright:
    add(mu, tk, strings([root, root + 12] + ch, L + 1.2, .5, 1.2, 1.1))
    add(mu, tk, piano(N(root), 3.0, .5))
    for j in range(int(L / .35)):
        add(mu, tk + j * .35, piano(N(ch[j % len(ch)] + 12), 1.8, .3))
    tk += L
mu = reverb(mu, 2.6, .35)
mu = mu[:int(SR * dur)]
fo = np.ones(len(mu)); k = int(SR * 1.2); fo[-k:] = np.linspace(1, 0, k)
write('music.wav', norm(mu) * .8 * fo)
print('sfx.wav + music.wav', dur, 's')
