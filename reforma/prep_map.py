"""Builds the parchment map for the reel «Как казахскую степь разрезали на части» from public-domain sources (fetch_data.sh).

Writes
  tex/base.jpg      the parchment: paper, sepia relief, seas with engraved ripple lines, ink coasts and rivers, faint graticule
  tex/archive.jpg   J. Arrowsmith's map of Central Asia (1872) warped into the same coordinates (for the overlay in scene 4)
  tex/speransky.png, tex/alexander.png   the two portraits, toned to sepia (Speransky as a torn paper cut-out)
  shapes.json       oblasts of 1867-1868 (approximate), zhuz areas, Kazakhstan outline, crack lines, perimeters
Map space: x = (lon - LON0) * cos(48°) * P, y = (LAT1 - lat) * P (pixels of base.jpg).
Usage: python3 prep_map.py"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from shapely.geometry import shape, box, Polygon, MultiPolygon, LineString, mapping
from shapely.ops import unary_union

LON0, LON1, LAT0, LAT1, P = 40.0, 92.0, 34.0, 58.0, 88
KX = math.cos(math.radians(48))
W, H = int((LON1 - LON0) * KX * P), int((LAT1 - LAT0) * P)
rng = np.random.default_rng(7)
px = lambda lon, lat: ((lon - LON0) * KX * P, (LAT1 - lat) * P)
D = lambda n: json.load(open(f'data/{n}.geojson'))['features']
print('base', W, H)


def fbm(h, w, scales, seed=0):
    r = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); tot = 0
    for s, a in scales:
        g = r.standard_normal((h // s + 3, w // s + 3)).astype(np.float32)
        z = ndimage.zoom(g, s, order=3)[:h, :w]; out += a * z; tot += a
    return out / tot


def geom_px(g):
    """shapely geometry lon/lat -> list of rings (pixel coords)."""
    polys = [g] if isinstance(g, Polygon) else list(getattr(g, 'geoms', []))
    out = []
    for p in polys:
        if p.is_empty: continue
        out.append([px(x, y) for x, y in p.exterior.coords])
    return out


def mask_of(geoms, scale=2, lines=None, width=1):
    im = Image.new('L', (W * scale, H * scale), 0); d = ImageDraw.Draw(im)
    for g in geoms:
        polys = [g] if isinstance(g, Polygon) else list(g.geoms)
        for p in polys:
            d.polygon([(a * scale, b * scale) for a, b in (px(x, y) for x, y in p.exterior.coords)], fill=255)
            for hole in p.interiors: d.polygon([(a * scale, b * scale) for a, b in (px(x, y) for x, y in hole.coords)], fill=0)
    return im


# ------------------------------------------------------------------ water
BB = box(LON0 - 2, LAT0 - 2, LON1 + 2, LAT1 + 2)
land = unary_union([shape(f['geometry']).intersection(BB) for f in D('ne_50m_land') if shape(f['geometry']).intersects(BB)])
ARAL1868 = Polygon([(61.1, 46.75), (61.6, 46.5), (61.9, 46.1), (61.8, 45.5), (61.3, 45.0), (61.0, 44.5), (60.4, 43.9), (59.9, 43.6), (59.2, 43.5),
                    (58.6, 43.7), (58.25, 44.2), (58.15, 44.9), (58.3, 45.4), (58.6, 45.6), (59.0, 45.9), (59.4, 46.15), (59.9, 46.5), (60.4, 46.8), (60.8, 46.85)])
def jag(p, n=6, a=.07, seed=4):
    r = np.random.default_rng(seed); c = list(p.exterior.coords); out = []
    for i in range(len(c) - 1):
        for j in range(n):
            u = j / n; out.append((c[i][0] * (1 - u) + c[i + 1][0] * u + r.normal(0, a), c[i][1] * (1 - u) + c[i + 1][1] * u + r.normal(0, a * .7)))
    return Polygon(out).buffer(0.05).buffer(-0.05)
ARAL1868 = jag(ARAL1868, 4, .03)
KEEP = {'Lake Balkhash', 'Lake Zaysan', 'Issyk-Kul', 'Alakol', 'Lake Sasykkol', 'Tengiz Köli', 'Lake Chany', 'Sarygamysh Köli', 'Ebinur Hu', 'Bosten Hu'}
lakes = [shape(f['geometry']) for f in D('ne_10m_lakes') if f['properties'].get('name') in KEEP] + [ARAL1868]
water = BB.difference(land).union(unary_union(lakes)).intersection(box(LON0, LAT0, LON1, LAT1))
wm = np.asarray(mask_of([water]).resize((W, H), Image.LANCZOS), np.float32) / 255

# ------------------------------------------------------------------ relief from Terrarium tiles (zoom 6)
Z = 6; tx0, tx1, ty0, ty1 = 39, 48, 19, 25
big = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
for x in range(tx0, tx1 + 1):
    for y in range(ty0, ty1 + 1):
        a = np.asarray(Image.open(f'data/dem/{Z}_{x}_{y}.png').convert('RGB'), np.float32)
        big[(y - ty0) * 256:(y - ty0 + 1) * 256, (x - tx0) * 256:(x - tx0 + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
lon = LON0 + xx / (KX * P); lat = LAT1 - yy / P
mx = ((lon + 180) / 360 * 2 ** Z - tx0) * 256
my = ((1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2 * 2 ** Z - ty0) * 256
elev = ndimage.map_coordinates(big, [my, mx], order=1)
elev = np.where(wm > .5, 0, np.maximum(elev, 0))
e = ndimage.gaussian_filter(elev, 1.2)
gy, gx = np.gradient(e, 1000 / P * 1.0)          # metres per pixel ~ 1.26 km
ex = 22.0
az, alt = math.radians(315), math.radians(42)
sl = np.arctan(ex * np.hypot(gx, gy) / 1000); asp = np.arctan2(-gx, gy)
shade = np.sin(alt) * np.cos(sl) + np.cos(alt) * np.sin(sl) * np.cos(az - asp)
shade = shade / np.sin(alt)                         # flat = 1
slope = np.clip(np.hypot(gx, gy) / 60, 0, 1)

# ------------------------------------------------------------------ paper
low = fbm(H, W, [(512, 1.0), (256, .7), (128, .5)], 1)
mid = fbm(H, W, [(64, 1.0), (24, .6), (8, .4)], 2)
grain = rng.standard_normal((H, W)).astype(np.float32)
paper = np.array([233, 216, 178], np.float32)
dark = np.array([196, 160, 112], np.float32)
stain = np.clip((fbm(H, W, [(380, 1), (160, .6)], 3) - .35) * 2.2, 0, 1)
col = paper[None, None] * (1 + .045 * low[..., None] + .02 * mid[..., None] + .018 * grain[..., None])
col = col * (1 - .22 * stain[..., None]) + dark[None, None] * .22 * stain[..., None]
# coffee-ring stains
for _ in range(5):
    cx, cy, r = rng.uniform(.1, .9) * W, rng.uniform(.1, .9) * H, rng.uniform(60, 190)
    d = np.hypot(xx - cx, yy - cy); ring = np.exp(-((d - r) / 5) ** 2) * .5 + np.exp(-((d - r) / 26) ** 2) * .2 + (d < r) * .06
    col *= (1 - .10 * ring[..., None])
Image.fromarray(np.clip(col[200:1100, 1500:2400], 0, 255).astype(np.uint8)).save('tex/paper.jpg', quality=90) if __import__('os').makedirs('tex', exist_ok=True) is None else 0
# land: relief in sepia (shadows warm brown, sunny slopes a little lighter), plus fine stipple on steep ground (engraving feel)
landm = 1 - wm
rel = np.clip(shade, .2, 1.6)
k = np.where(rel < 1, 1 - (1 - rel) * .75, 1 + (rel - 1) * .30)
shadow_col = np.array([.92, .86, .78], np.float32)
col = col * np.where(k[..., None] < 1, (k[..., None] * shadow_col + (1 - shadow_col) * k[..., None] ** 2), k[..., None]) ** (landm[..., None])
hi = np.clip((elev - 700) / 2600, 0, 1)
col = col * (1 - .22 * hi[..., None]) + np.array([150, 110, 72], np.float32) * .22 * hi[..., None]
stip = (rng.random((H, W)) < .16 * slope) * landm
col *= (1 - .18 * stip[..., None])
# deserts: fine dotted sand, as on old maps
DES = [Polygon([(62.0, 40.2), (66.5, 40.0), (67.6, 41.4), (66.2, 43.6), (63.2, 44.0), (61.4, 42.0)]),          # Kyzylkum
       Polygon([(69.6, 44.0), (73.0, 44.3), (74.0, 45.1), (72.0, 45.6), (69.8, 45.0)]),                      # Moyynkum
       Polygon([(58.2, 38.8), (61.8, 38.6), (63.6, 40.0), (61.5, 41.6), (59.0, 41.2), (57.4, 40.2)]),        # Karakum (Turkmen)
       Polygon([(60.6, 46.9), (64.5, 46.6), (65.2, 47.6), (62.0, 48.2), (60.5, 47.6)]),                      # Aral Karakum, Big Barsuki
       Polygon([(73.8, 44.9), (78.5, 44.6), (79.5, 45.4), (75.0, 45.7)]),                                     # Saryesik-Atyrau
       Polygon([(47.5, 46.4), (50.3, 46.6), (50.6, 48.3), (48.2, 48.9), (47.0, 47.5)])]                       # Ryn-peski (Bukey Horde)
dm = np.asarray(mask_of(DES, 1).filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
dots = (rng.random((H, W)) < .045 * dm) * landm
dots = ndimage.grey_dilation(dots, size=(2, 2)).astype(np.float32)
col = col * (1 - .22 * dots[..., None]) * (1 - .06 * dm[..., None]) + np.array([214, 178, 120], np.float32) * .06 * dm[..., None]
# water: muted sea-green wash, darker towards the coast, engraved ripple lines along the shore
dist = ndimage.distance_transform_edt(wm > .5).astype(np.float32)
wcol = np.array([176, 184, 160], np.float32) * (1 + .03 * low[..., None])
wcol = wcol * (1 - .10 * np.exp(-dist / 30)[..., None])
rip = np.exp(-dist / 16) * (dist < 60) * np.clip((np.cos(2 * np.pi * dist / 7.0) - .5) / .5, 0, 1) * (dist > 3)
wcol = wcol * (1 - .38 * rip[..., None]) + np.array([60, 70, 70], np.float32) * .0
col = col * (1 - wm[..., None]) + wcol * wm[..., None]

# ------------------------------------------------------------------ ink: coast, rivers, graticule (drawn at 2x, then reduced)
S = 2
ink = Image.new('L', (W * S, H * S), 0); di = ImageDraw.Draw(ink)
edge = np.asarray(Image.fromarray((wm > .5).astype(np.uint8) * 255).filter(ImageFilter.FIND_EDGES), np.float32) / 255
edge = ndimage.gaussian_filter(np.clip(ndimage.grey_dilation(edge, size=(2, 2)), 0, 1), .6)
RIV = {'Ural': 4, 'Volga': 5, 'Syr  Darya': 4, 'Amu  Darya': 4, 'Ertis': 4, 'Irtysh': 4, 'Esil': 3, 'Ishim': 3, 'Tobol': 3, 'Ile': 3, 'Naryn': 3, 'Ob': 3, 'Katun': 2, 'Biya': 2, 'Zarafshon': 2}
riv_ink = Image.new('L', (W * S, H * S), 0); dr = ImageDraw.Draw(riv_ink)
for f in D('ne_10m_rivers_lake_centerlines'):
    n = f['properties'].get('name')
    if n not in RIV: continue
    g = shape(f['geometry'])
    for ls in ([g] if g.geom_type == 'LineString' else g.geoms):
        pts = [tuple(v * S for v in px(x, y)) for x, y in ls.coords]
        dr.line(pts, fill=255, width=RIV[n], joint='curve')
grat = Image.new('L', (W * S, H * S), 0); dg = ImageDraw.Draw(grat)
for L in range(40, 95, 5):
    dg.line([tuple(v * S for v in px(L, LAT0)), tuple(v * S for v in px(L, LAT1))], fill=255, width=2)
for L in range(35, 60, 5):
    dg.line([tuple(v * S for v in px(LON0, L)), tuple(v * S for v in px(LON1, L))], fill=255, width=2)
riv = np.asarray(riv_ink.resize((W, H), Image.LANCZOS), np.float32) / 255 * landm
gr = np.asarray(grat.resize((W, H), Image.LANCZOS), np.float32) / 255
inkc = np.array([62, 42, 26], np.float32); rivc = np.array([70, 88, 92], np.float32)
col = col * (1 - .16 * gr[..., None]) + inkc * .16 * gr[..., None]
col = col * (1 - .8 * riv[..., None]) + rivc * .8 * riv[..., None]
col = col * (1 - .85 * edge[..., None]) + inkc * .85 * edge[..., None]
# paper fibres
fib = Image.new('L', (W, H), 0); dfb = ImageDraw.Draw(fib)
for _ in range(9000):
    x0, y0 = rng.uniform(0, W), rng.uniform(0, H); a = rng.uniform(0, np.pi); l = rng.uniform(4, 22)
    dfb.line([(x0, y0), (x0 + l * np.cos(a), y0 + l * np.sin(a))], fill=int(rng.uniform(20, 70)), width=1)
fb = np.asarray(fib, np.float32) / 255
col = col * (1 - .25 * fb[..., None]) + np.array([255, 246, 225], np.float32) * .25 * fb[..., None] * (rng.random((H, W))[..., None] < .5) + col * 0
import os; os.makedirs('tex', exist_ok=True)
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save('tex/base.jpg', quality=90)
print('tex/base.jpg')

# ------------------------------------------------------------------ oblasts of 1867-1868 (approximate, built from modern regions)
A1 = {}
for f in D('ne_10m_admin_1_states_provinces'):
    p = f['properties']
    if p['adm0_a3'] in ('KAZ', 'KGZ', 'UZB'): A1.setdefault((p['adm0_a3'], p['name']), []).append(shape(f['geometry']).buffer(0))
R = lambda *ks: unary_union([g for k in ks for g in A1[k]])
kaz = unary_union([shape(f['geometry']) for f in D('ne_10m_admin_0_countries') if f['properties']['ADM0_A3'] == 'KAZ']).buffer(0)
KZ = lambda n: ('KAZ', n)
west_k, east_k = box(60, 40, 73.5, 56), box(73.5, 40, 90, 56)
kar = R(KZ('Qaraghandy'))
# the Bukey Horde: Kazakhstan west of the Ural river, south of about 50.9 N
bukey = kaz.intersection(Polygon([(45, 50.9), (51.25, 50.9), (51.35, 50.2), (51.55, 49.2), (51.75, 48.2), (51.95, 47.1), (51.9, 46.5), (45, 46.5)]))
OB = {
 'ural':  R(KZ('West Kazakhstan'), KZ('Atyrau'), KZ('Mangghystau')).difference(bukey),
 'turgay': R(KZ('Aqtöbe'), KZ('Qostanay')),
 'akmola': unary_union([R(KZ('Aqmola'), KZ('North Kazakhstan'), KZ('Astana')), kar.intersection(west_k)]),
 'semey': unary_union([R(KZ('East Kazakhstan'), KZ('Pavlodar')), kar.intersection(east_k)]),
 'zhetisu': R(KZ('Almaty'), KZ('Almaty City'), ('KGZ', 'Ysyk-Köl'), ('KGZ', 'Chuy'), ('KGZ', 'Bishkek'), ('KGZ', 'Naryn')),
 'syr': R(KZ('Qyzylorda'), KZ('South Kazakhstan'), KZ('Zhambyl'), ('KGZ', 'Talas'), ('UZB', 'Tashkent'), ('UZB', 'Sirdaryo'), ('UZB', 'Jizzakh')),
}
OB = {k: v.buffer(0.02).buffer(-0.02).simplify(0.03) for k, v in OB.items()}
OB['bukey'] = bukey.simplify(0.03)
ZHUZ = {'orta': R(KZ('Qostanay'), KZ('North Kazakhstan'), KZ('Aqmola'), KZ('Astana'), KZ('Qaraghandy'), KZ('Pavlodar'), KZ('East Kazakhstan')).simplify(.04),
        'kishi': unary_union([R(KZ('West Kazakhstan'), KZ('Atyrau'), KZ('Mangghystau'), KZ('Aqtöbe')), R(KZ('Qyzylorda')).intersection(box(55, 40, 64.5, 50))]).simplify(.04)}
GG = {'turk': unary_union([OB['zhetisu'], OB['syr']]), 'oren': unary_union([OB['ural'], OB['turgay']]), 'sib': unary_union([OB['akmola'], OB['semey']])}


def rings(g, tol=0):
    g = g.buffer(0)
    if tol: g = g.simplify(tol)
    polys = [g] if g.geom_type == 'Polygon' else sorted(g.geoms, key=lambda p: -p.area)
    return [[[round(a, 1), round(b, 1)] for a, b in (px(x, y) for x, y in p.exterior.coords)] for p in polys if p.area > .02]


def plen(r): return float(sum(math.hypot(r[i + 1][0] - r[i][0], r[i + 1][1] - r[i][1]) for i in range(len(r) - 1)))


# crack lines: oblast borders inside Kazakhstan
inner = unary_union([g.boundary for k, g in OB.items() if k != 'bukey']).intersection(kaz.buffer(-0.08))
lines = []
for ls in ([inner] if inner.geom_type == 'LineString' else getattr(inner, 'geoms', [])):
    if ls.geom_type != 'LineString' or ls.length < .3: continue
    lines.append([[round(a, 1), round(b, 1)] for a, b in (px(x, y) for x, y in ls.simplify(.03).coords)])
out = {'W': W, 'H': H, 'P': P, 'LON0': LON0, 'LAT1': LAT1, 'KX': KX,
       'ob': {k: rings(v) for k, v in OB.items()}, 'zhuz': {k: rings(v) for k, v in ZHUZ.items()},
       'gg': {k: rings(v.buffer(.18, join_style=1), .05) for k, v in GG.items()},
       'kz': rings(kaz, .02), 'cracks': lines,
       'cen': {k: [round(c, 1) for c in px(*v.representative_point().coords[0])] for k, v in OB.items()}}
out['len'] = {k: [plen(r) for r in v] for k, v in out['ob'].items()}
out['glen'] = {k: [plen(r) for r in v] for k, v in out['gg'].items()}
out['clen'] = [plen(r) for r in lines]
json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
print('shapes.json', {k: len(v[0]) for k, v in out['ob'].items()}, len(lines), 'crack lines')

# ------------------------------------------------------------------ archive map (Arrowsmith 1872), warped into map space
im = Image.open('photos_src/arrowsmith.jpg').convert('RGB'); iw, ih = im.size
# control points read off the map: (lon, lat) -> (x, y) in the 1280 px wide scan
CP = [((48.03, 46.35), (112, 242)), ((55.10, 51.77), (335, 45)), ((59.8, 45.0), (470, 330)), ((60.36, 41.38), (465, 515)),
      ((69.25, 41.30), (720, 525)), ((73.5, 46.2), (890, 300)), ((50.0, 50.0), (205, 73)), ((50.0, 45.0), (172, 300)), ((50.0, 40.0), (150, 510))]
A = np.array([[1, lo, la, lo * la, lo * lo, la * la] for (lo, la), _ in CP]); bx = np.array([c[1][0] for c in CP]); by = np.array([c[1][1] for c in CP])
cx, *_ = np.linalg.lstsq(A, bx, rcond=None); cy, *_ = np.linalg.lstsq(A, by, rcond=None)
res = [(round(float(A[i] @ cx - bx[i]), 1), round(float(A[i] @ cy - by[i]), 1)) for i in range(len(CP))]
print('archive affine residuals (px):', res)
h2, w2 = H // 2, W // 2
yy2, xx2 = np.mgrid[0:h2, 0:w2].astype(np.float32) * 2
lo2 = LON0 + xx2 / (KX * P); la2 = LAT1 - yy2 / P
Q = [np.ones_like(lo2), lo2, la2, lo2 * la2, lo2 * lo2, la2 * la2]; sx = sum(c * q for c, q in zip(cx, Q)); sy = sum(c * q for c, q in zip(cy, Q))
src = np.asarray(im, np.float32)
warp = np.stack([ndimage.map_coordinates(src[..., c], [sy, sx], order=1, cval=235) for c in range(3)], -1)
inside = ((sx > 30) & (sx < iw - 30) & (sy > 30) & (sy < ih - 40)).astype(np.float32)
inside = ndimage.gaussian_filter(inside, 6)
Image.fromarray(np.dstack([np.clip(warp, 0, 255), inside * 255]).astype(np.uint8)).save('tex/archive.png')
print('tex/archive.png')

# ------------------------------------------------------------------ portraits: sepia, Speransky as a torn cut-out
def sepia(g, lo=(46, 30, 18), hi=(246, 232, 204)):
    a = np.asarray(g.convert('L'), np.float32) / 255
    a = np.clip((a - .04) / .92, 0, 1) ** 1.05
    return np.stack([lo[c] + (hi[c] - lo[c]) * a for c in range(3)], -1)
sp = Image.open('photos_src/speransky_gedan.jpg'); sw, sh = sp.size
sp = sp.crop((int(sw * .12), int(sh * .04), int(sw * .88), int(sh * .80)))
sp = sp.resize((600, int(600 * sp.size[1] / sp.size[0])), Image.LANCZOS); sw, sh = sp.size
rgb = sepia(sp)
pad = 26; Wp, Hp = sw + 2 * pad, sh + 2 * pad
yy3, xx3 = np.mgrid[0:Hp, 0:Wp].astype(np.float32)
# torn edge: distance to the rectangle edge, disturbed by noise
n1 = fbm(Hp, Wp, [(24, 1), (8, .6), (3, .5)], 9)
de = np.minimum.reduce([xx3, yy3, Wp - 1 - xx3, Hp - 1 - yy3])
alpha = np.clip((de - 10 - 9 * n1) / 1.5, 0, 1)
paperband = np.clip((de - 10 - 9 * n1 - 9) / 1.5, 0, 1)   # white paper rim inside the tear
canvas = np.zeros((Hp, Wp, 3), np.float32) + np.array([240, 228, 200], np.float32)
canvas[pad:pad + sh, pad:pad + sw] = rgb
canvas = canvas * paperband[..., None] + np.array([238, 226, 198], np.float32) * (1 - paperband[..., None])
Image.fromarray(np.dstack([np.clip(canvas, 0, 255), alpha * 255]).astype(np.uint8)).save('tex/speransky.png')
al = Image.open('photos_src/alex_photo.jpg'); aw, ah = al.size
al = al.crop((int(aw * .14), int(ah * .03), int(aw * .86), int(ah * .62))).resize((560, int(560 * (ah * .59) / (aw * .72))), Image.LANCZOS)
Image.fromarray(np.clip(sepia(al, (40, 26, 16), (250, 238, 214)), 0, 255).astype(np.uint8)).save('tex/alexander.png')
print('portraits done')
