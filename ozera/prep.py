"""Data for the Canada lake-names reel. Textures: NASA Blue Marble (public domain) via prep_tex.py; vectors: Natural Earth 10m (public domain) -> shapes.json."""
import json, subprocess, random
from shapely.geometry import shape, box, Point
D = '/home/user/data/'
subprocess.run(['python3', 'prep_tex.py', 'tex', 'can', '-142', '-50', '40', '84', '30', 'det', '-98', '-92', '52', '56', '240', 'kz', '45', '90', '39', '57', '40'], check=True)
subprocess.run(['python3', 'grade.py', 'tex/can.jpg', 'tex/det.jpg', 'tex/kz.jpg'], check=True)
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
            if r.geom_type == 'Polygon': out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
C = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in L('ne_10m_admin_0_countries')}
can = C['CAN']; kaz = C['KAZ']
S = {'can': rings(can, .05, .3), 'kaz': rings(kaz, .03, .1)}
lk = [shape(f['geometry']) for f in L('ne_10m_lakes')] + [shape(f['geometry']) for f in L('ne_10m_lakes_north_america')]
cl = [g for g in lk if g.representative_point().within(can)]
S['lakes'] = [r for g in cl for r in rings(g, .02, .0005)]
S['kzlakes'] = [r for g in lk if g.representative_point().within(kaz.buffer(.3)) for r in rings(g, .02, .0005)]
pts = [g.representative_point() for g in cl]; random.seed(4); random.shuffle(pts)
S['pts'] = [[round(p.x, 2), round(p.y, 2)] for p in pts[:400]]
A1 = {f['properties'].get('name'): shape(f['geometry']) for f in L('ne_10m_admin_1_states_provinces') if f['properties'].get('adm0_a3') == 'CAN'}
S['ns'] = rings(A1['Nova Scotia'], .01, .002)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()}, len(cl))
