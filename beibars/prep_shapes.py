"""Natural Earth 10m (shapefiles in /home/user/data/ne) -> shapes.json: Egypt, Syria and Kazakhstan (with Baikonur) as rings,
thin borders for the region, and the main rivers as lines (drawn thin turquoise)."""
import json, shapefile
from shapely.geometry import shape, box
from shapely.ops import unary_union
sf = shapefile.Reader('/home/user/data/ne/ne_10m_admin_0_countries.shp')
G = {sr.record['ADM0_A3']: shape(sr.shape.__geo_interface__) for sr in sf.iterShapeRecords()}
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        for r in polys(p.simplify(tol)): out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
S = {'cty': {}, 'borders': [], 'rivers': []}
G['KAZ'] = unary_union([G['KAZ'], G['KAB']]).buffer(0.0005).buffer(-0.0005)
for iso in ('KAZ', 'EGY', 'SYR'): S['cty'][iso] = rings(G[iso], .02, .05)
BB = box(0, 10, 100, 70)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(BB)
    if not g.is_empty: S['borders'] += rings(g, .03, .2)
R = shapefile.Reader('/home/user/data/ne/ne_10m_rivers_lake_centerlines.shp')
KEEP = {'Nile', 'Volga', 'Don', 'Dnipro', 'Dnepre', 'Danube', 'Ural', 'Irtysh', 'Syr Darya', 'Amu Darya', 'Euphrates', 'Tigris', 'Dniester', 'Ishim', 'Tobol'}
for sr in R.iterShapeRecords():
    if sr.record['name'] not in KEEP: continue
    g = shape(sr.shape.__geo_interface__).intersection(BB)
    for l in (g.geoms if hasattr(g, 'geoms') else [g]):
        if l.geom_type == 'LineString' and l.length > .2: S['rivers'].append([[round(x, 3), round(y, 3)] for x, y in l.simplify(.03).coords])
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S['cty'].items()}, len(S['borders']), len(S['rivers']))
