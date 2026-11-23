"""Natural Earth 10m geojson (in /home/user/data) -> shapes.json for the Hundred Years War map.
Medieval lands are approximated with modern French departments / Belgian provinces (schematic, said on screen).
  fra  - metropolitan France (blue base),  eng - England + Wales (red),  bre - Brittany (neutral duchy)
  norm / anjou / aquit / fland - the four contested lands of scene 3
  occ  - English + Burgundian north in 1428, per department with its centroid (blue reconquest runs by distance)
  rivers - Loire, Seine, Thames etc. as thin lines."""
import json
from shapely.geometry import shape, box, Point
from shapely.ops import unary_union
D = '/home/user/data/'
A1 = json.load(open(D + 'ne_10m_admin_1_states_provinces.geojson'))['features']
G = {f['properties']['iso_3166_2']: shape(f['geometry']).buffer(0) for f in A1 if f['properties']['adm0_a3'] in ('FRA', 'BEL')}
SU = {f['properties']['SU_A3']: shape(f['geometry']).buffer(0) for f in json.load(open(D + 'ne_10m_admin_0_map_subunits.geojson'))['features']}
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.012, min_area=.004):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        q = p.simplify(tol)
        for r in polys(q): out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
def U(codes): return unary_union([G['FR-%02d' % c if isinstance(c, int) else (c if c.startswith(('FR', 'BE')) else 'FR-' + c)] for c in codes]).buffer(.002).buffer(-.002)
EU = box(-12, 40, 16, 61)
metro = [k for k in G if k.startswith('FR-') and k not in ('FR-GF', 'FR-MQ', 'FR-GP', 'FR-RE', 'FR-YT')]
S = {}
S['fra'] = rings(unary_union([G[k] for k in metro]).buffer(.002).buffer(-.002))
S['eng'] = rings(unary_union([SU['ENG'], SU['WLS']]).buffer(.002).buffer(-.002))
S['bre'] = rings(U([22, 29, 35, 56]))
S['norm'] = rings(U([14, 27, 50, 61, 76]))
S['anjou'] = rings(U([49]))
S['aquit'] = rings(U([33, 40, 64, 47, 24]))
S['fland'] = rings(U(['BE-VWV', 'BE-VOV', 59]))
OCC = [14, 27, 50, 61, 76, 75, 77, 78, 91, 92, 93, 94, 95, 80, 60, '02', 62, 59, 51, '08', 10, 52, 72, 53, 28, 89, 21, 71, 58, 33, 40, 64, 'BE-VWV', 'BE-VOV']
ORL = Point(1.909, 47.902)
S['occ'] = []
for c in OCC:
    g = U([c]); ct = g.representative_point()
    S['occ'].append({'r': rings(g, .01, .0005), 'c': [round(ct.x, 2), round(ct.y, 2)], 'd': round(ct.distance(ORL), 2), 'gas': c in (33, 40, 64)})
S['occ'].sort(key=lambda o: o['d'])
S['rivers'] = []
KEEP = {'Loire', 'Seine', 'Thames', 'Garonne', 'Rhône', 'Somme', 'Dordogne', 'Rhine', 'Meuse', 'Escaut', 'Scheldt', 'Saône'}
for f in json.load(open(D + 'ne_10m_rivers_lake_centerlines.geojson'))['features']:
    if f['properties'].get('name') not in KEEP: continue
    g = shape(f['geometry']).intersection(EU)
    for l in polys(g):
        if l.geom_type == 'LineString' and l.length > .2: S['rivers'].append([[round(x, 3), round(y, 3)] for x, y in l.simplify(.01).coords])
json.dump(S, open('shapes.json', 'w'))
print({k: (len(v) if isinstance(v, list) else v) for k, v in S.items()})
