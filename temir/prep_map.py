"""Warm parchment map of Central Asia & neighbours (run once; Natural Earth geojson in ~/data).
map.jpg: equirectangular lon L0..L1, lat B0..B1, x = (lon-L0)*S*KX, y = (B1-lat)*S."""
import json, numpy as np, os
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape, box
D = os.path.expanduser('~/data/')
L0, L1, B0, B1, S, KX = 14, 102, 12, 72, 56, 0.77
W, H = int((L1 - L0) * S * KX), int((B1 - B0) * S)
print('map', W, H)
P = lambda lo, la: ((lo - L0) * S * KX, (B1 - la) * S)
clip = box(L0 - 2, B0 - 2, L1 + 2, B1 + 2)
def polys(f, names=None):
    out = []
    for ft in json.load(open(D + f))['features']:
        if names and ft['properties'].get('name') not in names: continue
        g = shape(ft['geometry']).intersection(clip)
        if g.is_empty: continue
        out += list(g.geoms) if hasattr(g, 'geoms') else [g]
    return [p for p in out if p.geom_type == 'Polygon']
mask = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(mask)
for p in polys('ne_50m_land.geojson'):
    dr.polygon([P(*c) for c in p.exterior.coords], fill=255)
    for r in p.interiors: dr.polygon([P(*c) for c in r.coords], fill=0)
for p in polys('ne_50m_lakes.geojson', {'Lake Balkhash'}) + polys('ne_10m_lakes_historic.geojson', {'Aral Sea'}):
    dr.polygon([P(*c) for c in p.exterior.coords], fill=0)
rng = np.random.default_rng(7)
def fbm(oct=6, base=5):
    acc = np.zeros((H, W), np.float32); amp = 1; tot = 0
    for o in range(oct):
        n = base * 2 ** o; a = rng.random((max(2, n * H // W), n)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray(a).resize((W, H), Image.BICUBIC)); tot += amp; amp *= .55
    return acc / tot
m = np.asarray(mask, np.float32) / 255
n1, n2 = fbm(), fbm(4, 60)
coast_in = np.asarray(mask.filter(ImageFilter.GaussianBlur(S * .35)), np.float32) / 255
paper = np.array([.93, .85, .69]); land_c = np.array([.86, .74, .52]); blot = np.array([.74, .60, .38])
k = np.clip((n1 - .4) * 2.0, 0, 1)[..., None]
land = land_c * (1 - k * .6) + blot * k * .6
land = land + (np.array([.80, .64, .40]) - land) * np.clip(1 - coast_in * 1.4, 0, 1)[..., None] * .5   # darker rim inside coast
sea = paper * .97 + np.array([-.06, -.02, .02])
img = land * m[..., None] + sea * (1 - m[..., None])
img = img * (.92 + .12 * n2[..., None])
im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
dr = ImageDraw.Draw(im, 'RGBA')
# offshore ripple lines (old-map style): dilated coast outlines
for i, (rad, a) in enumerate([(10, 110), (22, 70), (36, 40)]):
    e = mask.filter(ImageFilter.MaxFilter(2 * rad + 1)).filter(ImageFilter.FIND_EDGES)
    lay = Image.new('RGBA', (W, H), (90, 70, 50, 0)); lay.putalpha(e.point(lambda v: a if v > 40 else 0))
    im.paste(lay, (0, 0), lay)
# ink coastline
edge = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
ink = Image.new('RGBA', (W, H), (60, 38, 22, 0)); ink.putalpha(edge.point(lambda v: 230 if v > 40 else 0)); im.paste(ink, (0, 0), ink)
# rivers
RIV = {'Volga','Ural','Syr Darya','Amu Darya','Irtysh','Ob','Indus','Ganges','Tigris','Euphrates','Ili','Don','Dnieper','Kura','Yamuna','Zeravshan','Tobol','Ishim','Kama','Helmand'}
for ft in json.load(open(D + 'ne_50m_rivers_lake_centerlines.geojson'))['features']:
    if (ft['properties'].get('name') or '').replace('  ',' ') not in RIV: continue
    g = shape(ft['geometry']).intersection(clip)
    if g.is_empty: continue
    for l in (g.geoms if hasattr(g, 'geoms') else [g]):
        if l.geom_type != 'LineString': continue
        dr.line([P(*c) for c in l.coords], fill=(70, 80, 95, 170), width=4, joint='curve')
# mountains: little ink carets on mountain ranges (Tian Shan, Pamir, Hindu Kush, Caucasus, Altai, Zagros, Himalaya, Urals)
ranges = [[(70, 41.5), (74, 42.3), (78, 42.5), (82, 43), (86, 43)], [(72, 38.5), (74, 37.5)], [(66, 35), (70, 35.6), (72, 36.2)],
          [(40, 43.3), (44, 42.6), (48, 41.6)], [(85, 50), (88, 49.2), (90, 48.5)], [(48, 33), (51, 31), (54, 29)],
          [(76, 33.5), (80, 31), (84, 29), (88, 28), (92, 27.8)], [(59.5, 59), (59, 55), (58.5, 52)], [(32, 39), (36, 38), (40, 39.5)]]
for rg in ranges:
    for (a, b) in zip(rg, rg[1:]):
        for t in np.linspace(0, 1, 6, endpoint=False):
            lo, la = a[0] + (b[0] - a[0]) * t + rng.normal(0, .25), a[1] + (b[1] - a[1]) * t + rng.normal(0, .35)
            x, y = P(lo, la); s = 16 + rng.random() * 10
            dr.line([(x - s, y + s * .6), (x, y - s * .6), (x + s, y + s * .6)], fill=(75, 50, 30, 200), width=4, joint='curve')
            dr.line([(x, y - s * .6), (x + s * .5, y + s * .6)], fill=(75, 50, 30, 90), width=3)
im.save('map.jpg', quality=90)
json.dump(dict(L0=L0, L1=L1, B0=B0, B1=B1, S=S, KX=KX, W=W, H=H), open('map.json', 'w'))
