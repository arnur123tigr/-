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

S = {k: M[k] for k in M}
nxt = lambda s: M['s%d' % (int(s[1:]) + 1)] if 's%d' % (int(s[1:]) + 1) in M else END
# scene 1: boom, counter clicks, the dive
put(sfx, 0.02, boom(), .35)
t = .4
while t < M['five'] + .2: put(sfx, t, click(), .5); t += .055
put(sfx, M['five'] + .15, ding(990, 1.2), .4)
put(sfx, M['s2'] - .9, whoosh(1.0, 150, 1800), .7)
# scenes 2 and 5: hammer clacks in the gallery (in sync with the swings in scene.html), quiet drips
for sc in ('s2', 's5'):
    for i in range(2):
        k = 0
        while True:
            T = (math.pi * (2 * k + 1) - 2 * i) / 5; k += 1
            if T > nxt(sc) - .1: break
            if T > M[sc] + .2: put(sfx, T, clack(), .45 if i == 0 else .35)
put(sfx, M['s5'] + .2, band(noise(nxt('s5') - M['s5']), 30, 220) * np.linspace(0, 1, int(round((nxt('s5') - M['s5']) * SR))) * 1.2, .8)   # rising rumble
# scene 3: fire roar, bellows breathing, the copper flows
d3 = M['s4'] - M['s3']; r = roar(d3); r *= np.clip(0.4 + 0.6 * (tt(d3) - (M['bel'] - M['s3'])) / 2, 0.4, 1)[:len(r)]; put(sfx, M['s3'], r, .7)
t = M['s3'] + .2
while t < M['s4'] - .3: put(sfx, t, puff(), .5); t += 1 / 4.4
put(sfx, M['flow'] + .3, hiss(1.8), .25)
# scene 4: shimmer at the merge, sizzle while pouring, "dzin" when the axe comes out and at the real photo
put(sfx, M['s4'], whoosh(.4, 600, 5000), .3)
put(sfx, M['mix'] - .05, shimmer(), .3)
pour0, pour1 = M['mix'] + 1.1, M['ph1'] - .9
put(sfx, pour0, hiss(max(.4, pour1 - pour0)), .2)
put(sfx, pour1 + .4, ding(1320, 2.2), .7)
put(sfx, M['ph1'], whoosh(.5, 500, 4000), .35)
# scene 6: wheel creaks, hooves, distant cows
put(sfx, M['ph2'] + .2, moo(), .35); put(sfx, M['ph2'] + 2.6, moo(1.1), .22)
t = M['char'] - 1.8
while t < nxt('s6'):
    put(sfx, t, hoof(), .3); put(sfx, t + .11, hoof(), .22); t += .32
t = M['char'] - 1.5
while t < nxt('s6'): put(sfx, t, creak(), .25); t += .7
# scene 7: dzin, then the axe flies up
put(sfx, M['s7'] + .1, ding(1480, 2.0), .65)
put(sfx, M['cta'] + .2, whoosh(1.1, 300, 4000), .6)
put(sfx, END - 2.2, ding(1760, 1.8), .4)

# --- music: drone A + E, frame drum and dombra-like plucks in A minor pentatonic, 96 bpm ---
put(mus, 0, fade(drone(END, nf(45)) * .25 + drone(END, nf(52)) * .15, 1.5, 1.5))
bpm = 96; beat = 60 / bpm
pent = [57, 60, 62, 64, 67, 69, 72]
pat = [0, 4, 3, 4, 2, 4, 3, 1, 0, 4, 5, 4, 3, 2, 1, 2]
k = 0; t = 0.
while t < END:
    if k % 2 == 0: put(mus, t, drum(), .55 if k % 8 == 0 else .35)
    n = pent[pat[k % 16]] + (0 if (k // 16) % 2 == 0 else -2 if pat[k % 16] in (1, 3) else 0)
    put(mus, t, pluck(nf(n), .9), .35); put(mus, t + beat / 4, pluck(nf(n + 12), .5), .12) if k % 4 == 3 else None
    t += beat / 2; k += 1
te = np.arange(N) / SR; g = np.minimum(1, te / 1.0); g[te > END - .5] *= np.linspace(1, 0, (te > END - .5).sum()); mus *= g


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
