"""Sabalak reel: synthesised SFX (sfx.wav) and a dombra music bed (music.wav): quiet & mysterious, heroic from 23.4 s.
Times are video seconds (same as scene.html; the voice starts at 0.3 s)."""
import wave, numpy as np
SR = 48000; DUR = 36.6
rng = np.random.default_rng(7)
def tt(L): return np.arange(int(SR * L)) / SR
def norm(x): return x / (np.abs(x).max() + 1e-9)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
N = lambda n: 440 * 2 ** ((n - 69) / 12)

def pluck(f, L=1.6, bright=1.0, pos=.18):  # dombra-like twang (additive)
    t = tt(L); x = sum(np.sin(np.pi * h * pos) / h ** (1.3 - .3 * bright) * np.sin(2 * np.pi * f * h * t * (1 + .0007 * h)) * np.exp(-t * (1.6 + 1.1 * h)) for h in range(1, 14))
    return norm(x * np.minimum(1, t / .003))
def strum(notes, L=1.4, gap=.012, bright=1.0):
    out = np.zeros(int(SR * (L + gap * len(notes))))
    for i, n in enumerate(notes): add(out, i * gap, pluck(N(n), L, bright), 1)
    return norm(out)
def whoosh(L=.8):
    n = int(SR * L); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 200, 400 + 4000 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 1.8
def boom(f0=50, L=1.8):
    t = tt(L); f = f0 * (1 + 2.5 * np.exp(-t * 18)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3)
    return norm(s + .4 * band(rng.standard_normal(len(t)), 30, 900) * np.exp(-t * 12))
def drum(f0=90, L=.5, dec=9):
    t = tt(L); f = f0 * (1 + np.exp(-t * 35)); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dec) + .25 * band(rng.standard_normal(len(t)), 80, 2500) * np.exp(-t * 40))
def chime(f=1320, L=1.8):
    t = tt(L); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.0 + 1.5 * h)) / h for h in (1, 2.76, 5.4)))
def clop():
    t = tt(.08); return norm(band(rng.standard_normal(len(t)), 250, 1800) * np.exp(-t * 70))
def baa(f0=330, L=.7):  # sheep bleat: vibrato saw through two formants
    t = tt(L); f = f0 * (1 + .06 * np.sin(2 * np.pi * 22 * t)) * (1 - .1 * t)
    ph = np.cumsum(f) / SR; saw = 2 * (ph % 1) - 1
    v = band(saw, 500, 1100) + .6 * band(saw, 1500, 2600)
    return norm(v * np.minimum(1, t / .05) * np.minimum(1, (L - t) / .25))
def shout(L=1.0, f0=170):  # wordless distant cry «аaa»
    t = tt(L); f = f0 * (1 + .08 * np.minimum(1, t * 4)) * (1 + .01 * np.sin(2 * np.pi * 6 * t)); ph = np.cumsum(f) / SR; saw = 2 * (ph % 1) - 1
    v = band(saw, 650, 1000) + .7 * band(saw, 1100, 1500) + .2 * band(saw, 2400, 3000)
    return norm(v * np.minimum(1, t / .08) * np.minimum(1, (L - t) / .4))
def echo(x, d=.32, n=5, k=.5):
    out = np.zeros(len(x) + int(SR * d * n))
    for i in range(n): add(out, i * d, band(x, 300, 3000 - i * 400), k ** i)
    return out

