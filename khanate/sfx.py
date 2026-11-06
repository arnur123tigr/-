"""Synthesise the script's sound effects (sfx.wav) and a music bed (music.wav):
dombra + drum, tense (D minor, fast strumming) until the valley, then solemn (D major, broad)."""
import json, wave, subprocess, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
rng = np.random.default_rng(7)

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
def load(name):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', name, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
N = lambda n: 440 * 2 ** ((n - 69) / 12)

# ---------- effects ----------
def wind(L, lo=150, hi=900, rate=0.35):
    n = int(SR * L); t = np.arange(n) / SR
    x = band(rng.standard_normal(n), lo, hi)
    env = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + 1.3) * np.sin(2 * np.pi * rate * 0.37 * t)
    return norm(x * env) * np.minimum(1, t / 0.4) * np.minimum(1, (L - t) / 0.4)
def rustle(L):
    n = int(SR * L); x = band(rng.standard_normal(n), 1500, 7000)
    env = np.abs(np.sin(np.linspace(0, 9 * np.pi, n))) ** 2 * (0.6 + 0.4 * rng.random(n) ** 4)
    return norm(x * env) * np.minimum(1, np.arange(n) / (SR * 0.2))
def drum(f=70, L=0.7, noise=0.4):
    t = tt(L); x = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t * 25))) / SR) * np.exp(-t * 6)
    return norm(x + noise * band(rng.standard_normal(len(t)), 80, 1200) * np.exp(-t * 20))
def thunder(L=3.0):
    t = tt(L); x = band(rng.standard_normal(len(t)), 25, 400)
    env = np.exp(-t * 1.2) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 1.7 * t)) ** 3)
    crack = band(rng.standard_normal(len(t)), 800, 6000) * np.exp(-t * 18)
    return norm(np.tanh(2 * norm(x * env + 0.5 * crack)))
def hoof():
    t = tt(0.09); return norm(np.sin(2 * np.pi * 220 * t) * np.exp(-t * 70) + 0.8 * band(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 90))
def creak(L=0.5):
    t = tt(L); f = 380 + 120 * np.sin(np.pi * t / L)
    ph = np.cumsum(f) / SR; x = (ph % 1) - 0.5
    return band(x, 400, 3000) * np.sin(np.pi * t / L) ** 2
def whoosh(L, lo=300, hi=4000):
    n = int(SR * L); x = rng.standard_normal(n); t = np.arange(n) / n
    y = np.zeros(n); blk = 1024
    for k in range(0, n, blk):
        c = np.sin(np.pi * t[k]); y[k:k + blk] = band(x[k:k + blk], lo, lo + (hi - lo) * c)[:len(y[k:k + blk])]
    return norm(y) * np.sin(np.pi * t) ** 1.6
def river(L):
    n = int(SR * L); t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 250, 3500) + 0.4 * band(rng.standard_normal(n), 3500, 8000)
    return norm(x * (0.8 + 0.2 * np.sin(2 * np.pi * 0.9 * t))) * np.minimum(1, t / 0.3) * np.minimum(1, (L - t) / 0.3)
def chirp(f0=3200):
    t = tt(0.12); f = f0 + 1800 * np.sin(np.pi * t / 0.12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.12) ** 2
def birds(L):
    s = np.zeros(int(SR * L)); k = 0.1
    while k < L - 0.3:
        f0 = 2600 + 1500 * rng.random()
        for j in range(int(2 + 3 * rng.random())): add(s, k + j * 0.13, chirp(f0), 0.7)
        k += 0.5 + 0.7 * rng.random()
    return norm(s)
def neigh():
    t = tt(1.3); f = 520 + 380 * np.exp(-((t - 0.25) / 0.25) ** 2) - 180 * t
    f = f * (1 + 0.06 * np.sin(2 * np.pi * 22 * t) * np.minimum(1, t * 2))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(5 * ph)
    x = band(x + 0.15 * rng.standard_normal(len(t)), 300, 5000)
    return norm(x * np.minimum(1, t / 0.05) * np.exp(-t * 1.6))
