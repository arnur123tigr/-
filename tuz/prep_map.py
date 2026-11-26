"""Map assets for the saltiest-sea reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from tyn/ (<- kulja/ <- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds three detail textures (NASA Blue Marble NG C1 + Terrarium z7 relief):
  tex/dead.jpg   Levant / Dead Sea   lon 33..37.5, lat 29.5..33.5, 240 px/deg
  tex/aral.jpg   Aral Sea            lon 57..63,   lat 43..47.5,   200 px/deg
  tex/baltic.jpg Baltic Sea          lon 8..31,    lat 53..66.5,    80 px/deg
and shapes.json: borders, Kazakhstan, Dead Sea, Caspian, North/South Aral (Natural Earth lakes), Red Sea + gulfs, Baltic + gulfs
(Natural Earth marine areas), the desert shores of the Red Sea (land within ~2.5 deg), rivers flowing into the Baltic.
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, Point
from shapely.ops import unary_union
import mapkit as mk
DET = {'dead': (33.0, 37.5, 29.5, 33.5, 240), 'aral': (57.0, 63.0, 43.0, 47.5, 200), 'baltic': (8.0, 31.0, 53.0, 66.5, 80)}
BOX = (5, 150, 5, 78)


def make_tex():
    for k, R in DET.items():
        lon0, lon1, lat0, lat1, ppd = R
        img = np.asarray(mk.bm_region(*R)).astype(np.float32) / 255
        rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 7, 5.0, 6)
        Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save(f'tex/{k}.jpg', quality=88, subsampling=0)
        print(k, img.shape, flush=True)


def lines(geom):
    if not geom or not geom.get('coordinates'): return []
    t = geom['type']; c = geom['coordinates']
    return {'LineString': [c], 'MultiLineString': c, 'Polygon': [c[0]], 'MultiPolygon': [p[0] for p in c]}.get(t, [])
def inbox(r, b=BOX): return any(b[0] <= x <= b[1] and b[2] <= y <= b[3] for x, y in r)
def rnd(r, k=3): return [[round(x, k), round(y, k)] for x, y in r]
def thin(r, step=.04):
    o = [r[0]]
    for p in r[1:]:
        if abs(p[0] - o[-1][0]) + abs(p[1] - o[-1][1]) >= step: o.append(p)
    return o
def rings(g, step=.05, amin=.0005):
    polys = [g] if g.geom_type == 'Polygon' else [p for p in g.geoms if p.geom_type == 'Polygon']
    return [rnd(thin(list(p.exterior.coords), step)) for p in polys if p.area > amin]


def make_vec():
    out = {'borders': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    land = None
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        if f['properties']['ADMIN'] == 'Kazakhstan': out['kz'] = [rnd(thin(r, .05)) for r in lines(f['geometry']) if len(r) > 30]
    LK = {}
    for f in json.load(open('data/ne_10m_lakes.geojson'))['features']:
        n = f['properties'].get('name')
        if n in ('Dead Sea', 'North Aral Sea', 'South Aral Sea'): LK.setdefault(n, []).append(shape(f['geometry']).buffer(0))
    MR = {}
    for f in json.load(open('data/ne_10m_geography_marine_polys.geojson'))['features']:
        n = f['properties'].get('name')
        if n in ('Red Sea', 'Gulf of Suez', 'Gulf of Aqaba', 'Baltic Sea', 'Gulf of Finland', 'Gulf of Bothnia', 'Gulf of Riga', 'Caspian Sea', 'Arabian Sea'):
            MR.setdefault(n, []).append(shape(f['geometry']).buffer(0))
    U = lambda gs: unary_union(gs).buffer(.01).buffer(-.01)
    out['dead'] = rings(U(LK['Dead Sea']), .005, 1e-5)
    out['aralN'] = rings(U(LK['North Aral Sea']), .01, 1e-4); out['aralS'] = rings(U(LK['South Aral Sea']), .01, 1e-4)
    red = U(MR['Red Sea'] + MR['Gulf of Suez'] + MR['Gulf of Aqaba']); bal = U(MR['Baltic Sea'] + MR['Gulf of Finland'] + MR['Gulf of Bothnia'] + MR['Gulf of Riga'])
    out['red'] = rings(red, .03); out['baltic'] = rings(bal, .03, .002); out['casp'] = rings(U(MR['Caspian Sea']), .03)
    lnd = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open('data/ne_10m_land.geojson'))['features']
                       if shape(f['geometry']).intersects(red.buffer(3))])
    shore = red.buffer(2.6).intersection(lnd).difference(red.buffer(.02))
    out['desert'] = rings(shore.simplify(.03), .05, .01)
    riv = []
    for fn in ('ne_10m_rivers_lake_centerlines', 'ne_10m_rivers_europe'):
        for f in json.load(open(f'data/{fn}.geojson'))['features']:
            for r in lines(f['geometry']):
                if len(r) < 4: continue
                a, b = Point(r[0]), Point(r[-1])
                if not (8 < r[-1][0] < 31 and 53 < r[-1][1] < 66.5): continue
                da, db = bal.distance(a), bal.distance(b)
                if min(da, db) > .08: continue
                if da < db: r = r[::-1]                       # flow towards the sea
                L = sum(np.hypot(r[i + 1][0] - r[i][0], r[i + 1][1] - r[i][1]) for i in range(len(r) - 1))
                if L > .8: riv.append(rnd(thin(r, .03)))
    out['rivers'] = riv
    for f in json.load(open('data/ne_10m_lakes_historic.geojson'))['features']:
        if 'Aral' in (f['properties'].get('name') or ''): out['aral1960'] = rings(shape(f['geometry']).buffer(0), .03, .01)
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: len(v) for k, v in out.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
