"""Synthesise the script's sound effects (sfx.wav) and a music bed (music.wav):
dramatic (minor drums + strings) until the yacht scene, then comic (oom-pah tuba + pizzicato)."""
import json, wave, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
rng = np.random.default_rng(11)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(len(buf), i + len(sig))
    if j > i: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
N = lambda n: 440 * 2 ** ((n - 69) / 12)

# ---------- effects ----------
def tick(hi=True):
    t = tt(0.05); f = 4200 if hi else 3100
    return norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 180) + 0.5 * band(rng.standard_normal(len(t)), 2500, 9000) * np.exp(-t * 220))
def clock_tock(hi):
    t = tt(0.12); f = 1500 if hi else 1150
    return norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 60) + 0.6 * band(rng.standard_normal(len(t)), 800, 4000) * np.exp(-t * 90))
def whoosh(L, lo=300, hi=4000):
    n = int(SR * L); x = rng.standard_normal(n); t = np.arange(n) / n
    y = np.zeros(n); blk = 1024
    for k in range(0, n, blk):
        c = np.sin(np.pi * t[k]); y[k:k + blk] = band(x[k:k + blk], lo, lo + (hi - lo) * c)[:len(y[k:k + blk])]
    return norm(y) * np.sin(np.pi * t) ** 1.6
def waves(L):
    n = int(SR * L); t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 150, 2500)
    env = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 2.6 - 1.2)) ** 2
    return norm(x * env) * np.minimum(1, t / 0.3) * np.minimum(1, (L - t) / 0.4)
def brass(freq, L):
    t = tt(L); ph = 2 * np.pi * freq * t * (1 + 0.003 * np.sin(2 * np.pi * 5.5 * t))
    x = sum(np.sin(k * ph) / k ** 1.1 for k in range(1, 14))
    env = np.minimum(1, t / 0.04) * np.minimum(1, (L - t) / 0.08)
    return band(x, 150, 5000) * env
def fanfare():
    s = np.zeros(int(SR * 2.2))
    for t0, n, L in [(0, 60, 0.18), (0.2, 60, 0.12), (0.34, 60, 0.12), (0.48, 67, 0.5), (1.0, 64, 0.2), (1.22, 67, 0.2), (1.44, 72, 0.7)]:
        add(s, t0, brass(N(n), L)); add(s, t0, brass(N(n - 12), L), 0.4)
    return norm(s)
def cannon():
    t = tt(1.6); f = 45 + 70 * np.exp(-t * 12)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)
    x += 1.2 * band(rng.standard_normal(len(t)), 40, 1500) * np.exp(-t * 3.5)
    x += 0.8 * band(rng.standard_normal(len(t)), 1000, 8000) * np.exp(-t * 30)
    return norm(np.tanh(2 * norm(x)))
def explosion():
    t = tt(2.2)
    x = band(rng.standard_normal(len(t)), 30, 900) * np.exp(-t * 2.2) + 0.5 * band(rng.standard_normal(len(t)), 900, 5000) * np.exp(-t * 9)
    x += 0.6 * np.sin(2 * np.pi * np.cumsum(40 + 30 * np.exp(-t * 6)) / SR) * np.exp(-t * 3)
    return norm(np.tanh(1.8 * norm(x)))
def tinypop():
    t = tt(0.15); f = 900 + 1200 * np.exp(-t * 60)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) + 0.3 * band(rng.standard_normal(len(t)), 1000, 5000) * np.exp(-t * 70))
def plop():
    t = tt(0.25); f = 300 + 900 * t
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18))
def bubble(f0):
    t = tt(0.09); f = f0 * (1 + 2.5 * t / 0.09)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.09)
def gurgle(L):
    s = np.zeros(int(SR * L)); k = 0.0
    while k < L - 0.1:
        add(s, k, bubble(250 + 500 * rng.random()), 0.6 + 0.4 * rng.random()); k += 0.05 + 0.1 * rng.random()
    return norm(s) * np.linspace(1, 0.4, len(s))
def bell():
    s = np.zeros(int(SR * 1.6))
    for k in range(5):
        t = tt(1.5); x = sum(a * np.sin(2 * np.pi * 2350 * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 3), (2.76, .4, 6), (5.4, .2, 10)])
        add(s, k * 0.09, x * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * t))) * np.exp(-t * 2), 0.8 ** k)
    return norm(s)
