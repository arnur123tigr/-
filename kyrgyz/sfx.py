"""Soft "minimal line" sound design and a calm ambient bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
Usage: python3 sfx.py ru|kk   (run one language at a time)"""
import json, sys, wave
import numpy as np

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; END = B['end']
SR = 48000; N = int(END * SR) + SR
rng = np.random.default_rng(11)
sfx = np.zeros(N); mus = np.zeros(N)
PT = [M['s2'] + .3, M['dec'], M['s3'] + .5, M['s4'] + .5, M['s5'] + .5, M['s6'] + .4, M['p7'] + .4]   # as in scene.html


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

# scene 1: pen writes, strike, rewrite, line stretches into the axis
d = M['s2']
put(sfx, .2, click(), .6)
put(sfx, .25, swish(d * .30, 1500, 6000), .25)
put(sfx, d * .40, swish(d * .12 + .1, 2500, 8000), .45); put(sfx, d * .40, click(), .5)
put(sfx, d * .55, swish(d * .28, 1500, 6000), .25)
put(sfx, M['s2'] - .85, swish(1.0, 600, 4000), .5)
# points
for i, t in enumerate(PT):
    put(sfx, t, ping(1760 if i != 4 else 2093), .5 if i != 4 else .65)
    put(sfx, t + .1, swish(.7, 1200, 5000), .12)
put(sfx, M['ph1'] - .3, swish(.8, 500, 3000), .3)
put(sfx, M['rev'], thud(), .35)
put(sfx, M['brk'], thud(), .7); put(sfx, M['brk'] + .05, swish(1.2, 300, 2500), .3)
put(sfx, M['nm'] + .5, swish(.6, 2500, 8000), .3)
put(sfx, M['cap'], ping(1318, .8), .35)
put(sfx, PT[4] + 1.1, swish(.7, 2000, 7000), .3)          # erasing «Қырғыз»
put(sfx, PT[4] + 1.9, swish(.9, 1500, 6000), .3)          # writing «Қазақ»
put(sfx, PT[4] + 2.6, chord([69, 73, 76, 81]), .45)       # light chord on the name coming back
put(sfx, M['ph2'] - .2, swish(.8, 500, 3000), .3)
put(sfx, M['mv'], swish(1.3, 800, 3500), .25); put(sfx, M['mv'] + 1.25, ping(1568, .6), .3)
put(sfx, M['s6'] + .3, swish(1.2, 800, 3500), .25); put(sfx, M['s6'] + 1.45, ping(1568, .6), .3)
put(sfx, M['ssr'], chord([62, 66, 69, 74], 2.8), .5)
# overview: quiet ticks, 1925 blink
put(sfx, M['s7'], swish(1.3, 400, 2500), .35)
for k in range(int((M['s8'] - M['s7'] - 1.2) / .5)): put(sfx, M['s7'] + 1.2 + k * .5, tick(), .15)
put(sfx, M['y20'], ping(1318, .6), .3); put(sfx, M['y25'], ping(2093, .9), .45)
# arrow and end card
put(sfx, M['s8'], swish(1.2, 900, 6000), .5)
put(sfx, M['s8'] + .8, click(), .5)
put(sfx, END - 2.2, chord([64, 68, 71, 76], 2.2), .4)

# ambient bed: soft pad + slow plucked arpeggio, A major / F#m / D / E, 84 bpm
from scipy.signal import butter, sosfilt
prog = [[57, 61, 64], [54, 57, 61], [50, 54, 57], [52, 56, 59]]
bar = 60 / 84 * 4; t = 0.; k = 0
while t < END:
    ch = prog[k % 4]; tb = tt(bar + 1.5)
    pad = sum(np.sin(2 * np.pi * nf(n) * tb + np.sin(2 * np.pi * .3 * tb) * .5) + .4 * np.sin(2 * np.pi * nf(n + 12) * 1.003 * tb) for n in ch)
    pad *= np.minimum(1, tb / .8) * np.minimum(1, (bar + 1.5 - tb) / 1.2)
    put(mus, t, pad, .10)
    for j in range(8):
        n = (ch + [ch[0] + 12])[[0, 1, 2, 3, 2, 1, 2, 3][j]] + 12
        tp = tt(.9); put(mus, t + j * bar / 8, np.sin(2 * np.pi * nf(n) * tp) * np.exp(-tp * 5) * np.minimum(1, tp / .004), .16)
    put(mus, t, np.sin(2 * np.pi * nf(ch[0] - 12) * tt(bar)) * np.exp(-tt(bar) * 1.2), .25)
    t += bar; k += 1
mus = sosfilt(butter(2, 6000, 'low', fs=SR, output='sos'), mus)
te = np.arange(N) / SR; g = np.ones(N); g[te > END - 1] = np.linspace(1, 0, (te > END - 1).sum()); g[te < .5] = te[te < .5] / .5
mus *= g


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