def pop():
    t = tt(0.2); f = 300 + 900 * np.exp(-t * 35)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22))

fx = np.zeros(int(SR * (dur + 2)))
s1, s2, s3, s4, s5, s6, s7, se = (sc[k] for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'end'])
# s1-s2: wind + felt rustle; distant drum in s2
add(fx, 0, wind(s2['end'] + 0.3), 0.35)
add(fx, 0.2, rustle(s1['end'] - 0.3), 0.33)
for i, k in enumerate(np.arange(0.3, s2['end'] - s2['start'], 0.62)): add(fx, s2['start'] + k, band(drum(62, 0.8, 0.2), 30, 500), 0.55 if i % 2 == 0 else 0.35)
# s3: storm wind + thunder
add(fx, s3['start'], wind(s3['end'] - s3['start'] + 0.3, 80, 700, 0.6), 0.45)
for th in s3['thunder']: add(fx, s3['start'] + th, thunder(), 0.8)
# s4: hooves, creaking carts, whoosh during day/night cycle
for k in np.arange(0.05, s4['end'] - s4['start'], 0.115):
    add(fx, s4['start'] + k + 0.01 * rng.standard_normal(), hoof(), 0.28 + 0.1 * rng.random())
for k in np.arange(0.3, s4['end'] - s4['start'] - 0.4, 0.9): add(fx, s4['start'] + k, creak(0.45 + 0.2 * rng.random()), 0.12)
add(fx, s4['start'], wind(s4['end'] - s4['start'], 150, 700), 0.15)
add(fx, s4['start'] + s4['cycle'][0], whoosh(s4['cycle'][1] - s4['cycle'][0] + 0.3, 300, 5000), 0.4)
# s5: hooves slowing on the hill, river, birds
for k in np.arange(0.05, s5['end'] - s5['start'], 0.16): add(fx, s5['start'] + k, hoof(), 0.2)
add(fx, s5['start'], river(s5['end'] - s5['start'] + s6['end'] - s6['start']), 0.25)
add(fx, s5['start'] + 0.3, birds(s6['end'] - s5['start'] - 0.3), 0.18)
# s6: approaching hooves, neigh, pop for the bubble
for k in np.arange(0.0, 1.1, 0.1): add(fx, s6['start'] + k, hoof(), 0.2 + 0.2 * k)
add(fx, s6['start'] + 1.0, neigh(), 0.35)
add(fx, s6['start'] + s6['bubble'], pop(), 0.45)
# s7: solemn drums + crowd shout "Алаш!" (three layered takes)
for k in np.arange(0.0, s7['end'] - s7['start'] - 0.2, 0.75): add(fx, s7['start'] + k, drum(55, 1.0, 0.3), 0.6)
shout = load('alash_shout.mp3')
for dly, g in [(0, 0.75), (0.045, 0.5), (0.11, 0.4), (0.19, 0.3)]:
    sh = band(shout, 120, 7000) if dly else shout
    add(fx, s7['start'] + s7['shout'] + dly, sh, g)
add(fx, s7['start'] + s7['shout'], band(rng.standard_normal(int(SR * 3.0)), 300, 3000) * np.exp(-tt(3.0) * 0.9) * np.minimum(1, tt(3.0) / 0.2), 0.08)
# end: soft wind, CTA pops
add(fx, se['start'], wind(se['end'] - se['start'], 150, 800), 0.18)
add(fx, se['start'] + se['cta'], pop(), 0.5); add(fx, se['start'] + se['cta'] + 0.15, pop(), 0.4)
write('sfx.wav', fx[:int(SR * dur)])

