"""Natural Earth 10m -> shapes.json: country outlines in the reel's area, Turkey/Anatolia, Iran, Turkmenistan, Azerbaijan,
the Syr Darya and Amu Darya, hand-drawn historical areas (Zhetysu, Oghuz state ~IX-XI c.) and the Seljuk route."""
import json
from shapely.geometry import shape, box, Polygon
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
BB = box(18, 28, 90, 56); S = {'cty': {}, 'borders': []}
for f in L('ne_10m_admin_0_countries'):
    g = shape(f['geometry']); iso = f['properties']['ADM0_A3']
    if not g.intersects(BB): continue
    g = g.intersection(BB)
    S['borders'] += rings(g, .03, .05)
    if iso in ('TUR', 'IRN', 'TKM', 'AZE', 'KAZ', 'UZB'): S['cty'][iso] = rings(g, .02, .02)
tur = shape(next(f for f in L('ne_10m_admin_0_countries') if f['properties']['ADM0_A3'] == 'TUR')['geometry'])
S['anatolia'] = rings(max(polys(tur), key=lambda p: p.area), .02)
def river(names):
    out = []
    for f in L('ne_10m_rivers_lake_centerlines'):
        n = (f['properties'].get('name') or '')
        if n in names:
            for ls in (f['geometry']['coordinates'] if f['geometry']['type'] == 'MultiLineString' else [f['geometry']['coordinates']]):
                out.append([[round(x, 3), round(y, 3)] for x, y in ls])
    return out
S['syr'] = river({'Syr Darya', 'Syrdariya', 'Naryn'}); S['amu'] = river({'Amu Darya'})
print('syr parts', len(S['syr']), 'amu', len(S['amu']))
lakes = [shape(f['geometry']) for f in L('ne_10m_lakes_historic') if 'Aral' in (f['properties'].get('name') or '')]
S['aral'] = rings(lakes[0], .02) if lakes else []
print('aral', len(S['aral']))
# hand-drawn (approximate) areas
S['zhetysu'] = [[[73.6, 43.2], [74.8, 42.7], [77.5, 42.9], [80.2, 43.0], [81.0, 44.3], [80.4, 45.6], [78.8, 46.6], [76.0, 46.4], [74.2, 45.4], [73.4, 44.3]]]
S['oguz'] = [[[52.6, 46.6], [54.5, 48.6], [57.5, 49.8], [61.0, 49.6], [64.5, 48.2], [67.0, 46.4], [68.6, 44.4], [68.2, 42.6], [66.4, 41.9], [63.6, 42.4],
              [61.0, 43.0], [58.8, 42.6], [56.6, 41.7], [54.6, 42.3], [53.1, 44.0]]]
# Seljuk route: Jankent -> Bukhara -> Merv -> Dandanakan -> Nishapur -> Rey -> Hamadan -> Manzikert -> central Anatolia
S['route'] = [[61.95, 45.6], [62.6, 43.6], [63.6, 41.4], [64.42, 39.77], [62.9, 38.4], [61.83, 37.66], [59.6, 36.6], [58.8, 36.2], [55.0, 36.0], [51.4, 35.6],
              [48.5, 35.2], [45.8, 37.6], [42.54, 39.14], [39.0, 39.4], [35.5, 39.2], [32.8, 39.0]]
json.dump(S, open('shapes.json', 'w'))
print({k: len(v) for k, v in S.items()})
