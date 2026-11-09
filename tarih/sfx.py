"""Tarih reel: synthesise SFX (sfx.wav) and an epic music bed that speeds up toward the finale (music.wav).
Times are video seconds (same as scene.html; the voice starts at 0.3 s)."""
import wave, numpy as np
SR = 48000; DUR = 60.2
rng = np.random.default_rng(5)
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

def whoosh(L=.8):
    n = int(SR * L); x = rng.standard_normal(n); u = np.arange(n) / n; y = np.zeros(n)
    for k in range(0, n, 1024): y[k:k + 1024] = band(x[k:k + 1024], 200, 400 + 4000 * np.sin(np.pi * u[k]))[:len(y[k:k + 1024])]
    return norm(y) * np.sin(np.pi * u) ** 1.8
def boom(f0=55, L=1.6):
    t = tt(L); f = f0 * (1 + 2.5 * np.exp(-t * 18)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3)
    return norm(s + .4 * band(rng.standard_normal(len(t)), 30, 900) * np.exp(-t * 12))
def drum(f0=90, L=.5, dec=9):
    t = tt(L); f = f0 * (1 + np.exp(-t * 35)); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dec) + .25 * band(rng.standard_normal(len(t)), 80, 2500) * np.exp(-t * 40))
def chime(f=1320, L=1.6):
    t = tt(L); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + 1.5 * h)) / h for h in (1, 2.76, 5.4)))
def creak():
    t = tt(.25); f = 380 + 140 * np.sin(2 * np.pi * 7 * t); s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .5 + np.sin(2 * np.pi * np.cumsum(f * 2) / SR)
    return norm(band(s, 300, 2500) * np.sin(np.pi * t / .25))
def clop():
    t = tt(.08); return norm(band(rng.standard_normal(len(t)), 300, 2200) * np.exp(-t * 70))
def pop():
    t = tt(.2); f = 500 + 900 * np.exp(-t * 30); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18))
def brass(notes, L, att=.06):
    t = tt(L); env = np.minimum(1, t / att) * np.minimum(1, (L - t) / .4)
    x = sum(sum(np.sin(2 * np.pi * N(n) * h * t + h) / h ** 1.1 for h in range(1, 8)) for n in notes)
    return norm(band(x, 80, 5000)) * env

s = np.zeros(int(SR * DUR))
# 1: rewind (pitch falling tape noise + flutter), impact on «Кеттік»
L = 2.5; t = tt(L); f = 1800 * np.exp(-t * .5) * (1 + .3 * np.sin(2 * np.pi * 9 * t))
rw = band(rng.standard_normal(len(t)), 500, 6000) * .5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .4
add(s, .1, norm(rw) * np.minimum(1, t / .2) * np.minimum(1, (L - t) / .2), .35)
add(s, 3.1, boom(48, 2), .9)
# scene changes: slide whooshes
for x in [3.95, 6.9, 11.35, 23.45, 27.8, 31.55, 34.75, 38.75, 44.15, 49.3, 54.5]: add(s, x - .25, whoosh(.7), .35)
add(s, 18.1, whoosh(1.0), .5)                       # zoom out
# 2: chariot creak + hooves
for k in range(12): add(s, 4.0 + k * .24, creak(), .18)
for k in range(24): add(s, 4.0 + k * .12 + (k % 2) * .03, clop(), .28)
# 3: gold
add(s, 10.3, chime(1568), .5); add(s, 10.45, chime(2093), .35)
# 4: whoosh pops for Usun / Kangju
add(s, 12.1, whoosh(.5), .55); add(s, 13.8, whoosh(.5), .55)
# 5: gallop
for k in range(46): b = 15.5 + k * .062; add(s, b + (k % 4 == 3) * .02, clop(), .22 * (1 if k % 4 != 1 else .6))
# 6: big drum on 552
add(s, 18.4, boom(42, 2.2), .9); add(s, 20.3, drum(70, .8, 5), .4)
# 7: soft chimes for cities
for i in range(7): add(s, 24.9 + i * .25, chime(1046 * 2 ** (i / 7), 1.0), .2)
add(s, 25.6, chime(784, 2), .3)
# 8: war drums
for k in range(16): add(s, 28.2 + k * .16, drum(80 + (k % 2) * 30, .4, 10), .5 if k % 4 == 0 else .3)
add(s, 30.7, boom(50, 1.4), .5)
# 9: gold
add(s, 32.4, chime(1568), .45); add(s, 32.55, chime(2349), .3)
# 10: solemn chord
add(s, 36.6, brass([50, 57, 62, 66], 2.4, .1), .5)
# 11: alarming drums
for k in range(12): add(s, 39.3 + k * .18, drum(65, .35, 12), .45)
add(s, 41.7, whoosh(1.8), .35)
# 12: factory hum
L = 4.6; t = tt(L); hum = (np.sin(2 * np.pi * 50 * t) + .5 * np.sin(2 * np.pi * 100 * t) + .3 * band(rng.standard_normal(len(t)), 60, 400)) * np.minimum(1, t / .6) * np.minimum(1, (L - t) / .8)
add(s, 44.4, norm(hum) * (1 + .3 * np.sign(np.sin(2 * np.pi * 2 * t))), .22)
for i in range(4): add(s, 47.2 + i * .3, pop(), .3)
# 13: fanfare
add(s, 51.4, brass([62, 66, 69], .35), .45); add(s, 51.75, brass([62, 66, 69], .35), .45); add(s, 52.1, brass([67, 71, 74], 2.2), .55)
# end: card + CTA
for i in range(13): add(s, 54.95 + i * .07, pop(), .12)
add(s, 56.3, pop(), .5); add(s, 56.35, chime(1760, 1.0), .3)
write('sfx.wav', norm(s) * .9)

