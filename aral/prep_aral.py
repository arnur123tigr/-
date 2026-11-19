"""Aral data: (1) erase the 2004 water from the Blue Marble textures inside the 1960 shoreline (inpaint -> dry seabed),
(2) shoreline contours for the drying animation (levels 0..1: 1960 shore -> 2014 remnants) from a harmonic-like field
f = d_shore / (d_shore + d_remnant), (3) shapes.json: countries (KAZ incl. Baikonur), Lithuania, rivers, lakes.
Usage: python3 prep_aral.py   (needs /home/user/data/*.geojson from Natural Earth, tex/aral.jpg, tex/cas.jpg, tex/world.jpg)"""
import json, numpy as np, cv2
from PIL import Image
from shapely.geometry import shape, box, Polygon, MultiPolygon
from shapely.ops import unary_union
from scipy import ndimage
from skimage import measure
Image.MAX_IMAGE_PIXELS = None
D = '/home/user/data/'
L = lambda n: json.load(open(D + n + '.geojson'))['features']
polys = lambda g: list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.01, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        p = p.simplify(tol)
        for q in polys(p):
            if q.is_empty: continue
            out.append([[round(x, 3), round(y, 3)] for x, y in q.exterior.coords])
    return out

hist = [shape(f['geometry']) for f in L('ne_10m_lakes_historic') if 'Aral' in (f['properties'].get('name') or '')][0]
lk = {f['properties']['name']: shape(f['geometry']) for f in L('ne_10m_lakes') if 'Aral' in (f['properties'].get('name') or '')}
north, south = lk['North Aral Sea'], lk['South Aral Sea']
north_small = north.buffer(-.045).buffer(.02)          # North Aral before the Kok-Aral dam (lower level, smaller)
north_small = max(polys(north_small), key=lambda p: p.area)

