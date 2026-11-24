"""Sound for the Kulja 1881 reel: synth effects (sfx_<lang>.wav) and a music bed (music_<lang>.wav).
Everything is timed from beats.json (video seconds: the word times of the voiceover and the cues derived from them in timing.py),
so picture (scene.html) and sound follow the same marks.
Usage: python3 sfx.py ru|kk"""
import wave, json, sys
import numpy as np

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; DUR = B['end']; SR = 48000
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
def tap():                                                   # a tap on the screen
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


def wind(L, lo=250, hi=1400, gust=.35, seed=0):             # dry desert wind: band noise, slow gusts
    r = np.random.default_rng(seed); t = tt(L); x = band(r.standard_normal(len(t)), lo, hi)
    g = 1 + gust * np.sin(2 * np.pi * .23 * t + seed) + .5 * gust * np.sin(2 * np.pi * .61 * t + 2 * seed)
    return norm(x * g) * np.minimum(1, t / .6) * np.minimum(1, (L - t) / .6)
def sand(L, seed=1):                                         # sand streaming over a dune: a fine high hiss
    r = np.random.default_rng(seed); t = tt(L); return norm(band(r.standard_normal(len(t)), 3500, 11000) * (1 + .5 * np.sin(2 * np.pi * .4 * t))) * np.minimum(1, t / .4) * np.minimum(1, (L - t) / .4)
def armour(L, rate=3.0):                                     # far-off clinks of armour and spears
    out = np.zeros(int(SR * L))
    for k in range(int(L * rate)):
        f = rng.uniform(2400, 4200); t = tt(.3); p = sum(np.sin(2 * np.pi * f * h * t + k) * np.exp(-t * (22 + 6 * h)) / h for h in (1, 1.47, 2.3))
        add(out, rng.uniform(0, L - .3), norm(p), rng.uniform(.25, 1))
    return norm(out)
def fire(L):                                                 # a campfire: soft roar + crackles
    t = tt(L); base = band(rng.standard_normal(len(t)), 80, 900) * (1 + .3 * np.sin(2 * np.pi * 1.3 * t)) * .5; out = norm(base) * .4
    for k in range(int(L * 9)):
        c = tt(.02); add(out, rng.uniform(0, L - .05), norm(band(rng.standard_normal(len(c)), 1200, 7000) * np.exp(-c * 260)), rng.uniform(.2, 1))
    return norm(out) * np.minimum(1, t / .3) * np.minimum(1, (L - t) / .3)
def steps(L, rate=1.7):                                      # tired steps in sand
    out = np.zeros(int(SR * L)); T = .1
    while T < L - .2:
        c = tt(.18); add(out, T, norm(band(rng.standard_normal(len(c)), 150, 2200) * np.exp(-c * 22) * (1 - np.exp(-c * 90))), rng.uniform(.6, 1)); T += 1 / rate * rng.uniform(.9, 1.1)
    return norm(out)
def breath(L, rate=.55):                                     # heavy breathing
    out = np.zeros(int(SR * L)); T = 0.
    while T < L - 1:
        b = tt(1.1); env = np.sin(np.pi * b / 1.1) ** 2; add(out, T, norm(band(rng.standard_normal(len(b)), 400, 2600) * env), .8); T += 1 / rate
    return norm(out)
def flute(notes, t0s, Ls, g=1.0):                            # a breathy end-blown flute (like the sybyzgy): sine + noise, slow vibrato
    total = max(a + b for a, b in zip(t0s, Ls)) + .5; out = np.zeros(int(SR * total))
    for n, a, L in zip(notes, t0s, Ls):
        t = tt(L); f = N(n) * (1 + .006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / .4))
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + .18 * np.sin(4 * np.pi * np.cumsum(f) / SR)
        air = band(rng.standard_normal(len(t)), N(n) * .8, N(n) * 3) * .25
        env = np.minimum(1, t / .18) * np.minimum(1, (L - t) / .35); add(out, a, (tone + air) * env, g)
    return norm(out)