s = np.zeros(int(SR * DUR))
# wind bed (very quiet), steppe scenes only
wn = band(rng.standard_normal(len(s)), 150, 900); lfo = .6 + .4 * np.sin(2 * np.pi * np.arange(len(s)) / SR * .23)
mask = np.zeros(len(s)); t_all = np.arange(len(s)) / SR
mask += np.clip(np.minimum(t_all / .5, (5.7 - t_all) / .4), 0, 1); mask += .6 * np.clip(np.minimum((t_all - 10.4) / .3, (14.8 - t_all) / .3), 0, 1)
mask += np.clip(np.minimum((t_all - 32.0) / .6, (36.4 - t_all) / .5), 0, 1)
s += norm(wn) * lfo * mask * .12
# sheep
for x, f in [(1.3, 330), (3.6, 290), (12.6, 360), (33.4, 310)]: add(s, x, baa(f), .3)
# 2: single dombra note
add(s, 5.6, pluck(N(50), 3.0, 1.2), .7)
# 3: soft chime
add(s, 10.45, chime(1320), .4); add(s, 10.6, chime(1760), .25)
# 4: hoofbeats, both riders, accelerating -> impact
tb = 14.8
while tb < 18.4: add(s, tb, clop(), .3); add(s, tb + .07, clop(), .22); tb += .26 - .06 * (tb - 14.8) / 3.6
add(s, 18.25, whoosh(.4), .5); add(s, 18.4, boom(46, 2.0), 1.0); add(s, 18.42, band(rng.standard_normal(int(SR * .5)), 1500, 9000) * np.exp(-tt(.5) * 9), .5)
add(s, 18.45, chime(2200, 1.2), .3)
for k in range(8): add(s, 18.9 + k * .2, clop(), .2 * (1 - k / 8))
add(s, 19.25, drum(70, .5, 8), .5)   # Sharysh hits the ground
# 5: distant wordless cry with echoes
add(s, 20.6, echo(shout(1.1, 165)), .35); add(s, 22.5, echo(shout(1.3, 180)), .4)
# 6: ceremonial dabyl drums
for k in range(10): add(s, 23.5 + k * .4, drum(85, .6, 7), .55 if k % 2 == 0 else .35)
add(s, 27.4, whoosh(.6), .4)
# 7: flash + powerful dombra chord
add(s, 28.0, boom(44, 2.4), .8); add(s, 28.02, strum([38, 45, 50, 57], 3.0, .02, 1.3), .9); add(s, 29.8, strum([38, 45, 50], 2.0, .015), .5)
# end
add(s, 31.75, whoosh(.7), .3); add(s, 33.6, chime(1568, 1.4), .35)
write('sfx.wav', norm(s) * .9)

# ---- dombra music bed: D minor, sparse & mysterious -> heroic strumming from 23.4 s ----
m = np.zeros(int(SR * DUR))
t = tt(DUR); drone = (np.sin(2 * np.pi * N(38) * t) + .5 * np.sin(2 * np.pi * N(45) * t)) * (.5 + .5 * np.sin(2 * np.pi * .1 * t))
m += norm(band(drone, 40, 400)) * .12 * np.clip(np.minimum(t / 2, (DUR - t) / 1.5), 0, 1)
# part A: slow mysterious plucks (0 - 23.4)
pat = [50, 57, 53, 57, 52, 57, 53, 48]; bt = 60 / 84
k = 0; x = .4
while x < 23.2:
    n = pat[k % 8]; g = .35 + .25 * (x / 23.4)
    add(m, x, pluck(N(n), 1.8), g * (1 if k % 2 == 0 else .7))
    if x > 10.4 and k % 2 == 1: add(m, x + bt / 2, pluck(N(n + 12), 1.0, 1.3), g * .35)
    if x > 14.8 and k % 4 == 0: add(m, x, drum(60, .5, 7), .3)
    x += bt; k += 1
# part B: heroic kui-like strumming 120 bpm (23.4 - end)
prog = [[38, 45, 50], [38, 45, 50], [36, 43, 48], [41, 48, 53]]; bt = .5; x = 23.4; k = 0
while x < DUR - .8:
    ch = prog[(k // 4) % 4]; endg = min(1, (DUR - x) / 3) if x > 32 else 1
    add(m, x, strum(ch, .8, .01, 1.2), .55 * endg); add(m, x + bt * .5, strum(ch[::-1], .5, .008), .3 * endg); add(m, x + bt * .75, pluck(N(ch[2] + 12), .4, 1.3), .25 * endg)
    if k % 2 == 0: add(m, x, drum(62, .6, 6), .45 * endg)
    x += bt; k += 1
fade = np.ones(len(m)); n1 = int(SR * 2.0); fade[-n1:] = np.linspace(1, 0, n1)
write('music.wav', norm(m * fade) * .9)
print('ok')
