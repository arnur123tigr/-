"""Comic sound design (zaps, buzz, relay clicks, boings, tape) (pops, whooshes, knocks, pings) and a light upbeat bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
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

def buzz(d=1.4):   # cartoon bug buzz: detuned saw-ish wobble
    t = tt(d); f = 210 + 25 * np.sin(2 * np.pi * 9 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .5 + np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR) * .3
    return bp(x, 300, 4000) * np.sin(np.pi * t / d) ** .5
def zap(): t = tt(.25); f = 1800 * np.exp(-t * 14) + 120; return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 10) * .6
def beep(f=880, d=.16): t = tt(d); return np.sign(np.sin(2 * np.pi * f * t)) * .4 * np.minimum(1, (d - t) / .01)
def relay_click(): t = tt(.02); return (bp(rng.uniform(-1, 1, len(t)), 2500, 9000) + np.sin(2 * np.pi * 3200 * t)) * np.exp(-t * 400)
def tape(d=.6): t = tt(d); return bp(rng.uniform(-1, 1, len(t)), 1500, 7000) * (0.5 + .5 * np.sin(2 * np.pi * 38 * t) ** 2) * np.sin(np.pi * t / d)
def rip(d=.45): t = tt(d); return bp(rng.uniform(-1, 1, len(t)), 800, 6000) * (rng.uniform(0.3, 1, len(t)) ** 3) * np.exp(-t * 4)
def boing(): t = tt(.5); f = 200 + 120 * np.sin(2 * np.pi * 12 * t) * np.exp(-t * 5); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
def scribble(d): t = tt(d); return bp(rng.uniform(-1, 1, len(t)), 2000, 6000) * (0.4 + .6 * np.abs(np.sin(2 * np.pi * 6 * t)))

# scene 1: error zap, glass crack, bug buzzing
put(sfx, .05, zap(), .5); put(sfx, .1, pop(), .5)
put(sfx, .75, knock(1400), .6); put(sfx, .8, thud(), .35)
put(sfx, .95, buzz(2.4), .32)
put(sfx, M['zhuk'], boing(), .45); put(sfx, M['real'], ding(), .45)
put(sfx, M['s2'] - .1, rip(), .6)
# scene 2: icons click in, laugh burst
put(sfx, M['s2'] + .15, pop(), .55)
for i in range(3): put(sfx, M['s2'] + .6 + i * .45, click(), .7); put(sfx, M['s2'] + .62 + i * .45, pop(), .4)
put(sfx, M['funny'], buzz(.8), .25); put(sfx, M['funny'] + .1, boing(), .4)
put(sfx, M['s3'] - .55, boom(), .6); put(sfx, M['s3'] - .5, pop(), .5)
# scene 3: whoosh to the sign, relay clicks
put(sfx, M['s3'] + .5, pop(), .45)
put(sfx, M['relay'] - .3, whoosh(1.0), .45)
k = 0.
while M['relay'] + k < M['s4'] - .9:
    put(sfx, M['relay'] + .3 + k, relay_click(), .5 if k % .5 < .15 else .3); k += .13 + (hash := (np.sin(k * 91) * .5 + .5)) * .12
for i in range(4): put(sfx, M['click'] + i * .45, relay_click(), .9); put(sfx, M['click'] + i * .45, pop(), .35)
for i in range(3): put(sfx, M['s4'] - 1.0 + i * .25, beep(990, .12), .35)
# scene 4: beeps, ticking clock, check, cross
put(sfx, M['s4'] + .05, whoosh(.5), .35)
for i in range(4): put(sfx, M['s4'] + .4 + i * .3, beep(660 if i % 2 else 880), .3)
t = M['s4'] + .3
while t < M['s5'] - 1: put(sfx, t, tick(), .3); t += .25
put(sfx, M['s4'] + .8, pop(), .4)
put(sfx, M['check'], swish(.5, 2000, 7000), .3); put(sfx, M['ok'], ding(), .55)
put(sfx, M['still'] + .1, beep(440, .25), .45); put(sfx, M['still'] + .4, beep(440, .25), .45); put(sfx, M['still'] + .2, pop(), .45)
put(sfx, M['s5'] - .9, whoosh(.9), .4)
# scene 5: macro reveal, «ой!»
put(sfx, M['s5'], whoosh(.6, ), .4); put(sfx, M['moth'] - .3, pop(), .45)
put(sfx, M['s6'] - 1.0, boing(), .55); put(sfx, M['s6'] - 1.0, pop(), .5)
# scene 6: page slap, tape, scribble, museum
put(sfx, M['s6'], whoosh(.5), .4); put(sfx, M['s6'] + .25, knock(500), .5)
put(sfx, M['tape'] - .1, tape(.5), .5); put(sfx, M['tape'] + .3, tape(.5), .5)
put(sfx, M['wrote'], scribble(2.2), .18)
put(sfx, M['museum'] - .2, whoosh(.8), .35); put(sfx, M['museum'] + .5, pop(), .5); put(sfx, M['museum'] + .6, ding(), .35)
# scene 7: journal closes, Edison card, BUG bursts, columns, «пуф» on icons
put(sfx, M['s7'], thud(), .45); put(sfx, M['s7'] + .9, pop(), .5)
for i in range(6): put(sfx, M['world'] + i * .15, pop(), .4)
put(sfx, M['world'], buzz(1.2), .2)
put(sfx, M['debug'] - .1, pop(), .55); put(sfx, M['otl'] - .1, pop(), .55); put(sfx, M['otl'], ding(), .35)
for i in range(3): put(sfx, M['otl'] + .15 + i * .5, swish(.25, 300, 2500), .55); put(sfx, M['otl'] + .2 + i * .5, pop(), .4)
put(sfx, M['remove'] - .2, buzz(.9), .25)
# scene 8: quiz
put(sfx, M['s8'], whoosh(.5), .45); put(sfx, M['s8'] + .1, pop(), .5)
for i in range(3): put(sfx, M['o1'] + i * .55, pop(), .4)
k = 0
while M['qa'] + k * .5 < M['qb'] - .05: put(sfx, M['qa'] + k * .5, tick(), .5); k += 1
put(sfx, M['ans'], ding(), .7); put(sfx, M['ans'], chord([72, 76, 79], 1.6), .35)
# scene 9 + end
put(sfx, M['s9'], whoosh(.5), .4); put(sfx, M['s9'] + .1, boing(), .45); put(sfx, M['s9'] + .2, buzz(1.2), .2)
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
