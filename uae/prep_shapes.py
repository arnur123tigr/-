"""Natural Earth 10m -> shapes.json: UAE, its 7 emirates, Portugal/Austria (centred, for size), USA lower 48 states, Arabian Peninsula."""
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union
D = '/home/user/data/'
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.01, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        p = p.simplify(tol)
        for q in polys(p): out.append([[round(x, 3), round(y, 3)] for x, y in q.exterior.coords])
    return out
S = {}
A0 = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in L('ne_10m_admin_0_countries')}
uae = A0['ARE']; S['uae'] = rings(uae, .004, .0004)
c = uae.centroid; S['uae_c'] = [round(c.x, 3), round(c.y, 3)]
EM = {'Abu Dhabi': 'ad', 'Dubay': 'du', 'Sharjah': 'sh', 'Ajman': 'aj', 'Umm Al Qaywayn': 'uq', 'Ras Al Khaymah': 'rk', 'Fujayrah': 'fu'}
S['em'] = {}; S['em_c'] = {}
for f in L('ne_10m_admin_1_states_provinces'):
    p = f['properties']
    if p['adm0_a3'] == 'ARE' and p['name'] in EM:
        g = shape(f['geometry']); k = EM[p['name']]
        S['em'][k] = rings(g, .003, .0002); big = sorted(polys(g), key=lambda q: -q.area)[0]; r = big.representative_point()
        S['em_c'][k] = [round(r.x, 3), round(r.y, 3), round(g.area, 4)]
    if p['adm0_a3'] == 'USA' and p['name'] not in ('Alaska', 'Hawaii'):
        S.setdefault('us', []).extend(rings(shape(f['geometry']), .05, .05))
def centred(g):
    g = sorted(polys(g), key=lambda q: -q.area)[0]; c = g.centroid
    return {'lat': round(c.y, 2), 'r': [[[round(x - c.x, 3), round(y - c.y, 3)] for x, y in r] for r in rings(g, .01)]}
S['prt'] = centred(A0['PRT'].intersection(box(-10, 36, -6, 43))); S['aut'] = centred(A0['AUT']); S['are_c'] = centred(uae)
reg = {f['properties']['NAME']: shape(f['geometry']) for f in L('ne_10m_geography_regions_polys')}
print([n for n in reg if 'ARAB' in n])
ar = reg.get('ARABIAN PENINSULA')
if ar is not None: S['arabia'] = rings(ar, .05, .5)
bd = []
for k, g in A0.items():
    g = g.intersection(box(25, 5, 75, 45))
    if not g.is_empty: bd += rings(g, .01, .002)
S['borders'] = bd
json.dump(S, open('shapes.json', 'w'))
print({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in S.items()}, S['em_c'])
