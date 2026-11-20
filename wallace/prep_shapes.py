"""Natural Earth 10m admin-0 -> shapes.json: land west of the Wallace line (Asian side) and east of it (Australian side),
Bali and Lombok outlines, thin borders. Wallace line = schematic polyline WL (lon, lat)."""
import json, shapefile, numpy as np
from shapely.geometry import shape, box
R = shapefile.Reader('/home/user/data/ne/ne_10m_admin_0_countries.shp')
WL = [[115.78, -10.5], [115.78, -8.9], [115.85, -8.2], [116.6, -6.6], [117.9, -4.6], [118.7, -2.2], [119.1, 0.6], [120.2, 3.2], [122.5, 5.0], [126.0, 6.2], [127.6, 7.5]]
def line_lon(lat):
    lats = [p[1] for p in WL]; lons = [p[0] for p in WL]
    return float(np.interp(lat, lats, lons))
west, east, borders, bali, lombok = [], [], [], [], []
win = box(88, -46, 160, 24)
def rings(p, tol):
    p = p.simplify(tol, preserve_topology=True)
    return [[round(x, 3), round(y, 3)] for x, y in p.exterior.coords]
for sr in R.iterShapeRecords():
    g = shape(sr.shape.__geo_interface__).intersection(win)
    if g.is_empty: continue
    for p in (g.geoms if g.geom_type in ('MultiPolygon', 'GeometryCollection') else [g]):
        if p.geom_type != 'Polygon' or p.area < .004: continue
        c = p.representative_point()
        if p.bounds[1] > -9.1 and p.bounds[3] < -8.0 and 114.3 < c.x < 115.75: bali.append(rings(p, .003))
        if p.bounds[1] > -9.1 and p.bounds[3] < -8.0 and 115.9 < c.x < 116.8: lombok.append(rings(p, .003))
        r = rings(p, .02 if p.area > 2 else .008)
        if c.y > 22: continue
        (west if c.x < line_lon(min(max(c.y, -10.5), 7.5)) and not (c.y < -9.5 and c.x > 118) else east).append(r)
    gb = g.simplify(.04, preserve_topology=True)
    for p in (gb.geoms if gb.geom_type in ('MultiPolygon', 'GeometryCollection') else [gb]):
        if p.geom_type == 'Polygon' and p.area > .05: borders.append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords])
out = {'west': west, 'east': east, 'bali': bali, 'lombok': lombok, 'borders': borders, 'wl': WL}
json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
import os; print(os.path.getsize('shapes.json') // 1024, 'KB', len(west), len(east), len(bali), len(lombok))
