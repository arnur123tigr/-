"""Natural Earth 10m -> shapes.json. Kazakhstan merged with Baikonur (no hole). Shared border lines (KZ–RU, US–CA main + Alaska)
are the intersection of one country's outline with the other one, merged and ordered west -> east."""
import json, shapefile
from shapely.geometry import shape, box, LineString, MultiLineString
from shapely.ops import unary_union, linemerge
R = shapefile.Reader('/home/user/data/ne/ne_10m_admin_0_countries.shp')
F = [f.name for f in R.fields[1:]]
G = {}
for sr in R.iterShapeRecords():
    rec = dict(zip(F, sr.record)); G[rec['ADM0_A3']] = shape(sr.shape.__geo_interface__)
G['KAZ'] = unary_union([G['KAZ'], G['KAB']]).buffer(0.0005).buffer(-0.0005)
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, mn=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < mn: continue
        q = p.simplify(tol)
        for r in polys(q): out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
def shared(a, b, tol=.01):
    l = G[a].boundary.intersection(G[b].buffer(.02))
    ls = [g for g in (l.geoms if hasattr(l, 'geoms') else [l]) if g.geom_type == 'LineString']
    m = linemerge(MultiLineString(ls)); parts = polys(m) if m.geom_type == 'MultiLineString' else [m]
    out = []
    for p in parts:
        c = list(p.simplify(tol).coords)
        if c[0][0] > c[-1][0]: c = c[::-1]
        out.append([[round(x, 3), round(y, 3)] for x, y in c])
    out.sort(key=lambda r: -len(r)); return out, [round(p.length, 2) for p in parts]
S = {'cty': {}, 'borders': []}
for iso, tol in (('KAZ', .01), ('RUS', .03), ('CHN', .03), ('KGZ', .01), ('UZB', .01), ('TKM', .01), ('USA', .03), ('CAN', .03)):
    g = G[iso]
    if iso == 'RUS': g = g.intersection(box(19, 35, 180, 82))
    if iso == 'USA': g = g.intersection(box(-180, 15, -50, 75))
    S['cty'][iso] = rings(g, tol, .05)
S['kzru'], L1 = shared('KAZ', 'RUS'); S['usca'], L2 = shared('USA', 'CAN')
print('kzru parts', len(S['kzru']), L1[:5], 'usca', len(S['usca']), L2[:6])
for k in ('kzru', 'usca'):
    for r in S[k][:3]: print(k, len(r), r[0], r[-1])
BB = box(-180, 10, 180, 80)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(BB)
    if not g.is_empty: S['borders'] += rings(g, .05, .3)
json.dump(S, open('shapes.json', 'w'), separators=(',', ':'))
import os; print(os.path.getsize('shapes.json') // 1024, 'KB')
