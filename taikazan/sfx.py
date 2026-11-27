"""Sound for the «Тайқазан» reel: synth effects (sfx_<lang>.wav) and a music bed (music_<lang>.wav).
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
for a, L in ((.15, 2.2), (m('S2') + .1, 1.3), (m('S3') + .1, 1.3), (m('S4') + .1, 1.1), (m('S5') + .1, .9), (m('S7') + .1, 1.2), (m('S9') + .1, 1.1),
             (m('after') + .1, 1.0), (m('home') - .1, 1.2), (m('S13') + .1, 1.5)):
    add(s, a, whoosh(L, 220, 2400), .22)
# 1. the dive onto Turkestan; the kazan lifts off and flies away north
add(s, 1.7, riser(.6, 160, 1100), .12); add(s, 2.3, boom(42, 2.0, 1.9), .5); add(s, 2.35, sub(70, 32, 1.1), .28)
add(s, m('y54') - .1, rush(1.4, 300, 4500), .14); add(s, m('y54') + .1, drum(70, .5, 8), .25)
add(s, 0, drone(m('S3'), 41.2), .09)
# 2. there and back, the question mark
add(s, m('go') - .05, whoosh(1.1, 300, 2600), .16); add(s, m('back') - .05, whoosh(1.1, 300, 2600), .16); add(s, m('odd'), pop(), .25)
# 3. the mausoleum, the hall lights up, the kazan appears
add(s, m('maus') - .2, swell(1.0, (50, 57, 62)), .1); add(s, m('hall'), chime(1319, 1.4), .14); add(s, m('kaz'), bell(196, 3.0), .16)
# 4. 1399, Timur's order travels from Samarkand
add(s, m('y1399') - .05, stamp(), .35); add(s, m('tim') - .1, rush(1.0, 300, 4000), .12); add(s, m('tim') + .9, pop(), .2); add(s, m('master'), chime(1568, 1.2), .12)
# 5. the big drawing: weight, width, the man
add(s, m('S5') + .2, boom(48, 1.4, 2.4), .3); add(s, m('ton') - .05, drum(60, .6, 6), .3); add(s, m('wid') - .05, whoosh(.6, 400, 3000), .2); add(s, m('man') - .05, pop(), .22)
# 6. water pours in; twenty baths pop
t0 = m('l3000') - .2; L6 = 1.8; add(s, t0, band(rng.standard_normal(int(SR * L6)), 300, 3500) * np.minimum(1, tt(L6) / .2) * np.minimum(1, (L6 - tt(L6)) / .5) * .5, .25)
for i in range(20): add(s, m('bath') + i * .045, tap(), .1)
# 7. 1935: the road north-west, the Hermitage
add(s, m('y1935') - .05, stamp(), .35); add(s, m('y1935') + .5, gallop(m('erm') - m('y1935') - .5, 3.2), .05)
add(s, m('y1935') + .5, rush(m('erm') - m('y1935') - .6, 200, 2500), .08); add(s, m('erm') - .1, chime(1175, 1.4), .16); add(s, m('iran'), pop(), .2)
# 8. the km counter, the «temporary» stamp
for i in range(16): add(s, m('km') + i * .09, tick(2600 + 60 * i), .16)
add(s, m('temp') - .05, stamp(), .45)
# 9. the years run: a clock, a flipping counter; "not returned" lands heavily
add(s, m('over'), clock(m('y1989') - m('over') - .2, 2.4), .1); add(s, m('no') - .05, boom(46, 1.4, 2.4), .3)
n9 = 26
for i in range(n9): add(s, m('over') + .3 + (m('y1989') - .5 - m('over')) * i / n9, tick(3000), .12)
# 10. 1989: back home
add(s, m('y1989') - .1, chime(1319, 1.4), .2); add(s, m('y1989') - .05, drum(80, .5, 8), .3); add(s, m('after') + .2, rush(1.6, 250, 3000), .1)
add(s, m('home') + .5, boom(52, 1.6, 2.4), .3); add(s, m('home') + .55, bell(220, 3.5), .18); add(s, m('home') + .6, shimmer(1.2), .08)
# 11. not meat, but water; drops handed out
add(s, m('S11') + .5, swell(1.0, (45, 52, 57)), .1); add(s, m('meat') - .05, pop(), .25); add(s, m('meat') + .5, rush(.5, 400, 4000), .12)
for i in range(3): add(s, m('water') + i * .14, chime(1760 + 220 * i, .8), .1)
for i in range(6): add(s, m('give') + .2 + i * .18, pop(), .08)
# 12. ҰБТ / ЕНТ
add(s, m('ubt') - .1, boom(55, 1.2), .25); add(s, m('q') - .05, pop(), .25)
add(s, m('ans') + .4, chime(1319, 1.4), .22); add(s, m('ans') + .45, chime(1760, 1.2), .14)
# 13. the link, the end card
add(s, m('link') - .35, whoosh(.6, 300, 2600), .3); add(s, m('link') - .1, tap(), .35)
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
part(0, m('S3'), [Dm, Bb], pads=.13, low=.2, bright=.5)
part(m('S3'), m('S5'), [Dm, Bb, Gm, A], pads=.14, low=.2, dombra=.06, bright=.55)
part(m('S5'), m('S7'), [F, C, Dm, Bb], pads=.15, low=.22, dombra=.07, bright=.65)
part(m('S7'), m('S9'), [Dm, Bb, Gm, A], pads=.15, low=.24, dombra=.07, toms=.1, bright=.6)
part(m('S9'), m('y1989'), [Gm, A], pads=.13, low=.2, bright=.45)
part(m('y1989'), m('S12'), [F, C, Dm, Bb], pads=.17, low=.24, dombra=.08, toms=.12, bright=.8)
part(m('S12'), DUR, [F, C, Dm, Bb], pads=.2, low=.26, dombra=.09, toms=.14, bright=.9)
write(f'music_{LANG}.wav', norm(mu * np.minimum(1, np.arange(len(mu)) / (SR * .6))) * .9)
print(LANG, 'sfx + music', DUR, 's')
