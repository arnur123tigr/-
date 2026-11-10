"""One-time asset prep (data/ = Natural Earth: ne_50m_land, ne_50m_lakes, ne_50m_admin_0_countries, ne_50m_rivers_lake_centerlines geojson, NE2_50M_SR_W raster).
 map.jpg   - old-map look like the original reel: khaki land with relief, teal textured sea (Mercator, lon L0..L1, lat B0..B1, S px/deg)
 sat.jpg   - dark satellite crop of the Caribbean (Mercator, same formula, SS px/deg)
 shapes.json - 1803 territories (USA, Louisiana, Britain, Spain), France, Britain (Europe), Haiti, Hispaniola, Mississippi river"""
import json, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, box, mapping
from shapely.ops import unary_union
Image.MAX_IMAGE_PIXELS = None
D = 'data/'
my = lambda lat: math.log(math.tan(math.pi / 4 + lat * math.pi / 360)) * 180 / math.pi
L0, L1, B0, B1, S = -135, 45, -60, 80, 20
W, H = (L1 - L0) * S, int((my(B1) - my(B0)) * S)
print('map', W, H, 'YTOP', my(B1))
def P(lo, la): return ((lo - L0) * S, (my(B1) - my(max(-80, min(84, la)))) * S)
def polys(g): return g.geoms if g.geom_type == 'MultiPolygon' else [g]
mask = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(mask)
for f in json.load(open(D + 'ne_50m_land.geojson'))['features']:
    for p in polys(shape(f['geometry'])):
        dr.polygon([P(*c) for c in p.exterior.coords], fill=255)
        for r in p.interiors: dr.polygon([P(*c) for c in r.coords], fill=0)
for f in json.load(open(D + 'ne_50m_lakes.geojson'))['features']:
    if (f['properties'].get('scalerank') or 9) > 2: continue
    for p in polys(shape(f['geometry'])): dr.polygon([P(*c) for c in p.exterior.coords], fill=0)
