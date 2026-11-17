"""Sound for the desyatina reel: synth effects (sfx_<lang>.wav) and a music bed (music_<lang>.wav), timed from beats.json.
Usage: python3 sfx.py ru|kk"""
import json, sys
import numpy as np
from sfxlib import *

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
B = json.load(open('beats.json'))[LANG]; M = B['m']; DUR = B['end']
m = lambda k: M[k]


def clatter(L):             # train wheels on rail joints: ta-ta ... ta-ta
    out = np.zeros(int(SR * (L + .2))); T = 0.
    while T < L - .1:
        for off in (0, .11):
            t = tt(.06); add(out, T + off, norm(band(rng.standard_normal(len(t)), 120, 2400) * np.exp(-t * 60)), .8 * np.sin(np.pi * clamp(T / L)) ** .4)
        T += .42
    return norm(out)
def whistle(L=1.4):          # a distant steam whistle (two detuned tones)
    t = tt(L); env = np.minimum(1, t / .12) * np.minimum(1, (L - t) / .4)
    return norm(band((np.sin(2 * np.pi * 523 * t) + .8 * np.sin(2 * np.pi * 659 * t) + .3 * np.sin(2 * np.pi * 784 * t)) * env + .2 * rng.standard_normal(len(t)) * env, 300, 3000))
def clink(f=2400):           # metal block landing
    t = tt(.8); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (6 + 3 * h)) / h for h in (1, 1.7, 2.9, 4.1)) + .4 * band(rng.standard_normal(len(t)), 1000, 8000) * np.exp(-t * 50))
def glass(f=1760):           # glass ping
    t = tt(1.6); return norm(sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2 + 1.2 * h)) / h for h in (1, 2.32, 4.25)))

s = np.zeros(int(SR * DUR))
# 1: deep bass hit + odometer clicks
add(s, m('s1') - .2, boom(48, 2.2, 2.2), .5); add(s, m('s1') - .2, sub(70, 30, 1.6), .25)
for i in range(46): add(s, m('s1') + .25 + i * .045 * (1 + i / 40), tick(2800 + 300 * (i % 3)), .22)
add(s, m('s1') + 1.75, drum(70, .6, 7), .6)
# 2: soft hum, gold Kyrgyzstan drops in
add(s, m('S2'), drone(m('S3') - m('S2'), 55), .35); add(s, m('km') - .15, whoosh(.7, 200, 1800), .35); add(s, m('km') + .45, boom(60, 1.0), .45)
add(s, m('kg'), shimmer(.8), .18)
# 3: plates, peasant, the 30-desyatina block (metal ring)
add(s, m('S3'), drum(80, .5, 8), .45); add(s, m('S3') + .45, drum(80, .5, 8), .4)
add(s, m('flow') - .1, whoosh(.8, 220, 2000), .25); add(s, m('y1868') - .1, pop(), .25)
add(s, m('d30') + .15, clink(2200), .55); add(s, m('d30') + .15, boom(70, .6), .3)
# 4: wheels and a whistle
add(s, m('S4'), clatter(m('S5') - m('S4')), .35); add(s, m('ts') - .2, whistle(1.5), .22); add(s, m('st'), shimmer(1.4), .12)
# 5: flash, sphere, coins pouring as tiles stack
add(s, m('S5') - .1, boom(55, 1.4), .4); add(s, m('S5') + .1, glass(1568), .25)
for k in range(0, 40, 2): add(s, m('S5') + .9 + k * (m('yr') - m('S5') - .7) / 40, coin(), .22)
for k in range(0, 26, 2): add(s, m('yr') + k * (m('mil') + .6 - m('yr')) / 26, coin(), .18)
# 6: three coin impacts, each louder
for i, k in enumerate(('c1', 'c2', 'c3')): add(s, m(k) + .1, drum(80 - 10 * i, .7, 6), .45 + .2 * i); add(s, m(k) + .1, clink(1800 - 250 * i), .3 + .15 * i)
# 7: one low note
add(s, m('S7') + .2, swell(1.2, (38, 45, 50), 2.5), .4)
# 8: glass
add(s, m('S8') + .2, glass(1760), .3); add(s, m('link') - .2, whoosh(.8, 240, 2200), .3); add(s, m('link') + .9, glass(2093), .3)
e0 = m('End'); add(s, e0 + .05, boom(52, 1.6, 2.6), .35)
for i, f in enumerate((587, 880, 1175)): add(s, e0 + .3 + i * .07, chime(f, 1.5), .14)
write(f'sfx_{LANG}.wav', norm(s) * .9)

# music bed: dark D minor, slow documentary pulse; tension grows to the tax scene, quiet under the quote
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
part(0, m('S2'), [Dm], pads=.16, low=.3, bpm=80)
part(m('S2'), m('S3'), [Dm, Bb], pads=.16, low=.26, ost=.04, bright=.6, bpm=80)
part(m('S3'), m('S4'), [Dm, Bb, Gm, A], pads=.17, low=.28, ost=.07, toms=.14, build=.5, bpm=80)
part(m('S4'), m('S5'), [Dm, Bb, F, A], pads=.18, low=.3, ost=.09, toms=.22, hats=.02, build=.7, bpm=80)
part(m('S5'), m('S6'), [Gm, Dm, Bb, A], pads=.18, low=.3, ost=.08, toms=.22, bright=.7, bpm=80)
part(m('S6'), m('S7'), [Dm, A], pads=.2, low=.32, ost=.1, toms=.3, hats=.03, build=1.0, bpm=80)
part(m('S7'), m('S8'), [Dm], pads=.12, low=.2, bright=.5, bpm=80)
part(m('S8'), DUR, [Bb, F, Gm, Dm], pads=.18, low=.24, ost=.06, toms=.15, bpm=80)
fade = np.ones(len(mu)); n0 = int(SR * .6); fade[:n0] = np.linspace(.3, 1, n0); n1 = int(SR * 1.8); fade[-n1:] = np.linspace(1, 0, n1)
write(f'music_{LANG}.wav', norm(mu * fade) * .9)
print(LANG, 'sfx + music', DUR, 's')
