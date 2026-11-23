"""(python3 sfx.py kk|ru) Synthesise sound effects (sfx.wav) and a light 'study' music bed with a clock tick (music.wav),
timed from timeline.json."""
import json, wave, numpy as np
SR = 48000
import sys
LANG = sys.argv[1]
tl = json.load(open(f'timeline_{LANG}.json'))
MK = tl['marks']
sc = {s['id']: s for s in tl['scenes']}
dur = tl['dur']
N = int(SR * (dur + 1))
rng = np.random.default_rng(5)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if j > i: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x[:int(SR * dur)], -1, 1)
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32000).astype(np.int16).tobytes())

def chalk(L=0.3):   # squeaky chalk scribble
    n = int(SR * L); x = band(rng.standard_normal(n), 1800, 7000)
    env = np.abs(band(rng.standard_normal(n), 5, 40)); env /= env.max() + 1e-9
    env *= np.sin(np.linspace(0, np.pi, n)) ** 0.5
    t = tt(L); sq = np.sin(2 * np.pi * (2400 + 300 * np.sin(2 * np.pi * 7 * t)) * t) * 0.25
    return norm(x + sq * env) * env
def tick(f=2800, L=0.06):
    t = tt(L); return (np.sin(2 * np.pi * f * t) + 0.5 * band(rng.standard_normal(len(t)), 2000, 9000)) * np.exp(-t * 90)
def chime(freq, L=1.6):
    t = tt(L)
    x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 2.2), (2.01, .35, 3.5), (3.02, .15, 5)])
    return x * np.minimum(1, t / 0.005) / 1.5
def ding(freq=1568, L=2.0):   # bright "дың"
    t = tt(L)
    x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 1.6), (2.76, .4, 3), (5.4, .2, 6)])
    return x * np.minimum(1, t / 0.002) / 1.4
def rustle(L=0.8):
    n = int(SR * L); x = band(rng.standard_normal(n), 1200, 9000); env = np.zeros(n)
    for _ in range(16):
        c = rng.integers(0, n - 2000); w = rng.integers(800, 4000)
        env[c:c + w] += np.hanning(w)[:len(env[c:c + w])] * rng.uniform(.3, 1)
    return norm(x) * np.clip(env, 0, 1)
def swish(L=0.8):   # sponge wiping
    n = int(SR * L); t = tt(L)
    x = band(rng.standard_normal(n), 300, 3000)
    env = (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 4.5 * t))) * np.sin(np.pi * t / L)
    return norm(x) * env
def whoosh(L=0.45):
    n = int(SR * L); t = tt(L); x = band(rng.standard_normal(n), 400, 4000)
    return norm(x) * np.sin(np.pi * t / L) ** 2


def thud(L=0.35):
    t = tt(L); return np.sin(2 * np.pi * (90 * np.exp(-t * 8) + 45) * t) * np.exp(-t * 12)
def wind(L):
    n = int(SR * L); t = tt(L); x = band(rng.standard_normal(n), 150, 900)
    env = 0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t); env *= np.minimum(1, t / 0.6) * np.minimum(1, (L - t) / 0.6)
    return norm(x) * env
def steps(L):
    out = np.zeros(int(SR * L))
    for k in np.arange(0.2, L - 0.3, 0.62):
        n = int(SR * 0.18); x = band(rng.standard_normal(n), 300, 3000) * np.exp(-np.arange(n) / SR * 25)
        i = int(k * SR); out[i:i + n] += x[:len(out[i:i + n])]
    return norm(out)
def low(L=2.5):
    t = tt(L); return (np.sin(2 * np.pi * 55 * t) + 0.4 * np.sin(2 * np.pi * 82.4 * t)) * np.minimum(1, t / 0.3) * np.exp(-t * 0.9)
def pnote(f, L=1.8, damp=2.2):
    t = tt(L); x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * damp * m ** 0.5) for m, a in [(1, 1), (2, .5), (3, .25), (4, .12)])
    return x * np.minimum(1, t / 0.004)
def thunk(L=0.25):   # muted key
    t = tt(L); return np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40) + 0.3 * band(rng.standard_normal(len(t)), 200, 1500) * np.exp(-t * 50)
