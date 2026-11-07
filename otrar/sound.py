"""Synthesised SFX + music bed for the Otrar reel. Writes audio/sfx.wav and audio/music.wav (48 kHz)."""
import numpy as np, json, os, wave

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, "timeline.json")))
TOTAL = TL["total"]
N = int(TOTAL * SR)
rng = np.random.default_rng(5)

def t_arr(d):
    return np.arange(int(d * SR)) / SR

def env(n, a=0.005, r=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e

def put(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain

def lp(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y

def lp_fast(x, k):
    """moving-average low-pass (k samples)"""
    c = np.cumsum(np.insert(x, 0, 0))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.zeros(k - 1)])

def noise(d):
    return rng.standard_normal(int(d * SR))

def ks(freq, d, damp=0.996, bright=0.5):
    """Karplus-Strong plucked string (oud/dombra-like)."""
    n = int(d * SR)
    p = int(SR / freq)
    buf = rng.uniform(-1, 1, p)
    buf = lp_fast(buf, 2) * bright + buf * (1 - bright)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = damp * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out

def bell(freq, d=1.2):
    t = t_arr(d)
    x = sum(a * np.sin(2 * np.pi * freq * m * t) for m, a in ((1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)))
    return x * env(len(t), 0.002, 0.35)

def clink(freq):
    t = t_arr(0.35)
    x = sum(np.sin(2 * np.pi * freq * m * t) * a for m, a in ((1, 1), (1.53, 0.6), (2.9, 0.4), (4.2, 0.3)))
    return x * env(len(t), 0.001, 0.06)

def drum(freq=60, d=1.2, punch=1.0):
    t = t_arr(d)
    f = freq * (1 + 1.5 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env(len(t), 0.002, 0.35)
    x += lp_fast(noise(d), 6) * env(len(t), 0.001, 0.03) * 0.6 * punch
    return x

def frame_drum(d=0.5):
    t = t_arr(d)
    x = np.sin(2 * np.pi * 110 * t * (1 + 0.3 * np.exp(-t * 40))) * env(len(t), 0.002, 0.12)
    x += lp_fast(noise(d), 3) * env(len(t), 0.001, 0.02) * 0.4
    return x

def creak(d=1.4):
    t = t_arr(d)
    f0 = 140 + 60 * np.sin(2 * np.pi * 0.9 * t) + 30 * np.sin(2 * np.pi * 3.1 * t)
    ph = 2 * np.pi * np.cumsum(f0) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    am = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 23 * t))  # stick-slip
    x = lp_fast(saw * am, 4) * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.2)
    return x * 0.5

def step(d=0.12, bright=3):
    x = lp_fast(noise(d), bright) * env(int(d * SR), 0.001, 0.025)
    return x

def breath(d=0.55, inhale=True):
    t = t_arr(d)
    x = noise(d)
    x = x - lp_fast(x, 30)  # high-pass-ish
    x = lp_fast(x, 3)
    shape = np.sin(np.pi * t / d) ** 1.5
    return x * shape * (0.5 if inhale else 0.8)

def whoosh(d=0.6):
    t = t_arr(d)
    x = lp_fast(noise(d), 12) * np.sin(np.pi * t / d) ** 2
    return x

def thud():
    return drum(45, 0.9, 1.6) * 1.2

def hoof_gallop(d, rate=2.6):
    out = np.zeros(int(d * SR))
    k = 0.0
    while k < d:
        for off in (0, 0.07, 0.14):
            put(out, drum(180, 0.12, 2.0) * 0.5, k + off)
            put(out, step(0.08, 2) * 0.6, k + off)
        k += 1 / rate
    return out

def sh(name):
    return TL["shots"][name]

sfx = np.zeros(N)
# s1: camel bells, soft wind, camel steps
a, b = sh("s1")
for k in range(9):
    put(sfx, bell(rng.choice([880, 990, 1175, 1320])) * 0.18, a + 0.2 + k * 0.45 + rng.uniform(0, 0.1))
for k in range(16):
    put(sfx, step(0.15, 8) * 0.25, a + k * 0.27)
put(sfx, lp_fast(noise(b - a), 60) * 0.04 * np.ones(int((b - a) * SR)), a)
# s2: coins clinking
a, b = sh("s2")
for k in range(14):
    put(sfx, clink(rng.uniform(2400, 4200)) * 0.22, a + 0.15 + k * 0.22 + rng.uniform(0, 0.08))
for k in range(5):
    put(sfx, bell(1046 + 100 * k) * 0.08, a + 0.3 + k * 0.6)
# s3: gate creak
a, b = sh("s3")
put(sfx, creak(1.6) * 0.5, a + 0.2)
for k in range(10):
    put(sfx, step(0.1, 5) * 0.15, a + 0.4 + k * 0.22)