def crackle(L):                                              # old film: dust pops and a faint projector hum
    out = np.zeros(int(SR * L)); t = tt(L); out += .15 * norm(band(rng.standard_normal(len(t)), 2000, 9000)) * .2
    for k in range(int(L * 14)):
        c = tt(.012); add(out, rng.uniform(0, L - .02), norm(band(rng.standard_normal(len(c)), 1500, 9000) * np.exp(-c * 400)), rng.uniform(.15, 1))
    out += .12 * np.sin(2 * np.pi * 48 * t) * (1 + .3 * np.sin(2 * np.pi * 24 * t))
    return norm(out) * np.minimum(1, t / .3) * np.minimum(1, (L - t) / .3)
def stamp():                                                 # a seal slammed onto paper
    t = tt(.5); return norm(np.sin(2 * np.pi * np.cumsum(110 * (1 + 1.2 * np.exp(-t * 40))) / SR) * np.exp(-t * 14) + .7 * band(rng.standard_normal(len(t)), 300, 4000) * np.exp(-t * 45))
def shot(far=1.0):                                           # a rifle shot with a short echo
    t = tt(1.0); x = band(rng.standard_normal(len(t)), 200, 6000 * far) * np.exp(-t * 30) + .6 * np.sin(2 * np.pi * np.cumsum(70 * (1 + 2 * np.exp(-t * 50))) / SR) * np.exp(-t * 12)
    y = x.copy(); add(y, .18, x * .35); add(y, .41, band(x, 200, 2000) * .18); return norm(y)
def bell(f=196, L=4.0):                                      # one low memorial bell
    t = tt(L); return norm(sum(np.sin(2 * np.pi * f * h * t + h) * np.exp(-t * (.7 + .5 * h)) / h for h in (1, 2, 2.4, 3, 4.2, 5.4)))


def heart(L, rate=1 / 1.15):                                 # a slow, quiet heartbeat: lub-dub
    out = np.zeros(int(SR * (L + .5))); T = 0.
    while T < L:
        for off, g, f in ((0, 1, 55), (.22, .7, 48)):
            t = tt(.25); add(out, T + off, np.sin(2 * np.pi * np.cumsum(f * (1 + .6 * np.exp(-t * 40))) / SR) * np.exp(-t * 18), g)
        T += 1 / rate
    return norm(out)
def crowd(L, seed=3):                                        # a crowd murmur that grows
    r = np.random.default_rng(seed); t = tt(L); x = band(r.standard_normal(len(t)), 250, 2200) * (1 + .4 * np.sin(2 * np.pi * 2.1 * t) * np.sin(2 * np.pi * .37 * t))
    return norm(x) * np.minimum(1, t / L) ** 1.3 * np.minimum(1, (L - t) / .4)
def ring_ear(L=2.4, f=3900):                                 # ringing in the ears after the blast
    t = tt(L); return np.sin(2 * np.pi * f * t) * np.exp(-t * 1.4) * np.minimum(1, t / .05)


def clock(L, rate=2.0):                                      # a ticking clock (the open question)
    out = np.zeros(int(SR * (L + .1))); T = 0.; k = 0
    while T < L: add(out, T, tick(2600 if k % 2 else 3400), 1 if k % 2 == 0 else .7); T += 1 / rate; k += 1
    return norm(out)


s = np.zeros(int(SR * DUR))
m = lambda k: M[k]
# camera flights
for a, L in ((.15, 2.6), (m('S4') - .1, 1.2), (m('pek') - .9, 1.3), (m('S9') - .1, 1.0), (m('S10') + .1, 2.2), (m('ret') - .3, 1.3), (m('pay') - .2, .9), (m('ak') - .5, 1.0), (m('S12') - .1, 1.2), (m('S15') - .1, 1.4)):
    add(s, a, whoosh(L, 220, 2400), .22)