# ---------- music: dombra + frame drum ----------
mu = np.zeros(int(SR * (dur + 3)))
def ks(freq, L=0.6, bright=0.5, damp=0.996):
    n = int(SR * L); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p); buf = band(np.concatenate([buf] * 4), 0, 2000 + 6000 * bright)[:p]
    out = np.zeros(n); b = buf.copy()
    for i in range(0, n, p):
        seg_ = b.copy(); out[i:i + p] = seg_[:len(out[i:i + p])]
        b = damp * 0.5 * (b + np.roll(b, -1))
    return out * np.minimum(1, np.arange(n) / 30)
def strum(notes, L=0.35, g=1.0, down=True):
    s = np.zeros(int(SR * L) + 600)
    for j, n in enumerate(notes if down else notes[::-1]): add(s, j * 0.012, ks(N(n), L), g)
    return s
def dauyl(low=True):
    t = tt(0.45); f = (90 if low else 160) * (1 + 0.4 * np.exp(-t * 40))
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (8 if low else 14)) + 0.3 * band(rng.standard_normal(len(t)), 200, 3000) * np.exp(-t * 35))
def pad(freq, L):
    t = tt(L); ph = 2 * np.pi * freq * t
    x = sum(np.sin(k * ph * (1 + 0.002 * np.sin(2 * np.pi * (4.5 + k * 0.4) * t))) / k ** 1.3 for k in range(1, 8))
    return band(x, 80, 3000) * np.minimum(1, t / 0.6) * np.minimum(1, (L - t) / 0.5)

cut = sc['s5']['start']
# tense part: 6/8 küy gallop, Dm drone (D-A) with melody on top string, 132 bpm-ish
beat = 0.17
mel = [74, 74, 72, 74, 76, 74, 72, 70, 69, 69, 70, 72, 74, 72, 70, 69, 67, 69, 70, 69, 67, 65, 64, 62]
i = 0; t0 = 0.0
while t0 < cut - 0.2:
    phrase = (i // 24) % 2
    m = mel[i % 24] - (0 if phrase == 0 else 2 * (i % 2))
    lvl = 0.6 + 0.4 * min(1, t0 / cut)
    if i % 3 == 0: add(mu, t0, strum([50, 57, m], 0.4), 0.42 * lvl)
    else: add(mu, t0, strum([57, m], 0.25, down=i % 3 == 1), 0.3 * lvl)
    if i % 6 == 0: add(mu, t0, dauyl(True), 0.5 * lvl)
    if i % 6 == 3: add(mu, t0, dauyl(False), 0.3 * lvl)
    if t0 > sc['s3']['start'] and i % 6 == 4: add(mu, t0, dauyl(False), 0.22)
    i += 1; t0 += beat
add(mu, sc['s3']['start'], pad(N(38), sc['s4']['start'] - sc['s3']['start'] + 0.4), 0.18)   # dark drone under storm
add(mu, cut - 0.2, dauyl(True), 0.7)
# solemn part: D major, slower strums, broad pad, steady drum
chords = [[50, 57, 62, 66], [55, 62, 67, 71], [57, 64, 69, 73], [50, 57, 62, 66]]   # D G A D
bl = 1.6; k = 0; t0 = cut
while t0 < dur - 0.4:
    ch = chords[k % 4]; L = min(bl, dur - t0)
    for n in ch[:3]: add(mu, t0, pad(N(n), L + 0.3), 0.07)
    add(mu, t0, pad(N(ch[0] - 12), L + 0.3), 0.1)
    for j in range(4):
        tj = t0 + j * bl / 4
        if tj < dur - 0.3: add(mu, tj, strum([ch[0], ch[1], ch[2] + (12 if j == 2 else 0)], 0.5, down=j % 2 == 0), 0.3)
    add(mu, t0, dauyl(True), 0.45); add(mu, t0 + bl / 2, dauyl(True), 0.3)
    k += 1; t0 += bl
mu = mu[:int(SR * dur)]
fade = np.ones(len(mu)); kf = int(SR * 0.8); fade[-kf:] = np.linspace(1, 0, kf)
write('music.wav', norm(mu) * 0.8 * fade)
print('sfx.wav + music.wav', dur, 's')
