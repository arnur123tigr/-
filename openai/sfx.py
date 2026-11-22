"""Synthesised sound for the reel: effects track sfx.wav from cues.json ({dur, cues:[{t,k}], lift}) and a tense documentary
music bed music.wav (92 bpm, A minor pulse + pad + ticks; gets fuller after 'lift')."""
import json, wave, numpy as np
C = json.load(open('cues.json')); SR = 48000; DUR = C['dur']
rng = np.random.default_rng(3)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    if i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
noise = lambda L: rng.standard_normal(int(SR * L))
def sweep(L, lo, hi0, hi1):
    n = int(SR * L); x = noise(L); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], lo, hi0 + (hi1 - hi0) * u[k])[:len(y[k:k + 1024])]
    return norm(y)
def whoosh(L=.7): u = np.linspace(0, 1, int(SR * L)); return sweep(L, 200, 400, 4000) * np.sin(np.pi * u) ** 1.8
def pop(): t = tt(.22); f = 500 + 900 * np.exp(-t * 30); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16))
def hit():
    t = tt(1.0); f = 45 + 110 * np.exp(-t * 14); b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    k = band(noise(1.0), 300, 5000) * np.exp(-t * 40); return norm(b + .8 * k)
def rip(): t = tt(.45); return norm(band(noise(.45), 1500, 7000) * (np.abs(np.sin(t * 160)) ** .5) * np.exp(-t * 5))
def flip(): t = tt(.18); return norm(band(noise(.18), 800, 6000) * np.exp(-t * 25))
def rustle(L=.8): t = tt(L); return norm(band(noise(L), 1200, 8000) * (.5 + .5 * np.sin(t * 40)) * np.sin(np.pi * t / L))
def drone(L=3.0): t = tt(L); return norm((np.sin(2 * np.pi * 55 * t) + .5 * np.sin(2 * np.pi * 82.4 * t)) * np.minimum(1, t * 2) * np.minimum(1, (L - t) * 2))
def proj(L=2.5): t = tt(L); cl = (np.sin(2 * np.pi * 24 * t) > .92).astype(float); return norm(band(noise(L), 1000, 6000) * cl * .9 + .1 * band(noise(L), 100, 400))
def chain():
    out = np.zeros(int(SR * .7))
    for i in range(6):
        t = tt(.12); s = sum(np.sin(2 * np.pi * f * t) for f in (2300 + i * 150, 3400 + i * 90)) * np.exp(-t * 40); add(out, i * .09 + rng.random() * .02, s, .5 + .5 * rng.random())
    return norm(out)
def shutter(): a = flip(); b = np.zeros(int(SR * .35)); add(b, 0, a); add(b, .09, a, .7); t = tt(.35); return norm(b + .2 * np.sin(2 * np.pi * 900 * t) * np.exp(-t * 30))
def tvon(): t = tt(1.0); return norm(.6 * np.sin(2 * np.pi * 15700 * t) * np.exp(-t * 3) + band(noise(1.0), 500, 8000) * np.exp(-t * 3))
def crowd(L=2.5): t = tt(L); return norm(band(noise(L), 250, 2500) * (np.minimum(1, t) * np.minimum(1, (L - t) * 1.5)) * (1 + .3 * np.sin(t * 7)))
def buzz(L=1.0): t = tt(L); return norm(np.sin(2 * np.pi * 150 * t) * (np.sin(2 * np.pi * 3 * t) > 0) * band(np.ones(len(t)), 0, 1e9) * (1 + .3 * np.sin(2 * np.pi * 300 * t)))
def join(): t = tt(.6); return norm(np.sin(2 * np.pi * np.where(t < .2, 660, 880) * t) * np.exp(-((t % .2) * 12)) * (t < .4))
def typing(L=1.6):
    out = np.zeros(int(SR * L)); k = 0.0
    while k < L - .05: t = tt(.04); add(out, k, band(noise(.04), 1500, 6000) * np.exp(-t * 120)); k += .055 + rng.random() * .05
    return norm(out)
def marker(): t = tt(.5); return norm(band(noise(.5), 2000, 7000) * .6 * np.sin(np.pi * t / .5))
def door(): t = tt(.6); return norm(np.sin(2 * np.pi * (70 + 40 * np.exp(-t * 20)) * t) * np.exp(-t * 9) + .4 * band(noise(.6), 200, 2000) * np.exp(-t * 25))
def cash():
    out = np.zeros(int(SR * .9))
    for i in range(5): t = tt(.12); add(out, i * .13, band(noise(.12), 300, 3000) * np.exp(-t * 30) + .5 * np.sin(2 * np.pi * 90 * t) * np.exp(-t * 30))
    return norm(out)
