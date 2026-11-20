"""Natural Earth 10m + PB2002 plates -> shapes.json for the Almaty earthquake reel.
cty: countries (Kazakhstan merged with Baikonur), reg: mountain ranges (NE geography regions), kzz: Kazakhstan regions split
into the seismic south/east (red) and the calm north/centre (green), plate: India-Eurasia boundary polyline."""
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union, linemerge
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
S = {'cty': {}, 'borders': [], 'reg': {}, 'kzz': {}, 'plate': []}
G['KAZ'] = unary_union([G['KAZ'], G['KAB']]).buffer(0.0005).buffer(-0.0005)
# India as Natural Earth draws it (incl. disputed Kashmir parts it claims is not needed: use the IND unit as is)
for iso in ('KAZ', 'IND', 'CHN', 'KGZ', 'UZB', 'TJK', 'PAK', 'NPL', 'AFG', 'MNG', 'RUS', 'TKM'):
    g = G[iso]
    if iso == 'RUS': g = g.intersection(box(19, 35, 180, 82))
    S['cty'][iso] = rings(g, .03, .05)
BB = box(20, -10, 130, 75)
for iso, g in G.items():
    if iso == 'KAB': continue
    g = g.intersection(BB)
    if not g.is_empty: S['borders'] += rings(g, .03, .3)
R = json.load(open(D + 'ne_10m_geography_regions_polys.geojson'))['features']
for f in R:
    n = f['properties']['NAME']
    if n in ('TIAN SHAN', 'HIMALAYAS', 'PLATEAU OF TIBET', 'PAMIRS'): S['reg'][n.split()[-1]] = rings(shape(f['geometry']), .03, .02)
A = json.load(open(D + 'ne_10m_admin_1_states_provinces.geojson'))['features']
red = {'East Kazakhstan', 'Almaty', 'Almaty City', 'Zhambyl', 'South Kazakhstan'}
kzr = [shape(f['geometry']) for f in A if f['properties']['adm0_a3'] == 'KAZ' and f['properties']['name'] in red]
redg = unary_union(kzr).buffer(.01).intersection(G['KAZ'])
S['kzz']['red'] = rings(redg, .03, .05); S['kzz']['green'] = rings(G['KAZ'].difference(redg.buffer(.005)), .03, .05)
P = json.load(open(D + 'plates.json'))['features']
segs = [shape(f['geometry']) for f in P if f['properties']['Name'] in ('EU-IN', 'IN-EU')]
m = linemerge(unary_union(segs))
for l in polys(m) if m.geom_type == 'MultiLineString' else [m]:
    S['plate'].append([[round(x, 3), round(y, 3)] for x, y in l.coords])
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()}, list(S['reg']), [ (l[0], l[-1], len(l)) for l in S['plate']])
