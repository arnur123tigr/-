"""Natural Earth 10m -> shapes.json: highlighted countries, world borders, Syr Darya, Balkhash + Aral (Kazakhstan merged with Baikonur)."""
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union
D = '/home/user/data/'
F = json.load(open(D + 'ne_10m_admin_0_countries.geojson'))['features']
G = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in F}
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        for r in polys(p.simplify(tol)): out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
S = {'cty': {}, 'borders': [], 'riv': {}, 'lake': {}}
G['KAZ'] = unary_union([G['KAZ'], G['KAB']]).buffer(0.0005).buffer(-0.0005)
for iso in ('KAZ', 'CAN', 'NAM', 'AUS', 'UZB', 'RUS', 'CHN', 'KGZ', 'TKM', 'FRA', 'USA', 'IND', 'KOR', 'JPN'):
    g = G[iso]
    if iso in ('USA', 'RUS', 'CAN'): g = g.intersection(box(-170, 20, 180, 76))
    S['cty'][iso] = rings(g, .03, .3)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(box(-180, -60, 180, 84))
    if not g.is_empty: S['borders'] += rings(g, .04, .3)
for f in json.load(open(D + 'ne_10m_rivers_lake_centerlines.geojson'))['features']:
    if f['properties'].get('name') == 'Syr  Darya':
        for l in polys(shape(f['geometry']).simplify(.01)): S['riv'].setdefault('syr', []).append([[round(x, 3), round(y, 3)] for x, y in l.coords])
for f in json.load(open(D + 'ne_10m_lakes.geojson'))['features']:
    n = f['properties'].get('name')
    if n in ('Lake Balkhash', 'North Aral Sea', 'South Aral Sea'): S['lake'][n] = rings(shape(f['geometry']), .01)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()}, len(S['riv']['syr']))