# s4: hard drum hit at "шпионами" (VO 12.46 + offset), guards' steps, spear clank
off = TL["vo_offset"]
put(sfx, drum(55, 1.6, 1.4) * 0.9, 12.40 + off)
put(sfx, drum(80, 1.0, 1.0) * 0.4, 12.40 + off + 0.02)
a, b = sh("s4")
for k in range(18):
    put(sfx, step(0.1, 4) * 0.18, a + 0.3 + k * 0.13)
for k in range(4):
    put(sfx, clink(1800 + 300 * k) * 0.08, a + 1.0 + k * 0.4)
# s5: running steps + heavy breathing
a, b = sh("s5")
k = a + 0.1
while k < b - 0.1:
    put(sfx, step(0.1, 3) * 0.35, k)
    k += 0.19
k = a + 0.0
inh = True
while k < b - 0.3:
    put(sfx, breath(0.42, inh) * 0.18, k)
    k += 0.45
    inh = not inh
# s6: hoofbeats fading, then silence in the tent
a, b = sh("s6")
g = hoof_gallop(1.2)
g *= np.linspace(1, 0, len(g))
put(sfx, g * 0.35, a)
put(sfx, lp_fast(noise(b - a - 1.0), 40) * 0.02, a + 1.0)  # fire crackle bed
for k in range(10):
    put(sfx, step(0.03, 1) * 0.12, a + 1.1 + rng.uniform(0, b - a - 1.2))
# s7: gallop + scroll fall thud
a, b = sh("s7")
put(sfx, hoof_gallop((b - a) * 0.6) * 0.3, a)
T7 = b - a
put(sfx, thud() * 0.8, a + T7 * 0.72 + 0.45)
put(sfx, whoosh(0.4) * 0.15, a + T7 * 0.72)
# s8: war drums & horn
a, b = sh("s8")
for k in range(int((b - a) / 0.5)):
    put(sfx, drum(50, 1.0, 1.0) * (0.45 if k % 2 == 0 else 0.25), a + k * 0.5)
put(sfx, whoosh(1.2) * 0.2, a)

# ------------------------------------------------------------- music
mus = np.zeros(N)
# hijaz on D: D Eb F# G A Bb C D
D = 146.83
scale = [1, 16 / 15, 5 / 4, 4 / 3, 3 / 2, 8 / 5, 9 / 5, 2]
# drone (calm part 0..10.8, continues quieter)
t = np.arange(N) / SR
drone = (np.sin(2 * np.pi * D / 2 * t) + 0.5 * np.sin(2 * np.pi * D * 3 / 4 * t) +
         0.3 * np.sin(2 * np.pi * D * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * t))
cut1 = TL["shots"]["s4"][0]
cut2 = TL["shots"]["s8"][0]
dr_env = np.where(t < cut1, 1.0, np.where(t < cut2, 0.7, 0.9))
mus += drone * 0.10 * dr_env
# oud phrases in the calm part
melody = [0, 1, 2, 1, 0, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 4]
k = 0.0
i = 0
while k < cut1 - 0.5:
    f = D * scale[melody[i % len(melody)]]
    put(mus, ks(f, 1.2, 0.995) * 0.35, k)
    if i % 4 == 0:
        put(mus, ks(D / 2, 1.5, 0.996) * 0.25, k)
    k += 0.34 if i % 3 else 0.68
    i += 1
for k in np.arange(0.0, cut1, 0.68):
    put(mus, frame_drum() * 0.25, k)
    put(mus, frame_drum(0.3) * 0.12, k + 0.34)
# tense part: low pulse + ostinato
for k in np.arange(cut1, cut2, 0.42):
    put(mus, drum(42, 0.6, 0.3) * 0.35, k)
for j, k in enumerate(np.arange(cut1, cut2, 0.21)):
    f = D * scale[[0, 1, 0, 2][j % 4]]
    put(mus, ks(f, 0.4, 0.99, 0.8) * 0.18, k)
tense = np.sin(2 * np.pi * D / 4 * t) * ((t > cut1) & (t < cut2)) * 0.12
mus += tense
# epic end: brass-like chord swells + big drums
ep = (t >= cut2)
swell = np.clip((t - cut2) / 1.5, 0, 1) * ep
chord = sum(np.sign(np.sin(2 * np.pi * D * r * t)) * a for r, a in ((0.5, 0.5), (1, 0.4), (1.5, 0.3), (2, 0.2)))
chord = lp_fast(chord, 20)
mus += chord * swell * 0.10
for k in np.arange(cut2, TOTAL, 1.0):
    put(mus, drum(38, 1.6, 1.0) * 0.6, k)
    put(mus, drum(70, 0.6, 1.2) * 0.3, k + 0.5)
# fade out end
fade = np.clip((TOTAL - t) / 1.2, 0, 1)
mus *= fade
sfx *= fade

def save(name, x):
    x = x / max(1e-6, np.max(np.abs(x))) * 0.9
    y = (x * 32767).astype(np.int16)
    with wave.open(os.path.join(HERE, "audio", name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())

save("sfx.wav", sfx)
save("music.wav", mus)
print("ok")
