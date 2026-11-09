"""Synthesise sound effects (sfx.wav) and a light 'study' music bed with a clock tick (music.wav),
timed from timeline.json."""
import json, wave, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
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

fx = np.zeros(N)
s = sc['s1']['start']
for k, t0 in enumerate([0.05, 0.3, 0.55, 0.75, 0.95, 1.15]): add(fx, s + t0, chalk(0.3), 0.35)
s = sc['s2']['start']
for t0 in [0.05, 0.3, 0.7, 1.1, 1.5]: add(fx, s + t0, tick(), 0.5)
d2 = sc['s2']['end'] - s
add(fx, s + d2 - 0.85, swish(0.8), 0.35)
add(fx, sc['s3']['start'] + 0.1, chime(1046.5), 0.25)
add(fx, sc['s4']['start'] + 0.05, rustle(0.95), 0.35)
add(fx, sc['s5']['start'], whoosh(), 0.25)
add(fx, sc['s5']['start'] + 0.2, chime(1174.7), 0.25)
s = sc['s6']['start']
add(fx, s + 2.95, ding(1568), 0.3); add(fx, s + 4.45, ding(1760), 0.3)
add(fx, sc['s7']['start'] + 0.2, chime(1318.5), 0.25)
s = sc['end']['start']
add(fx, s + 0.2, chalk(0.7), 0.3); add(fx, s + 0.9, chalk(0.3), 0.3)
add(fx, s + 1.25, ding(2093), 0.22)
add(fx, s + 1.8, chime(1568), 0.2)
write('sfx.wav', fx)

# ---------- music: light study tune, 104 bpm, marimba-like pluck + soft bass + clock tick ----------
bpm = 104; beat = 60 / bpm
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
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]   # C G Am F
pattern = [0, 1, 2, 1, 2, 1, 0, 2]                                    # eighth-note arpeggio
mel = [76, None, 74, 72, None, 74, 76, None, 79, None, 76, 74, None, 72, 74, None]
mu = np.zeros(N)
bar = 4 * beat; nb = int(dur / bar) + 1
for b in range(nb):
    ch = chords[b % 4]; t0 = b * bar
    add(mu, t0, bass(m2f(ch[0] - 24), bar), 0.35)
    add(mu, t0, pad([m2f(n) for n in ch], bar), 0.10)
    for k in range(8):
        add(mu, t0 + k * beat / 2, pluck(m2f(ch[pattern[k]] + 12), 0.7, 0.55 if k % 2 else 0.7), 0.35)
    if b >= 1:  # gentle melody from bar 2
        for k in range(8):
            n = mel[(b % 2) * 8 + k]
            if n: add(mu, t0 + k * beat / 2, pluck(m2f(n), 1.1, 0.6), 0.25)
    for k in range(4): add(mu, t0 + k * beat, tick(3200 if k % 2 else 2600, 0.05), 0.18)
fo = np.ones(N); i0 = int(SR * (dur - 1.5)); fo[i0:] = np.linspace(1, 0, N - i0).clip(0)
fo[:int(SR * 0.3)] = np.linspace(0, 1, int(SR * 0.3))
write('music.wav', norm(mu) * 0.8 * fo)
print('sfx.wav + music.wav', dur, 's')
