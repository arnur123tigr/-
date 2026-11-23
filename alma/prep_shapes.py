"""Natural Earth 10m -> shapes.json: KZ (with Baikonur), borders for the Silk Road map (Europe to China), Jungar Alatau polygon."""
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
S = {'cty': {}, 'borders': [], 'reg': {}}
G['KAZ'] = unary_union([G['KAZ'], G['KAB']]).buffer(0.0005).buffer(-0.0005)
for iso in ('KAZ',): S['cty'][iso] = rings(G[iso], .02, .05)
BB = box(-12, 22, 100, 64)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(BB)
    if not g.is_empty: S['borders'] += rings(g, .04, .3)
for f in json.load(open(D + 'ne_10m_geography_regions_polys.geojson'))['features']:
    n = f['properties'].get('NAME')
    if n == 'Alataw Mts.': S['reg']['JET'] = rings(shape(f['geometry']), .02)
json.dump(S, open('shapes.json', 'w'))
print({k: len(v) for k, v in S.items()})
