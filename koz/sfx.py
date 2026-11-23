"""Sound effects and a soft science music bed for the eye reel, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
All synthesised (no samples). Filtering is done with FFT so it stays fast.
Usage: python3 sfx.py ru|kk"""
import json, math, sys, wave
import numpy as np

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; END = B['end']
SR = 48000; N = int(END * SR) + SR
rng = np.random.default_rng(11)
sfx = np.zeros(N); mus = np.zeros(N)


def put(buf, t, x, g=1.):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * g
def tt(d): return np.arange(int(round(d * SR))) / SR
def noise(d): return rng.uniform(-1, 1, int(round(d * SR)))
def band(x, lo=0, hi=24000):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def fade(x, a=.005, r=.05):
    n = len(x); e = np.ones(n); na, nr = max(1, int(a * SR)), max(1, int(r * SR)); e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return x * e
def nf(n): return 440 * 2 ** ((n - 69) / 12)
def echo(x, d=.18, g=.4, n=4):
    y = np.concatenate([x, np.zeros(int(d * n * SR))])
    for k in range(1, n + 1): i = int(d * k * SR); y[i:i + len(x)] += x * g ** k
    return y

# --- effects ---
def boom(d=1.4):
    t = tt(d); f = 70 * np.exp(-t * 3) + 32
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6) + band(noise(d), 0, 300) * np.exp(-t * 6) * .8, .002, .3)
def click(): d = .025; t = tt(d); return band(noise(d), 1500, 7000) * np.exp(-t * 300) * .8
def whoosh(d=.8, lo=200, hi=2500):
    t = tt(d); x = band(noise(d), lo, hi); return fade(x * np.sin(np.pi * t / d) ** 2 * 2.2, .01, .05)
def clack():   # stone on stone, short, with a cave echo
    d = .12; t = tt(d); x = band(noise(d), 400, 4000) * np.exp(-t * 60) + np.sin(2 * np.pi * 380 * t) * np.exp(-t * 45) * .5
    return echo(x, .16, .35, 4)
def roar(d):   # fire: low rumbling noise with crackles
    t = tt(d); x = band(noise(d), 40, 900) * (0.7 + 0.3 * np.sin(t * 2.1) * np.sin(t * 0.7))
    for k in range(int(d * 9)): i = rng.integers(0, len(x) - 400); x[i:i + 300] += band(noise(300 / SR), 2000, 9000) * np.exp(-np.arange(300) / 40) * 2
    return fade(x, .3, .4)
def puff(): d = .45; t = tt(d); return band(noise(d), 150, 1400) * np.sin(np.pi * t / d) ** 2
def hiss(d): t = tt(d); return fade(band(noise(d), 3000, 12000) * (0.6 + 0.4 * np.sin(t * 9)), .05, .2)
def ding(f=1320, d=2.0):
    t = tt(d); x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * (2.2 + m)) for m, a in ((1, 1), (2.76, .4), (5.4, .2), (8.9, .08)))
    return fade(x, .001, .2)
def shimmer(d=1.0):
    t = tt(d); return fade(sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 3) for f in (880, 1108, 1318, 1760)) * .3, .002, .2)
def creak(d=.35):
    t = tt(d); f = 160 + 60 * np.sin(t * 9); x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3; return fade(band(x, 300, 2500) * np.sin(np.pi * t / d), .01, .05)
def moo(d=1.3):
    t = tt(d); f = 120 + 25 * np.sin(np.pi * t / d) - 15 * t
    x = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in range(1, 7)); return fade(band(x, 80, 1500) * np.sin(np.pi * t / d) ** .7, .05, .2)
def hoof(): d = .07; t = tt(d); return band(noise(d), 100, 1500) * np.exp(-t * 60)
def drone(d, f):
    t = tt(d); x = sum(np.sin(2 * np.pi * f * h * t + h) / h ** 1.3 for h in range(1, 9)); return band(x, 40, 1200)
def pluck(f, d=1.2):   # Karplus-Strong, vectorised per period
    P = max(2, int(SR / f)); n = int(d * SR); y = np.zeros(n + P); y[:P] = rng.uniform(-1, 1, P)
    for s in range(P, n + P, P):
        prev = y[s - P:s]; nxt = np.roll(prev, -1); seg = .996 * .5 * (prev + nxt); y[s:s + P] = seg[:len(y[s:s + P])]
    return fade(y[:n], .001, .1)
def drum(d=.35):
    t = tt(d); f = 110 * np.exp(-t * 18) + 60; return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) + band(noise(d), 200, 1200) * np.exp(-t * 30) * .3, .001, .05)

