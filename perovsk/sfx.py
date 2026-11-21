"""Flat-vector "pop & slide" sound design and a serious ambient bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
Usage: python3 sfx.py ru|kk"""
import json, sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; END = B['end']
SR = 48000; N = int(END * SR) + SR
rng = np.random.default_rng(7)
sfx = np.zeros(N); mus = np.zeros(N)


def put(buf, t, x, g=1.):
    i = int(t * SR)
    if i < 0 or i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * g
def tt(d): return np.arange(int(round(d * SR))) / SR
def nf(n): return 440 * 2 ** ((n - 69) / 12)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)

def pop():      # bubbly pop for things that spring in
    t = tt(.12); f = 380 + 900 * np.exp(-t * 40); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)
def swish(d=.4, lo=900, hi=5000): t = tt(d); return bp(rng.uniform(-1, 1, len(t)), lo, hi) * np.sin(np.pi * t / d) ** 2
def ping(f=1760, d=1.0): t = tt(d); return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 4) * np.minimum(1, t / .003)
def boom():     # cannon: low sweep + noise burst
    t = tt(1.1); f = 90 * np.exp(-t * 4) + 32
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) + lp(rng.uniform(-1, 1, len(t)), 900) * np.exp(-t * 9) * 1.4
def crack(): t = tt(.35); return bp(rng.uniform(-1, 1, len(t)), 1500, 7000) * np.exp(-t * 18) * (1 + (rng.uniform(0, 1, len(t)) > .97) * 2)
def creak():    # wooden sign creak: slow filtered saw glide
    t = tt(.7); f = 180 + 60 * np.sin(2 * np.pi * 1.3 * t); ph = np.cumsum(f) / SR
    return bp(2 * (ph % 1) - 1, 300, 2500) * np.sin(np.pi * t / .7) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
def thud(): t = tt(.6); f = 70 * np.exp(-t * 4) + 40; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + lp(rng.uniform(-1, 1, len(t)), 400) * np.exp(-t * 14) * .7
def hoof(): t = tt(.09); return lp(rng.uniform(-1, 1, len(t)), 600) * np.exp(-t * 60) + np.sin(2 * np.pi * 110 * t) * np.exp(-t * 50) * .6
def chord(notes, d=2.2): t = tt(d); return sum(np.sin(2 * np.pi * nf(n) * t) * np.exp(-t * 1.6) for n in notes) / len(notes) * np.minimum(1, t / .01)
def tick(): t = tt(.04); return np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 160)
def splash(): t = tt(.9); return bp(rng.uniform(-1, 1, len(t)), 600, 4000) * np.exp(-t * 5) * (1 + .5 * np.sin(2 * np.pi * 9 * t))

# scene 1: pill pop, sign trembles, slips, wipe
put(sfx, .5, pop(), .5)
put(sfx, 1.0, creak(), .35); put(sfx, M['kz'] - 1.4, creak(), .35)
put(sfx, M['kz'] - .9, swish(.5, 500, 3000), .4); put(sfx, M['kz'] - .35, thud(), .4)
put(sfx, M['kz'] - .5, pop(), .5)
put(sfx, M['s2'] - .6, swish(.8, 400, 4000), .45)
# scene 2
put(sfx, M['s2'] + .5, pop(), .5); put(sfx, M['s2'] + .3, splash(), .25); put(sfx, M['ak'], ping(1760), .35); put(sfx, M['mq'], pop(), .45)
# scene 3: army slides in, cannon shots
put(sfx, M['s3'] + .1, swish(.9, 300, 2500), .4); put(sfx, M['s3'] + .4, ping(1760), .3); put(sfx, M['s3'] + .7, pop(), .45)
a, b = M['s3'] + 1.3, M['s4'] - .5; n = max(3, round((b - a) / .85))
for i in range(n):
    t = a + (b - a) * i / (n - 1); put(sfx, t, boom(), .5); put(sfx, t + .45, crack(), .35)
put(sfx, M['ph'] - .1, swish(.6, 600, 3500), .35)
# scene 4: three pops on the sign
for k in ('s4', 'n2', 'n3'): put(sfx, M[k] + (.9 if k == 's4' else 0), pop(), .55)
put(sfx, M['n4'], pop(), .45)
# scene 5: gallop
put(sfx, M['s5'] + .9, swish(.8, 300, 2500), .3)
t = M['s5'] + .3
while t < M['s6'] - .2:
    for d in (0, .07, .16): put(sfx, t + d, hoof(), .28)
    t += .45
put(sfx, M['rd'] + .3, pop(), .45); put(sfx, M['age'], pop(), .4)
# scene 6: sign pops, bright chord on Kyzylorda, overview pops
put(sfx, M['s6'] + .6, ping(1568, .7), .3); put(sfx, M['n5'], pop(), .55); put(sfx, M['n6'], pop(), .55)
put(sfx, M['n6'] + .1, chord([72, 76, 79, 84], 2.6), .5)
for i in range(6): put(sfx, M['n6'] + 1.52 + i * .14, pop(), .3)
# scene 7: quiz
put(sfx, M['s7'] - .2, swish(.6, 500, 4000), .4)
for i in range(3): put(sfx, M['op'] + i * .55, pop(), .45)
t = M['ans'] - 3
while t < M['ans'] - .05: put(sfx, t, tick(), .35); t += .5
put(sfx, M['ans'], ping(2093, 1.4), .55); put(sfx, M['ans'] + .05, chord([76, 80, 83], 1.4), .3)
# scene 8 and end card
put(sfx, M['s8'] - .1, swish(.7, 500, 4000), .4); put(sfx, M['cta'] - .3, pop(), .5)
put(sfx, END - 2.2, chord([64, 68, 71, 76], 2.2), .4)

# ambient bed: D minor, soft pad + slow plucks + low pulse, 80 bpm (serious, unhurried)
prog = [[50, 53, 57], [46, 50, 53], [43, 46, 50], [45, 49, 52]]
bar = 60 / 80 * 4; t = 0.; k = 0
while t < END:
    ch = prog[k % 4]; tb = tt(bar + 1.5)
    pad = sum(np.sin(2 * np.pi * nf(n) * tb + np.sin(2 * np.pi * .3 * tb) * .5) + .4 * np.sin(2 * np.pi * nf(n + 12) * 1.003 * tb) for n in ch)
    pad *= np.minimum(1, tb / .8) * np.minimum(1, (bar + 1.5 - tb) / 1.2)
    put(mus, t, pad, .10)
    for j in range(8):
        n = (ch + [ch[0] + 12])[[0, 2, 1, 3, 2, 1, 2, 3][j]] + 12
        tp = tt(.9); put(mus, t + j * bar / 8, np.sin(2 * np.pi * nf(n) * tp) * np.exp(-tp * 5) * np.minimum(1, tp / .004), .13)
    for j in range(4):
        tp = tt(.5); put(mus, t + j * bar / 4, np.sin(2 * np.pi * nf(ch[0] - 12) * tp) * np.exp(-tp * 6), .3)
    t += bar; k += 1
mus = lp(mus, 6000)
te = np.arange(N) / SR; g = np.ones(N); g[te > END - 1] = np.linspace(1, 0, (te > END - 1).sum()); g[te < .5] = te[te < .5] / .5
mus *= g


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