# ---- 1. erase water inside the 1960 shoreline ----
def erase(path, l0, l1, b0, b1):
    im = np.asarray(Image.open(path).convert('RGB')).copy(); h, w = im.shape[:2]
    lon0, lon1, lat0, lat1 = 57.5, 62.5, 43, 47.3
    x0, x1 = int((lon0 - l0) / (l1 - l0) * w), int((lon1 - l0) / (l1 - l0) * w)
    y0, y1 = int((b1 - lat1) / (b1 - b0) * h), int((b1 - lat0) / (b1 - b0) * h)
    sub = im[y0:y1, x0:x1]; sh, sw = sub.shape[:2]
    poly = np.zeros((sh, sw), np.uint8)
    g = hist.buffer(.05)
    pts = np.array([[(x - lon0) / (lon1 - lon0) * sw, (lat1 - y) / (lat1 - lat0) * sh] for x, y in g.exterior.coords], np.int32)
    cv2.fillPoly(poly, [pts], 1)
    r, gg, b = [sub[..., i].astype(int) for i in range(3)]
    water = ((gg - r > 4) | ((r + gg + b) < 200)) & (poly > 0)
    water = ndimage.binary_dilation(water, iterations=max(2, sw // 300)) & (poly > 0)
    res = cv2.inpaint(np.ascontiguousarray(sub[..., ::-1]), water.astype(np.uint8) * 255, max(3, sw // 120), cv2.INPAINT_TELEA)[..., ::-1].astype(float)
    # salty seabed: lighten, desaturate toward pale beige, fine grain
    rng = np.random.default_rng(5); n = ndimage.gaussian_filter(rng.standard_normal((sh, sw)), max(1, sw / 600)); n = n / (n.std() + 1e-6)
    pale = np.array([205, 192, 165], float)
    m = ndimage.gaussian_filter(water.astype(float), max(1, sw / 500))[..., None]
    res = res * .45 + pale * .55 + n[..., None] * 9
    sub[:] = np.clip(sub * (1 - m) + res * m, 0, 255).astype(np.uint8)
    Image.fromarray(im).save(path, quality=92); print('erased', path, water.sum())
erase('tex/aral.jpg', 55.5, 64.5, 42.5, 48.5)
erase('tex/cas.jpg', 50, 78, 34, 52)
erase('tex/world.jpg', -180, 180, -90, 90)

# ---- 2. drying contours ----
lon0, lon1, lat0, lat1, R = 57.9, 62.2, 43.2, 47.1, 120      # grid, R px per degree
gw, gh = int((lon1 - lon0) * R), int((lat1 - lat0) * R)
def raster(g):
    m = np.zeros((gh, gw), np.uint8)
    for p in polys(g):
        pts = np.array([[(x - lon0) * R, (lat1 - y) * R] for x, y in p.exterior.coords], np.int32); cv2.fillPoly(m, [pts], 1)
    return m > 0
sea = raster(hist); rem = raster(unary_union([south, north_small])) & sea
ds = ndimage.distance_transform_edt(sea); dr = ndimage.distance_transform_edt(~rem)
f = np.where(sea, ds / (ds + dr + 1e-6), 0); f[rem] = 1 + ndimage.distance_transform_edt(rem)[rem] * .01
f = ndimage.gaussian_filter(f, 1.2)
LEV = []
for k in np.linspace(0, 1, 61):
    lev = max(k, .015)
    cs = measure.find_contours(np.pad(f, 1), lev)
    rr = []
    for c in cs:
        if len(c) < 8: continue
        pg = Polygon([(lon0 + (x - 1) / R, lat1 - (y - 1) / R) for y, x in c])
        if not pg.is_valid: pg = pg.buffer(0)
        if pg.area < .002: continue
        rr += rings(pg, .006)
    LEV.append(rr)
print('levels', len(LEV), [len(l) for l in LEV[::10]])

# ---- 3. shapes ----
BB = box(40, 30, 90, 56); S = {'borders': [], 'cty': {}}
for ft in L('ne_10m_admin_0_countries'):
    g = shape(ft['geometry']); iso = ft['properties']['ADM0_A3']
    if iso == 'LTU': S['ltu'] = {'r': rings(g, .01, .01)}
    if not g.intersects(BB): continue
    g = g.intersection(BB)
    if iso != 'KAB': S['borders'] += rings(g, .02, .02)
    if iso in ('KAZ', 'KAB', 'UZB', 'TKM'): S['cty'][iso] = g
S['cty']['KAZ'] = unary_union([S['cty']['KAZ'], S['cty'].pop('KAB')]).buffer(.002)   # Baikonur is Kazakhstan territory
S['cty'] = {k: rings(v, .01, .01) for k, v in S['cty'].items()}
ltu = S['ltu']['r']; cx = np.mean([p[0] for r in ltu for p in r]); cy = np.mean([p[1] for r in ltu for p in r])
S['ltu'] = {'lat': cy, 'r': [[[x - cx, y - cy] for x, y in r] for r in ltu]}
hx, hy = hist.centroid.x, hist.centroid.y
S['aral1960c'] = {'lat': hy, 'r': [[[x - hx, y - hy] for x, y in r] for r in rings(hist, .01)]}
def river(names):
    out = []
    for ft in L('ne_10m_rivers_lake_centerlines'):
        if ' '.join((ft['properties'].get('name') or '').split()) in names:
            gm = ft['geometry']
            for ls in (gm['coordinates'] if gm['type'] == 'MultiLineString' else [gm['coordinates']]):
                out.append([[round(x, 3), round(y, 3)] for x, y in ls])
    return out
S['syr'] = river({'Syr Darya', 'Syrdariya'}); S['amu'] = river({'Amu Darya'})
S['aral1960'] = rings(hist, .004); S['north'] = rings(north, .004); S['north_small'] = rings(north_small, .004); S['south'] = rings(south, .004)
S['levels'] = LEV
json.dump(S, open('shapes.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in S.items()})
