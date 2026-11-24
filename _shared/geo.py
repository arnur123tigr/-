"""Shared helpers for shapes.json: Natural Earth 10m (public domain) -> simplified lon/lat rings and lines."""
import json
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union, linemerge
from shapely import affinity
D = '/home/user/data/'
_cache = {}
def feats(n):
    if n not in _cache: _cache[n] = json.load(open(D + n + '.geojson'))['features']
    return _cache[n]
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.03, min_area=0):
    out = []
    for p in polys(g):
        if p.is_empty or p.geom_type != 'Polygon' or p.area < min_area: continue
        q = p.simplify(tol)
        for r in polys(q):
            if r.geom_type == 'Polygon' and not r.is_empty: out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
def lines(g, tol=.02):
    out = []
    for l in polys(g):
        if l.geom_type == 'LineString' and not l.is_empty: out.append([[round(x, 3), round(y, 3)] for x, y in l.simplify(tol).coords])
    return out
def countries():
    return {f['properties']['ADM0_A3']: shape(f['geometry']).buffer(0) for f in feats('ne_10m_admin_0_countries')}
def units():
    return {f['properties']['GU_A3']: shape(f['geometry']).buffer(0) for f in feats('ne_10m_admin_0_map_units')}
def region(name):
    return unary_union([shape(f['geometry']).buffer(0) for f in feats('ne_10m_geography_regions_polys') if f['properties']['NAME'] == name])
def centroid(g): c = g.representative_point(); return [round(c.x, 2), round(c.y, 2)]
