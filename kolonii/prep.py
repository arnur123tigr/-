"""Data for the 13 colonies reel. Textures: NASA Blue Marble (public domain) via prep_tex.py; vectors: Natural Earth 10m (public domain) -> shapes.json.
The 13 colonies are drawn with today's state borders (Massachusetts with Maine), New France is a simplified hand polygon: both are schematic."""
import json, subprocess
from shapely.geometry import shape, box, Polygon
from shapely.ops import unary_union
D = '/home/user/data/'
subprocess.run(['python3', 'prep_tex.py', 'tex', 'am', '-105', '-52', '22', '56', '36', 'bos', '-72.2', '-69.6', '41.6', '43.2', '240', 'gb', '-12', '6', '48', '61', '50'], check=True)
subprocess.run(['python3', 'grade.py', 'tex/am.jpg', 'tex/bos.jpg', 'tex/gb.jpg'], check=True)
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
st = {f['properties'].get('postal'): shape(f['geometry']) for f in L('ne_10m_admin_1_states_provinces') if f['properties'].get('adm0_a3') == 'USA'}
COL = [['NH', ['NH']], ['MA', ['MA', 'ME']], ['RI', ['RI']], ['CT', ['CT']], ['NY', ['NY']], ['NJ', ['NJ']], ['PA', ['PA']], ['DE', ['DE']], ['MD', ['MD']],
       ['VA', ['VA', 'WV']], ['NC', ['NC']], ['SC', ['SC']], ['GA', ['GA']]]
S = {'col': {k: rings(unary_union([st[p] for p in ps]), .02, .005) for k, ps in COL}}
S['colall'] = rings(unary_union([st[p] for _, ps in COL for p in ps]).buffer(.01), .02, .05)
C = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in L('ne_10m_admin_0_countries')}
land = unary_union([C['USA'], C['CAN']]).intersection(box(-110, 24, -50, 60))
nf = Polygon([(-55, 52), (-60, 47.5), (-64, 48), (-67, 45.6), (-71.5, 45), (-74.5, 45), (-76.5, 44), (-79, 43.2), (-80.5, 42.3), (-81.5, 41.5), (-83, 41.6), (-84.5, 39.5),
              (-85.5, 38), (-87.5, 35.5), (-88.2, 31.5), (-89.3, 30.2), (-90.5, 29.3), (-94, 29.6), (-96, 31), (-98, 36), (-101, 41), (-104, 46), (-104, 52), (-95, 55),
              (-80, 54), (-70, 55), (-60, 55)])
S['nf'] = rings(nf.intersection(land), .03, .2)
east = Polygon([(-55, 52), (-60, 47.5), (-64, 48), (-67, 45.6), (-71.5, 45), (-74.5, 45), (-76.5, 44), (-79, 43.2), (-80.5, 42.3), (-81.5, 41.5), (-83, 41.6), (-84.5, 39.5),
                (-85.5, 38), (-87.5, 35.5), (-88.2, 31.5), (-89.3, 30.2), (-90, 30), (-91, 35), (-90.5, 40), (-91.5, 44), (-95, 49), (-95, 55), (-80, 54), (-70, 55), (-60, 55)])
S['nf_e'] = rings(east.intersection(land), .03, .2)   # what Britain got in 1763 (Canada + east of the Mississippi)
S['gbr'] = rings(C['GBR'], .02, .05); S['irl'] = rings(C['IRL'], .02, .05)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
