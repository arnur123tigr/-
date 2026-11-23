"""Flat-vector «pop & slide» sound design (pops, whooshes, knocks, pings) and a light upbeat bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
Usage: python3 sfx.py ru|kk   (run one language at a time)"""
import json, sys, wave
import numpy as np

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; END = B['end']
SR = 48000; N = int(END * SR) + SR
rng = np.random.default_rng(11)
sfx = np.zeros(N); mus = np.zeros(N)
def put(buf, t, x, g=1.):
    i = int(t * SR)
    if i < 0 or i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * g
def tt(d): return np.arange(int(round(d * SR))) / SR
def nf(n): return 440 * 2 ** ((n - 69) / 12)
def lp1(x, a):   # one-pole low-pass, vectorised enough for short sounds
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x)
def bp(x, lo, hi):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)

def click(): t = tt(.03); return bp(rng.uniform(-1, 1, len(t)), 2000, 9000) * np.exp(-t * 300)
def ping(f=1760, d=1.2):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 4) * np.minimum(1, t / .003)
def swish(d=.6, lo=900, hi=5000):   # a line being drawn: filtered noise with a rise and fall
    t = tt(d); e = np.sin(np.pi * t / d) ** 2
    return bp(rng.uniform(-1, 1, len(t)), lo, hi) * e
def thud():
    t = tt(.8); f = 70 * np.exp(-t * 3) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) + lp1(rng.uniform(-1, 1, len(t)), .05) * np.exp(-t * 12) * .6
def chord(notes, d=2.2):
    t = tt(d); x = sum(np.sin(2 * np.pi * nf(n) * t) * np.exp(-t * 1.6) for n in notes) / len(notes)
    return x * np.minimum(1, t / .01)
def tick(): t = tt(.04); return np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 160)

def pop(): t = tt(.12); f = 300 + 900 * np.exp(-t * 40); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
def boom(): return thud()
def whoosh(d=.5): return swish(d, 400, 3000)
def ding(): return ping(2093, 1.0)
def knock(f=900): t = tt(.12); return np.sin(2 * np.pi * f * t) * np.exp(-t * 45) + bp(rng.uniform(-1, 1, len(t)), 1500, 5000) * np.exp(-t * 90) * .4

def baa(d=.7, f0=330):   # synthetic «бее»: buzzy vowel with a wobble
    t = tt(d); vib = 1 + .06 * np.sin(2 * np.pi * 7 * t); f = f0 * vib * (1 + .15 * np.exp(-t * 6))
    ph = 2 * np.pi * np.cumsum(f) / SR; x = sum(np.sin(k * ph) / k ** .8 for k in range(1, 9))
    x = bp(x, 350, 3200) * np.minimum(1, t / .05) * np.minimum(1, (d - t) / .2) * (1 + .5 * np.sin(2 * np.pi * 16 * t))
    return x / max(1e-6, np.abs(x).max())
def zap(d=.6):
    t = tt(d); return (bp(rng.uniform(-1, 1, len(t)), 2500, 9000) * (np.sin(2 * np.pi * 60 * t) > 0) + .5 * np.sign(np.sin(2 * np.pi * 120 * t))) * np.exp(-t * 6)
def slurp(d=.5):
    t = tt(d); f = 900 * np.exp(-t * 3); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * .7

