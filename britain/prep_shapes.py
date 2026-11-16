import json
from shapely.geometry import shape, box, Point, mapping
from shapely.ops import unary_union, linemerge
D = '/home/user/data/'
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=0.01, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        p = p.simplify(tol)
        if p.is_empty: continue
        for q in polys(p): out.append([[round(x, 3), round(y, 3)] for x, y in q.exterior.coords])
    return out
def lines(g, tol=0.01):
    out = []
    for p in polys(g):
        if p.geom_type == 'LineString': out.append([[round(x, 3), round(y, 3)] for x, y in p.simplify(tol).coords])
        elif p.geom_type == 'MultiLineString': out += lines(p, tol)
    return out
mu = {f['properties']['GEOUNIT']: shape(f['geometry']) for f in L('ne_10m_admin_0_map_units')}
land = [shape(f['geometry']) for f in L('ne_10m_land')]
lakes = [(f['properties'].get('name') or '', shape(f['geometry'])) for f in L('ne_10m_lakes')]
# ---- britain
B = {}
for k, n in [('eng', 'England'), ('sco', 'Scotland'), ('wal', 'Wales'), ('nir', 'Northern Ireland'), ('irl', 'Ireland')]:
    B[k] = rings(mu[n], .008, .0005)
gb = unary_union([mu['England'], mu['Scotland'], mu['Wales']])
B['gb'] = rings(gb, .008, .0005); B['uk'] = B['gb'] + B['nir']
B['ireland_isl'] = rings(unary_union([mu['Northern Ireland'], mu['Ireland']]), .008, .0005)
big = sorted(polys(gb), key=lambda p: -p.area)[0]; irl_big = sorted(polys(unary_union([mu['Northern Ireland'], mu['Ireland']])), key=lambda p: -p.area)[0]
B['gb_main'] = rings(big, .008); B['irl_main'] = rings(irl_big, .008)
small = []
for g in [gb, mu['Northern Ireland'], mu['Ireland']]:
    for p in polys(g):
        if p.area < big.area * .5 and p.area < irl_big.area * .5 and p.area > 0.0008:
            c = p.representative_point(); small.append([round(c.x, 3), round(c.y, 3), round(p.area, 4)])
B['small'] = small
EU = ['AUT','BEL','BGR','HRV','CYP','CZE','DNK','EST','FIN','FRA','DEU','GRC','HUN','IRL','ITA','LVA','LTU','LUX','MLT','NLD','POL','PRT','ROU','SVK','SVN','ESP','SWE']
eu = []; eur = []
for f in L('ne_50m_admin_0_countries'):
    p = f['properties']; g = shape(f['geometry']).intersection(box(-25, 34, 45, 72))
    if g.is_empty: continue
    if p['ADM0_A3'] in EU: eu += rings(g, .03, .02)
    eur += rings(g, .03, .02)
B['eu'] = eu
json.dump(B, open('/home/user/work/brit/shapes.json', 'w'))
print('brit', {k: len(v) for k, v in B.items()})
# ---- opposites
O = {}
isl = next(p for g in land for p in polys(g) if p.contains(Point(-99, 72.6)))
O['island'] = rings(isl, .01)
O['lakes'] = [r for n, g in lakes if any(s in n for s in ['Superior', 'Michigan', 'Huron', 'Erie', 'Ontario']) for r in rings(g, .01, .05)]
fb = box(21, 60, 32, 65.5); O['finlakes'] = [r for n, g in lakes if g.intersects(fb) for r in rings(g.intersection(fb), .005, .002)]
def coast(bb, tol=.005):
    bx = box(*bb); out = []
    for g in land:
        if not g.intersects(bx): continue
        for p in polys(g):
            i = p.exterior.intersection(bx)
            if i.geom_type == 'MultiLineString': i = linemerge(i)
            out += [l for l in lines(i, tol) if len(l) > 3]
    return out
O['panama'] = coast((-82.5, 6.8, -76.5, 10.2)); O['gib'] = coast((-7.2, 35.2, -4.3, 37.3))
O['cape'] = coast((14, -35.5, 32, -28), .02); O['bengal'] = coast((78, 8, 95, 24), .02)
json.dump(O, open('/home/user/work/opp/shapes.json', 'w'))
print('opp', {k: len(v) for k, v in O.items()}, sum(len(r) for r in O['finlakes']))
