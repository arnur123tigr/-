"""Sound effects and a warm steppe music bed for the Bronze Age reel, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
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
def grind(d):   # drill: low motor with a rough metallic edge
    t = tt(d); f = 55 + 6 * np.sin(t * 3); x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .35 + band(noise(d), 800, 3500) * (.5 + .5 * np.sin(t * 31) ** 2) * .6
    return fade(band(x, 40, 5000), .3, .4)
def tick(): d = .03; t = tt(d); return band(noise(d), 2500, 9000) * np.exp(-t * 250)
def thud(): d = .5; t = tt(d); f = 90 * np.exp(-t * 10) + 45; return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7), .001, .1)
def shovel():   # spade into soil: crunchy noise + low knock
    d = .22; t = tt(d); return band(noise(d), 300, 3000) * np.exp(-t * 22) * .8 + np.sin(2 * np.pi * 140 * t) * np.exp(-t * 30) * .5
# scene 1: shovel hits in time with the digging (phase of manPose: hit when the spade goes down)
t = .3
while t < M['s2'] - .9: put(sfx, t, shovel(), .6); t += 1 / 1.6
put(sfx, M['s2'] - .9, whoosh(1.0, 150, 1800), .7)
# scene 2: elevator ding, cabin starts
put(sfx, M['icons'] - .1, ding(1320, 2.0), .6); put(sfx, M['icons'] + .1, ding(1046, 2.0), .45)
put(sfx, M['s3'] - .8, whoosh(.9, 150, 1500), .6)
# scene 3: rock rustle under the narration, little clicks on each bracket
d3 = M['s4'] - M['s3']; put(sfx, M['s3'], fade(band(noise(d3), 100, 1200) * .25, .5, .6), .5)
for k in ('ocean', 'plain', 'mount', 'l1', 'l2', 'l3'): put(sfx, M[k] + .1, click(), .7)
# scene 4: drill grinding, hiss at the hot bottom, a stop knock
dg = M['res'] + .8 - M['drill']; put(sfx, M['drill'], grind(dg), .55)
put(sfx, M['hot'], hiss(1.8), .3); put(sfx, M['hot'] + 2.0, thud(), .8)
put(sfx, M['s5'] - .8, whoosh(1.0, 200, 2000), .5)
# scene 5: silence and a "tuk"
put(sfx, M['s5'] + .6, thud(), .7); put(sfx, M['crust'] + .1, click(), .6)
put(sfx, M['s6'] - .9, whoosh(1.1, 120, 1600), .7)
# scene 6: deep rumble of the mantle
d6 = M['s7'] - M['s6']; put(sfx, M['s6'], fade(band(noise(d6), 25, 160) * 1.6 + drone(d6, 41) * .25, .8, .8), .6)
# scene 7: bright whoosh into the core, shimmer
put(sfx, M['s7'] - .4, whoosh(.8, 600, 6000), .6); put(sfx, M['core'], shimmer(1.4), .35)
# scene 8: ding, ticking during the pause, the right-answer ding
put(sfx, M['s8'] + .1, ding(1480, 1.6), .5)
t = M['wait'] - 3.0
while t < M['wait'] - .05: put(sfx, t, tick(), .8); t += .5
put(sfx, M['wait'], ding(1760, 2.2), .7); put(sfx, M['wait'] + .12, ding(2217, 2.0), .45)
# scene 9: whoosh up, final chord
put(sfx, M['cta'] + .2, whoosh(1.1, 300, 4000), .55)
for f in (523.25, 659.25, 783.99, 1046.5): put(sfx, END - 2.2, ding(f, 2.0), .22)

# --- music: airy pad + soft pulse + bell arpeggio (C major pentatonic, 100 bpm) ---
put(mus, 0, fade(drone(END, nf(48)) * .22 + drone(END, nf(55)) * .14 + drone(END, nf(64)) * .08, 1.5, 1.5))
bpm = 100; beat = 60 / bpm
pent = [72, 74, 76, 79, 81, 84]
pat = [0, 2, 4, 2, 3, 1, 4, 5, 0, 2, 3, 2, 1, 3, 4, 2]
k = 0; t = 0.
while t < END:
    if k % 4 == 0: put(mus, t, drum(), .45 if k % 16 == 0 else .25)
    n = pent[pat[k % 16]] - (0 if (k // 32) % 2 == 0 else 3 if pat[k % 16] in (1, 4) else 0)
    put(mus, t, ding(nf(n), .9), .10)
    t += beat / 2; k += 1
te = np.arange(N) / SR; g = np.minimum(1, te / 1.0); g[te > END - .5] *= np.linspace(1, 0, (te > END - .5).sum()); mus *= g


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