# scene 1: «бее», hearts pop, father crossed
put(sfx, .25, baa(.75, 340), .45); put(sfx, .1, pop(), .4)
for i in range(3): put(sfx, .45 + i * .3, pop(), .5)
put(sfx, M['oke'], knock(500), .5); put(sfx, M['oke'] + .1, pop(), .45)
put(sfx, M['s2'] - .6, whoosh(.7), .5)
# scene 2: tag + ENT pill
put(sfx, M['s2'] + .1, pop(), .6); put(sfx, M['s2'] + .2, click(), .5); put(sfx, M['ent'], ding(), .5)
put(sfx, M['s3'] - .3, whoosh(.6), .45)
# scene 3: mother 1, cell flies out, nucleus «чпок»
put(sfx, M['s3'] + .1, pop(), .5); put(sfx, M['s3'] + .5, baa(.6, 380), .25)
put(sfx, M['cell'], whoosh(.8), .4); put(sfx, M['cell'] + .7, pop(), .45)
put(sfx, M['dna'], pop(), .7); put(sfx, M['dna'] + .05, ping(1568, .8), .35)
put(sfx, M['s4'] - .4, whoosh(.6), .45)
# scene 4: mother 2, egg, pipette, nucleus in, zap
put(sfx, M['s4'] + .1, pop(), .5); put(sfx, M['s4'] + .5, baa(.6, 290), .22)
put(sfx, M['egg'], whoosh(.8), .4); put(sfx, M['egg'] + .7, pop(), .45)
put(sfx, M['rm'], swish(.5, 1500, 6000), .3); put(sfx, M['rm'] + .5, slurp(.5), .45)
put(sfx, M['put'], whoosh(.7), .4); put(sfx, M['put'] + .75, pop(), .55)
put(sfx, M['zap'], zap(.7), .45); put(sfx, M['zap'], ping(2637, .9), .3)
# scene 5: division pops, flight into mother 3, 277 fails, one success
for i, d in enumerate((.4, .9, 1.4)): put(sfx, M['s5'] + d, pop(), .35 + .05 * i)
put(sfx, M['s5'] + 1.9, whoosh(.7), .35); put(sfx, M['s5'] + 2.6, ping(1318, 1.0), .35)
for i in range(14): put(sfx, M['try'] + .25 + i * 1.9 / 14, knock(420 + (i % 3) * 40), .18)
put(sfx, M['try'] + 2.25, chord([72, 76, 79], 1.6), .4); put(sfx, M['try'] + 2.25, ding(), .5)
# scene 6: film shot, lamb bleat
put(sfx, M['s6'] - .35, whoosh(.6), .4); put(sfx, M['s6'] + 1.4, baa(.6, 520), .25); put(sfx, M['s6'] + .45, pop(), .4)
put(sfx, M['s7'] - .2, whoosh(.6), .4)
# scene 7: mothers pop, aha chord
for i in range(3): put(sfx, M['s7'] + .3 + i * .15, pop(), .4)
put(sfx, M['s7'] + .7, pop(), .5)
put(sfx, M['face'], chord([64, 68, 71, 76], 2.2), .45); put(sfx, M['face'] + .1, ding(), .35)
put(sfx, M['copy'], pop(), .5)
# scene 8: quiz
put(sfx, M['s8'] - .1, whoosh(.5), .45); put(sfx, M['s8'] + .05, pop(), .45)
for i in range(3): put(sfx, M['o1'] + i * .9, pop(), .4)
k = 0
while M['qa'] + k * .5 < M['qb'] - .05: put(sfx, M['qa'] + k * .5, tick(), .45); k += 1
put(sfx, M['ans'], ding(), .7); put(sfx, M['ans'], chord([72, 76, 79], 1.6), .35)
# scene 9 + end card
put(sfx, M['s9'] - .1, whoosh(.6), .45); for_ = [put(sfx, M['s9'] + .3 + i * .15, pop(), .35) for i in range(4)]
put(sfx, M['s9'] + .9, baa(.7, 360), .3)
put(sfx, M['cta'] - .2, pop(), .5)
put(sfx, END - 2.2, chord([64, 68, 71, 76], 2.2), .45)

# ambient bed: soft pad + slow plucked arpeggio, A major / F#m / D / E, 84 bpm
from scipy.signal import butter, sosfilt
prog = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
bar = 60 / 104 * 4; t = 0.; k = 0
while t < END:
    ch = prog[k % 4]; tb = tt(bar + 1.5)
    pad = sum(np.sin(2 * np.pi * nf(n) * tb + np.sin(2 * np.pi * .3 * tb) * .5) + .4 * np.sin(2 * np.pi * nf(n + 12) * 1.003 * tb) for n in ch)
    pad *= np.minimum(1, tb / .8) * np.minimum(1, (bar + 1.5 - tb) / 1.2)
    put(mus, t, pad, .10)
    for j in range(8):
        n = (ch + [ch[0] + 12])[[0, 1, 2, 3, 2, 1, 2, 3][j]] + 12
        tp = tt(.9); put(mus, t + j * bar / 8, np.sin(2 * np.pi * nf(n) * tp) * np.exp(-tp * 5) * np.minimum(1, tp / .004), .16)
    put(mus, t, np.sin(2 * np.pi * nf(ch[0] - 12) * tt(bar)) * np.exp(-tt(bar) * 1.2), .25)
    for j in range(4):   # soft kick on beats, closed hat on off-beats
        tk = tt(.25); put(mus, t + j * bar / 4, np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 14), .22)
        th = tt(.05); put(mus, t + j * bar / 4 + bar / 8, bp(rng.uniform(-1, 1, len(th)), 6000, 12000) * np.exp(-th * 80), .05)
    t += bar; k += 1
mus = sosfilt(butter(2, 6000, 'low', fs=SR, output='sos'), mus)
te = np.arange(N) / SR; g = np.ones(N); g[te > END - 1] = np.linspace(1, 0, (te > END - 1).sum()); g[te < .5] = te[te < .5] / .5
mus *= g


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
