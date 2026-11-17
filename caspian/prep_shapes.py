"""Natural Earth 10m -> shapes.json: Caspian (hole in the Eurasia land polygon), Black Sea, Sea of Azov+Marmara+Aegean+Med water, five Caspian countries, Volga/Ural rivers."""
import json
from shapely.geometry import shape, box, Point, Polygon
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
land = unary_union([shape(f['geometry']).intersection(box(-20, 20, 75, 62)) for f in L('ne_10m_land')])
water = box(-20, 20, 75, 62).difference(land)
casp = next(p for p in polys(water) if p.contains(Point(51, 42)))
S['caspian'] = rings(casp, .02); c = casp.centroid; S['casp_c'] = [round(c.x, 2), round(c.y, 2)]
sea = next(p for p in polys(water) if p.contains(Point(34, 43)))   # Black Sea + everything connected to it
M = {f['properties']['name']: shape(f['geometry']) for f in L('ne_10m_geography_marine_polys')}
blk = sea.intersection(box(27, 40.9, 42, 47.5)); blk = max(polys(blk), key=lambda p: p.area)
S['black'] = rings(blk, .02)
azov = sea.intersection(box(34.8, 45.2, 39.5, 47.5)); S['azov'] = rings(azov, .02, .05)
marm = sea.intersection(box(26, 40, 29.9, 41.3)); S['marmara'] = rings(marm, .01, .01)
aeg = sea.intersection(box(22, 35, 28.5, 41)); S['aegean'] = rings(aeg, .02, .05)
med = sea.intersection(box(-6, 30, 37, 46)); S['med'] = rings(med, .03, .3)
S['route'] = [[34, 43.3], [30.5, 42.4], [29.05, 41.2], [28.2, 40.75], [26.4, 40.2], [25.3, 38.5], [23.5, 36.4], [19, 35.5], [12, 37.4], [8, 37.8], [2, 37.0], [-3, 36.2], [-5.6, 35.95], [-9, 36.0], [-14, 36.3]]
C = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in L('ne_10m_admin_0_countries')}
S['cty'] = {k: rings(C[k].intersection(box(30, 25, 90, 60)), .03, .2) for k in ['RUS', 'KAZ', 'TKM', 'IRN', 'AZE']}
riv = []
for f in L('ne_10m_rivers_lake_centerlines'):
    n = f['properties'].get('name') or ''
    if n in ('Volga', 'Ural', 'Kura', 'Terek'):
        g = shape(f['geometry']).intersection(box(30, 30, 70, 60))
        for l in (g.geoms if hasattr(g, 'geoms') else [g]):
            if l.geom_type == 'LineString' and len(l.coords) > 2: riv.append([[round(x, 3), round(y, 3)] for x, y in l.simplify(.03).coords])
S['rivers'] = riv
# Paratethys (rough, hand-drawn): from the Alps foreland to the Aral
S['para'] = [[10, 47.5], [14, 48.8], [18, 48.6], [22, 47.8], [26, 48.3], [30, 48.8], [35, 49.5], [40, 50.2], [45, 50.5], [50, 49.6], [55, 48.2], [60, 47.4], [62, 45.4], [60, 43.4], [56, 41.2], [53, 38.5], [50, 37.6], [48, 39.5], [45, 41.3], [41, 41.0], [36, 41.2], [31, 41.0], [27, 42.5], [24, 43.2], [20, 44.5], [16, 45.2], [12, 45.8], [10, 46.6]]
json.dump(S, open('shapes.json', 'w'))
print({k: len(v) for k, v in S.items()}, S['casp_c'], casp.area)
