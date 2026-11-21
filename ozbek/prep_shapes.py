"""Natural Earth 10m -> shapes.json for the «өзбек» reel: borders, KAZ/UZB outlines, rivers (Syr Darya, Amu Darya, Irtysh, Ural/Zhaiyk, Tobol, Ishim,
hand-drawn Chu), the historical Aral, and hand-drawn approximate areas: Abulkhair's Uzbek ulus (~1446-1468), Moghulistan, Maverannahr oases."""
import json
from shapely.geometry import shape, box
D = '/home/user/data/'
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        for q in polys(p.simplify(tol)): out.append([[round(x, 3), round(y, 3)] for x, y in q.exterior.coords])
    return out
BB = box(30, 28, 100, 62); S = {'cty': {}, 'borders': []}
for f in L('ne_10m_admin_0_countries'):
    g = shape(f['geometry']); iso = f['properties']['ADM0_A3']
    if not g.intersects(BB): continue
    g = g.intersection(BB); S['borders'] += rings(g, .03, .05)
    if iso in ('KAZ', 'UZB', 'KGZ', 'TKM', 'TJK'): S['cty'][iso] = rings(g, .02, .02)
def river(names):
    out = []
    for f in L('ne_10m_rivers_lake_centerlines'):
        if (f['properties'].get('name') or '') in names:
            g = f['geometry']
            for ls in (g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]):
                out.append([[round(x, 3), round(y, 3)] for x, y in ls])
    return out
S['syr'] = river({'Syr  Darya', 'Syr Darya'}); S['amu'] = river({'Amu  Darya', 'Amu Darya'})
S['other'] = river({'Irtysh', 'Ural', 'Tobol', 'Ishim'})
S['chu'] = [[[76.2, 42.75], [75.6, 42.85], [75.0, 42.95], [74.5, 43.4], [74.0, 43.9], [73.4, 44.5], [72.6, 44.9], [71.6, 45.3], [70.6, 45.5]]]
lakes = [shape(f['geometry']) for f in L('ne_10m_lakes_historic') if 'Aral' in (f['properties'].get('name') or '')]
S['aral'] = rings(lakes[0], .02) if lakes else []
# approximate historical areas (hand-drawn)
S['ulus'] = [[[51.4, 46.9], [51.2, 49.5], [52.0, 51.4], [55.0, 53.0], [58.5, 54.6], [62.5, 56.0], [66.5, 56.4], [70.5, 55.6], [74.0, 54.2], [76.5, 52.3],
              [76.0, 49.8], [74.0, 47.6], [71.8, 46.0], [70.2, 44.4], [69.0, 43.0], [67.6, 43.0], [66.0, 43.9], [63.5, 44.6], [61.2, 45.3], [58.5, 45.7],
              [55.6, 45.4], [53.2, 45.8]]]
S['mogul'] = [[[73.0, 42.2], [75.5, 41.3], [78.5, 41.2], [81.5, 41.6], [84.0, 43.0], [84.6, 45.0], [82.6, 46.6], [80.0, 47.2], [77.5, 46.8], [75.2, 46.0],
               [73.6, 45.2], [72.8, 43.8]]]
S['maver'] = [[[63.0, 39.2], [64.6, 40.6], [66.6, 41.0], [68.6, 41.2], [69.6, 40.6], [68.6, 39.2], [67.2, 38.6], [65.2, 38.4], [63.6, 38.6]]]
json.dump(S, open('shapes.json', 'w'))
print({k: len(v) for k, v in S.items()}, list(S['cty']))
