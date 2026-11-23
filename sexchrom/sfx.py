"""Soft "minimal line" sound design (sex chromosomes reel) and a calm ambient bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
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

def coin():   # crown "ding"
    t = tt(1.6); return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((2637, 3), (3951, 5), (5274, 7))) / 3 * np.minimum(1, t / .002)
def beep(): t = tt(.12); return np.sin(2 * np.pi * 1900 * t) * np.minimum(1, (.12 - t) / .03) * np.minimum(1, t / .005)
def cluck():
    t = tt(.16); f = 700 + 500 * np.exp(-t * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * (1 + .5 * np.sin(2 * np.pi * 90 * t))
def splash(): t = tt(.9); return bp(rng.uniform(-1, 1, len(t)), 500, 6000) * np.exp(-t * 6) * np.minimum(1, t / .01)

S = lambda k: M[k]
# 1: crown and six ticks as the wives disappear
put(sfx, .15, swish(1.2, 1500, 6000), .25); put(sfx, 1.3, coin(), .35)
for i in range(6): put(sfx, .5 + i * .22, swish(.35, 2000, 7000), .12)
for i in range(6): put(sfx, S('n1') + .3 + i * (S('s2') - S('n1') - .9) / 6, tick(), .35)
put(sfx, S('n1') + 1.0, ping(1318, .8), .3)
# 2: cell, click, pill
put(sfx, S('s2'), swish(1.0, 900, 5000), .3); put(sfx, S('s2') + .9, click(), .6); put(sfx, S('ent'), ping(1760, .6), .3)
# 3: columns, two «тук»
put(sfx, S('s3'), swish(.8, 600, 3500), .3)
put(sfx, S('xx') + .3, thud(), .45); put(sfx, S('xx') + .7, thud(), .35)
put(sfx, S('xy') + .3, thud(), .45); put(sfx, S('xy') + 1.0, thud(), .35)
put(sfx, S('pair'), chord([69, 73, 76]), .3)
# 4: gametes fly, ping on every cell
put(sfx, S('s4') + .4, swish(1.2, 1200, 5000), .2)
for r in range(2): put(sfx, S('mom') + .4 + r * .35, swish(.8, 1500, 6000), .2)
for q in range(2): put(sfx, S('dad') + .9 + q * .4, swish(.8, 1500, 6000), .2)
for r in range(2): put(sfx, S('gx') + .15 + r * .3, ping(1568 + r * 200, .7), .35)
for r in range(2): put(sfx, S('gy') + .15 + r * .3, ping(2093 + r * 200, .7), .35)
put(sfx, S('fa'), chord([62, 66, 69, 74], 2.4), .4)
# 5: Y grows, blinking beep on SRY, two roads, 50/50
put(sfx, S('s5'), swish(1.0, 600, 4000), .3)
for k in range(5): put(sfx, S('s5') + 1.2 + k * .78, beep(), .14)
put(sfx, S('m'), swish(.8, 1200, 5000), .25); put(sfx, S('f'), swish(.8, 1200, 5000), .25)
put(sfx, S('p50'), ping(1318, .9), .3); put(sfx, S('p50') + .1, ping(1976, .9), .25)
# 6: hen, cluck, crocodile, splash
put(sfx, S('s6') + .1, swish(1.8, 1500, 6000), .2)
put(sfx, S('bird'), cluck(), .4); put(sfx, S('bird') + .22, cluck(), .32)
put(sfx, S('croc'), swish(1.4, 800, 4000), .25); put(sfx, S('croc') + .3, splash(), .35)
# 7: crown again, light chord, die rolling
put(sfx, S('s7'), coin(), .3); put(sfx, S('s7') + 1.3, chord([67, 71, 74, 79]), .35)
for k in range(10): put(sfx, S('none') + k * .13, click(), .3 * (1 - k / 12))
# 8: quiz ticking and «динь»
put(sfx, S('s8'), click(), .5)
for i in range(3): put(sfx, S('o1') + i * .45, swish(.4, 2000, 7000), .2)
t = S('qa')
while t < S('ans') - .1: put(sfx, t, tick(), .4); t += .5
put(sfx, S('ans'), ping(2093, 1.3), .5); put(sfx, S('ans') + .05, ping(2637, 1.3), .3)
# 9: handshake, arrow, final chord
put(sfx, S('s9') + .8, click(), .5); put(sfx, S('cta') - .3, swish(1.0, 900, 6000), .4)
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