def rustle(L):
    n = int(SR * L); x = band(rng.standard_normal(n), 2000, 9000)
    env = np.abs(np.sin(np.linspace(0, 14 * np.pi, n))) ** 3 * np.sin(np.linspace(0, np.pi, n))
    return norm(x * env)
def kaching():
    s = np.zeros(int(SR * 1.2)); t = tt(1.0)
    add(s, 0, band(rng.standard_normal(int(SR * 0.08)), 1500, 7000) * np.exp(-tt(0.08) * 50), 0.8)
    for fr, k in [(2637, 0.08), (3520, 0.16)]:
        add(s, k, sum(a * np.sin(2 * np.pi * fr * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 4), (2.4, .3, 8)]))
    return norm(s)
def pop():
    t = tt(0.2); f = 300 + 900 * np.exp(-t * 35)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22))
def boing():
    t = tt(0.6); f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5))
def slide(L=0.9, up=False):
    t = tt(L); u = t / L
    f = (500 + 900 * u) if up else (1300 - 900 * u ** 0.8)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 + 0.05 * np.sin(2 * np.pi * 6 * t))) * np.sin(np.pi * u) ** 0.6

fx = np.zeros(int(SR * (dur + 2)))
s1, s2, s3, s4, s5, s6, s7, se = (sc[k] for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'end'])
# s1: splash rise, stopwatch ticking while counting, whoosh fly-through
add(fx, s1['start'] + 0.25, waves(1.4), 0.35)
for k in np.arange(0.3, s1['end'] - 0.6, 0.25): add(fx, s1['start'] + k, tick(int(k * 4) % 2 == 0), 0.32)
add(fx, s1['start'] + s1['text'], pop(), 0.3)
add(fx, s1['end'] - 0.7, whoosh(0.9, 300, 6000), 0.55)
# s2: waves
add(fx, s2['start'], waves(s2['end'] - s2['start'] + 0.2), 0.45)
add(fx, s2['start'] + s2['sign'] + 0.1, pop(), 0.28)
# s3: royal fanfare as he sits
add(fx, s3['start'] + s3['sit'][1] - 0.15, fanfare(), 0.42)
add(fx, s3['start'] + s3['text'], pop(), 0.25)
# s4: clock ticking (tick-tock)
for i, k in enumerate(np.arange(0.1, s4['end'] - s4['start'], 0.5)): add(fx, s4['start'] + k, clock_tock(i % 2 == 0), 0.38)
add(fx, s4['start'], waves(s4['end'] - s4['start']), 0.15)
# s5: minute click, cannons and hits
add(fx, s5['start'] + 0.4, clock_tock(True), 0.5)
for i, st in enumerate(s5['shots']):
    add(fx, s5['start'] + st, cannon(), 0.75)
    add(fx, s5['start'] + st + 0.22, explosion(), 0.55)
# s6: tiny pop, plop, big hit, gurgle
add(fx, s6['start'] + s6['shot'], tinypop(), 0.55)
add(fx, s6['start'] + s6['shot'] + 0.6, plop(), 0.4)
add(fx, s6['start'] + s6['hit'], explosion(), 0.6)
add(fx, s6['start'] + s6['hit'] + 0.4, slide(1.2), 0.22)
add(fx, s6['start'] + s6['hit'] + 0.45, gurgle(s6['end'] - s6['start'] - s6['hit']), 0.5)
add(fx, s6['start'], waves(s6['end'] - s6['start']), 0.18)
# s7: ticks, stopwatch bell, door, running feet
for k in np.arange(0.05, s7['stop'], 0.25): add(fx, s7['start'] + k, tick(), 0.3)
add(fx, s7['start'] + s7['stop'], bell(), 0.6)
add(fx, s7['start'] + s7['run'][0], boing(), 0.25)
for k in np.arange(s7['run'][0] + 0.1, s7['run'][1], 0.14): add(fx, s7['start'] + k, pop(), 0.12)
# end: paper rustle, ka-ching, pops for CTA
add(fx, se['start'] + se['bill'][0], rustle(se['bill'][1] - se['bill'][0]), 0.35)
add(fx, se['start'] + se['card'], kaching(), 0.5)
add(fx, se['start'] + se['cta'], pop(), 0.5); add(fx, se['start'] + se['cta'] + 0.15, pop(), 0.4)
write('sfx.wav', fx[:int(SR * dur)])