# ---- epic music bed: D minor, toms + low strings + ostinato, tempo 96 -> 136 bpm ----
m = np.zeros(int(SR * DUR))
beats = []; tb = 0.0
while tb < DUR:
    beats.append(tb); bpm = 96 + 40 * (tb / DUR) ** 1.3; tb += 60 / bpm
prog = [[50, 53, 57], [46, 50, 53], [41, 45, 48], [48, 52, 55]]   # Dm Bb F C
for bi, b0 in enumerate(beats):
    bar = bi // 4; ch = prog[bar % 4]; beat = (beats[bi + 1] - b0) if bi + 1 < len(beats) else .5
    inten = .5 + .5 * (b0 / DUR)
    if bi % 4 == 0:   # string pad for the whole bar
        L = beat * 4 + .3; t = tt(L)
        pad = sum(np.sin(2 * np.pi * N(n) * t + np.sin(2 * np.pi * 5 * t) * .02 * h) * (1 / h) for n in ch for h in (1, 2, 3))
        add(m, b0, norm(band(pad, 60, 2500)) * np.minimum(1, t / .4) * np.minimum(1, (L - t) / .3), .22)
        add(m, b0, np.sin(2 * np.pi * N(ch[0] - 12) * t) * np.minimum(1, t / .05) * np.exp(-t * .8), .3)
    # ostinato (eighth notes)
    for e in range(2):
        L = beat / 2; t = tt(L); n = [ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12][(bi * 2 + e) % 4]
        add(m, b0 + e * L, (np.sin(2 * np.pi * N(n) * t) + .3 * np.sin(2 * np.pi * N(n) * 2 * t)) * np.exp(-t * 9), .12 * inten)
    # toms: boom on 1 and 3, extra hits as it builds
    if bi % 2 == 0: add(m, b0, drum(60, .6, 6), .45)
    if b0 > 20 and bi % 4 == 3: add(m, b0 + beat / 2, drum(95, .3, 12), .3)
    if b0 > 38: add(m, b0 + beat / 2, drum(120, .2, 18), .18)
    th = tt(.04); add(m, b0 + beat / 2, band(rng.standard_normal(len(th)), 6000, 12000) * np.exp(-th * 90), .05 * inten)
fade = np.ones(len(m)); n0 = int(SR * 1.0); fade[:n0] = np.linspace(0, 1, n0); n1 = int(SR * 2.0); fade[-n1:] = np.linspace(1, 0, n1)
write('music.wav', norm(m * fade) * .9)
print('ok', len(beats))
