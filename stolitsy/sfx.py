"""Four capitals reel: synth SFX (sfx_<lang>.wav) + light music bed (music_<lang>.wav), timed from beats.json.
Usage: python3 sfx.py ru|kk. Video seconds; the voice starts at 0.3 s."""
import wave, numpy as np
import json, sys
LANG = sys.argv[1] if len(sys.argv) > 1 else "ru"
B = json.load(open("beats.json"))[LANG]; OFF = 0.3
SR = 48000; DUR = B["end"]
b = lambda k: B[k] + OFF
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
add(s, 0.15, whoosh(.6), .6)                                  # 1: quick push-in
add(s, b("oren") - .05, pop(), .6); add(s, b("oren"), chime(1568, .8), .25)   # 2: click on the name
add(s, b("y1920"), pop(), .35)
add(s, b("y1925") + .2, whoosh(1.2), .6)                       # 3: flight, then hit
add(s, b("strike"), whoosh(.4), .3)
add(s, b("kazakh"), boom(55, 1.4), .8); add(s, b("kazakh"), drum(110, .4, 10), .5)
add(s, b("y1929") + .1, whoosh(1.0), .55); add(s, b("y1997") + .1, whoosh(1.0), .55)   # 4: two whooshes
add(s, b("alm"), pop(), .3); add(s, b("akm"), pop(), .3)
add(s, b("ent") - .2, whoosh(.7), .35)
for x in B["n"]: add(s, x + OFF - .03, pop(), .7); add(s, x + OFF, chime(1318, .5), .15)   # 5: four clicks
add(s, b("order"), drum(80, .5, 8), .5)
add(s, b("cta") - .3, whoosh(.6), .35)
for i in range(5): add(s, b("cta") + .05 + i * .1, clop(), .25)        # typing
add(s, b("link") - .5, pop(), .4); add(s, b("link") - .45, chime(1760, 1.0), .25)
write(f"sfx_{LANG}.wav", norm(s) * .9)

# ---- epic music bed: D minor, toms + low strings + ostinato, tempo 96 -> 136 bpm ----
m = np.zeros(int(SR * DUR))
beats = []; tb = 0.0
while tb < DUR:
    beats.append(tb); bpm = 112 + 12 * (tb / DUR); tb += 60 / bpm
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
write(f'music_{LANG}.wav', norm(m * fade) * .9)
print('ok', len(beats))
