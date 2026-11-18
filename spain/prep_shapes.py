"""Natural Earth 10m -> shapes.json: Spain mainland, Llívia, Ceuta, Melilla, France (metropolitan), Portugal, Andorra, Gibraltar, Morocco, UK."""
import json
from shapely.geometry import shape, box, Point
D = '/home/user/data/'
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        q = p.simplify(tol)
        for r in polys(q): out.append([[round(x, 4), round(y, 4)] for x, y in r.exterior.coords])
    return out
C = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in L('ne_10m_admin_0_countries')}
S = {}
esp = C['ESP']
P = polys(esp)
def near(lon, lat): return [p for p in P if p.distance(Point(lon, lat)) < .05]
main = max(P, key=lambda p: p.area)
S['esp'] = rings(main, .01)
S['esp_isl'] = rings(esp.intersection(box(-1, 38, 5, 41)), .01, .001)            # Balearics
S['llivia'] = rings(near(1.98, 42.465)[0], .001) if near(1.98, 42.465) else []
S['ceuta'] = rings(near(-5.32, 35.89)[0], .001) if near(-5.32, 35.89) else []
S['melilla'] = rings(near(-2.95, 35.29)[0], .001) if near(-2.95, 35.29) else []
S['fra'] = rings(C['FRA'].intersection(box(-6, 41, 10, 52)), .01, .05)
S['prt'] = rings(C['PRT'].intersection(box(-10, 36, -6, 42.5)), .01, .01)
S['and'] = rings(C['AND'], .001)
S['gib'] = rings(C['GIB'], .0005)
S['mar'] = rings(C['MAR'].intersection(box(-14, 27, 0, 36.5)), .01, .05)
S['gbr'] = rings(C['GBR'], .02, .05)
print({k: (len(v), sum(len(r) for r in v)) for k, v in S.items()})
json.dump(S, open('shapes.json', 'w'))
from shapely.ops import nearest_points
a, b = nearest_points(near(1.98, 42.465)[0], main)
S['ll_line'] = [[round(a.x, 4), round(a.y, 4)], [round(b.x, 4), round(b.y, 4)]]
from pyproj import Geod
print('ll dist km', Geod(ellps='WGS84').inv(a.x, a.y, b.x, b.y)[2] / 1000, 'llivia c', near(1.98, 42.465)[0].centroid, 'gib c', C['GIB'].centroid, 'and c', C['AND'].centroid)
json.dump(S, open('shapes.json', 'w'))
S['esp_gib'] = rings(main.intersection(box(-6.2, 35.9, -4.6, 36.8)), .0005, .0001)
json.dump(S, open('shapes.json', 'w')); print('esp_gib', len(S['esp_gib']))
