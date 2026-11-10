"""Synthesise the script SFX (sfx.wav) and a minimal piano music bed (music.wav) for the Shokan reel:
calm A minor start, tense pulse in the middle (route, disguise, caravan), quiet bright finale."""
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

def pluck(f=110, L=2.5):            # Karplus-Strong taut string
    n = int(SR / f); buf = rng.standard_normal(n) * .8; out = np.zeros(int(SR * L))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = .996 * .5 * (buf[i % n] + buf[(i + 1) % n])
    t = tt(L); return norm(out * np.exp(-t * 1.2))

s1, s2, s3, s4, s5, s6, s7, se = (sc[k] for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'end'])
fx = np.zeros(int(SR * (dur + 2)))
# S1: a single piano note
add(fx, .05, reverb(piano(N(57), 4.0, 1.0), 2.4, .4), .5)
add(fx, s1['vanish'], whoosh(.6, 1500, 7000), .1)
# S2: low hum, gate thud and the cross
add(fx, s2['start'], drone(s2['end'] - s2['start'] + .3), .45)
add(fx, s2['start'] + s2['city'], chime(880, 1.2), .07)
add(fx, s2['start'] + s2['gate'] + .55, thud(50, 1.0), .45)
add(fx, s2['start'] + s2['cross'] + .05, scratch(.25), .25); add(fx, s2['start'] + s2['cross'] + .28, scratch(.25), .25)
# S3: hair dust + fabric rustle
add(fx, s3['start'] + s3['shave'], shimmer(.8), .05)
add(fx, s3['start'] + s3['morph'], rustle(1.1), .32)
add(fx, s3['start'] + s3['morph'] + .3, rustle(.7), .2)
# S4: taut string twangs, soft steps
for tw in s4['twang']: add(fx, s4['start'] + tw, pluck(98, 2.4), .3)
for k in range(int((s4['end'] - s4['start']) / .36)): add(fx, s4['start'] + k * .36, band(rng.standard_normal(int(SR * .08)), 200, 1500) * np.exp(-tt(.08) * 40), .05)
# S5: quill scratching, sheets
a = s5['start']
for k in range(int((s5['end'] - a) / .38)): add(fx, a + .1 + k * .38, scratch(.3), .09)
for k in range(1, 27): add(fx, a + k * .2, rustle(.15), .04)
# S6: soft bright chord
for n in (57, 64, 69, 72, 76): add(fx, s6['start'] + s6['book'] + .7, piano(N(n), 3.5, .45), .45)
add(fx, s6['start'] + s6['langs'], shimmer(1.8), .05)
# S7: silence, one note
add(fx, s7['start'] + s7['y29'], reverb(piano(N(45), 4.0, 1.0), 2.4, .45), .45)
# END: phone down, book opens, "25" pops
a = se['start']
add(fx, a + se['phone'] + .55, thud(120, .25, .2), .12)
add(fx, a + se['open'], rustle(.5), .25)
add(fx, a + se['n25'], pop(), .4); add(fx, a + se['n25'] + .02, chime(2093, .8), .15)
write('sfx.wav', fx[:int(SR * dur)])

# ---------- music: minimal piano ----------
mu = np.zeros(int(SR * (dur + 5)))
calm = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]   # Am F C G
def arp(t0, t1, step, vel, prog, bass_every=8):
    i = 0; tk = t0
    while tk < t1:
        k = int((tk - t0) // (step * 8)) % len(prog); root, ch = prog[k]
        add(mu, tk, piano(N([ch[0], ch[1], ch[2], ch[1] + 12][i % 4] + 12), 1.8, vel * (1 if i % 2 == 0 else .8)))
        if i % bass_every == 0: add(mu, tk, piano(N(root), 3.5, vel * 1.3))
        i += 1; tk += step
arp(1.2, s2['start'], .5, .30, calm)                                         # calm opening
tense = [(45, [57, 60, 64]), (44, [56, 60, 64]), (41, [57, 60, 65]), (40, [56, 59, 64])]  # Am  Ab+  F  E
arp(s2['start'], s5['start'], .25, .32, tense, 4)                            # conflict: faster pulse
for k in range(int((s5['start'] - s2['start']) / 1.0)): add(mu, s2['start'] + k, piano(N(33), 2.0, .5))   # low heartbeat
arp(s5['start'], s6['start'], .3, .26, calm)                                 # writing: steady
bright = [(41, [60, 65, 69]), (48, [60, 64, 67]), (45, [60, 64, 69])]        # F C Am — warm
arp(s6['start'] + .7, s7['start'] + .4, .45, .24, bright)
arp(se['start'] + .4, dur, .6, .22, [(45, [60, 64, 69]), (41, [60, 65, 69]), (48, [60, 64, 67]), (45, [60, 64, 69])])
mu = reverb(mu, 2.8, .4)[:int(SR * dur)]
fo = np.ones(len(mu)); k = int(SR * 1.5); fo[-k:] = np.linspace(1, 0, k)
write('music.wav', norm(mu) * .8 * fo)
print('sfx.wav + music.wav', dur, 's')
