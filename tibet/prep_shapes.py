"""Natural Earth 10m -> shapes.json: Plateau of Tibet (smoothed), metropolitan France, country borders around Asia."""
import json
from shapely.geometry import shape, box
from shapely.ops import unary_union
D = '/home/user/data/'
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        p = p.simplify(tol)
        for q in polys(p): out.append([[round(x, 3), round(y, 3)] for x, y in q.exterior.coords])
    return out
S = {}
tib = next(shape(f['geometry']) for f in L('ne_10m_geography_regions_polys') if f['properties']['NAME'] == 'PLATEAU OF TIBET')
tib = unary_union(polys(tib)).buffer(.6).buffer(-.6).simplify(.05)
S['tibet'] = rings(tib, .05, .5)
c = tib.centroid; S['tibet_c'] = [round(c.x, 2), round(c.y, 2)]; S['tibet_area_deg'] = tib.area
fr = next(shape(f['geometry']) for f in L('ne_10m_admin_0_countries') if f['properties']['ADM0_A3'] == 'FRA')
fr = fr.intersection(box(-6, 41, 10, 52)); fr = sorted(polys(fr), key=lambda p: -p.area)[0]
fc = fr.centroid; S['france'] = [[[round(x - fc.x, 3), round(y - fc.y, 3)] for x, y in r] for r in rings(fr, .03)]
S['france_lat'] = round(fc.y, 2)
bd = []
for f in L('ne_10m_admin_0_countries'):
    g = shape(f['geometry']).intersection(box(20, -15, 160, 80))
    if not g.is_empty: bd += rings(g, .04, .3)
S['borders'] = bd
json.dump(S, open('shapes.json', 'w'))
print(len(S['tibet']), [len(r) for r in S['tibet']], S['tibet_c'], len(bd))
