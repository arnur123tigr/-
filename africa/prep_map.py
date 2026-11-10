"""Prepare assets (run once; data/ holds Natural Earth: ne_50m_land, ne_50m/110m_admin_0_countries geojson, NE2_50M_SR_W raster).
 parch.png  - antique parchment world map (Mercator, lon -180..180, lat -78..84, S px/deg), like the original reel
 world.jpg  - satellite texture, equirectangular 2048x1024 (globe + gores)
 shapes.json- country outlines in lon/lat for highlights; w110 = all countries for the 'true size' panel"""
import json, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape, Polygon, MultiPolygon, box
from shapely.ops import unary_union
Image.MAX_IMAGE_PIXELS = None
D = 'data/'
my = lambda lat: math.log(math.tan(math.pi / 4 + lat * math.pi / 360)) * 180 / math.pi
S, LAT0, LAT1 = 14, -78, 84
W, H = 360 * S, int((my(LAT1) - my(LAT0)) * S)
print('parch', W, H, 'Ytop', my(LAT1))
def P(lo, la): return ((lo + 180) * S, (my(LAT1) - my(max(LAT0 - 5, min(LAT1 + 5, la)))) * S)
mask = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(mask)
for f in json.load(open(D + 'ne_50m_land.geojson'))['features']:
    g = shape(f['geometry'])
    for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
        dr.polygon([P(*c) for c in p.exterior.coords], fill=255)
        for r in p.interiors: dr.polygon([P(*c) for c in r.coords], fill=0)
rng = np.random.default_rng(3)
def fbm(oct=6, base=6):
    acc = np.zeros((H, W), np.float32); amp = 1; tot = 0
    for o in range(oct):
        n = base * 2 ** o; a = rng.random((max(2, n * H // W), n)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray(a).resize((W, H), Image.BICUBIC)); tot += amp; amp *= .55
    return acc / tot
m = np.asarray(mask, np.float32) / 255
n1, n2, n3 = fbm(), fbm(5, 10), fbm(4, 40)
inner = np.asarray(mask.filter(ImageFilter.GaussianBlur(S * 1.2)), np.float32) / 255     # land depth
outer = np.asarray(mask.filter(ImageFilter.GaussianBlur(S * .5)), np.float32) / 255
# land: parchment tan with darker brown blotches, lighter rim near coasts
tan = np.array([.72, .56, .34]); dark = np.array([.42, .31, .17]); light = np.array([.85, .72, .50])
k = np.clip((n1 - .35) * 2.2, 0, 1)[..., None]
land = tan * (1 - k) + dark * k
land = land * (.82 + .3 * n3[..., None]) + (light - land) * np.clip(1 - inner * 1.6, 0, 1)[..., None] * .55
# ocean: dark olive-green, mottled, slightly lighter halo along coasts
sea = np.array([.13, .17, .11]) + (np.array([.25, .30, .20]) - np.array([.13, .17, .11])) * np.clip((n2 - .3) * 1.8, 0, 1)[..., None]
sea = sea * (.85 + .3 * n3[..., None]) + np.array([.10, .10, .05]) * (outer * (1 - m))[..., None]
img = land * m[..., None] + sea * (1 - m[..., None])
img = img * (1 - .25 * (1 - outer[..., None]) * m[..., None]) * 0 + img
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save('parch.jpg', quality=90)

src = Image.open(D + 'NE2_50M_SR_W/NE2_50M_SR_W.tif').convert('RGB').resize((2048, 1024), Image.LANCZOS)
src.save('world.jpg', quality=90)

C = {f['properties']['ADM0_A3']: f for f in json.load(open(D + 'ne_50m_admin_0_countries.geojson'))['features']}
def rings(g, tol, minA=None):
    g = g.simplify(tol, preserve_topology=True)
    ps = g.geoms if g.geom_type == 'MultiPolygon' else [g]
    return [[[round(x, 2), round(y, 2)] for x, y in p.exterior.coords] for p in ps if p.area > (minA if minA is not None else tol * tol * 6)]
G = lambda a: shape(C[a]['geometry'])
afr = unary_union([shape(f['geometry']) for f in C.values() if f['properties']['CONTINENT'] == 'Africa']).buffer(.02).buffer(-.02)
def largest(g): return max(g.geoms, key=lambda p: p.area) if g.geom_type == 'MultiPolygon' else g
rus = G('RUS'); rus = unary_union([Polygon([(x + 360 if x < 0 else x, y) for x, y in p.exterior.coords]) for p in rus.geoms])
eu_ex = {'RUS', 'KAZ', 'TUR', 'GEO', 'ARM', 'AZE', 'CYN', 'CYP'}
eur = unary_union([shape(f['geometry']) for a, f in C.items() if f['properties']['CONTINENT'] == 'Europe' and a not in eu_ex]).intersection(box(-25, 34, 45, 72)).buffer(.03).buffer(-.03)
usa = largest(G('USA'))
out = {'AFR': rings(afr, .08, .3), 'GRL': rings(G('GRL'), .08, .3), 'COD': rings(G('COD'), .05), 'RUS': rings(rus, .08, .5),
       'USA': rings(usa, .06), 'CHN': rings(G('CHN'), .06, .3), 'IND': rings(G('IND'), .05, .3), 'JPN': rings(G('JPN'), .04, .2), 'EUR': rings(eur, .06, .4)}
for k, g in [('GRL', G('GRL')), ('COD', G('COD')), ('RUS', rus), ('USA', usa), ('CHN', G('CHN')), ('IND', G('IND')), ('JPN', G('JPN')), ('EUR', eur), ('AFR', afr)]:
    c = g.centroid; out['c_' + k] = [round(c.x, 2), round(c.y, 2)]
w = []
for f in json.load(open(D + 'ne_110m_admin_0_countries.geojson'))['features']:
    g = shape(f['geometry'])
    for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
        if p.area < .5: continue
        r = [[round(x, 1), round(y, 1)] for x, y in p.simplify(.15).exterior.coords]
        c = p.centroid; w.append({'c': [round(c.x, 2), round(c.y, 2)], 'r': r})
out['w110'] = w
json.dump(out, open('shapes.json', 'w'))
print({k: (len(v) if isinstance(v, list) else v) for k, v in out.items() if not k.startswith('c_')})
