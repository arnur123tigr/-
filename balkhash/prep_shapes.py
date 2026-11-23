"""Balkhash shapes.json from Natural Earth 10m (data in /home/user/data):
lake split at the Uzynaral strait into west/east, Kapshagay, Alakol, countries (KAZ incl. Baikonur, CHN), borders,
rivers Ile (+ Künes source branch), Ertis, Aral 1960 + today (inset), and schematic small rivers (Karatal, Lepsy, Ayagoz).
Usage: python3 prep_shapes.py"""
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union
D = '/home/user/data/'
L = lambda n: json.load(open(D + n + '.geojson'))['features']
polys = lambda g: list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.01, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        for q in polys(p.simplify(tol)):
            if not q.is_empty: out.append([[round(x, 4), round(y, 4)] for x, y in q.exterior.coords])
    return out
SPLIT = 75.52   # Uzynaral strait (Saryesik peninsula), west part ≈ 58 % of the area
lakes = {f['properties'].get('name'): shape(f['geometry']) for f in L('ne_10m_lakes') if f['properties'].get('name') in ('Lake Balkhash', 'Kapchagay Reservoir', 'Alakol')}
bal = lakes['Lake Balkhash']
S = {'west': rings(bal.intersection(box(70, 40, SPLIT, 50)), .002, 1e-4), 'east': rings(bal.intersection(box(SPLIT, 40, 82, 50)), .002, 1e-4),
     'lake': rings(bal, .002, 1e-4), 'kap': rings(lakes['Kapchagay Reservoir'], .003), 'alakol': rings(lakes['Alakol'], .004)}
BB = box(40, 30, 96, 57); S['borders'] = []; C = {}
for ft in L('ne_10m_admin_0_countries'):
    g = shape(ft['geometry']); iso = ft['properties']['ADM0_A3']
    if not g.intersects(BB): continue
    g = g.intersection(BB)
    if iso in ('KAZ', 'KAB', 'CHN'): C[iso] = g
C['KAZ'] = unary_union([C['KAZ'], C.pop('KAB')]).buffer(.002)   # Baikonur is Kazakhstan territory
S['cty'] = {k: rings(v, .01, .01) for k, v in C.items()}
for ft in L('ne_10m_admin_0_boundary_lines_land'):   # borders as lines (no box edges)
    g = shape(ft['geometry'])
    if g.intersects(BB):
        for ls in polys(g.simplify(.02)): S['borders'].append([[round(x, 3), round(y, 3)] for x, y in ls.coords])
def river(names, tol=.005):
    out = []
    for ft in L('ne_10m_rivers_lake_centerlines'):
        if (ft['properties'].get('name') or '') in names and ft['properties'].get('featurecla') == 'River':
            gm = shape(ft['geometry']).simplify(tol)
            for ls in polys(gm): out.append([[round(x, 3), round(y, 3)] for x, y in ls.coords])
    return out
S['ile'] = river({'Ile'}); S['kunes'] = river({'Künes'}); S['ertis'] = river({'Ertis', 'Ertix'})
hist = [shape(f['geometry']) for f in L('ne_10m_lakes_historic') if 'Aral' in (f['properties'].get('name') or '')][0]
S['aral1960'] = rings(hist, .01); S['aralnow'] = rings(unary_union([shape(f['geometry']) for f in L('ne_10m_lakes') if 'Aral' in (f['properties'].get('name') or '')]), .01)
# schematic small rivers of the east part (traced from the Blue Marble texture)
S['karatal'] = [[78.8, 45.0], [78.3, 45.15], [77.95, 45.27], [77.75, 45.55], [77.6, 45.85], [77.4, 46.15], [77.17, 46.42]]
S['lepsy'] = [[80.6, 45.55], [80.0, 45.8], [79.5, 46.1], [79.1, 46.35], [78.95, 46.47]]
S['ayagoz'] = [[80.55, 47.65], [80.1, 47.45], [79.7, 47.2], [79.35, 47.0], [79.2, 46.85]]
json.dump(S, open('shapes.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in S.items()})
