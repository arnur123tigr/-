"""8-bit effects and a chiptune bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
Usage: python3 sfx.py ru|kk"""
import json, sys, wave
import numpy as np

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; END = B['end']
SR = 48000; N = int(END * SR) + SR
rng = np.random.default_rng(7)
sfx = np.zeros(N); mus = np.zeros(N)


def put(buf, t, x, g=1.):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * g
def tt(d): return np.arange(int(round(d * SR))) / SR
def sq(f, d, duty=.5):
    t = tt(d); f = np.broadcast_to(f, t.shape) if np.ndim(f) else np.full(t.shape, f)
    ph = np.cumsum(f) / SR; return np.where((ph % 1) < duty, 1., -1.)
def tri(f, d):
    t = tt(d); ph = np.cumsum(np.full(t.shape, f) if not np.ndim(f) else f) / SR; return 2 * np.abs(2 * (ph % 1) - 1) - 1
def env(x, a=.005, r=.08, hold=None):
    n = len(x); e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return x * e
def noise(d, step=1):   # step > 1 = lower "8-bit" noise
    n = int(round(d * SR)); v = rng.uniform(-1, 1, n // step + 1); return np.repeat(v, step)[:n]
def lp(x, k=.1):
    y = np.zeros_like(x); a = 0.; k = np.broadcast_to(k, x.shape)
    for i in range(len(x)): a += k[i] * (x[i] - a); y[i] = a
    return y
def nf(n): return 440 * 2 ** ((n - 69) / 12)

# --- effects ---
def hit():
    d = .35; t = tt(d); f = 220 * np.exp(-t * 9) + 40
    return env(sq(f, d) * np.exp(-t * 7) * .8 + noise(d, 6) * np.exp(-t * 14) * .6, .001, .05)
def hoof():
    d = .07; t = tt(d); return env(noise(d, 10) * np.exp(-t * 60) * .9 + sq(90, d) * np.exp(-t * 50) * .4, .001, .02)
def beep(f=880, d=.09): return env(sq(f, d, .25) * .5, .002, .02)
def blip(f=1320): return env(sq(np.linspace(f, f * 1.5, int(.06 * SR)), .06, .5) * .4, .001, .02)
def arp(notes, step=.06, duty=.5, g=.45):
    return np.concatenate([env(sq(nf(n), step, duty) * g, .002, .015) for n in notes])
def pluck(f, d=.6):
    n = int(SR / f); buf = rng.uniform(-1, 1, n); out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = .5 * (buf[i % n] + buf[(i + 1) % n]) * .996
    return np.round(out * 6) / 6 * .7    # coarse steps: 8-bit flavour
def crackle(d):
    x = np.zeros(int(d * SR))
    for _ in range(int(d * 14)):
        i = rng.integers(0, len(x) - 2000); L = rng.integers(200, 1500); x[i:i + L] += noise(L / SR, 3)[:L] * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(.2, .7)
    return x
def shot():
    d = .22; t = tt(d); return env(noise(d, 4) * np.exp(-t * 22) * .9 + sq(70 * np.exp(-t * 8) + 30, d) * np.exp(-t * 18) * .4, .001, .03)
def boom():
    d = .9; t = tt(d); return env(noise(d, 14) * np.exp(-t * 4.5) + sq(60 * np.exp(-t * 3) + 25, d) * np.exp(-t * 4) * .6, .001, .2)
def whoosh(d=.5):
    t = tt(d); x = noise(d, 2); return lp(x, .05 + .25 * np.sin(np.pi * t / d)) * np.sin(np.pi * t / d) * 1.4
def ice():
    d = .18; t = tt(d); return env(lp(noise(d, 2), .35) * (np.exp(-t * 20) + .3 * (rng.uniform(size=len(t)) > .97)), .001, .05)
def coin(): return np.concatenate([env(sq(nf(83), .07, .5) * .45, .001, .01), env(sq(nf(88), .32, .5) * .45, .001, .25)])
def cry():   # "battle cry": rising square chord swell + noise
    d = 1.1; t = tt(d); f = 180 + 160 * np.minimum(1, t / .5)
    x = (sq(f, d, .3) + sq(f * 1.5, d, .3) * .6 + noise(d, 8) * .5) * np.sin(np.pi * np.minimum(1, t / d)) ** .7
    return env(x * .45, .05, .3)

def chunk_hooves(t0, t1, rate, g=.6, gallop=False):
    t = t0; k = 0
    while t < t1:
        put(sfx, t, hoof(), g * (1 if k % 2 == 0 else .7))
        t += (1 / rate) * ((.35, .35, 1.3)[k % 3] if gallop else 1); k += 1

# scene 1
put(sfx, 0.02, hit(), .9)
chunk_hooves(.2, M['s2'] - .1, 3.4, .45)
# scene 2: alarm when the bar turns red, card pop
for i in range(6):
    tb = M['s2'] + (M['s3'] - M['s2']) * .55 + i * .8
    if tb < M['s3'] - .3: put(sfx, tb, np.concatenate([beep(988), np.zeros(int(.05 * SR)), beep(740)]), .5)
put(sfx, M['zh'], arp([72, 76, 79, 84], .05), .4)
put(sfx, M['s3'] - .3, whoosh(.6), .5)
# scene 3: fire, dombra
put(sfx, M['s3'], crackle(M['s4'] - M['s3']), .35)
pat = [57, 64, 62, 64, 57, 64, 60, 64, 55, 62, 60, 62]
for i, n in enumerate(pat * 2):
    tb = M['s3'] + .8 + i * .16
    if tb < M['s4'] - .4: put(sfx, tb, pluck(nf(n), .5), .45 if i % 4 else .6)
put(sfx, M['mah'], arp([67, 71, 74, 79], .05), .4)
# scene 4: quest jingle, gallop growing, counter ticks, battle cry
put(sfx, M['s4'] + .05, arp([69, 73, 76, 81, 76, 81], .07), .4)
tt0 = M['s4']; d4 = M['s5'] - M['s4']
t = tt0; k = 0
while t < M['s5']:
    fr = (t - tt0) / d4; put(sfx, t, hoof(), .35 + .45 * fr); t += (.11, .11, .26)[k % 3] * (1.15 - .3 * fr); k += 1
tc = M['cnt'] - M['s4']
for i in range(12):
    put(sfx, M['s4'] + tc * .45 + i * (tc * .45 + .6) / 12, blip(1200 + i * 40), .35)
put(sfx, M['ring'] - .2, cry(), .55)
# scene 5: flash boom, gunfire, short game over
put(sfx, M['s5'], boom(), .5)
t = M['hit'] - .4
while t < M['scat'] + .6:
    put(sfx, t, shot(), rng.uniform(.35, .7)); t += rng.uniform(.08, .28)
put(sfx, M['hit'], boom(), .5)
go = np.concatenate([env(sq(nf(n), .13, .5) * .5, .002, .03) for n in (67, 63, 60)] + [env(sq(nf(55), .35, .5) * .5, .002, .25)])
put(sfx, M['scat'] + .2, go, .65)
# scene 6: wind (quiet), ice, slow hooves, coin
d6 = M['s7'] - M['s6']; w = lp(noise(d6, 3), .02); w *= np.minimum(1, np.minimum(tt(d6) / .5, (d6 - tt(d6)) / .5)) * 1.6
put(sfx, M['s6'], w, .25)
t = M['s6'] + .2
while t < M['s7'] - .2: put(sfx, t, ice(), .35); put(sfx, t + .05, hoof(), .25); t += rng.uniform(.25, .45)
put(sfx, M['post'] + .3, coin(), .7)
# scene 7: one dombra note
put(sfx, M['fade'], pluck(nf(52), 2.2), .7)
put(sfx, M['mon'], whoosh(.5), .25)
# scene 8: rows, highlight, level complete, end
for i in range(4): put(sfx, M['s8'] + .4 + i * .45, blip(900), .45)
put(sfx, M['s8'] + 2.4, arp([72, 79, 84], .07), .6)
put(sfx, M['cta'], arp([60, 64, 67, 72, 67, 72, 76, 79, 84], .075, .5, .5), .7)
put(sfx, END - 2.2, arp([84, 88, 91, 96], .06, .25), .45)

# --- chiptune bed: A minor pentatonic, 112 bpm ---
bpm = 112; st = 60 / bpm / 4
bass = [45, 45, 52, 45, 43, 43, 50, 43, 41, 41, 48, 41, 43, 43, 50, 52]
lead = [69, None, 72, 74, 76, None, 74, 72, 69, None, 67, 69, 72, None, None, None,
        76, None, 79, 76, 74, None, 72, 74, 76, None, 74, 72, 69, None, None, None]
s = 0; t = 0.
while t < END:
    b = bass[(s // 4) % len(bass)]
    if s % 2 == 0: put(mus, t, env(tri(nf(b), st * 1.9), .002, .03), .55)
    a = [57, 60, 64, 67][s % 4] + (0 if (s // 16) % 2 == 0 else -2)
    put(mus, t, env(sq(nf(a + 12), st * .9, .125), .001, .02), .12)
    ln = lead[(s // 2) % len(lead)]
    if s % 2 == 0 and ln and (s // 64) % 2 == 1: put(mus, t, env(sq(nf(ln), st * 1.8, .25), .003, .05), .2)
    if s % 4 == 0: put(mus, t, env(noise(.05, 2) * np.exp(-tt(.05) * 50), .001, .01), .25)
    t += st; s += 1
# music envelope: full in 1-6 and 8, gone in 7
te = np.arange(N) / SR; g = np.ones(N)
g[(te > M['s7'] - .3) & (te < M['s8'])] = 0
g = np.convolve(g, np.ones(int(.4 * SR)) / int(.4 * SR), 'same'); g[te > END - .4] *= np.linspace(1, 0, (te > END - .4).sum())
mus *= g


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
