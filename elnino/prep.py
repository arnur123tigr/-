"""Data for the El Niño reel (JAS re-make). Pacific-centred: longitudes < -30 are shifted +360 (so the Pacific is continuous).
Textures: NASA Blue Marble (public domain) via prep_tex.py; vectors: Natural Earth 10m (public domain) -> shapes.json."""
import json, subprocess
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely.affinity import translate
from PIL import Image
D = '/home/user/data/'
subprocess.run(['python3', 'prep_tex.py', 'tex', 'w1', '90', '180', '-50', '66', '14', 'w2', '-180', '-30', '-50', '66', '14', 'peru', '-92', '-68', '-22', '6', '40'], check=True)
a, b = Image.open('tex/w1.jpg'), Image.open('tex/w2.jpg'); im = Image.new('RGB', (a.width + b.width, a.height)); im.paste(a, (0, 0)); im.paste(b, (a.width, 0)); im.save('tex/pac.jpg', quality=90)
for f in ['w1', 'w2']: subprocess.run(['rm', f'tex/{f}.jpg'])
for f in ['pac', 'peru']: subprocess.run(['python3', 'grade.py', f'tex/{f}.jpg'], check=True)
Image.open(D + 'world.jpg').save('tex/world.jpg', quality=90); subprocess.run(['python3', 'grade.py', 'tex/world.jpg'], check=True)
C = {f['properties']['ADM0_A3']: shape(f['geometry']).buffer(0) for f in json.load(open(D + 'ne_10m_admin_0_countries.geojson'))['features']}
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.05, min_area=0, shift=True):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        q = p.simplify(tol)
        for r in polys(q):
            if r.geom_type != 'Polygon': continue
            xs = [x for x, _ in r.exterior.coords]; dx = 360 if shift and max(xs) < -30 else 0
            out.append([[round(x + dx, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
S = {}
S['can'] = rings(C['CAN'], .08, .3)
S['usa_s'] = rings(C['USA'].intersection(box(-125, 24, -75, 37.5)), .06, .1)
S['flood'] = rings(unary_union([C[k] for k in ['ECU', 'PER', 'PRY', 'URY']] + [C['BRA'].intersection(box(-58, -34, -48, -24)), C['ARG'].intersection(box(-62, -35, -53, -25))]), .05, .05)
S['idn'] = rings(C['IDN'], .05, .05); S['aus'] = rings(C['AUS'], .06, .1)
S['peru'] = rings(unary_union([C['PER'], C['ECU']]), .02, .01)
S['ind'] = rings(C['IND'], .06, .1, False); S['chn'] = rings(C['CHN'], .06, .1, False)
# land mask for the warm/cold water layer (lon 90..330)
land = unary_union([g for k, g in C.items() if g.intersects(box(90, -60, 180, 72)) or g.intersects(box(-180, -60, -30, 72))])
land = unary_union([land.intersection(box(90, -60, 180, 72)), land.intersection(box(-180, -60, -30, 72))])
S['land'] = rings(land, .08, .05)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
