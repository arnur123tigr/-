"""Synth sound library (from the kaganat reel): effects and the music-bed parts."""
import wave
import numpy as np
SR = 48000
rng = np.random.default_rng(11)
N = lambda n: 440 * 2 ** ((n - 69) / 12)                     # MIDI note -> Hz
clamp = lambda v, a=0., b=1.: max(a, min(b, v))
seg = lambda t, a, b: clamp((t - a) / (b - a))
ease_out = lambda t: 1 - (1 - clamp(t)) ** 3
ease_io = lambda t: 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2


def tt(L): return np.arange(int(SR * L)) / SR
def norm(x): return x / (np.abs(x).max() + 1e-9)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def add(buf, t, sig, g=1.0):
    i = int(round(t * SR)); a = max(0, -i); i = max(0, i); j = min(len(buf), i + len(sig) - a)
    if i < j: buf[i:j] += g * sig[a:a + j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
def fades(x, a=.01, r=.05):
    n = len(x); e = np.ones(n); na = min(n, int(SR * a)); nr = min(n, int(SR * r)); e[:na] *= np.linspace(0, 1, na); e[n - nr:] *= np.linspace(1, 0, nr); return x * e


# ------------------------------------------------------------------ effects
def sweep(L, fc, bw=.55):
    """Noise through a band-pass whose centre fc(u) [Hz, u = 0..1] moves in time; bw in octaves."""
    n = int(SR * L); win, hop = 2048, 512; x = rng.standard_normal(n + win); y = np.zeros(n + win); w = np.hanning(win); f = np.maximum(np.fft.rfftfreq(win, 1 / SR), 1)
    for k in range(0, n, hop):
        g = np.exp(-.5 * (np.log2(f / fc(min(1, k / n))) / bw) ** 2)
        y[k:k + win] += np.fft.irfft(np.fft.rfft(x[k:k + win] * w) * g, win) * w
    return norm(y[:n])
def whoosh(L=.8, f0=250, f1=2600):                           # passes by: up and down again
    u = np.arange(int(SR * L)) / (SR * L); return sweep(L, lambda v: f0 * (f1 / f0) ** np.sin(np.pi * v)) * np.sin(np.pi * u) ** 1.7
def rush(L=.8, f0=300, f1=5000):                             # comes at you and stops dead (an arrow, a fast front)
    u = np.arange(int(SR * L)) / (SR * L); return fades(sweep(L, lambda v: f0 * (f1 / f0) ** v) * u ** 2.2, .01, .015)
def riser(L, f0=180, f1=1400):                               # tension: air + a tone climbing
    t = tt(L); u = t / L; tone = np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** u) / SR) * .25
    return fades((sweep(L, lambda v: f0 * 2 * (f1 / f0) ** v, .7)[:len(t)] + tone) * u ** 2, .02, .04)
def boom(f0=55, L=1.6, dec=3.0):
    t = tt(L); f = f0 * (1 + 2.5 * np.exp(-t * 18)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dec)
    return norm(s + .4 * band(rng.standard_normal(len(t)), 30, 900) * np.exp(-t * 12))
def sub(f0=80, f1=34, L=1.3):                                # the floor drops away
    t = tt(L); u = t / L; return fades(np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** u) / SR) * np.exp(-t * 2.2), .02, .1)
def rumble(L=1.6):
    t = tt(L); return norm(band(rng.standard_normal(len(t)), 28, 140)) * np.exp(-t * 2.6)
def drum(f0=90, L=.5, dec=9):
    t = tt(L); f = f0 * (1 + np.exp(-t * 35)); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dec) + .25 * band(rng.standard_normal(len(t)), 80, 2500) * np.exp(-t * 40))
def chime(f=1320, L=1.4):
    t = tt(L); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + 1.5 * h)) / h for h in (1, 2.76, 5.4)))
def pop():
    t = tt(.2); f = 500 + 900 * np.exp(-t * 30); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18))
def tick(f=3200):                                            # one step of the year counter
    t = tt(.03); return norm(band(rng.standard_normal(len(t)), f * .6, f * 1.8) * np.exp(-t * 190) + .5 * np.sin(2 * np.pi * f * t) * np.exp(-t * 260))
