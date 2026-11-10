"""One-time asset prep (data/ = Natural Earth: NE2_HR_LC_SR_W.tif raster, ne_10m_land, ne_10m/50m_admin_0_countries geojson).
 sat.jpg  - satellite-style North Atlantic (Mercator, lon L0..L1, lat B0..B1, S px/deg): dark teal sea, light shelf near coasts, white ice
 hi.jpg   - same look, sharper crop around Iceland + south Greenland (HS px/deg), drawn on top when zoomed in
 shapes.json - Greenland, Iceland, Norway, Florida, Spain outlines (lon/lat)
 parch.jpg is reused from the africa/ reel (whole world parchment, 14 px/deg)."""
import json, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape, box
from shapely.ops import unary_union
Image.MAX_IMAGE_PIXELS = None
D = 'data/'
my = lambda lat: math.log(math.tan(math.pi / 4 + lat * math.pi / 360)) * 180 / math.pi
iy = lambda y: math.degrees(2 * math.atan(math.exp(math.radians(y))) - math.pi / 2)
src = Image.open(D + 'NE2_HR_LC_SR_W.tif').convert('RGB'); SRC = np.asarray(src); H0, W0 = SRC.shape[:2]; PPD = W0 / 360
LAND = [shape(f['geometry']) for f in json.load(open(D + 'ne_10m_land.geojson'))['features']]
def polys(g): return g.geoms if g.geom_type == 'MultiPolygon' else [g]
rng = np.random.default_rng(5)
def make(L0, L1, B0, B1, S, name):
    YT = my(B1); W, H = int((L1 - L0) * S), int((YT - my(B0)) * S)
    print(name, W, H, 'YT', YT)
    xs = ((L0 + (np.arange(W) + .5) / S + 180) * PPD).astype(int).clip(0, W0 - 1)
    lat = np.array([iy(YT - (j + .5) / S) for j in range(H)]); ys = ((90 - lat) * PPD).astype(int).clip(0, H0 - 1)
    img = SRC[ys][:, xs].astype(np.float32) / 255
    mask = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(mask)
    P = lambda lo, la: ((lo - L0) * S, (YT - my(max(-85, min(85, la)))) * S)
    bb = box(L0 - 2, B0 - 2, L1 + 2, B1 + 2)
    for g in LAND:
        if not g.intersects(bb): continue
        for p in polys(g):
            dr.polygon([P(*c) for c in p.exterior.coords], fill=255)
            for r in p.interiors: dr.polygon([P(*c) for c in r.coords], fill=0)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(S / 40)), np.float32)[..., None] / 255
    shelf = np.asarray(mask.filter(ImageFilter.GaussianBlur(S * .9)), np.float32)[..., None] / 255
    shelf2 = np.asarray(mask.filter(ImageFilter.GaussianBlur(S * .25)), np.float32)[..., None] / 255
    noise = np.asarray(Image.fromarray((rng.random((max(2, H // 40), max(2, W // 40))) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32)[..., None] / 255
    sea = np.array([.05, .22, .27]) + np.array([.10, .22, .20]) * np.clip(shelf * 1.6, 0, 1) ** 1.3 + np.array([.06, .12, .10]) * shelf2 + (noise - .5) * .03
    lum = img.mean(-1, keepdims=True)
    land = np.clip(lum + (img - lum) * 1.25, 0, 1) ** 1.35 * np.array([.96, 1.0, .9])
    out = land * m + sea * (1 - m)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(name, quality=90)
    return YT
y1 = make(-100, 40, -56, 84, 30, 'sat.jpg')
y2 = make(-56, -8, 57, 73, 80, 'hi.jpg')
C10 = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in json.load(open(D + 'ne_10m_admin_0_countries.geojson'))['features']}
C50 = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in json.load(open(D + 'ne_50m_admin_0_countries.geojson'))['features']}
def rings(g, tol, minA):
    g = g.simplify(tol, preserve_topology=True); out = []
    for p in polys(g):
        if p.area > minA: out.append([[round(x, 3), round(y, 3)] for x, y in p.exterior.coords])
    return out
out = {'GRL': rings(C10['GRL'], .03, .05), 'ISL': rings(C10['ISL'], .01, .02),
       'NOR': rings(C50['NOR'].intersection(box(3, 57, 32, 72)), .03, .05),
       'FLA': rings(C50['USA'].intersection(box(-87.6, 24.4, -79.8, 31.0)), .02, .02),
       'ESP': rings(C50['ESP'].intersection(box(-10, 35, 5, 44)), .02, .05),
       'YT': [y1, y2]}
json.dump(out, open('shapes.json', 'w'))
print({k: len(v) for k, v in out.items()})
