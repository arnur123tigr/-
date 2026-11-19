"""Natural Earth 10m -> shapes.json. Kazakhstan is merged with the Baikonur unit (no hole). Europe's five countries are stored
as offsets in km from their centroid (dx east, dy north) so the scene can move them into Kazakhstan at true size."""
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
for iso in ('KAZ', 'UZB', 'KGZ', 'TJK', 'TKM', 'AFG', 'RUS', 'CHN', 'MNG', 'TCD', 'BOL', 'LIE', 'CHE', 'AUT', 'IRN', 'NER', 'MLI', 'ETH'):
    g = G[iso]
    if iso == 'RUS': g = g.intersection(box(19, 35, 180, 82))
    S['cty'][iso] = rings(g, .005 if iso in ('LIE', 'CHE', 'AUT') else .03, 0 if iso == 'LIE' else .05)
BB = box(-25, -60, 160, 80)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(BB)
    if not g.is_empty: S['borders'] += rings(g, .05, .3)
# Europe: mainland parts only (France without overseas, Spain + Balearics, UK incl. N. Ireland)
EU = {'FRA': box(-6, 41, 10, 52), 'DEU': box(5, 47, 16, 56), 'ESP': box(-10, 35.5, 5, 44), 'ITA': box(6, 36, 19, 48), 'GBR': box(-9, 49.5, 2, 61)}
for iso, bb in EU.items():
    g = G[iso].intersection(bb); c = g.centroid; parts = []
    for p in polys(g):
        if p.area < .08: continue
        q = p.simplify(.02)
        parts.append([[round((x - c.x) * 111.32 * math.cos(math.radians(y)), 1), round((y - c.y) * 110.57, 1)] for x, y in q.exterior.coords])
    km2 = sum(shape({'type': 'Polygon', 'coordinates': [r]}).area for r in parts)
    S['eu'][iso] = {'c': [round(c.x, 2), round(c.y, 2)], 'r': parts}; print(iso, round(km2))
kz = G['KAZ']; print('KAZ deg-area poly count', len(polys(kz)), 'centroid', kz.centroid)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