# 1. the coin falls: a deep boom and a ring of coins
add(s, m('r9') - .6, riser(.6, 160, 1100), .12); add(s, m('r9') + .08, boom(40, 2.2, 1.8), .55); add(s, m('r9') + .1, coin(), .35); add(s, m('r9') + .1, chime(2637, 1.6), .12)
add(s, 0, drone(m('S3'), 41.2), .1)
# 2. the distance line
add(s, m('alm') - .05, pop(), .2); add(s, m('km') - .05, pop(), .25)
# 3. the open question: a clock
add(s, m('kz') - .1, pop(), .2); add(s, m('kz'), clock(m('S4') - m('kz') - .3, 2.0), .22)
# 4-5. 1864: fire, the rising
add(s, m('S4') + .05, pop(), .2); add(s, m('xj'), fire(m('S6') - m('xj')), .1); add(s, m('rise') - .05, boom(48, 1.4, 2.4), .3)
add(s, m('kul') - .05, drum(80, .5, 8), .3)
# 6. 1871: the army marches in
add(s, m('S6') + .05, pop(), .2); add(s, m('rus') - .2, gallop(2.4, 2.6), .14); add(s, m('rus') + .1, rush(1.1, 250, 3500), .15); add(s, m('quote') - .05, pop(), .22)
# 7. «temporary» crossed out, ten years run
add(s, m('tmp') + .45, rush(.35, 800, 6000), .18)
for i in range(10): add(s, m('tmp') + .2 + (m('y10') + 1.2 - m('tmp') - .2) * (.5 - .5 * np.cos(np.pi * (i + 1) / 10)), tick(3000), .35)
add(s, m('y10') - .05, stamp(), .45)
# 8. Livadia, Beijing, the death sentence
add(s, m('S8') + .05, pop(), .2); add(s, m('big') - .05, swell(.8, (50, 57, 62)), .1); add(s, m('pek') + .4, pop(), .22); add(s, m('death') + .08, stamp(), .5)
add(s, m('death') + .1, sub(70, 32, 1.2), .3)
# 9. on the edge of war: drums and tension
a, b = m('S9'), m('S10')
for i, t0 in enumerate(np.arange(a + .1, b + .3, .32)): add(s, t0, drum(62 + 6 * (i % 2), .5, 8), .25 + .02 * i)
add(s, a, riser(b - a + .4, 120, 900), .14); add(s, m('war') - .05, boom(44, 1.6, 2.2), .3)
# 10. the treaty: the pen, the seal, the money
add(s, m('spb') + .3, crackle(.8), .05); add(s, m('spb') + 1.0, stamp(), .45); add(s, m('ret') + .9, pop(), .2)
add(s, m('pay') - .05, coin(), .35); add(s, m('pay') + .4, shimmer(1.6), .1)
for i in range(6): add(s, m('pay') + .3 + i * .28, coin(), .14)
# 11. Alaska
add(s, m('ak') - .05, pop(), .22); add(s, m('ak') + .4, pop(), .2); add(s, m('ak') + .7, chime(1568, 1.2), .12)
# 12. the new border, the choice
add(s, m('west') + .2, rush(1.2, 300, 4000), .12); add(s, m('y1') - .05, pop(), .22); add(s, m('move') - .05, pop(), .22)
# 13. the people move: steps, then the «aha»
add(s, m('k50') - .2, steps(m('ver') - m('k50') + 1.5, 2.2), .1); add(s, m('k50') - .05, pop(), .2)
add(s, m('zhar') - .05, pop(), .18); add(s, m('ver') - .05, pop(), .18)
add(s, m('aha') - 1.5, riser(1.5, 160, 1400), .14); add(s, m('aha') + .02, boom(46, 1.8, 2), .35)
for i, f in enumerate((587, 740, 880)): add(s, m('aha') + .1 + i * .06, chime(f, 1.8), .12)
add(s, m('uy') - .05, pop(), .25); add(s, m('uy') + .1, shimmer(1.0), .08); add(s, m('kor') - .05, rush(1.4, 400, 5000), .12)
# 14. ҰБТ
add(s, m('ubt') - .1, boom(55, 1.2), .25); add(s, m('q') - .05, pop(), .25)
add(s, m('ans') - .05, pop(), .25); add(s, m('ans') + .1, chime(1319, 1.4), .25); add(s, m('ans') + .12, chime(1760, 1.2), .15)
# 15. the coin again, the link, the end card
add(s, m('S15') + 1.2, coin(), .25); add(s, m('S15') + 2.0, whoosh(.6, 300, 2600), .3); add(s, m('S15') + 2.2, tap(), .35)
e0 = m('last') + .55
add(s, e0 - .2, whoosh(.6, 240, 2200), .25); add(s, e0 + .05, boom(52, 1.6, 2.6), .3)
for i, f in enumerate((587, 880, 1175)): add(s, e0 + .3 + i * .07, chime(f, 1.5), .14)
write(f'sfx_{LANG}.wav', norm(s) * .9)

