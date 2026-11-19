"""Data for the Asia-regions reel (JAS re-make). Textures: NASA Blue Marble (public domain) via prep_tex.py; vectors: Natural Earth 10m (public domain) -> shapes.json."""
import json, subprocess
from shapely.geometry import shape, box
from shapely.ops import unary_union
D = '/home/user/data/'
subprocess.run(['python3', 'prep_tex.py', 'tex', 'asia', '20', '180', '-14', '82', '16'], check=True)
subprocess.run(['python3', 'grade.py', 'tex/asia.jpg'], check=True)
from PIL import Image
Image.open(D + 'world.jpg').save('tex/world.jpg', quality=90); subprocess.run(['python3', 'grade.py', 'tex/world.jpg'], check=True)
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.03, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        q = p.simplify(tol)
        for r in polys(q):
            if r.geom_type == 'Polygon': out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
C = {f['properties']['ADM0_A3']: shape(f['geometry']).buffer(0) for f in L('ne_10m_admin_0_countries')}
R = {'south': 'IND PAK AFG BGD NPL BTN LKA MDV', 'central': 'KAZ UZB TKM KGZ TJK', 'east': 'CHN MNG PRK KOR JPN TWN',
     'se': 'VNM THA LAO KHM MMR MYS SGP IDN PHL BRN TLS', 'me': 'IRN IRQ SAU ISR PSX JOR SYR LBN TUR YEM OMN ARE QAT BHR KWT', 'cauc': 'GEO ARM AZE'}
S = {}
for k, v in R.items():
    gs = [C[a] for a in v.split() if a in C]; missing = [a for a in v.split() if a not in C]
    if missing: print('missing', k, missing)
    S[k] = rings(unary_union(gs), .04, .02)
S['north'] = rings(C['RUS'].intersection(box(60, 41, 180, 82)), .06, .1)
S['russia_eu'] = rings(C['RUS'].intersection(box(19, 41, 60, 82)), .06, .1)
S['egy'] = rings(C['EGY'], .04, .05)
S['all'] = rings(unary_union([C[a] for v in R.values() for a in v.split() if a in C] + [C['RUS'].intersection(box(60, 41, 180, 82))]).buffer(.05), .08, .5)
for a in ['IND', 'PAK', 'AFG', 'BGD', 'NPL', 'BTN', 'LKA', 'MDV', 'KAZ', 'UZB', 'CHN', 'MNG', 'PRK', 'KOR', 'JPN', 'TWN', 'VNM', 'THA', 'IDN', 'PHL', 'IRN', 'IRQ', 'SAU', 'ISR', 'PSX']:
    S['c_' + a] = rings(C[a], .03, .002)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