def key():                                                   # a key of the on-screen keyboard
    t = tt(.07); return norm(band(rng.standard_normal(len(t)), 500, 3200) * np.exp(-t * 85) + .6 * np.sin(2 * np.pi * 1150 * t) * np.exp(-t * 120))
def coin():                                                  # a few coins: bright metal pings
    out = np.zeros(int(SR * .9))
    for k in range(5):
        f = rng.uniform(3300, 5200); t = tt(.45); p = sum(np.sin(2 * np.pi * f * h * t + k) * np.exp(-t * (14 + 5 * h)) / h for h in (1, 1.52, 2.41, 3.17))
        add(out, .02 + k * rng.uniform(.045, .085), norm(p), rng.uniform(.5, 1))
    return norm(out)
def crack():                                                 # stone splitting: a sharp snap, a rattle of smaller ones, a low thump
    out = np.zeros(int(SR * .9)); t = tt(.12); add(out, 0, norm(band(rng.standard_normal(len(t)), 900, 9000) * np.exp(-t * 60)), 1)
    for k in range(14):
        t = tt(.05); add(out, .02 + rng.uniform(0, .38) ** 1.3, norm(band(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 140)), rng.uniform(.25, .7))
    t = tt(.6); add(out, 0, np.sin(2 * np.pi * np.cumsum(95 * (1 + 1.5 * np.exp(-t * 30))) / SR) * np.exp(-t * 9), .9)
    return norm(out)
def debris(L=1.4):                                           # pieces settling: clicks thinning out
    out = np.zeros(int(SR * L)); n = int(55 * L)
    for k in range(n):
        t0 = L * rng.uniform(0, 1) ** 1.8; t = tt(.03); add(out, t0, norm(band(rng.standard_normal(len(t)), 1800, 7500) * np.exp(-t * 200)), rng.uniform(.2, 1) * np.exp(-t0 * 2.2))
    return norm(out)
def drone(L, f=55.0):                                        # the overlord: a low, uneasy tone (a minor second beating against the root)
    t = tt(L); x = sum(np.sin(2 * np.pi * f * m * t + m) / m ** 1.4 for m in (1, 2, 3, 4)) + .7 * sum(np.sin(2 * np.pi * f * 1.0595 * m * t) / m ** 1.6 for m in (1, 2, 3))
    return norm(band(x, 35, 420)) * np.minimum(1, t / .5) * np.minimum(1, (L - t) / .5) * (1 + .15 * np.sin(2 * np.pi * .7 * t))
def swell(L, notes=(50, 57, 62), rel=.3):                    # lands growing: a chord rising out of nothing
    t = tt(L + rel); x = sum(np.sin(2 * np.pi * N(n) * h * t + h + n) / h ** 1.2 for n in notes for h in (1, 2, 3, 4))
    return norm(band(x, 60, 3200)) * np.minimum(1, t / L) ** 1.6 * np.minimum(1, (L + rel - t) / rel)
def shimmer(L=1.2):                                          # gold dust: little high pings
    out = np.zeros(int(SR * (L + .5)))
    for k in range(int(26 * L)):
        f = rng.choice([2093, 2349, 2794, 3136, 3520, 4186]) * rng.choice([1, 1, 2]); t = tt(.35)
        add(out, rng.uniform(0, L), np.sin(2 * np.pi * f * t) * np.exp(-t * 16), rng.uniform(.3, 1))
    return norm(out)


def gallop(L, rate=2.35):                                    # riders on the road: hoofbeats, three to the stride, far away
    out = np.zeros(int(SR * (L + .3))); T = 0.
    while T < L - .3:
        for off, g, f in ((0, 1, 150), (.125, .7, 185), (.25, .9, 135)):
            t = tt(.09); hit = band(rng.standard_normal(len(t)), 90, 1300) * np.exp(-t * 70) + .8 * np.sin(2 * np.pi * np.cumsum(f * (1 + .8 * np.exp(-t * 60))) / SR) * np.exp(-t * 45)
            add(out, T + off, norm(hit), g * rng.uniform(.75, 1) * np.sin(np.pi * clamp((T + off) / L)) ** .5)
        T += 1 / rate
    return norm(out)


