"""Comic / trailer sound effects and an epic drum bed, timed from beats.json -> sfx_<lang>.wav, music_<lang>.wav (48 kHz mono).
Everything is synthesised (no samples). Usage: python3 sfx.py ru|kk   (run one language at a time)"""
import json, sys, wave
import numpy as np
from scipy.signal import lfilter, butter

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
def noise(d): return rng.uniform(-1, 1, int(round(d * SR)))
def filt(x, f, kind='low', o=2):
    b, a = butter(o, np.array(f) / (SR / 2), kind); return lfilter(b, a, x)
def sine(f, d):
    t = tt(d); ph = 2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR; return np.sin(ph)
def fade(x, a=.003, r=.05):
    n = len(x); e = np.ones(n); na, nr = max(1, int(a * SR)), max(1, int(r * SR)); e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return x * e

def hit(big=1.):        # cinematic impact: pitched-down sub thump + noise crack + tail
    d = 1.4 * big; t = tt(d)
    sub = sine(110 * np.exp(-t * 6) + 38, d) * np.exp(-t * 3.2)
    crack = filt(noise(d), [300, 6000], 'band') * np.exp(-t * 22)
    tail = filt(noise(d), 900) * np.exp(-t * 3) * .25
    return fade(sub * 1.0 + crack * .7 + tail, .001, .3)
def drum():             # taiko-like
    d = .8; t = tt(d); return fade(sine(85 * np.exp(-t * 4) + 48, d) * np.exp(-t * 6) + filt(noise(d), 500) * np.exp(-t * 18) * .5, .001, .2)
def whoosh(d=.55, up=False):
    t = tt(d); env = np.sin(np.pi * t / d) ** 2; x = noise(d)
    lo = filt(x, [400, 2600] if not up else [700, 5000], 'band'); return lo * env * 1.6
def rip():              # paper tear: crackly band noise with jitter
    d = .55; t = tt(d); x = filt(noise(d), [1200, 7000], 'band'); g = (rng.uniform(size=len(t)) > .6) * 1. + .3
    g = filt(g, 300); return fade(x * g * np.exp(-t * 2.5) * 2.2, .002, .08)
def flip():
    d = .35; t = tt(d); return fade(filt(noise(d), [800, 5000], 'band') * np.sin(np.pi * t / d) * (1 + .5 * np.sin(t * 90)) * 1.2, .005, .05)
def clang():            # metal "ДЫҢ"
    d = 1.6; t = tt(d); x = sum(sine(f, d) * np.exp(-t * k) * g for f, k, g in [(523, 3, 1), (1187, 4, .6), (1960, 6, .45), (2730, 7, .3), (3410, 9, .2)])
    return fade(x * .5 + filt(noise(d), [2000, 8000], 'band') * np.exp(-t * 30) * .6, .001, .3)
def ding():             # coin
    d = 1.0; t = tt(d); return fade(sum(sine(f, d) * np.exp(-t * k) * g for f, k, g in [(2093, 5, 1), (3136, 7, .5), (4186, 9, .3)]) * .45, .001, .2)
def horn():             # short war horn: low brassy saw with swell
    d = 1.5; t = tt(d); f = 146.8 * (1 + .006 * np.sin(2 * np.pi * 5 * t)) * (1 - .03 * np.exp(-t * 8))
    ph = np.cumsum(f) / SR; saw = 2 * (ph % 1) - 1; x = filt(saw, 1400) * np.minimum(1, t / .25) * np.exp(-np.maximum(0, t - 1.0) * 6)
    return fade(x * .8, .02, .25)
def hoof():
    d = .09; t = tt(d); return fade(filt(noise(d), [200, 2500], 'band') * np.exp(-t * 55) + sine(120, d) * np.exp(-t * 45) * .6, .001, .02)
def crackle(d):
    x = np.zeros(int(d * SR))
    for _ in range(int(d * 40)):
        i = rng.integers(0, len(x) - 3000); L = rng.integers(300, 2500); x[i:i + L] += filt(noise(L / SR), [1500, 7000], 'band')[:L] * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(.3, 1)
    return x
def pop():
    d = .12; t = tt(d); return fade(sine(600 + 900 * t / d, d) * np.exp(-t * 30) * .7, .001, .03)
def wind(d):
    x = filt(noise(d), [150, 700], 'band'); t = tt(d); return x * np.minimum(1, np.minimum(t / .6, (d - t) / .6)) * 1.3

