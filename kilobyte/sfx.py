"""8-bit sound: sfx.wav (error buzz, coin, clicks, blips, rising notes, blops, ticks, level-clear jingle, fanfare) and a
chiptune music bed music.wav (square-wave arpeggio + triangle bass + noise hats, 120 bpm). Cue times come from cues.json."""
import json, wave, numpy as np
C = json.load(open('cues.json')); SR = 48000; DUR = C['dur']
rng = np.random.default_rng(3)
def norm(x): return x / (np.abs(x).max() + 1e-9)
def tt(L): return np.arange(int(SR * L)) / SR
def add(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < j: buf[i:j] += g * sig[:j - i]
def write(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32000).astype(np.int16).tobytes())
N = lambda n: 440 * 2 ** ((n - 69) / 12)
def sq(f, L, duty=.5, dec=0.):
    t = tt(L); ph = (np.cumsum(np.broadcast_to(f, t.shape)) / SR) % 1; x = np.where(ph < duty, 1., -1.)
    env = np.exp(-t * dec) if dec else np.ones_like(t); env[-200:] *= np.linspace(1, 0, 200); return x * env
def tri(f, L):
    t = tt(L); ph = (f * t) % 1; return (4 * np.abs(ph - .5) - 1)
def noise(L, dec=40):
    t = tt(L); x = np.sign(rng.standard_normal(len(t))); return x * np.exp(-t * dec)
def notes(seq, step, duty=.5, dec=6):
    out = np.zeros(int(SR * (step * len(seq) + .4)))
    for k, n in enumerate(seq):
        if n: add(out, k * step, sq(N(n), step * 1.6, duty, dec))
    return out
FX = {
  'err': lambda: np.concatenate([sq(110, .12, .5), np.zeros(int(SR * .03)), sq(92, .22, .5, 4)]),
  'coin': lambda: np.concatenate([sq(N(83), .07, .5), sq(N(88), .35, .5, 7)]),
  'click': lambda: sq(1800, .025, .5, 120) + noise(.025, 200) * .5,
  'blip': lambda: sq(np.linspace(600, 1200, int(SR * .07)), .07, .25, 25),
  'blop': lambda: sq(np.linspace(500, 160, int(SR * .12)), .12, .5, 15),
  'tick': lambda: sq(2400, .02, .5, 150),
  'ding': lambda: notes([76, 79, 84, 88], .07, .25, 5),
  'clear': lambda: notes([72, 76, 79, 84, 0, 79, 84], .09, .5, 4),
  'fan': lambda: notes([67, 72, 76, 79, 0, 76, 79, 84, 84], .1, .5, 3),
  'zap': lambda: sq(np.linspace(1500, 200, int(SR * .25)), .25, .5, 6) * .8 + noise(.25, 10) * .25,
}
GAIN = {'err': .35, 'coin': .35, 'click': .4, 'blip': .25, 'blop': .35, 'tick': .25, 'ding': .3, 'clear': .32, 'fan': .32, 'zap': .18}
s = np.zeros(int(SR * DUR))
for k, ts in C.items():
    if k == 'dur': continue
    if k == 'rise':   # rising 8-bit notes for the staircase
        for i, t0 in enumerate(ts): add(s, t0, sq(N(60 + 2 * i), .18, .25, 10), .25)
        continue
    for t0 in ts: add(s, t0, norm(FX[k]()), GAIN[k])
write('sfx.wav', norm(s) * .9)
# ---- chiptune bed ----
bpm = 120; st = 60 / bpm / 4; m = np.zeros(int(SR * (DUR + 1)))
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]   # Am F C G
for b in range(int(DUR / (16 * st)) + 1):
    root, ch = prog[b % 4]; t0 = b * 16 * st
    for k in range(16):
        n = ch[k % 3] + 12 * (1 + (k // 3) % 2 * 0); add(m, t0 + k * st, sq(N(n + 12), st * .9, .125, 9) * .10)
        if k % 2 == 0: add(m, t0 + k * st, tri(N(root - 12 + (12 if k % 8 == 6 else 0)), st * 1.8) * .30)
        if k % 4 == 2: add(m, t0 + k * st, noise(.04, 90) * .06)
        if k % 8 == 0: add(m, t0 + k * st, sq(np.linspace(160, 40, int(SR * .12)), .12, .5, 18) * .22)
        if k % 8 == 4: add(m, t0 + k * st, noise(.12, 25) * .12)
m = m[:int(SR * DUR)]
fade = np.ones(len(m)); n0 = int(SR * 1.0); fade[:n0] = np.linspace(0, 1, n0); n1 = int(SR * 2.5); fade[-n1:] = np.linspace(1, 0, n1)
write('music.wav', norm(m * fade) * .9); print('sfx + music ok', DUR)
