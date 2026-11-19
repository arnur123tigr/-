"""Natural Earth 10m admin-0 -> shapes.json: South American countries (Spanish-speaking ones, Brazil, the Guianas),
Portugal and Spain (mainland), thin borders of the Atlantic world, and true-size outlines (degree offsets) for the same-scale scene."""
import json, shapefile
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
R = shapefile.Reader('/home/user/data/ne/ne_10m_admin_0_countries.shp')
F = [f.name for f in R.fields[1:]]
G = {}
for sr in R.iterShapeRecords():
    rec = dict(zip(F, sr.record)); G[rec['ADM0_A3']] = shape(sr.shape.__geo_interface__)
def rings(g, tol):
    g = g.simplify(tol, preserve_topology=True); out = []
    for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
        if p.area < tol * tol * 4: continue
        out.append([[round(x, 3), round(y, 3)] for x, y in p.exterior.coords])
    return out
SPA = 'ARG BOL CHL COL ECU PRY PER URY VEN'.split()
out = {'cty': {}, 'borders': []}
for k in SPA + ['BRA', 'GUY', 'SUR']: out['cty'][k] = rings(G[k], .02)
out['cty']['GUF'] = rings(G['FRA'].intersection(box(-56, 0, -50, 7)), .02)
out['cty']['PRT'] = rings(G['PRT'].intersection(box(-10, 36, -6, 43)), .01)
out['cty']['ESP'] = rings(G['ESP'].intersection(box(-10, 35.5, 5, 44.5)), .01)
out['spa'] = SPA
# thin borders: every country in the Atlantic half of the world
win = box(-120, -60, 90, 75)
for k, g in G.items():
    g2 = g.intersection(win)
    if g2.is_empty: continue
    g2 = g2.simplify(.05, preserve_topology=True)
    for p in (g2.geoms if g2.geom_type in ('MultiPolygon', 'GeometryCollection') else [g2]):
        if p.geom_type != 'Polygon' or p.area < .02: continue
        out['borders'].append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords])
# true-size outlines (offsets from the centroid in degrees; drawn with cos(lat) of the country)
for k, g in (('prt_s', G['PRT'].intersection(box(-10, 36, -6, 43))), ('bra_s', G['BRA'])):
    c = g.centroid; out[k] = {'lat': c.y, 'lon': c.x, 'r': [[[round(x - c.x, 3), round(y - c.y, 3)] for x, y in r] for r in rings(g, .02)]}
json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
import os; print('shapes.json', os.path.getsize('shapes.json') // 1024, 'KB', {k: len(v) for k, v in out['cty'].items()}, len(out['borders']))
