"""Vector overlays for the map (lon/lat): rivers, modern borders (thin, faint), the khaganate outline. -> shapes.json
Natural Earth 10m (public domain) from /home/user/data; the Chu and the Talas are not in Natural Earth, so they are traced by hand."""
import json, shapefile
from shapely.geometry import shape, box
D = '/home/user/data/'
BB = box(52, 30, 98, 55)
def lines(g, tol=.02):
    g = g.intersection(BB).simplify(tol)
    if g.is_empty: return []
    gs = list(g.geoms) if hasattr(g, 'geoms') else [g]
    return [[[round(x, 3), round(y, 3)] for x, y in q.coords] for q in gs if q.geom_type == 'LineString']
out = {'rivers': {}, 'borders': []}
r = shapefile.Reader(D + 'ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines')
for s, rec in zip(r.shapes(), r.records()):
    n = rec['name']
    if n in ('Ile', 'Syr Darya', 'Naryn', 'Amu Darya', 'Künes'):
        out['rivers'].setdefault(n, []).extend(lines(shape(s.__geo_interface__)))
out['rivers']['Chu'] = [[[76.0, 42.25], [75.6, 42.2], [75.3, 42.55], [75.05, 42.78], [74.6, 42.97], [74.0, 43.2], [73.75, 43.6], [73.0, 44.0], [72.0, 44.4], [71.0, 44.8], [70.0, 45.0], [69.0, 45.15]]]
out['rivers']['Talas'] = [[[73.1, 42.4], [72.24, 42.52], [71.7, 42.75], [71.38, 42.92], [70.9, 43.3], [70.4, 43.9], [70.1, 44.4]]]
b = shapefile.Reader(D + 'ne_10m_admin_0_boundary_lines_land/ne_10m_admin_0_boundary_lines_land')
for s in b.shapes(): out['borders'] += lines(shape(s.__geo_interface__), .03)
# Turgesh khaganate 704-756, approximate (Zhetysu and the Talas valley, from the Syr Darya to the eastern Tian Shan)
out['turgesh'] = [[68.6, 42.2], [69.4, 44.0], [71.0, 45.2], [73.0, 46.0], [74.8, 46.8], [77.2, 47.0], [79.8, 46.6], [82.4, 46.3], [84.8, 45.4], [86.4, 44.3], [85.6, 43.2], [83.0, 42.6], [80.4, 41.9], [78.0, 41.4], [75.6, 41.2], [73.4, 41.3], [71.2, 41.4], [69.6, 41.3]]
json.dump(out, open('shapes.json', 'w'))
print({k: len(v) for k, v in out['rivers'].items()}, len(out['borders']))