# scene 1
put(sfx, .02, hit(1.1), .8)
put(sfx, 1.0, whoosh(.45), .55); put(sfx, 1.42, hit(.6), .55)
put(sfx, M['bod'], hit(.8), .6)
# scene 2
put(sfx, M['s2'] - .05, rip(), .8)
put(sfx, M['s2'] + .02, drum(), .6); put(sfx, M['map'] + .2, drum(), .4); put(sfx, M['map'] + .55, drum(), .3)
put(sfx, M['map'] + .7, pop(), .4); put(sfx, M['map'] + 1.0, pop(), .4)
put(sfx, M['ush'], pop(), .5); put(sfx, M['suy'] + .1, whoosh(.35), .4)
# scene 3
put(sfx, M['s3'], flip(), .7); put(sfx, M['sulu'] - .1, hit(.5), .5)
for k in ('ar', 'ch', 'et'): put(sfx, M[k] - .1, whoosh(.4), .35); put(sfx, M[k] + .35, hit(.75), .75)
# scene 4: gallop, clash, retreat, stamp
t = M['s4'] - .1; k = 0
while t < M['clash'] - .1:
    put(sfx, t, hoof(), (.5, .4, .65)[k % 3]); t += (.09, .09, .24)[k % 3]; k += 1
put(sfx, M['clash'] - .2, whoosh(.3), .5); put(sfx, M['clash'], clang(), .8); put(sfx, M['clash'], hit(.9), .7)
put(sfx, M['clash'] + .9, pop(), .4); put(sfx, M['clash'] + 1.3, whoosh(.9), .4)
put(sfx, M['nick'] + .75, hit(.8), .75); put(sfx, M['nick'] + 1.7, hit(.6), .6)
# scene 5
put(sfx, M['s5'] - .1, whoosh(.4, True), .6); put(sfx, M['s5'] + .25, whoosh(1.0), .3)
put(sfx, M['s5'] + .9, pop(), .4)
tc = M['s5'] + 1.7
for i in range(3): put(sfx, tc + i * .18, ding(), .5)
put(sfx, M['horn'] - .1, horn(), .7)
# scene 6
put(sfx, M['s6'] + .05, hit(1.2), .9); put(sfx, M['s6'], wind(M['chn'] - M['s6']), .18)
put(sfx, M['chn'] - .15, whoosh(.4), .4)
put(sfx, M['tz'] - .9, whoosh(1.0), .35); put(sfx, M['tz'] + .1, hit(.9), .8); put(sfx, M['tz'] + .1, crackle(.6), .6)
put(sfx, M['sy'] - .7, whoosh(.9), .35); put(sfx, M['sy'] + .1, hit(.9), .8); put(sfx, M['sy'] + .1, crackle(.6), .6)
put(sfx, M['atl'] + .3, clang(), .35)
# scene 7
put(sfx, M['s7'] - .05, whoosh(.4), .5); put(sfx, M['s7'] + .05, hit(.6), .5)
put(sfx, M['ans'] + .1, hit(1.0), .85)
put(sfx, M['cta'] - .1, whoosh(.6, True), .7); put(sfx, M['cta'] + .2, pop(), .4)
put(sfx, END - 1.8, hit(.5), .35)

# --- epic bed: D minor drone + pad + taiko groove, 92 bpm ---
bpm = 92; beat = 60 / bpm
d = END + 1; t = tt(d)
chords = [(50, 53, 57), (46, 50, 53), (48, 52, 55), (45, 49, 52)]   # Dm Bb C A
nf = lambda n: 440 * 2 ** ((n - 69) / 12)
bar = beat * 4
for i in range(int(d / (bar * 2)) + 1):
    t0 = i * bar * 2; ch = chords[i % 4]; seg = bar * 2 + .3
    pad = sum(sum(sine(nf(n + 12) * (1 + dt), seg) for dt in (-.003, .003)) for n in ch)
    pad = filt(pad, 1800) * np.minimum(1, tt(seg) / .4) * np.minimum(1, (seg - tt(seg)) / .4)
    put(mus, t0, pad, .05)
    put(mus, t0, fade(sine(nf(ch[0] - 12), seg), .2, .3), .22)
for i in range(int(d / beat)):
    tb = i * beat; p = i % 8
    if p in (0, 3, 4, 6): put(mus, tb, drum(), .55 if p == 0 else .38)
    if p in (2, 6): put(mus, tb, fade(filt(noise(.12), [2000, 8000], 'band') * np.exp(-tt(.12) * 30), .001, .03), .2)
# the bed drops out under the helmet panel (sad beat) and comes back on the map
te = np.arange(N) / SR; g = np.ones(N)
g[(te > M['s6']) & (te < M['chn'])] = .25
w = int(.5 * SR); g = np.convolve(g, np.ones(w) / w, 'same'); g[te > END - .6] *= np.linspace(1, 0, (te > END - .6).sum())
mus *= g


def save(name, x):
    x = x[:int(END * SR)]; x = x / max(1e-6, np.abs(x).max()) * .9
    with wave.open(name, 'w') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((x * 32767).astype(np.int16).tobytes())
save(f'sfx_{LANG}.wav', sfx); save(f'music_{LANG}.wav', mus)
print('ok', END)
