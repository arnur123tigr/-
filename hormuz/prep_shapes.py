"""Natural Earth 10m admin-0 (shapefile in /home/user/data/ne) -> shapes.json: a few countries as rings (Kazakhstan merged
with the Baikonur unit, no hole) + thin borders for the region."""
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
        for r in polys(p.simplify(tol)): out.append([[round(x, 4), round(y, 4)] for x, y in r.exterior.coords])
    return out
S = {'cty': {}, 'borders': []}
G['KAZ'] = unary_union([G['KAZ'], G['KAB']]).buffer(0.0005).buffer(-0.0005)
for iso, tol, ma in (('KAZ', .02, .05), ('IRN', .01, .002), ('OMN', .005, .0005), ('ARE', .01, .01), ('RUS', .03, .05), ('TUR', .01, .01), ('SAU', .03, .05)):
    g = G[iso]
    if iso == 'RUS': g = g.intersection(box(19, 35, 80, 60))
    S['cty'][iso] = rings(g, tol, ma)
BB = box(-25, -40, 150, 75)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(BB)
    if not g.is_empty: S['borders'] += rings(g, .03, .2)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S['cty'].items()}, len(S['borders']))
