"""One-time asset prep for the Atlakh 751 reel.
Needs Natural Earth geojson in ../../data/ (github.com/nvkelso/natural-earth-vector/geojson):
ne_50m_land, ne_10m_lakes, ne_10m_rivers_lake_centerlines, ne_10m_admin_0_countries.
 -> shapes.json (lon/lat rings: land, lakes, rivers, KAZ outline)
 -> paper.jpg   (1080x1920 faded old paper, screen-fixed)"""
import json, numpy as np, sys
from shapely.geometry import shape, box, LineString
from shapely.ops import unary_union
from PIL import Image, ImageFilter
D = sys.argv[1] if len(sys.argv) > 1 else '../../data/'
VIEW = box(0, -15, 170, 80)
def polys(g):
    return list(g.geoms) if g.geom_type in ('MultiPolygon', 'GeometryCollection') else [g]
def rings(g, tol, minA):
    g = g.simplify(tol, preserve_topology=True); out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < minA: continue
        out.append([[round(x, 3), round(y, 3)] for x, y in p.exterior.coords])
        out += [[[round(x, 3), round(y, 3)] for x, y in r.coords] for r in p.interiors if abs(r.envelope.area) > minA]
    return out
land = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(D + 'ne_50m_land.geojson'))['features']]).intersection(VIEW)
NEAR = box(50, 34, 92, 52)
lakes = []
for f in json.load(open(D + 'ne_10m_lakes.geojson'))['features']:
    g = shape(f['geometry']).buffer(0)
    if (g.intersects(NEAR) and g.area > .02) or g.area > 1.5: lakes.append(g)
water = unary_union(lakes).intersection(VIEW)
L = rings(land, .02, .01)
out = {'land': L, 'lakes': rings(water, .012, .02)}
riv = []
for f in json.load(open(D + 'ne_10m_rivers_lake_centerlines.geojson'))['features']:
    g = shape(f['geometry']); sr = f['properties'].get('scalerank') or 9
    if not g.intersects(VIEW): continue
    if g.intersects(NEAR) and sr <= 7 or sr <= 3:
        for l in (g.geoms if g.geom_type == 'MultiLineString' else [g]):
            l = l.simplify(.01)
            riv.append({'w': 1 if sr <= 5 else .7, 'p': [[round(x, 3), round(y, 3)] for x, y in l.coords]})
# hand-drawn small rivers missing from Natural Earth
riv.append({'w': .8, 'name': 'Talas', 'p': [[73.4, 42.33], [72.9, 42.42], [72.24, 42.52], [71.8, 42.6], [71.55, 42.72], [71.37, 42.88], [71.1, 43.1], [70.7, 43.4], [70.3, 43.85], [70.05, 44.35]]})
riv.append({'w': .8, 'name': 'Chu', 'p': [[75.9, 42.2], [75.6, 42.55], [75.3, 42.82], [74.8, 42.95], [74.3, 43.05], [73.7, 43.4], [73.1, 43.85], [72.4, 44.25], [71.6, 44.6], [70.6, 45.0], [69.6, 45.35]]})
out['rivers'] = riv
kz = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(D + 'ne_10m_admin_0_countries.geojson'))['features'] if f['properties']['ADM0_A3'] in ('KAZ', 'KAB')]).buffer(.01).buffer(-.01)
out['KAZ'] = [r for r in rings(kz, .03, .3)][:3]
json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in out.items()})
# paper
W, H = 1080, 1920; rng = np.random.default_rng(7)
def noise(n, sh=(H, W)):
    a = rng.random((max(2, n * sh[0] // sh[1]), n)).astype(np.float32)
    return np.asarray(Image.fromarray(a).resize((sh[1], sh[0]), Image.BICUBIC))
f = sum(noise(4 * 2 ** o) * .55 ** o for o in range(6)) / sum(.55 ** o for o in range(6))
fine = rng.random((H, W)).astype(np.float32)
fibers = np.asarray(Image.fromarray((rng.random((H, W)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .6)) ** 2)
vig = np.clip(r - .55, 0, 1) ** 1.6
base = np.array([.90, .83, .68]); stain = np.array([.74, .62, .42]); burn = np.array([.45, .32, .18])
k = np.clip((f - .42) * 2.4, 0, 1)[..., None]
img = base * (1 - k * .55) + stain * k * .55
img = img * (.95 + .06 * fine[..., None] + .08 * (fibers[..., None] - .5))
img = img * (1 - vig[..., None] * 1.1) + burn * vig[..., None] * 1.1 * .6
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save('paper.jpg', quality=92)
