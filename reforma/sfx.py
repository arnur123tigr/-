"""Sound for the reform reel: synth effects (sfx_<lang>.wav) and a music bed (music_<lang>.wav), timed from beats.json.
Usage: python3 sfx.py ru|kk"""
import json, sys
import numpy as np
from sfxlib import *

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; DUR = B['end']
m = lambda k: M[k]


def rustle(L=.6):            # paper: crackly noise bursts
    out = np.zeros(int(SR * L)); n = int(90 * L)
    for k in range(n):
        t0 = rng.uniform(0, L * .9); t = tt(.025); add(out, t0, norm(band(rng.standard_normal(len(t)), 1500, 9000) * np.exp(-t * 120)), rng.uniform(.2, 1) * np.sin(np.pi * t0 / L))
    return norm(out + .3 * norm(band(rng.standard_normal(len(out)), 800, 6000)) * np.sin(np.pi * np.arange(len(out)) / len(out)))
def stamp():                 # a seal pressed: low thud + a little paper
    t = tt(.5); s = np.sin(2 * np.pi * np.cumsum(70 * (1 + 1.2 * np.exp(-t * 40))) / SR) * np.exp(-t * 12)
    return norm(s + .35 * band(rng.standard_normal(len(t)), 200, 3000) * np.exp(-t * 35))
def quill(L=1.0):            # pen scratching
    t = tt(L); env = (.6 + .4 * np.abs(np.sin(2 * np.pi * 3.3 * t))) * np.minimum(1, t / .05) * np.minimum(1, (L - t) / .1)
    return norm(band(rng.standard_normal(len(t)), 2500, 9000) * env * (1 + .5 * (rng.random(len(t)) < .002)))
def step():                  # a foot on a wooden step
    t = tt(.25); return norm(np.sin(2 * np.pi * np.cumsum(110 * (1 + .8 * np.exp(-t * 50))) / SR) * np.exp(-t * 22) + .5 * band(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 60))
def shatter():               # a gold crown breaking: bright metal + glass bits
    out = np.zeros(int(SR * 1.2)); add(out, 0, crack(), .7)
    for k in range(10):
        f = rng.uniform(2500, 6000); t = tt(.4); add(out, rng.uniform(0, .5) ** 1.4, np.sin(2 * np.pi * f * t) * np.exp(-t * 18), rng.uniform(.2, .6))
    return norm(out)

s = np.zeros(int(SR * DUR))
# 1. two sheets fall and are sealed, the cracks run
for t0 in (.15, .55): add(s, t0, rustle(.55), .55); add(s, t0 + .5, stamp(), .9); add(s, t0 + .5, boom(60, .8), .35)
add(s, m('cut') - .35, crack(), .9); add(s, m('cut') - .1, debris(1.2), .4); add(s, m('cut') + .2, crack(), .5); add(s, m('cut') - .35, sub(80, 34, 1.2), .4)
# 2. rewind, statutes, crowns
add(s, m('S2') - .1, whoosh(.7, 2000, 300), .45)
for k in range(10): add(s, m('S2') + k * .06, tick(2600), .15)
add(s, m('S2') + .9, rustle(.5), .4); add(s, m('S2') + .9, pop(), .25)
add(s, m('sper') - .1, rustle(.4), .35); add(s, m('sper') + .3, stamp(), .4)
add(s, m('orta') + .1, shatter(), .7); add(s, m('y1824') + .5, rustle(.5), .4); add(s, m('kishi') + .05, shatter(), .7)
add(s, m('kishi') + .5, stamp(), .7)
# page turn
add(s, m('S3') - .05, rustle(.7), .6); add(s, m('S3') - .05, whoosh(.6, 400, 2500), .25)
# 3. Alexander, the pen
add(s, m('S3') + .35, chime(880, 1.4), .15); add(s, m('S3') + .4, swell(1.4, (50, 57, 62)), .18)
add(s, m('zhet') - .1, quill(1.3), .35); add(s, m('syr') - .05, quill(1.3), .35)
add(s, m('syr') + 1.0, quill(1.0), .2)
# 4. four seals
add(s, m('S4'), drum(70, .5, 8), .4)
for k in ('ural', 'turg', 'akm', 'sem'): add(s, m(k) - .1, quill(.6), .25); add(s, m(k) + .05, stamp(), .7); add(s, m(k) + .05, boom(55, .7), .18)
add(s, m('gg'), rustle(.8), .45); add(s, m('gg') + .1, swell(1.2, (45, 52, 57)), .15)
add(s, m('buk'), whoosh(1.0, 300, 1500), .3)
# 5. steps
for i in range(5): add(s, m('S5') + .15 + i * .35, step(), .55)
add(s, m('top'), stamp(), .5); add(s, m('top') + .15, stamp(), .35); add(s, m('top') + .3, stamp(), .35)
add(s, m('low'), pop(), .3); add(s, m('low') + .2, pop(), .3)
# 6. coins
for i in range(37): add(s, m('S6') + .1 + i * .045, pop(), .06)
for k in range(0, 37, 3): add(s, m('tax') + .15 + k * .04, coin(), .35)
add(s, m('sult'), whoosh(.5, 300, 2200), .3); add(s, m('sult') + .4, coin(), .4)
# 7. flash, plaque
add(s, m('S7') - .1, whoosh(.4, 300, 3000), .4); add(s, m('S7'), boom(50, 1.2), .6); add(s, m('S7') + .4, stamp(), .6)
for k in ('d', 'g3', 'o6'): add(s, m(k) - .03, drum(75, .5, 8), .5)
# 8. scroll, seal, end
add(s, m('S8'), rustle(1.0), .6); add(s, m('S8') + 1.15, stamp(), .9)
add(s, m('link') - .1, pop(), .3); add(s, m('link'), chime(1319, .9), .15)
e0 = m('End'); add(s, e0 - .2, whoosh(.6, 240, 2200), .3); add(s, e0 + .05, boom(52, 1.6, 2.6), .45)
for i, f in enumerate((587, 880, 1175)): add(s, e0 + .3 + i * .07, chime(f, 1.5), .16)
write(f'sfx_{LANG}.wav', norm(s) * .9)

# music bed: D minor, slow and calm at first, the tension grows towards the reform and the tax
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
part(0, m('S2'), [Dm, Bb], pads=.18, low=.24, toms=.18, bpm=92)
part(m('S2'), m('S3'), [Dm, Gm], pads=.16, low=.26, ost=.05, bright=.7, bpm=92)
part(m('S3'), m('S4'), [Dm, Bb, Gm, A], pads=.18, low=.28, ost=.08, toms=.2, hats=.02, build=.6, bpm=92)
part(m('S4'), m('S5'), [Dm, Bb, F, A], pads=.2, low=.3, ost=.1, toms=.3, hats=.03, build=.8, bpm=92)
part(m('S5'), m('S6'), [Gm, Dm], pads=.18, low=.3, toms=.26, bright=.6, bpm=92)
part(m('S6'), m('S7'), [Dm, A], pads=.2, low=.3, ost=.1, toms=.32, hats=.03, build=1.0, bpm=92)
part(m('S7'), DUR, [Bb, F, Gm, Dm], pads=.2, low=.26, ost=.07, toms=.2, hats=.02, bpm=92)
fade = np.ones(len(mu)); n0 = int(SR * .6); fade[:n0] = np.linspace(.3, 1, n0); n1 = int(SR * 1.8); fade[-n1:] = np.linspace(1, 0, n1)
write(f'music_{LANG}.wav', norm(mu * fade) * .9)
print(LANG, 'sfx + music', DUR, 's')