m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
fx = np.zeros(N)
st = lambda k: sc[k]['start']; en = lambda k: sc[k]['end']
for k in ['s1', 's2', 's4', 's5', 's6', 's7', 's8', 's9']:
    for t0 in [0.05, 0.4, 0.8, 1.3]: add(fx, st(k) + t0, chalk(0.3), 0.22)
add(fx, en('s1') - 0.55, swish(0.55), 0.3)
add(fx, MK['winter'] + 0.5, chalk(0.2), 0.3); add(fx, MK['winter'] + 0.8, thud(), 0.25)
add(fx, st('s3'), wind(en('s3') - st('s3')), 0.10); add(fx, st('s3') + 0.3, steps(en('s3') - st('s3') - 0.6), 0.10)
for t0 in np.arange(0.4, en('s4') - st('s4') - 0.5, 0.5): add(fx, st('s4') + t0, tick(), 0.18)
for k in ['s4', 's5', 's6', 's7']: add(fx, en(k) - 0.45, whoosh(0.45), 0.2)
add(fx, MK['why'], low(2.5), 0.35)
add(fx, MK['piano'] + 0.6, sum(np.pad(pnote(m2f(n)), (0, 0)) for n in [57, 60, 64]) / 3, 0.35)
for j, n in enumerate([62, 65, 69]):
    add(fx, MK['keys'] + 0.5 + j * 0.2, thunk(), 0.35)
add(fx, MK['y2008'] + 0.1, sum(pnote(m2f(n), 2.4, 1.5) for n in [60, 64, 67, 72]) / 4, 0.35)
add(fx, MK['rev'] + 0.4, chime(1318.5), 0.18)
for t0 in np.arange(0, 3 - 1e-6, 1.0): add(fx, MK['q1'] + t0, tick(2600), 0.5)
add(fx, MK['ans'], ding(1568), 0.32)
add(fx, MK['voend'] + 0.05, sum(pnote(m2f(n), 2.4, 1.2) for n in [57, 64, 69, 72]) / 4, 0.35)
write('sfx.wav', fx)

# ---------- music: light study tune, 104 bpm, marimba-like pluck + soft bass + clock tick ----------
bpm = 80; beat = 60 / bpm
def pluck(freq, L=0.9, vel=1.0):
    t = tt(L)
    x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 18)
    return x * np.exp(-t * 5.5) * np.minimum(1, t / 0.003) * vel
def bass(freq, L):
    t = tt(L); x = np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(4 * np.pi * freq * t)
    return x * np.minimum(1, t / 0.02) * np.exp(-t * 1.5)
def pad(fs, L):
    t = tt(L); x = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate(fs)) / len(fs)
    return x * np.minimum(1, t / 0.4) * np.minimum(1, (L - t) / 0.4)
m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
pattern = [0, 1, 2, 1, 2, 1, 0, 2]                                    # eighth-note arpeggio
mel = [76, None, None, 72, None, None, 74, None, 72, None, None, 69, None, None, 71, None]
mu = np.zeros(N)
bar = 4 * beat; nb = int(dur / bar) + 1
for b in range(nb):
    ch = chords[b % 4]; t0 = b * bar
    add(mu, t0, bass(m2f(ch[0] - 24), bar), 0.35)
    add(mu, t0, pad([m2f(n) for n in ch], bar), 0.10)
    for k in range(8):
        add(mu, t0 + k * beat / 2, pluck(m2f(ch[pattern[k]] + 12), 0.9, 0.45 if k % 2 else 0.55), 0.28)
    if b >= 1:  # gentle melody from bar 2
        for k in range(8):
            n = mel[(b % 2) * 8 + k]
            if n: add(mu, t0 + k * beat / 2, pluck(m2f(n), 1.1, 0.6), 0.25)
fo = np.ones(N); i0 = int(SR * (dur - 1.5)); fo[i0:] = np.linspace(1, 0, N - i0).clip(0)
fo[:int(SR * 0.3)] = np.linspace(0, 1, int(SR * 0.3))
write(f'music.wav', norm(mu) * 0.8 * fo)
print('sfx.wav + music.wav', dur, 's')