def coins():
    out = np.zeros(int(SR * 1.2))
    for i in range(10): t = tt(.25); f = 3000 + rng.random() * 3000; add(out, rng.random() * .9, np.sin(2 * np.pi * f * t) * np.exp(-t * 25), .5 + .5 * rng.random())
    return norm(out)
def beep(): t = tt(.3); return norm(np.sin(2 * np.pi * 1760 * t) * (t < .15) * np.exp(-t * 5))
def line(): t = tt(1.2); return norm(band(noise(1.2), 2000, 6000) * .5 * np.sin(np.pi * t / 1.2))
def tick(L=1.5):
    out = np.zeros(int(SR * L))
    for i in range(int(L / .07)): t = tt(.02); add(out, i * .07, np.sin(2 * np.pi * 2500 * t) * np.exp(-t * 300))
    return norm(out)
def heart():
    out = np.zeros(int(SR * .8)); t = tt(.2)
    for d in (0, .22): add(out, d, np.sin(2 * np.pi * 50 * t) * np.exp(-t * 18))
    return norm(out)
def keys(L=1.5): return typing(L) * .7
def rise(L=2.0): t = tt(L); return norm(sweep(L, 200, 300, 6000) * (t / L) ** 2)
def ding(f=880): t = tt(1.5); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + h)) / h for h in (1, 2.01, 3.02)))
FX = {'whoosh': (whoosh, .22, -.35), 'pop': (pop, .2, 0), 'hit': (hit, .55, 0), 'rip': (rip, .25, 0), 'flip': (flip, .2, 0), 'drone': (drone, .18, 0),
      'proj': (proj, .06, 0), 'chain': (chain, .18, 0), 'shutter': (shutter, .25, 0), 'tvon': (tvon, .15, 0), 'crowd': (crowd, .12, 0), 'buzz': (buzz, .2, 0),
      'join': (join, .12, 0), 'type': (typing, .22, 0), 'marker': (marker, .2, 0), 'door': (door, .4, 0), 'cash': (cash, .3, 0), 'coins': (coins, .18, 0),
      'beep': (beep, .15, 0), 'line': (line, .15, 0), 'rustle': (rustle, .2, 0), 'tick': (tick, .12, 0), 'heart': (heart, .35, 0), 'keys': (keys, .2, 0),
      'rise': (rise, .18, -1.6), 'ding': (ding, .35, 0)}
s = np.zeros(int(SR * DUR))
for q in C['cues']:
    f, g, sh = FX[q['k']]; add(s, q['t'] + sh, f(), g)
write('sfx.wav', s)

# music bed
bpm = 92; beat = 60 / bpm; n = int(SR * DUR); m = np.zeros(n); lift = C.get('lift', DUR)
N = lambda k: 440 * 2 ** ((k - 69) / 12)
prog = [45, 41, 48, 43]   # A F C G (minor feel)
t1 = tt(beat / 2)
for i in range(int(DUR / (beat / 2))):
    t0 = i * beat / 2; root = prog[int(t0 / (beat * 8)) % 4]
    env = np.exp(-t1 * 9); add(m, t0, np.sin(2 * np.pi * N(root - 12) * t1) * env * (1.0 if i % 2 == 0 else .6), .5)   # pulse bass
    hat = band(rng.standard_normal(len(t1)), 6000, 12000) * np.exp(-t1 * 60); add(m, t0, hat, .06 if t0 < lift else .1)
    if t0 >= lift and i % 4 == 0: add(m, t0, np.sin(2 * np.pi * np.cumsum(50 + 80 * np.exp(-t1 * 25)) / SR) * np.exp(-t1 * 7), .6)    # kick after the lift
for bar in range(int(DUR / (beat * 8)) + 1):
    t0 = bar * beat * 8; root = prog[bar % 4]; L = beat * 8 + .5; t = tt(L)
    pad = sum(np.sin(2 * np.pi * N(root + iv) * t + np.sin(t * .7 + iv)) for iv in (12, 15, 19, 24)) / 4
    add(m, t0, pad * np.minimum(1, t / .8) * np.minimum(1, (L - t) / .5), .22 if t0 < lift else .3)
arp = [0, 3, 7, 12, 7, 3]
for i in range(int(DUR / (beat / 2))):
    t0 = i * beat / 2
    if t0 < lift - 30: continue
    root = prog[int(t0 / (beat * 8)) % 4]; t = tt(.3); add(m, t0, np.sin(2 * np.pi * N(root + 24 + arp[i % 6]) * t) * np.exp(-t * 10), .08)
fade = np.ones(n); k = int(SR * 2.5); fade[-k:] = np.linspace(1, 0, k); fade[:int(SR * .5)] = np.linspace(0, 1, int(SR * .5))
write('music.wav', norm(m) * fade * .8)
print('sfx + music', DUR)
