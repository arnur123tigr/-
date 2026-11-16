"""Procedural 'terrain diorama' cards (640x640): land/sea shapes with hillshaded relief, beaches, shallow water."""
import numpy as np
from PIL import Image, ImageFilter
N = 640; rng = np.random.default_rng(7)
y, x = np.mgrid[0:N, 0:N] / N
def noise(oct=6, seed=0):
    r = np.random.default_rng(seed); o = np.zeros((N, N))
    for k in range(oct):
        s = 2 ** (k + 2); g = r.standard_normal((s + 1, s + 1))
        im = Image.fromarray(g.astype(np.float32)).resize((N, N), Image.BICUBIC)
        o += np.asarray(im) / 2 ** k
    return o / 2
wx = noise(4, 99) * .045; wy = noise(4, 98) * .045
X, Y = x + wx, y + wy
def disk(cx, cy, rx, ry=None):
    ry = ry or rx; r = min(rx, ry); return r * (1 - np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2))
def rect(x0, x1, y0, y1):
    return np.minimum(np.minimum(X - x0, x1 - X), np.minimum(Y - y0, y1 - Y))
U = np.maximum; I = np.minimum
def cap(ax, ay, bx, by, r):
    px, py = X - ax, Y - ay; vx, vy = bx - ax, by - ay
    h = np.clip((px * vx + py * vy) / (vx * vx + vy * vy), 0, 1)
    return r - np.sqrt((px - vx * h) ** 2 + (py - vy * h) ** 2)
def ring(cx, cy, r): return np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - r
S = {
 'peninsula': lambda: U(rect(-1, .2, -1, 2), U(cap(.12, .52, .58, .46, .15), disk(.62, .45, .17, .2))),
 'gulf': lambda: I(rect(-1, 2, .3, 2), -U(cap(.5, .2, .5, .55, .13), disk(.5, .6, .25, .2))),
 'isthmus': lambda: U(U(rect(-1, 2, -1, .3), rect(-1, 2, .7, 2)), cap(.5, .2, .52, .8, .055)),
 'strait': lambda: I(U(rect(-1, 2, -1, .55), rect(-1, 2, .45, 2)), -cap(-.5, .5, 1.5, .5, .06)),
 'island': lambda: U(disk(.48, .5, .27, .2), disk(.6, .42, .14, .1)),
 'lake': lambda: -U(disk(.4, .48, .19, .15), disk(.63, .55, .17, .13)),
 'archipelago': lambda: np.max([disk(*a) for a in [(.3, .3, .1, .07), (.6, .26, .12, .08), (.44, .5, .1, .07), (.73, .55, .1, .07), (.3, .72, .09, .06), (.57, .76, .1, .065)]], 0),
 'lakes': lambda: -np.max([disk(*a) for a in [(.3, .3, .11, .08), (.62, .28, .12, .08), (.45, .52, .1, .075), (.74, .6, .1, .07), (.28, .72, .09, .065), (.56, .79, .11, .065)]], 0),
 'cape': lambda: U(rect(-1, 2, -1, .26), np.minimum(.2 * np.clip(1 - (Y - .22) / .66, 0, 1) - np.abs(X - .5 - (Y - .25) * .12), .88 - Y)),
 'bay': lambda: I(rect(-1, 2, -1, .74), ring(.5, .5, .3)),
}
def render(name, seed):
    f = S[name]()
    n = noise(6, seed); f = f + n * .012        # natural coastline
    land = f > 0
    d = Image.fromarray(land.astype(np.uint8) * 255)
    # distance-ish field from coast (blurred mask)
    dl = np.asarray(d.filter(ImageFilter.GaussianBlur(22))).astype(float) / 255
    dl2 = np.asarray(d.filter(ImageFilter.GaussianBlur(40))).astype(float) / 255
    hn = noise(7, seed + 11); rid = 1 - np.abs(noise(6, seed + 21)); hn = hn * .5 + rid * .8
    h = np.where(land, np.clip(dl2 * 1.6 - .5, 0, 1) * (.55 + .45 * hn) + np.clip(dl * 2 - 1, 0, 1) * .25, 0)
    gy, gx = np.gradient(h * 140)
    shade = np.clip(.75 + 1.3 * (-gx * .6 - gy * .8) / np.sqrt(1 + gx ** 2 + gy ** 2), .2, 1.45)
    rock = np.array([138, 112, 86]); hi = np.array([196, 176, 150]); sand = np.array([222, 205, 168]); grn = np.array([110, 112, 70])
    t = np.clip(h * 1.6, 0, 1)[..., None]
    col = rock * (1 - t) + hi * t
    col = col * (1 - np.clip(hn * .5 + .2, 0, .35)[..., None]) + grn * np.clip(hn * .5 + .2, 0, .35)[..., None] * .8
    beach = np.clip(1 - (dl - .5) / .12, 0, 1)[..., None] * land[..., None]
    col = col * shade[..., None]
    col = col * (1 - beach * .8) + sand * beach * .8
    # sea
    ds = 1 - dl
    shallow = np.array([84, 190, 196]); mid = np.array([30, 118, 150]); deep = np.array([12, 62, 98])
    a = np.clip((ds - .5) / .5, 0, 1)[..., None] ** .7
    sea = np.where(a < .35, shallow + (mid - shallow) * (a / .35), mid + (deep - mid) * ((a - .35) / .65))
    sn = noise(5, seed + 5)[..., None]; sea = sea * (.93 + .1 * sn)
    foam = np.clip(1 - np.abs(ds - .5) / .03, 0, 1)[..., None] * .6
    sea = sea * (1 - foam) + 245 * foam
    img = np.where(land[..., None], col, sea)
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))
    im.save(f'cards/{name}.jpg', quality=92)
for i, k in enumerate(S): render(k, i * 3 + 1); print(k)
ims = [Image.open(f'cards/{k}.jpg').resize((200, 200)) for k in S]
sh = Image.new('RGB', (1000, 400))
for i, im in enumerate(ims): sh.paste(im, ((i % 5) * 200, (i // 5) * 200))
sh.save('/tmp/claude-0/-home-user/5b7d334e-6136-5073-b2d9-631178e151e2/scratchpad/cards.jpg')