nxt = lambda s: M['s%d' % (int(s[1:]) + 1)] if 's%d' % (int(s[1:]) + 1) in M else END
def tick(): d = .03; t = tt(d); return band(noise(d), 2500, 9000) * np.exp(-t * 250) * .7 + np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 200) * .4
def tuk(): d = .25; t = tt(d); f = 180 * np.exp(-t * 12) + 90; return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18), .001, .05)
def glassding(): return ding(2093, 2.4) * .8 + ding(3136, 2.4) * .3
def rustle(d=1.4):
    x = np.zeros(int(d * SR))
    for k in range(int(d * 40)): i = rng.integers(0, len(x) - 600); x[i:i + 500] += np.sign(np.sin(np.arange(500) * (0.3 + rng.random()))) * np.exp(-np.arange(500) / 120) * .4
    return fade(band(x, 1500, 9000), .1, .3)
def chord(fs, d=2.5): t = tt(d); return fade(sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 1.2) for f in fs) * .3, .02, .6)
def thud(): d = .5; t = tt(d); f = 90 * np.exp(-t * 10) + 45; return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8) + band(noise(d), 100, 900) * np.exp(-t * 25) * .5, .001, .05)
# s1: flip whoosh, s2 click, cut whoosh
put(sfx, 0.05, boom(1.2), .25)
put(sfx, 1.0, whoosh(1.2, 200, 3000), .6)
put(sfx, M['s2'] - .7, whoosh(.8, 300, 4000), .5)
put(sfx, M['s2'] + .1, click(), .9); put(sfx, M['s2'] + .16, click(), .6)
put(sfx, M['s3'] - .9, whoosh(1.0, 150, 2500), .6)
# s3: three "tuk" for the layers (+ cornea)
for m in ('scl', 'cho', 'ret'): put(sfx, M[m] + .05, tuk(), .55)
put(sfx, M['here'] + .1, shimmer(1.2), .3)
# s4: glass ring when light refracts, shimmer at the image
put(sfx, M['s4'] + .2, whoosh(.8, 600, 5000), .3)
put(sfx, M['ref'] + .1, glassding(), .5)
put(sfx, M['inv'] + .4, shimmer(1.0), .35)
# s5: pixel rustle, then silence before the tease
put(sfx, M['s5'] - .5, whoosh(.9, 200, 3000), .4)
put(sfx, M['rod'], rustle(1.6), .35); put(sfx, M['cone'], rustle(1.6), .35)
put(sfx, M['tease'] + .2, whoosh(1.4, 300, 5000), .45)
# s6: brain turns the picture, stumble, soft chord when it works
put(sfx, M['s6'] + 1.2, whoosh(1.0, 300, 3000), .4)
put(sfx, M['fall'] + .45, thud(), .8); put(sfx, M['fall'] + .75, thud(), .4)
put(sfx, M['ok'] + .3, chord([523.25, 659.25, 783.99]), .5)
# s7: ticking while the viewer tries it, puff at "gone"
t = M['near']
while t < M['gone']: put(sfx, t, tick(), .5); t += .5
put(sfx, M['gone'], puff(), .8)
# s8: ticking timer, ding at the answer
t = M['ans'] - 3.0
while t < M['ans'] - .05: put(sfx, t, tick(), .7); t += .5
put(sfx, M['ans'], ding(1568, 2.0), .5)
# s9: final chord
put(sfx, M['s9'] + .5, whoosh(1.0, 300, 4000), .4)
put(sfx, END - 2.2, chord([392, 523.25, 659.25, 783.99], 2.2), .6)

# --- music: warm curious pad + soft plucked arpeggio (C major pentatonic, 100 bpm) ---
def pad(d, fs):
    t = tt(d); x = sum(np.sin(2 * np.pi * f * t + np.sin(t * .7 + f) * .5) * (1 + .3 * np.sin(t * .3 + f)) for f in fs); return band(x, 60, 3000)
bpm = 100; beat = 60 / bpm; bar = beat * 4
prog = [[48, 55, 64], [45, 52, 60], [41, 48, 57], [43, 50, 59]]   # C Am F G
t = 0.; k = 0
while t < END:
    put(mus, t, fade(pad(bar + .5, [nf(n) for n in prog[k % 4]]) * .12, .3, .5))
    arp = [prog[k % 4][0] + 24, prog[k % 4][1] + 24, prog[k % 4][2] + 12, prog[k % 4][1] + 24]
    for j in range(8): put(mus, t + j * beat / 2, pluck(nf(arp[j % 4] + (12 if j == 5 else 0)), .8), .22 if j % 2 == 0 else .14)
    if k % 2 == 1: put(mus, t, drum(.3), .18)
    t += bar; k += 1
te = np.arange(N) / SR; g = np.minimum(1, te / 1.0); g[te > END - .5] *= np.linspace(1, 0, (te > END - .5).sum()); mus *= g
# music dips at the quiz pause so the ticking is heard
for a_, b_ in ((M['ans'] - 3.1, M['ans'] + .3),):
    i0, i1 = int(a_ * SR), int(b_ * SR); mus[i0:i1] *= .45


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
