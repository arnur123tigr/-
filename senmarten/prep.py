"""Data for the Saint Martin reel. Textures: NASA Blue Marble (public domain) via prep_tex.py; vectors: Natural Earth 10m (public domain) -> shapes.json.
Saint Martin close-up outline and border: OpenStreetMap (ODbL)."""
import json, subprocess, math, random
from shapely.geometry import shape, box, Polygon, LineString
from shapely.ops import unary_union
D = '/home/user/data/'
subprocess.run(['python3', 'prep_tex.py', 'tex', 'eu', '-8', '12', '40', '56', '40', 'car', '-72', '-56', '10', '24', '60'], check=True)
subprocess.run(['python3', 'grade.py', 'tex/eu.jpg', 'tex/car.jpg'], check=True)
from PIL import Image
Image.open(D + 'world.jpg').save('tex/world.jpg', quality=90); subprocess.run(['python3', 'grade.py', 'tex/world.jpg'], check=True)
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        q = p.simplify(tol)
        for r in polys(q):
            if r.geom_type == 'Polygon': out.append([[round(x, 4), round(y, 4)] for x, y in r.exterior.coords])
    return out
C = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in L('ne_10m_admin_0_countries')}
S = {'nld': rings(C['NLD'].intersection(box(2, 50, 8, 54)), .01, .01), 'fra': rings(C['FRA'].intersection(box(-6, 41, 10, 52)), .01, .05)}
S['esp'] = rings(C['ESP'].intersection(box(-10, 35, 5, 44.5)), .02, .1); S['gbr'] = rings(C['GBR'], .02, .05); S['prt'] = rings(C['PRT'].intersection(box(-10, 36, -6, 42.5)), .01, .01)
S['aia'] = rings(C['AIA'], .0005); S['blm'] = rings(C['BLM'], .0005)
# Saint Martin close-up: coastline and land border from OpenStreetMap (© OpenStreetMap contributors, ODbL), fetched with the OSM API
# (/api/0.6/map tiles + relation 1891583) into /home/user/data/smt_osm.json.
O = json.load(open(D + 'smt_osm.json'))
S['smt'] = O['smt']; S['border'] = O['border']
u = unary_union([Polygon(r) for r in O['smt'][:2]]).buffer(.0025).buffer(-.0025)
S['walk'] = [[round(x, 5), round(y, 5)] for x, y in u.exterior.simplify(.0002).coords]
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
