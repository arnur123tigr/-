"""Prepare map shapes for the "3000 years of Kazakhstan history" reel -> shapes.json (lon/lat rings).
Needs Natural Earth geojson in data/ (from github.com/nvkelso/natural-earth-vector/geojson):
  ne_10m_admin_0_countries, ne_50m_admin_0_countries, ne_50m_lakes.
Kazakhstan = 'Kazakhstan' UNION 'Baikonur' (Natural Earth keeps Baikonur separate -> hole); holes dropped.
Historical states are hand-drawn approximate polygons, clipped to land."""
import json
from shapely.geometry import shape, Polygon, MultiPolygon, box
from shapely.ops import unary_union

D = 'data/'
def load(p, key):
    out = {}
    for f in json.load(open(D + p))['features']:
        k = f['properties'][key]; g = shape(f['geometry']).buffer(0)
        out[k] = unary_union([out[k], g]) if k in out else g
    return out
A10 = load('ne_10m_admin_0_countries.geojson', 'ADM0_A3')
A = load('ne_50m_admin_0_countries.geojson', 'ADM0_A3')
VIEW = box(-15, 5, 150, 78)

kz = unary_union([A10['KAZ'], A10['KAB']]).buffer(0.003).buffer(-0.003)
parts = kz.geoms if kz.geom_type == 'MultiPolygon' else [kz]
kz = MultiPolygon([Polygon(p.exterior) for p in parts if p.area > 0.01])
print('KZ holes', sum(len(p.interiors) for p in kz.geoms))

land = unary_union([g for k, g in A.items() if k not in ('KAZ', 'KAB')] + [kz]).intersection(VIEW)
lakes = {}
for f in json.load(open(D + 'ne_50m_lakes.geojson'))['features']:
    n = f['properties'].get('name') or ''
    g = shape(f['geometry']).buffer(0)
    if g.intersects(box(40, 35, 115, 58)) and g.area > .3: lakes[n] = g
print('lakes', list(lakes))
water = unary_union(list(lakes.values()))
land = land.difference(water)

def rings(g, tol=.04, minA=.05):
    g = g.simplify(tol, preserve_topology=True)
    ps = g.geoms if g.geom_type in ('MultiPolygon', 'GeometryCollection') else [g]
    out = []
    for p in ps:
        if p.geom_type != 'Polygon' or p.area < minA: continue
        out.append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords])
        for h in p.interiors:
            if Polygon(h).area > minA: out.append([[round(x, 2), round(y, 2)] for x, y in h.coords])
    return out
def clipL(pts): return Polygon(pts).buffer(0).intersection(land)

# --- historical blobs (approximate) ---
H = {}
H['saka'] = clipL([[54, 44], [58, 47], [64, 48.5], [70, 49.5], [76, 50.5], [84, 51.5], [88, 50], [87, 47], [83, 45], [80, 43], [76, 41.3], [71, 40.3], [65, 39.5], [59, 40.5], [55, 42]])
H['usun'] = clipL([[73.2, 43.3], [74.5, 45.6], [77, 46.8], [80.5, 46.6], [82.5, 45.2], [81.5, 43.2], [79, 42.0], [76, 42.0], [74, 42.4]])
H['kangju'] = clipL([[61.5, 42.0], [62.8, 44.8], [66, 46.2], [69.8, 45.6], [72.2, 43.6], [71, 41.4], [68.5, 40.2], [64.5, 40.0], [62.3, 40.7]])
H['turk'] = clipL([[34, 44.5], [38, 47.5], [45, 50.5], [52, 53.5], [60, 55.5], [70, 56], [80, 54.5], [90, 53.5], [100, 52.5], [110, 52], [120, 51.5], [127, 48.5], [126, 43.5], [120, 41.5], [111, 41], [100, 40.5], [92, 39.5], [84, 38.2], [76, 37], [68, 36.5], [60, 37.5], [53, 40], [47, 41.5], [41, 43]])
H['karakh'] = clipL([[60.5, 38.5], [61.8, 41.8], [65.5, 44.2], [70, 45.3], [75, 46.3], [79.5, 45.8], [80.8, 43.5], [79.5, 40.5], [77, 37.8], [72.5, 36.8], [67, 36.8], [62.5, 37.2]])
EXT = Polygon([[24, 44], [30, 50], [38, 55], [50, 58.5], [62, 58], [72, 57], [85, 54.5], [100, 54.5], [115, 54], [128, 52], [134, 45], [126, 38], [121, 30], [113, 22], [104, 21], [96, 26], [88, 28.5], [79, 30], [70, 30.5], [62, 26.5], [54, 26], [46, 29.5], [38, 33], [34, 37], [36, 41]])
GH = Polygon([[10, 43], [10, 70], [74, 70], [80, 52], [74, 49.5], [67, 46.5], [60, 43.5], [54, 41.5], [46, 41], [40, 42.5]])
IL = Polygon([[10, 10], [10, 43], [40, 42.5], [46, 41], [54, 41.5], [60, 41.5], [64, 38.5], [69, 36], [72, 30], [72, 10]])
CH = Polygon([[64, 38.5], [60, 41.5], [60, 43.5], [67, 46.5], [74, 49.5], [80, 52], [88, 50], [93, 45], [91, 38], [82, 31], [72, 30], [69, 36]])
ext = EXT.buffer(0).intersection(land)
H['gh'] = ext.intersection(GH); H['il'] = ext.intersection(IL); H['ch'] = ext.intersection(CH)
H['yuan'] = ext.difference(unary_union([GH, IL, CH]))
H['mongol'] = ext
H['empire'] = unary_union([A['RUS'].intersection(VIEW), kz, A['UZB'], A['TKM'], A['KGZ'], A['TJK']]).difference(water)
H['ussr'] = H['empire']

out = {'land': rings(land, .04, .08), 'lakes': {k: rings(v, .03, .1) for k, v in lakes.items()},
       'KAZ': rings(kz, .015, .01)}
for c in ['RUS', 'CHN', 'MNG', 'UZB', 'KGZ', 'TKM', 'TJK', 'AFG', 'IRN', 'UKR', 'AZE', 'GEO', 'ARM', 'TUR', 'IND', 'PAK']:
    out[c] = rings(A[c].intersection(VIEW), .05, .1)
for k, g in H.items(): out['h_' + k] = rings(g, .04, .05)
c = kz.centroid; out['center'] = [round(c.x, 2), round(c.y, 2)]
json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in out.items()}, 'KB', len(json.dumps(out)) // 1024)
