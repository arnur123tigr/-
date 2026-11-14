"""Sound for the Turkic Khaganate reel: synth effects (sfx_<lang>.wav) and a music bed (music_<lang>.wav).
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


def crossings(v, t0, t1, gap=.05):
    """Times in [t0, t1] where the year counter v(T) reaches a new whole year (at most one tick per `gap` seconds)."""
    out = []; last = int(np.floor(v(t0) + 1e-6)); T = t0
    while T <= t1:
        k = int(np.floor(v(T) + 1e-6))
        if k > last:
            last = k
            if not out or T - out[-1] >= gap: out.append(T)
        T += .002
    return out


s = np.zeros(int(SR * DUR))
m = lambda k: M[k]
# cuts between scenes: a short breath of air into a soft low thud
for k in ('S2', 'S3', 'S4', 'S5', 'S6'): add(s, m(k) - .22, whoosh(.5, 300, 3200), .32); add(s, m(k), drum(70, .4, 10), .3)

# 1. one dot on the Altai, the pull-back, the wave of light
add(s, .16, boom(48, 1.4), .6); add(s, .18, chime(1319, 1.2), .2); add(s, .42, pop(), .35)
add(s, .25, riser(m('Pull') - .2, 160, 900), .3)
add(s, m('Pull'), whoosh(1.5, 220, 2400), .6); add(s, m('Pull'), sub(90, 38, 1.3), .45)
add(s, m('Wave'), swell(m('WaveW') - m('Wave')), .3)
add(s, m('Title2'), drum(80, .5, 8), .5)
add(s, m('huang'), pop(), .3); add(s, m('black'), pop(), .3)
add(s, m('WaveW'), boom(60, 1.0), .5); add(s, m('WaveW'), chime(988, 1.0), .15)

# 2. small Turks, big Rouran
add(s, m('S2'), drone(m('S3') - m('S2') + .25, 55), .3)
add(s, m('S2') + .25, pop(), .3); add(s, m('S2') + .5, pop(), .3)
add(s, m('rouran') - .1, boom(45, 1.2), .45); add(s, m('rouran') + .05, drum(60, .5, 8), .3)

# 3. 552: the counter, the army gathering, the arrow, the blow, the khaganate
stop3 = m('y552') + .8
t3 = crossings(lambda T: 538 + 14 * ease_out(seg(T, m('S3'), stop3)), m('S3'), stop3 + .01)
for t in t3[:-1]: add(s, t, tick(), .22)
add(s, t3[-1] if t3 else stop3, tick(2400), .4); add(s, stop3, pop(), .35); add(s, stop3, chime(1175, .8), .14)
add(s, m('bumin'), pop(), .3)
add(s, m('bumin'), riser(m('Launch') - m('bumin'), 150, 1200), .32)
add(s, m('Launch'), rush(m('Hit') - m('Launch'), 350, 5200), .7)
add(s, m('Hit'), boom(50, 1.8), 1.0); add(s, m('Hit'), crack(), .8); add(s, m('Hit'), sub(70, 30, 1.5), .55); add(s, m('Hit') + .05, debris(1.4), .45)
add(s, m('Found'), swell(1.5, (50, 57, 62, 65)), .38); add(s, m('Found'), shimmer(1.4), .16)
add(s, m('Found') + .65, pop(), .3); add(s, m('Found') + 1.55, chime(1175, 1.0), .18)

# 4. east to the Huang He, west to the Black Sea
v4 = lambda T: 552 + 3 * ease_io(seg(T, m('S4') + .2, m('huang2') + .3)) + 15 * ease_io(seg(T, m('west') + .2, m('black2') + .6))
for t in crossings(v4, m('S4'), m('black2') + .62): add(s, t, tick(), .2)
add(s, m('S4') + .1, swell(m('huang2') + .45 - m('S4') - .1), .3)
add(s, m('huang2'), pop(), .3); add(s, m('huang2'), chime(1568, .8), .18)
add(s, m('istemi'), pop(), .3)
add(s, m('west') + .1, riser(m('black2') + .55 - m('west') - .1, 150, 1300), .27)
add(s, m('zhet'), pop(), .3)
add(s, m('zhet') - .25, rush(m('black2') + .55 - m('zhet') + .25, 260, 3600), .42)
add(s, m('black2') + .35, pop(), .3)
add(s, m('black2') + .55, boom(55, 1.4), .7); add(s, m('black2') + .55, chime(1319, 1.2), .2)

# 5. the Silk Road, the embassy of 568
add(s, m('S5') + .05, shimmer(1.3), .22)
for i, f in enumerate((698, 880, 1047)): add(s, m('S5') + .08 + i * .09, chime(f, .9), .14)
L5 = m('y568') - .2 - m('S5') - .05; u5 = np.arange(int(SR * L5)) / (SR * L5)
add(s, m('S5') + .05, sweep(L5, lambda v: 900 + 1500 * v, .5) * np.sin(np.pi * u5) ** .7, .06)     # the line running west
add(s, m('turks'), coin(), .42)
add(s, m('y568') - .18, drum(80, .5, 8), .5); add(s, m('y568') - .18, pop(), .3)
add(s, m('Dot'), pop(), .4); add(s, m('Dot') + .1, gallop(m('Arrive') - m('Dot') - .1), .3); add(s, m('Dot'), whoosh(m('Arrive') - m('Dot'), 400, 1800), .07)
add(s, max(m('emb') - .1, m('Dot') + .1), pop(), .25)
add(s, m('Arrive'), chime(1047, 1.4), .26); add(s, m('Arrive') + .06, chime(1568, 1.4), .2); add(s, m('Arrive') + .05, coin(), .42); add(s, m('Arrive'), boom(70, .8), .3)

# 6. 603: the split
stop6 = m('y603') + .6
t6 = crossings(lambda T: 568 + 35 * ease_out(seg(T, m('S6'), stop6)), m('S6'), stop6 + .01, .055)
for t in t6[:-1]: add(s, t, tick(), .18)
add(s, stop6, tick(2200), .4); add(s, stop6, drum(65, .5, 8), .4)
r0 = max(m('S6') + .5, m('Crack') - 1.5); add(s, r0, riser(m('Crack') - r0, 200, 1700), .42)
add(s, m('Crack'), crack(), 1.0); add(s, m('Crack'), boom(42, 2.0, 2.4), .9); add(s, m('Crack') + .03, rumble(1.6), .5); add(s, m('Crack') + .08, debris(1.2), .45)
add(s, m('Crack') + .12, whoosh(.95, 240, 2200), .42)
add(s, m('east'), pop(), .3); add(s, m('westk'), pop(), .3)

# 7. what to remember, the comment, the link
add(s, m('S7'), sub(80, 35, 1.2), .4); add(s, m('S7'), whoosh(.7, 200, 1200), .25)
add(s, m('nm') - .05, pop(), .3)
add(s, m('d1') - .03, drum(75, .6, 7), .7); add(s, m('d1') - .03, tick(2400), .3)
add(s, m('d2') - .03, drum(60, .7, 6), .8); add(s, m('d2') - .03, tick(2000), .3)
add(s, m('cta') - .18, whoosh(.45, 300, 2600), .3)
add(s, m('key') + .02, key(), .5); add(s, m('key') + .3, key(), .5)
add(s, m('key') + .95, pop(), .5); add(s, m('key') + .97, chime(1760, .9), .22)
add(s, m('link') - .12, whoosh(.45, 300, 2600), .3)
add(s, m('bio') - .25, pop(), .3); add(s, m('bio') - .22, chime(1319, .9), .2)
add(s, m('desc') - .3, pop(), .25)
# the end card (navy, the logo): air, a soft low landing, three notes of the home chord
e0 = m('last') - .1
add(s, e0 - .2, whoosh(.6, 240, 2200), .3); add(s, e0 + .05, boom(52, 1.6, 2.6), .45); add(s, e0 + .05, sub(72, 36, 1.2), .3)
for i, f in enumerate((587, 880, 1175)): add(s, e0 + .3 + i * .07, chime(f, 1.5), .16)
write(f'sfx_{LANG}.wav', norm(s) * .9)

# ------------------------------------------------------------------ music bed: D minor, about 116 bpm; every part starts on a cut
Dm, Bb, F, C, Gm, A = [50, 53, 57], [46, 50, 53], [41, 45, 48], [48, 52, 55], [43, 46, 50], [45, 49, 52]
mu = np.zeros(int(SR * DUR))
def pad(notes, L, g, bright=1.0):
    t = tt(L + .35); x = sum(np.sin(2 * np.pi * N(n) * h * t + np.sin(2 * np.pi * 5 * t) * .02 * h + n) / h ** 1.3 for n in notes for h in (1, 2, 3, 4))
    return norm(band(x, 60, 2400 * bright)) * np.minimum(1, t / .35) * np.minimum(1, (L + .35 - t) / .35) * g
def bass(n, L, g):
    t = tt(L); f = N(n - 12 if n >= 48 else n); return (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t)) * np.minimum(1, t / .02) * np.exp(-t * 1.3) * np.minimum(1, (L - t) / .05) * g
def pluck(n, L, g, dec=9):
    t = tt(L); f = N(n); return (np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .15 * np.sin(6 * np.pi * f * t)) * np.exp(-t * dec) * np.minimum(1, t / .004) * g
def hat(g):
    t = tt(.04); return band(rng.standard_normal(len(t)), 6000, 12000) * np.exp(-t * 90) * g
def part(t0, t1, prog, bpm=116, pads=.22, low=.3, ost=0., arp=0., toms=0., hats=0., build=0., bright=1.0, skip=0):
    """One part of the bed between two cuts: whole beats fitted to its length; chords change every 4 beats."""
    n = max(2, int(round((t1 - t0) * bpm / 60))); bt = (t1 - t0) / n
    for i in range(skip, n):
        b0 = t0 + i * bt; ch = prog[(i // 4) % len(prog)]; k = 1 + build * (i / n)           # k: how much the part has built up
        if i % 4 == 0 or i == skip:
            L = min(4 - i % 4, n - i) * bt
            if pads: add(mu, b0, pad(ch, L, pads * (.8 + .2 * k), bright))
            if low: add(mu, b0, bass(ch[0], L, low))
        for e in range(2):                                    # eighth notes
            if ost: add(mu, b0 + e * bt / 2, pluck([ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12][(i * 2 + e) % 4], bt / 2, ost * k))
            if arp:
                for q in range(2): add(mu, b0 + (e + q / 2) * bt / 2, pluck([ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1], ch[0] + 12, ch[2]][(i * 4 + e * 2 + q) % 8] + 24, bt / 2, arp, 12))
        if toms:
            if i % 2 == 0: add(mu, b0, drum(60, .6, 6), toms * k)
            if build and i >= n - 2:
                for q in range(4): add(mu, b0 + q * bt / 4, drum(95 + 10 * q, .25, 14), toms * .5 * (i - n + 2 + q / 4) / 2 + .1)
            elif i % 4 == 3: add(mu, b0 + bt / 2, drum(95, .3, 12), toms * .6)
        if hats: add(mu, b0 + bt / 2, hat(hats * k))
part(0, m('S2'), [Dm, Bb], pads=.2, low=.26, ost=.05, toms=.22, hats=.02, build=.6)                         # 1  the hook
part(m('S2'), m('S3'), [Dm, Gm], pads=.16, low=.3, toms=.18, bright=.6)                                    # 2  dark and still
part(m('S3'), m('Hit'), [Dm, A], pads=.2, low=.3, ost=.1, toms=.34, hats=.03, build=1.0)                   # 3  builds to the blow
part(m('Hit'), m('S4'), [Bb, F], pads=.24, low=.34, ost=.1, toms=.3, hats=.03, skip=1)                      # ... and opens up
part(m('S4'), m('S5'), [Dm, Bb, F, C], pads=.22, low=.32, ost=.13, toms=.42, hats=.04, build=.5)           # 4  the lands grow
part(m('S5'), m('S6'), [F, C, Dm, Bb], pads=.18, low=.24, arp=.075, hats=.035, bright=1.3)                 # 5  the Silk Road: lighter, a running figure
part(m('S6'), m('Crack'), [Gm, A], pads=.2, low=.3, ost=.1, toms=.34, hats=.03, build=1.0)                 # 6  tension ...
part(m('Crack'), m('S7'), [Dm], pads=.15, low=.34, toms=.2, bright=.55, skip=1)                             # ... and the fall
part(m('S7'), DUR, [Dm, Bb, F, C], pads=.2, low=.28, ost=.09, toms=.3, hats=.03)                            # 7  steady to the end
fade = np.ones(len(mu)); n0 = int(SR * .6); fade[:n0] = np.linspace(.3, 1, n0); n1 = int(SR * 1.8); fade[-n1:] = np.linspace(1, 0, n1)
write(f'music_{LANG}.wav', norm(mu * fade) * .9)
print(LANG, 'sfx + music', DUR, 's')
