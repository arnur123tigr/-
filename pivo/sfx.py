"""Clay flat-vector sound design (tuk on clay, bul of beer, wind, waves, keys) (pops, whooshes, knocks, pings) and a light upbeat bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
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

def tuk(): t = tt(.18); return np.sin(2 * np.pi * np.cumsum(180 + 260 * np.exp(-t * 50)) / SR) * np.exp(-t * 28) + bp(rng.uniform(-1, 1, len(t)), 300, 2500) * np.exp(-t * 60) * .5
def bul():
    t = tt(.35); f = 400 + 500 * np.sin(np.pi * t / .35) ** 2; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / .35) ** 2
def waves(d):
    t = tt(d); return bp(rng.uniform(-1, 1, len(t)), 200, 1400) * (.5 + .5 * np.sin(2 * np.pi * t / 2.6) ** 2) * np.minimum(1, t / .5) * np.minimum(1, (d - t) / .5)
def wind(d):
    t = tt(d); return bp(rng.uniform(-1, 1, len(t)), 250, 900) * (.6 + .4 * np.sin(2 * np.pi * t / 3.1)) * np.minimum(1, t / .6) * np.minimum(1, (d - t) / .6)
def scratch(d):
    t = tt(d); return bp(rng.uniform(-1, 1, len(t)), 2500, 7000) * (.3 + .7 * (np.sin(2 * np.pi * t * 3.3) > .2)) * np.minimum(1, t / .1) * np.minimum(1, (d - t) / .2)
def key(): t = tt(.05); return bp(rng.uniform(-1, 1, len(t)), 1800, 6000) * np.exp(-t * 120)

# scene 1
put(sfx, .35, tuk(), .7); put(sfx, M['not'], pop(), .5); put(sfx, M['not'] + .5, pop(), .45)
put(sfx, M['not'] + .4, swish(.3, 2000, 6000), .3); put(sfx, M['not'] + .9, swish(.3, 2000, 6000), .3)
put(sfx, M['arpa'], tuk(), .8); put(sfx, M['arpa'] + .1, whoosh(.4), .3); put(sfx, M['beer'], bul(), .6); put(sfx, M['beer'] + .05, pop(), .4)
put(sfx, 1.0, whoosh(.4), .3)
# scene 2: map
put(sfx, M['s2'] - .45, whoosh(.8), .45); put(sfx, M['s2'], wind(M['s3'] - M['s2']), .18)
put(sfx, M['s2'] + 1.0, ping(1760, 1.0), .45); put(sfx, M['ent'], pop(), .55)
# scene 3: film shot
put(sfx, M['s3'] - .4, whoosh(.7), .4); put(sfx, M['s3'] + .3, scratch(M['s4'] - M['s3'] - .5), .2)
# scene 4: decode + Kushim
put(sfx, M['s4'] - .3, thud(), .5)
for m in ('t1', 't2', 't3'): put(sfx, M[m], ping(2093, .8), .5); put(sfx, M[m], pop(), .35)
put(sfx, M['kushim'] + .2, pop(), .6); put(sfx, M['kushim'] + .5, boom(), .45)
put(sfx, M['poet'], pop(), .45); put(sfx, M['poet'] + .35, swish(.3, 2000, 6000), .35); put(sfx, M['acc'], ding(), .55)
# scene 5: three whooshes
put(sfx, M['s5'] - .4, whoosh(.6), .45)
put(sfx, M['s5'] + .3, whoosh(.45), .4); put(sfx, M['ideo'] - .1, whoosh(.45), .4); put(sfx, M['cune'] - .1, whoosh(.45), .4); put(sfx, M['hiero'] - .1, pop(), .5)
# scene 6: pile, sea, squeeze
put(sfx, M['s6'] - .45, whoosh(.6), .45)
for i in range(10): put(sfx, M['s6'] - .1 + i * .15, knock(500 + 60 * (i % 5)), .2)
put(sfx, M['s6'] + .4, pop(), .45)
put(sfx, M['phoen'] - .2, waves(M['s7'] - M['phoen'] + .2), .3); put(sfx, M['one'], pop(), .45)
put(sfx, M['n22'] - .2, swish(.9, 500, 5000), .45); put(sfx, M['n22'] + .7, boom(), .4)
for i in range(22): put(sfx, M['n22'] + .3 + i * .03, click(), .25)
put(sfx, M['n22'] + .9, ding(), .5)
# scene 7: letter morphs, phone keys
put(sfx, M['s7'] - .4, whoosh(.7), .45)
for m in ('greek', 'latin'): put(sfx, M[m] - .1, whoosh(.35), .4); put(sfx, M[m], pop(), .45)
put(sfx, M['phone'] - .2, whoosh(.6), .4)
for i in range(6): put(sfx, M['phone'] + .6 + i * .11, key(), .5)
put(sfx, M['loop'], tuk(), .6); put(sfx, M['loop'] + .1, bul(), .45)
# scene 8: quiz
put(sfx, M['s8'] - .4, whoosh(.6), .45)
for i in range(3): put(sfx, M['o1'] + i * .55, pop(), .4)
k = 0
while M['qa'] + k * .5 < M['ans'] - .05: put(sfx, M['qa'] + k * .5, tick(), .45); k += 1
put(sfx, M['ans'], ding(), .7); put(sfx, M['ans'], chord([72, 76, 79], 1.6), .35)
# scene 9 + end
put(sfx, M['s9'] - .4, whoosh(.6), .45); put(sfx, M['s9'] + .2, tuk(), .6); put(sfx, M['s9'] + .45, bul(), .45)
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