# relief from the Natural Earth II raster (10800x5400, 30 px/deg, lon -180.., lat 90..)
src = Image.open(D + 'NE2_50M_SR_W/NE2_50M_SR_W.tif').convert('L')
ys = np.array([(90 - math.degrees(2 * math.atan(math.exp(math.radians(my(B1) - (j + .5) / S))) - math.pi / 2)) * 30 for j in range(H)])
xs = np.array([((L0 + (i + .5) / S) + 180) * 30 for i in range(W)])
A = np.asarray(src, np.float32) / 255
rel = A[np.clip(ys.astype(int), 0, 5399)][:, np.clip(xs.astype(int), 0, 10799)]
rel = np.asarray(Image.fromarray((rel * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255
rng = np.random.default_rng(3)
def fbm(oct=6, base=6):
    acc = np.zeros((H, W), np.float32); amp = 1; tot = 0
    for o in range(oct):
        n = base * 2 ** o; a = rng.random((max(2, n * H // W), n)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray(a).resize((W, H), Image.BICUBIC)); tot += amp; amp *= .55
    return acc / tot
m = np.asarray(mask, np.float32) / 255
n1, n2 = fbm(), fbm(5, 30)
halo = np.asarray(mask.filter(ImageFilter.GaussianBlur(S * .35)), np.float32) / 255
hl = (rel - np.median(rel[m > .5])) if (m > .5).any() else rel
land = np.array([.60, .55, .40])[None, None] * (1 + 1.1 * hl[..., None]) * (.94 + .12 * n1[..., None])
sea = np.array([.32, .47, .47])[None, None] * (.9 + .16 * n1[..., None] + .08 * n2[..., None])
sea = sea - np.array([.05, .06, .05]) * (halo * (1 - m))[..., None] * 0 + np.array([.03, .04, .04]) * (halo * (1 - m))[..., None]
img = land * m[..., None] + sea * (1 - m[..., None])
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save('map.jpg', quality=88)

# satellite Caribbean crop
SL0, SL1, SB0, SB1, SS = -92, -56, 6, 32, 48
SW, SH_ = (SL1 - SL0) * SS, int((my(SB1) - my(SB0)) * SS)
print('sat', SW, SH_, 'YTOP', my(SB1))
srcc = Image.open(D + 'NE2_50M_SR_W/NE2_50M_SR_W.tif').convert('RGB')
x0, x1 = (SL0 + 180) * 30, (SL1 + 180) * 30; y0, y1 = (90 - SB1) * 30, (90 - SB0) * 30
crop = np.asarray(srcc.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.BICUBIC), np.float32) / 255
ys = np.array([(SB1 - math.degrees(2 * math.atan(math.exp(math.radians(my(SB1) - (j + .5) / SS))) - math.pi / 2)) * 60 for j in range(SH_)])
xs = np.arange(SW) * 60 / SS
sat = crop[np.clip(ys.astype(int), 0, crop.shape[0] - 1)][:, np.clip(xs.astype(int), 0, crop.shape[1] - 1)]
smask = Image.new('L', (SW, SH_), 0); d2 = ImageDraw.Draw(smask)
def SP(lo, la): return ((lo - SL0) * SS, (my(SB1) - my(la)) * SS)
for f in json.load(open(D + 'ne_50m_land.geojson'))['features']:
    for p in polys(shape(f['geometry'])):
        if p.bounds[2] < SL0 - 5 or p.bounds[0] > SL1 + 5 or p.bounds[3] < SB0 - 5 or p.bounds[1] > SB1 + 5: continue
        d2.polygon([SP(*c) for c in p.exterior.coords], fill=255)
sm = np.asarray(smask.filter(ImageFilter.GaussianBlur(2)), np.float32)[..., None] / 255
shal = np.asarray(smask.filter(ImageFilter.GaussianBlur(SS * .6)), np.float32)[..., None] / 255
ocean = np.array([.04, .14, .20]) + np.array([.12, .38, .36]) * shal ** 1.2           # deep navy with turquoise shallows near coasts
landc = np.clip((sat - .08) * 1.0, 0, 1) ** 1.25 * np.array([.82, .92, .72])
out = landc * sm + ocean * (1 - sm)
out *= (.95 + .1 * np.asarray(Image.fromarray((rng.random((SH_ // 8, SW // 8)) * 255).astype(np.uint8)).resize((SW, SH_), Image.BICUBIC), np.float32)[..., None] / 255)
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save('sat.jpg', quality=88)

# ---- territories ----
C = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in json.load(open(D + 'ne_50m_admin_0_countries.geojson'))['features']}
usa48 = C['USA'].intersection(box(-126, 24, -66, 50))
miss = [(-95.2, 47.6), (-93.1, 45.0), (-91.2, 43.5), (-91.0, 41.0), (-90.2, 38.7), (-89.2, 37.0), (-90.0, 35.1), (-91.1, 33.0), (-91.6, 31.0)]
east = Polygon(miss + [(-91.6, 31.0), (-81.6, 31.0), (-81.4, 30.6), (-60, 30.6), (-60, 52), (-95.2, 52)])
us1803 = usa48.intersection(east)
lw = [(-89.0, 29.0), (-89.6, 31.0)] # Isle of Orleans boundary
louis_poly = Polygon([(-89.2, 28.5), (-89.6, 30.2), (-91.6, 31.0)] + miss[::-1] + [(-95.2, 49.0), (-114, 49.0), (-113.5, 47.5), (-111, 44.5), (-109, 42.5),
                      (-106.5, 40.5), (-105.5, 38.5), (-103, 37), (-100, 36.5), (-100, 34.5), (-94.0, 33.0), (-93.8, 29.6), (-93.8, 28.5)])
louis = usa48.intersection(louis_poly)
oregon = usa48.intersection(Polygon([(-130, 42), (-111, 42), (-109, 42.5), (-111, 44.5), (-113.5, 47.5), (-114, 49), (-130, 49)]))
ca = [k for k in ('MEX', 'GTM', 'BLZ', 'HND', 'SLV', 'NIC', 'CRI', 'PAN', 'CUB', 'DOM', 'PRI') if k in C]
spain = unary_union([usa48.difference(us1803).difference(louis).difference(oregon)] + [C[k] for k in ca])
brit = unary_union([C['CAN']])
def rings(g, tol=.04, minA=.02):
    g = g.simplify(tol, preserve_topology=True); out = []
    for p in polys(g) if g.geom_type in ('Polygon', 'MultiPolygon') else [x for x in g.geoms if x.geom_type == 'Polygon']:
        if p.area > minA: out.append([[round(x, 3), round(y, 3)] for x, y in p.exterior.coords])
    return out
def ctr(g): c = g.representative_point(); return [round(c.x, 2), round(c.y, 2)]
out = {}
for k, g, tol, mA in [('US', us1803, .03, .05), ('LA', louis, .03, .05), ('SP', spain, .03, .05), ('BR', brit, .05, .3), ('OR', oregon, .03, .1),
                      ('FR', C['FRA'].intersection(box(-6, 41, 10, 52)), .015, .01), ('GB', unary_union([C['GBR'], C['IRL']]), .015, .02), ('ES', C['ESP'].intersection(box(-10, 35, 5, 44)), .02, .05),
                      ('HT', C['HTI'], .006, .002), ('DO', C['DOM'], .006, .002), ('CU', C['CUB'], .01, .01), ('USNOW', usa48, .03, .05)]:
    out[k] = rings(g, tol, mA); out['c_' + k] = ctr(g)
# Mississippi river from NE rivers (named), fallback to hand line
rv = []
for f in json.load(open(D + 'ne_50m_rivers_lake_centerlines.geojson'))['features']:
    if (f['properties'].get('name') or '').startswith('Mississippi'):
        g = shape(f['geometry']); rv += [[[round(x, 3), round(y, 3)] for x, y in l.coords] for l in (g.geoms if g.geom_type == 'MultiLineString' else [g])]
out['MS'] = rv or [miss]
json.dump(out, open('shapes.json', 'w'))
print({k: len(v) for k, v in out.items() if not k.startswith('c_')})