# ------------------------------------------------------------------ music bed: D minor, mysterious; tension at the war, lift at the «aha», bright at the end
Dm, Bb, F, C, Gm, A = [50, 53, 57], [46, 50, 53], [41, 45, 48], [48, 52, 55], [43, 46, 50], [45, 49, 52]
mu = np.zeros(int(SR * DUR))
def pad(notes, L, g, bright=1.0):
    t = tt(L + .35); x = sum(np.sin(2 * np.pi * N(n) * h * t + np.sin(2 * np.pi * 5 * t) * .02 * h + n) / h ** 1.3 for n in notes for h in (1, 2, 3, 4))
    return norm(band(x, 60, 2400 * bright)) * np.minimum(1, t / .5) * np.minimum(1, (L + .35 - t) / .35) * g
def bass(n, L, g):
    t = tt(L); f = N(n - 12 if n >= 48 else n); return (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t)) * np.minimum(1, t / .02) * np.exp(-t * .8) * np.minimum(1, (L - t) / .05) * g
def pluck(n, L, g, dec=6):
    t = tt(L); f = N(n); return (np.sin(2 * np.pi * f * t) + .45 * np.sin(4 * np.pi * f * t) + .25 * np.sin(6 * np.pi * f * t)) * np.exp(-t * dec) * np.minimum(1, t / .003) * g
def part(t0, t1, prog, bpm=72, pads=.2, low=.28, dombra=0., toms=0., bright=.8):
    n = max(2, int(round((t1 - t0) * bpm / 60))); bt = (t1 - t0) / n
    for i in range(n):
        b0 = t0 + i * bt; ch = prog[(i // 4) % len(prog)]
        if i % 4 == 0:
            L = min(4, n - i) * bt
            if pads: add(mu, b0, pad(ch, L, pads, bright))
            if low: add(mu, b0, bass(ch[0], L, low))
        if dombra:
            for off, q in ((0, 0), (.5, 2), (.75, 1)): add(mu, b0 + off * bt, pluck(ch[q] + 12, bt * .6, dombra * (1 if off == 0 else .7)))
        if toms and i % 2 == 0: add(mu, b0, drum(58, .7, 5), toms)
part(0, m('S4'), [Dm, Bb], pads=.13, low=.2, bright=.5)
part(m('S4'), m('S9'), [Dm, Bb, Gm, A], pads=.15, low=.24, dombra=.07, toms=.1, bright=.6)
part(m('S9'), m('S10'), [Gm, A], pads=.16, low=.26, toms=.14, bright=.55)
part(m('S10'), m('S13'), [Dm, Bb, F, C], pads=.16, low=.24, dombra=.08, toms=.1, bright=.75)
part(m('S13'), m('aha'), [Dm, Bb], pads=.14, low=.22, dombra=.06, bright=.6)
part(m('aha'), m('S14'), [F, C, Dm, Bb], pads=.22, low=.3, dombra=.1, toms=.16, bright=1.0)
part(m('S14'), m('ans'), [Dm, Bb], pads=.12, low=.18, dombra=.05, bright=.6)
part(m('ans'), DUR, [F, C, Dm, Bb], pads=.2, low=.26, dombra=.09, toms=.14, bright=.9)
write(f'music_{LANG}.wav', norm(mu * np.minimum(1, np.arange(len(mu)) / (SR * .6))) * .9)
print(LANG, 'sfx + music', DUR, 's')
