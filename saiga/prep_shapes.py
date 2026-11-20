"""Natural Earth 10m -> shapes.json. Kazakhstan is merged with the Baikonur unit (no hole)."""
import json, math
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
        q = p.simplify(tol)
        for r in polys(q): out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
S = {'cty': {}, 'borders': [], 'eu': {}}
G['KAZ'] = unary_union([G['KAZ'], G['KAB']]).buffer(0.0005).buffer(-0.0005)
for iso in ('KAZ', 'UZB', 'KGZ', 'TKM', 'RUS', 'CHN', 'MNG'):
    g = G[iso]
    if iso == 'RUS': g = g.intersection(box(19, 35, 180, 82))
    S['cty'][iso] = rings(g, .005 if iso in ('LIE', 'CHE', 'AUT') else .03, 0 if iso == 'LIE' else .05)
BB = box(-25, -60, 160, 80)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(BB)
    if not g.is_empty: S['borders'] += rings(g, .05, .3)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
