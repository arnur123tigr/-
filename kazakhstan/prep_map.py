"""Prepare map assets (run once; needs data/ with Natural Earth files, see README in build.sh):
 map_hi.jpg  - Natural Earth II, Miller projection, lon -20..150, lat -55..85, 26 px/deg, satellite-style grade
 world.jpg   - same raster, equirectangular 2048x1024 (texture for the globe scene)
 shapes.json - country outlines in lon/lat. Kazakhstan = Natural Earth 'Kazakhstan' UNION 'Baikonur'
               (Natural Earth keeps the leased Baikonur area as a separate unit, which leaves a hole; we fill it)."""
import json, math, numpy as np
from PIL import Image
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
Image.MAX_IMAGE_PIXELS = None
D = 'data/'
src = np.asarray(Image.open(D + 'NE2_HR_LC_SR_W.tif').convert('RGB'))
H0, W0 = src.shape[:2]; ppd = W0 / 360
my = lambda lat: 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * lat * math.pi / 180)) * 180 / math.pi

def grade(out):
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    ocean = np.clip((b - r - .08) / .12, 0, 1)[..., None]
    lum = out.mean(-1, keepdims=True)
    land = (np.clip(lum + (out - lum) * 1.15, 0, 1) ** 2.2) * np.array([.95, .98, .82])
    deep = np.array([.06, .24, .32]); shallow = np.array([.20, .50, .55])
    sea = deep + (shallow - deep) * np.clip((lum - .45) / .35, 0, 1) ** 1.5
    return np.clip(land * (1 - ocean) + sea * ocean, 0, 1)

LON0, LON1, LAT0, LAT1, S = -20, 150, -55, 85, 26
Y0, Y1 = my(LAT0), my(LAT1)
w, h = int((LON1 - LON0) * S), int((Y1 - Y0) * S)
xs = ((LON0 + (np.arange(w) + .5) / S + 180) % 360 * ppd).astype(int).clip(0, W0 - 1)
yv = Y1 - (np.arange(h) + .5) / S
lat = (np.arctan(np.exp(yv * math.pi / 180 / 1.25)) - math.pi / 4) / 0.4 * 180 / math.pi
ys = ((90 - lat) * ppd).astype(int).clip(0, H0 - 1)
out = grade(src[ys][:, xs].astype(np.float32) / 255)
Image.fromarray((out * 255).astype(np.uint8)).save('map_hi.jpg', quality=88)
print('map_hi', w, h, 'Y1', Y1)

sm = np.asarray(Image.fromarray(src).resize((2048, 1024), Image.LANCZOS)).astype(np.float32) / 255
Image.fromarray((grade(sm) * 255).astype(np.uint8)).save('world.jpg', quality=88)

def geo(path, key):
    return {f['properties'][key]: shape(f['geometry']) for f in json.load(open(D + path))['features']}
A = geo('adm10.geojson', 'ADM0_A3')
kz = unary_union([A['KAZ'], A['KAB']]).buffer(0.0005).buffer(-0.0005)   # merge Baikonur into Kazakhstan, close slivers
# keep only the outer ring of each part -> guaranteed no holes inside Kazakhstan
from shapely.geometry import Polygon, MultiPolygon
parts = kz.geoms if kz.geom_type == 'MultiPolygon' else [kz]
kz = MultiPolygon([Polygon(p.exterior) for p in parts if p.area > 0.01])
print('KZ parts', len(kz.geoms), 'holes', sum(len(p.interiors) for p in kz.geoms))
A5 = geo('adm50.geojson', 'ADM0_A3')
west_eu = unary_union([A5[c] for c in ['FRA', 'DEU', 'NLD', 'BEL', 'LUX', 'CHE', 'AUT', 'LIE']])
S1 = json.load(open(D + 'adm1_50.geojson'))['features']
texas = next(shape(f['geometry']) for f in S1 if f['properties'].get('name') == 'Texas')

def rings(g, tol):
    g = g.simplify(tol, preserve_topology=True)
    ps = g.geoms if g.geom_type == 'MultiPolygon' else [g]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in ps if p.area > tol * tol * 4]

out = {'KAZ': rings(kz, .02), 'WEU': rings(west_eu, .03), 'TEX': rings(texas, .03)}
for c in ['RUS', 'CHN', 'MNG', 'UZB', 'KGZ', 'TKM']:
    out[c] = rings(A5[c], .05)
out['RUS'] = [r for r in out['RUS'] if min(p[0] for p in r) > -10]   # drop the part across the antimeridian
c = kz.centroid; out['center'] = [round(c.x, 2), round(c.y, 2)]
b = A['KAB'].centroid; out['baikonur'] = [round(b.x, 2), round(b.y, 2)]
json.dump(out, open('shapes.json', 'w'))

# ---- ethnic mosaic (mosaic.png): Voronoi patches inside Kazakhstan, Miller grid lon 46..88, lat 40..56, 20 px/deg
import shapely
ML0, ML1, MA0, MA1, MS = 46, 88, 40, 56, 20
mw, mh = (ML1 - ML0) * MS, int((my(MA1) - my(MA0)) * MS)
lon = ML0 + (np.arange(mw) + .5) / MS; yy = my(MA1) - (np.arange(mh) + .5) / MS
la = (np.arctan(np.exp(yy * math.pi / 180 / 1.25)) - math.pi / 4) / 0.4 * 180 / math.pi
LO, LA = np.meshgrid(lon, la); pts = np.c_[LO.ravel(), LA.ravel()]
inside = np.zeros(len(pts), bool)
inside = shapely.contains_xy(kz, pts[:, 0], pts[:, 1])
rng = np.random.default_rng(7); n = 60
seeds = np.c_[rng.uniform(46, 88, n), rng.uniform(40, 56, n)]
idx = (((pts[:, None, :] - seeds[None]) * [0.68, 1]) ** 2).sum(-1).argmin(1)
pal = np.array([[236, 72, 120], [70, 200, 90], [255, 200, 40], [70, 120, 230], [250, 120, 40], [150, 90, 220], [40, 190, 210], [230, 60, 60], [160, 220, 60], [240, 150, 200]])
col = pal[rng.integers(0, len(pal), n)][idx]
img = np.dstack([col.reshape(mh, mw, 3), (inside * 235).reshape(mh, mw)]).astype(np.uint8)
im = Image.fromarray(img, 'RGBA'); im.save('mosaic.png'); print('mosaic', mw, mh, 'ytop', my(MA1))
print({k: len(v) for k, v in out.items()}, 'baikonur', out['baikonur'])