# ---------- music ----------
mu = np.zeros(int(SR * (dur + 3)))
cut = s6['start']               # drama -> comedy
def string(freq, L):
    t = tt(L); ph = 2 * np.pi * freq * t
    x = sum(np.sin(k * ph * (1 + 0.002 * np.sin(2 * np.pi * (5 + k * 0.3) * t))) / k for k in range(1, 10))
    return band(x, 80, 3500) * np.minimum(1, t / 0.35) * np.minimum(1, (L - t) / 0.4)
def timp(f=55):
    t = tt(0.9); return norm(np.sin(2 * np.pi * np.cumsum(f * (1 + 0.3 * np.exp(-t * 30))) / SR) * np.exp(-t * 4) + 0.3 * band(rng.standard_normal(len(t)), 60, 400) * np.exp(-t * 15))
# drama: D minor -> Bb -> Gm -> A, 2 s per chord, drums on beats, building
chords = [[50, 57, 62, 65], [46, 53, 58, 62], [43, 50, 55, 58], [45, 52, 57, 61]]
bpm = 100; beat = 60 / bpm
k = 0; t0 = 0.0
while t0 < cut:
    L = min(beat * 4, cut - t0 + 0.3)
    for n in chords[k % 4]: add(mu, t0, string(N(n), L), 0.09)
    add(mu, t0, string(N(chords[k % 4][0] - 12), L), 0.12)
    k += 1; t0 += beat * 4
b = 0
while b * beat < cut - 0.1:
    t = b * beat; lvl = 0.25 + 0.5 * t / cut
    add(mu, t, timp(55 if b % 4 != 3 else 73), lvl * (1 if b % 2 == 0 else 0.6))
    if t > sc['s4']['start']: add(mu, t + beat / 2, timp(55), lvl * 0.35)
    b += 1
add(mu, cut - 0.9, timp(41), 0.9)                       # dramatic hit before the switch
# comedy: F major oom-pah, tuba + pizzicato melody, 132 bpm
def tuba(freq, L=0.28):
    t = tt(L); ph = 2 * np.pi * freq * t
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    return x * np.minimum(1, t / 0.02) * np.exp(-t * 4)
def pluck(freq, L=0.3):
    t = tt(L); x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 10), (2, .5, 15), (3, .25, 22)])
    return x * np.minimum(1, t / 0.003)
def chuck(freqs, L=0.15):
    return sum(pluck(f, L) for f in freqs) / len(freqs)
cb = 60 / 132
bass = [41, 36, 41, 36, 34, 41, 36, 41]                  # F C F C Bb F C F (per bar: root on 1, fifth on 3)
mel = [72, 0, 69, 0, 72, 74, 72, 0, 70, 0, 67, 0, 69, 70, 69, 0,
       65, 0, 69, 72, 77, 0, 76, 74, 72, 0, 67, 0, 72, 0, 0, 0]
chd = {41: [65, 69, 72], 36: [64, 67, 72], 34: [62, 65, 70]}
nb = int((dur - cut) / cb) + 1
for i in range(nb):
    t = cut + i * cb
    if t > dur - 0.8: break
    bar = (i // 4) % len(bass); root = bass[bar]
    if i % 2 == 0: add(mu, t, tuba(N(root if i % 4 == 0 else root + 7)), 0.32)
    else: add(mu, t, chuck([N(n) for n in chd[root]]), 0.15)
    for h in range(2):
        n = mel[(i * 2 + h) % len(mel)]
        if n: add(mu, t + h * cb / 2, pluck(N(n)), 0.13)
for n in (53, 65, 69, 72): add(mu, dur - 0.8, pluck(N(n), 0.8), 0.15)
mu = mu[:int(SR * dur)]
fade = np.ones(len(mu)); kf = int(SR * 0.6); fade[-kf:] = np.linspace(1, 0, kf)
write('music.wav', norm(mu) * 0.8 * fade)
print('sfx.wav + music.wav', dur, 's')
