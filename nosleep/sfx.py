"""Synthesise the script's sound effects (sfx.wav) and a minimal piano + clock-ticking music bed (music.wav)."""
import json, wave, numpy as np
SR = 48000
tl = json.load(open('timeline.json'))
sc = {s['id']: s for s in tl['scenes']}
dur = tl['scenes'][-1]['end']
rng = np.random.default_rng(11)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    if j > i: buf[i:j] += g * sig[:j - i]
def reverb(x, L=2.2, mix=0.3, damp=3.0):
    t = tt(L); ir = rng.standard_normal(len(t)) * np.exp(-t * damp); ir = band(ir, 200, 7000); ir /= np.sqrt((ir ** 2).sum())
    n = len(x) + len(ir); F = 1 << int(np.ceil(np.log2(n)))
    wet = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
    return (1 - mix) * x + mix * wet
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())

# ---------- effects ----------
def tick(hi=True, slow=1.0):
    """clock tick; slow>1 stretches & lowers it (the 'slowed' tick of scene 2)"""
    L = 0.08 * slow; t = tt(L)
    f = (3400 if hi else 2700) / slow
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 140 / slow) + 0.5 * band(rng.standard_normal(len(t)), 1500 / slow, 9000 / slow) * np.exp(-t * 220 / slow)
    x += 0.5 * np.sin(2 * np.pi * 900 / slow * t) * np.exp(-t * 90 / slow)
    return norm(x)
def click():
    t = tt(0.06)
    x = band(rng.standard_normal(len(t)), 2000, 12000) * np.exp(-t * 260) + 0.8 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 200)
    return norm(x)
def bulb_off():
    t = tt(0.12); f = 900 * np.exp(-t * 18) + 120
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30))
def rustle(L=0.35):
    t = tt(L); x = band(rng.standard_normal(len(t)), 1800, 9000)
    am = np.abs(band(rng.standard_normal(len(t)), 5, 40)); am = am / (am.max() + 1e-9)
    return norm(x * (0.3 + am) * np.sin(np.pi * t / L) ** 0.7)
def tock():
    t = tt(0.15); f = 420 + 300 * np.exp(-t * 40)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28))
def heartbeat():
    s = np.zeros(int(SR * 0.6))
    for k, g, f0 in [(0, 1.0, 62), (0.17, 0.65, 55)]:
        t = tt(0.25); f = f0 + 30 * np.exp(-t * 30)
        add(s, k, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16) * np.minimum(1, t / 0.006), g)
    return norm(np.tanh(1.5 * s))
def wave_swell(L=1.4):
    t = tt(L); x = band(rng.standard_normal(len(t)), 150, 1400)
    return norm(x) * np.sin(np.pi * t / L) ** 2
def whoosh(L=0.5, lo=400, hi=3500):
    t = tt(L); x = band(rng.standard_normal(len(t)), lo, hi)
    return norm(x) * np.sin(np.pi * t / L) ** 1.5
def chime(fr=1760, L=1.2):
    t = tt(L)
    x = sum(a * np.sin(2 * np.pi * fr * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 4), (2.76, .3, 7), (5.4, .1, 12)])
    return norm(x * np.minimum(1, t / 0.002))
def ding():
    s = np.zeros(int(SR * 1.4))
    add(s, 0, chime(1568, 1.3)); add(s, 0.09, chime(2093, 1.3), 0.8)
    return norm(s)
def scratch(L=0.22):
    t = tt(L); x = band(rng.standard_normal(len(t)), 2500, 8000) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
    return norm(x * np.sin(np.pi * t / L))
def pop():
    t = tt(0.2); f = 300 + 900 * np.exp(-t * 35)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22))

