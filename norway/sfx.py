"""Norway vs Australia reel. Synthesised SFX (sfx.wav) and a dark cinematic music bed (music.wav). Cue times = VO seconds."""
import wave, numpy as np
SR = 48000; OFF = 0.3; DUR = 71
rng = np.random.default_rng(5)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int((t + OFF) * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
N = lambda n: 440 * 2 ** ((n - 69) / 12)
def whoosh(L=1.0):
    n = int(SR * L); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 150, 250 + 3000 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 2
def clink(f=None):
    f = f or 2400 + rng.random() * 1800; t = tt(.35)
    x = sum(np.sin(2 * np.pi * f * h * t + rng.random() * 6) * np.exp(-t * (14 + 6 * h)) / h for h in (1, 1.52, 2.33, 3.1))
    return norm(x + .3 * band(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-t * 80))
def thud():
    t = tt(.5); f = 70 + 120 * np.exp(-t * 25); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9))
def boom():
    t = tt(2.2); f = 42 + 60 * np.exp(-t * 6); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    return norm(x + .4 * band(rng.standard_normal(len(t)), 30, 400) * np.exp(-t * 3))
def tick():
    t = tt(.04); return norm(band(rng.standard_normal(len(t)), 2500, 7000) * np.exp(-t * 120))
def ding(f=1320):
    t = tt(1.4); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (3 + h)) / h for h in (1, 2.01, 3.02)))
def riser(L):
    t = tt(L); f = 200 + 1600 * (t / L) ** 2; return norm(band(rng.standard_normal(len(t)), 300, 5000) * (t / L) ** 2 * .6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / L) ** 3 * .2)

s = np.zeros(int(SR * DUR))
for c in [0, .25]: add(s, c + .75, thud(), .7)                                    # flag spheres land
for i in range(28): add(s, 3.6 + i * .07, clink(), .16)                           # stack grows
for i in range(14): add(s, 7.2 + i * .1, clink(), .14)                            # AU coins fly away
add(s, 7.0, whoosh(1.2), .35)
for c in [9.05, 10.25, 13.85, 17.55, 20.85, 33.35, 37.55, 43.15, 44.65, 52.25]: add(s, c, whoosh(.8), .45)   # cuts
for i in range(6): add(s, 12.6 + i * .06, thud(), .25)                            # pawns pop
for i in range(26): add(s, 15.6 + i * .05, tick(), .25)                           # 78% counter
for i in range(60): add(s, 17.9 + i * .045 + rng.random() * .02, clink(), .12)    # coin rain
add(s, 20.2, band(rng.standard_normal(SR) * np.exp(-tt(1) * 5), 200, 1500), .3)   # safe dial
add(s, 21.4, riser(2.2), .25)                                                     # chart grows
for i in range(20): add(s, 25.5 + i * .05, tick(), .22)                           # $60B count
for c in [27.4, 28.2, 28.8]: add(s, c, thud(), .4)                                 # tiles
add(s, 31.6, boom(), .35)                                                         # Australia, other way
for i in range(24): add(s, 35.5 + i * .05, tick(), .22)                           # $50B count
add(s, 37.8, ding(990), .3)                                                       # $1 coin
for i in range(30): add(s, 40.95 + i * .012, clink(), .07)                        # split into cents
for i in range(3): add(s, 41.95 + i * .13, clink(1800), .35)                      # 3 cents drop
add(s, 43.3, boom(), .5)                                                          # worst part
for c in [44.9, 45.3, 45.7, 46.0, 46.4, 46.8]: add(s, c, thud(), .35)             # plant builds
add(s, 47.4, boom(), .45)                                                         # $0
add(s, 50.6 + .6, clink(1500), .4)                                                # single coin
add(s, 53.5, thud(), .35)                                                          # "="
for i in range(28): add(s, 54.9 + i * .06, clink(), .15)                          # Norway stack
for i in range(14): add(s, 57.1 + i * .1, clink(), .13)                           # coins sail away
add(s, 57.0, whoosh(1.4), .35)
add(s, 59.0, whoosh(1.0), .4); add(s, 61.5, ding(1180), .3); add(s, 63.8, ding(1320), .25); add(s, 68.4, ding(1560), .4)
write('sfx.wav', norm(s) * .9)

# music: dark minimal pulse, D minor, 90 bpm (drone + soft pluck ostinato + sub kick)
bpm = 90; beat = 60 / bpm; bar = 4 * beat; m = np.zeros(int(SR * DUR)); t_bar = tt(bar)
prog = [[50, 53, 57], [46, 50, 53], [43, 46, 50], [45, 49, 52]]   # Dm Bb Gm A
def addm(t, sig, g): i = int(t * SR); j = min(len(m), i + len(sig)); m[i:j] += g * sig[:j - i] if i < j else 0
for b in range(int(DUR / bar) + 1):
    ch = prog[b % 4]; t0 = b * bar
    pad = sum(band(np.sin(2 * np.pi * N(n) * t_bar) + .5 * np.sin(2 * np.pi * N(n) * 1.005 * t_bar) + .25 * np.sign(np.sin(2 * np.pi * N(n - 12) * t_bar)), 60, 1200) for n in ch)
    addm(t0, pad * np.minimum(1, t_bar / .6) * np.minimum(1, (bar - t_bar) / .6), .08)
    addm(t0, np.sin(2 * np.pi * N(ch[0] - 24) * t_bar) * np.minimum(1, t_bar / .1) * np.minimum(1, (bar - t_bar) / .2), .22)
    for k in range(8):
        tp = tt(beat); n = [ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12][k % 4] + (12 if k == 6 else 0)
        addm(t0 + k * beat / 2, (np.sin(2 * np.pi * N(n) * tp) + .3 * np.sin(2 * np.pi * N(n) * 3 * tp)) * np.exp(-tp * 9), .1)
    for k in range(4):
        tk = tt(.4); addm(t0 + k * beat, np.sin(2 * np.pi * np.cumsum(48 * (1 + 2.5 * np.exp(-tk * 28))) / SR) * np.exp(-tk * 8), .3 if k % 2 == 0 else .18)
fade = np.ones(len(m)); n0 = int(SR * 1.0); fade[:n0] = np.linspace(0, 1, n0); n1 = int(SR * 2.5); fade[-n1:] = np.linspace(1, 0, n1)
write('music.wav', norm(m * fade) * .9)
print('ok')