fx = np.zeros(int(SR * (dur + 2)))
s1, s2, s3, s4, s5, s6, s7, se = (sc[k] for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'end'])
# S1: ticking clock (second hand jumps on whole seconds)
for k in range(0, 4): add(fx, s1['start'] + k, tick(k % 2 == 0), 0.55)
# S2: slowed, stretched ticking + soft rush of spinning hands
add(fx, s2['start'] + 0.1, whoosh(2.6, 200, 1600), 0.12)
for k in (0.1, 1.05, 2.15, 3.35): add(fx, s2['start'] + k, tick(True, 2.6), 0.55)
# S3: two ticks, bulbs go out, silence, sharp click on the head snap
a = s3['start']
for k in (0.0, 0.75): add(fx, a + k, tick(k == 0), 0.5)
for k in range(6): add(fx, a + .2 + [3, 0, 4, 1, 5, 2][k] * .13 + .18, bulb_off(), 0.12)
add(fx, a + s3['click'], click(), 0.95)
add(fx, a + s3['click'] + 0.02, tock(), 0.3)
# S4: paper rustle as words leave the notebook, soft tock when they bounce off the brain
for i in range(10):
    add(fx, s4['start'] + .1 + i * .2, rustle(0.3), 0.22)
    add(fx, s4['start'] + .1 + i * .2 + 1.05, tock(), 0.12 if i in (2, 6) else 0.18)
# S5: low heartbeat synced to the red pulse
b = s5['start'] + s5['beat0']
while b < s5['end'] - 0.3: add(fx, b, heartbeat(), 0.85); b += s5['period']
# S6: soft waves, pages landing
for k in np.arange(0, s6['end'] - s6['start'], 1.33): add(fx, s6['start'] + k, wave_swell(1.6), 0.22)
for i in range(5):
    add(fx, s6['start'] + .7 + i * .48, whoosh(0.5, 900, 5000), 0.12)
    add(fx, s6['start'] + .7 + i * .48 + .8, chime(1320 + i * 110, 0.7), 0.07)
# S7: pen ticks for checkmarks, then "ding"
for i in range(5): add(fx, s7['start'] + .35 + i * .3, scratch(), 0.18)
add(fx, s7['start'] + s7['ding'], ding(), 0.55)
# END: bubble + plus pop
add(fx, se['start'] + .6, pop(), 0.18)
add(fx, se['start'] + se['plus'], pop(), 0.45); add(fx, se['start'] + se['plus'] + .02, chime(2093, 0.8), 0.18)
write('sfx.wav', fx[:int(SR * dur)])

# ---------- music: minimal piano + clock ticking, 60 BPM ----------
N = lambda n: 440 * 2 ** ((n - 69) / 12)
def piano(freq, L=2.5, vel=1.0):
    t = tt(L); x = np.zeros(len(t))
    for m, a in [(1, 1), (2, .45), (3, .22), (4, .12), (5, .06), (6, .03)]:
        fm = freq * m * (1 + 0.0004 * m * m)
        x += a * np.sin(2 * np.pi * fm * t) * np.exp(-t * (1.1 + 0.9 * m) * (freq / 440) ** 0.3)
    x += 0.02 * band(rng.standard_normal(len(t)), 1000, 6000) * np.exp(-t * 80)
    return x * np.minimum(1, t / 0.004) * vel
mu = np.zeros(int(SR * (dur + 3)))
# chords (4 s each): Am - F - C - G | Am - F - C - G ... calmer, brighter end on C
prog = [(57, [64, 69, 72]), (53, [65, 69, 72]), (48, [64, 67, 72]), (55, [62, 67, 71])]
mel = {12: 76, 16: 77, 20: 79, 24: 76, 28: 72}
for b in range(int(dur)):
    root, ch = prog[(b // 4) % 4]
    if b < dur - 2.5:
        if b % 4 == 0: add(mu, b, piano(N(root), 4.0, 0.7))
        add(mu, b + 0.5 * (b % 2), piano(N(ch[b % 3] + 12 * (b % 4 == 3)), 2.2, 0.38))
    if b in mel: add(mu, b + 0.02, piano(N(mel[b]), 3.0, 0.45))
for n in (48, 60, 64, 67, 72): add(mu, dur - 2.6, piano(N(n), 3.0, 0.5))
mu = reverb(mu, 2.4, 0.35)
# clock ticks on every beat, very soft
for b in range(int(dur)): add(mu, b + 0.0, tick(b % 2 == 0), 0.10)
mu = mu[:int(SR * dur)]
fade = np.ones(len(mu)); k = int(SR * 1.0); fade[-k:] = np.linspace(1, 0, k)
write('music.wav', norm(mu) * 0.8 * fade)
print('sfx.wav + music.wav', dur, 's')
