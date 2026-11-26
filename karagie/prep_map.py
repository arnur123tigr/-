"""Map assets for the Karagiye reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from tyn/ (<- kulja/ <- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  Mangystau + Atyrau, lon 48..56, lat 41..48.5, 200 px/deg, relief from Terrarium z9
  tex/peak.jpg    Khan Tengri, lon 78.5..81.5, lat 41.5..43.3, 240 px/deg, relief from Terrarium z9
  shapes.json     borders, Kazakhstan outline, land below sea level round the Caspian (Terrarium z7 < 0 m on land),
                  the Karagiye bowl (z9 < -40 m), the west-east height profile Karagiye -> Khan Tengri (z7, max along a 0.25 deg strip)
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
import contourpy
import mapkit as mk
DETAIL = (48.0, 56.0, 41.0, 48.5, 200)
PEAK = (78.5, 81.5, 41.5, 43.3, 240)
BOX = (10, 150, 10, 78)
KARA, KT = (51.76, 43.38), (80.17, 42.21)


def make_tex():
    for name, win in (('detail', DETAIL), ('peak', PEAK)):
        lon0, lon1, lat0, lat1, ppd = win
        img = np.asarray(mk.bm_region(*win)).astype(np.float32) / 255
        rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 9, 4.0 if name == 'detail' else 2.2, 6)
        Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save(f'tex/{name}.jpg', quality=88, subsampling=0)
        print(name, img.shape)


def lines(geom):
    t = geom['type']; c = geom['coordinates']
    return {'LineString': [c], 'MultiLineString': c, 'Polygon': [c[0]], 'MultiPolygon': [p[0] for p in c]}.get(t, [])
def inbox(r, b=BOX): return any(b[0] <= x <= b[1] and b[2] <= y <= b[3] for x, y in r)
def rnd(r, k=3): return [[round(x, k), round(y, k)] for x, y in r]
def thin(r, step=.04):
    o = [r[0]]
    for p in r[1:]:
        if abs(p[0] - o[-1][0]) + abs(p[1] - o[-1][1]) >= step: o.append(p)
    return o
def rings(g, step=.05, amin=.05):
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [rnd(thin(list(p.exterior.coords), step)) for p in polys if p.area > amin]


def contour_poly(hm, thr, lon0, lat1, ppd, below=True):
    """Polygons where hm < thr (row 0 = north)."""
    g = contourpy.contour_generator(z=(hm if below else -hm).astype(np.float64), fill_type=contourpy.FillType.OuterCode)
    polys = []
    for pts, codes in zip(*g.filled(-1e9, thr if below else -thr)):
        # split into rings: code 1 = move to
        idx = list(np.where(codes == 1)[0]) + [len(codes)]
        rs = [pts[idx[i]:idx[i + 1]] for i in range(len(idx) - 1)]
        cv = lambda r: [(lon0 + (x + .5) / ppd, lat1 - (y + .5) / ppd) for x, y in r]
        if len(rs[0]) < 4: continue
        p = Polygon(cv(rs[0]), [cv(r) for r in rs[1:] if len(r) >= 4]).buffer(0)
        polys.append(p)
    return unary_union(polys)


def make_vec():
    out = {'borders': [], 'kz': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    land = []
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        a = f['properties']['ADMIN']
        if a == 'Kazakhstan': out['kz'] += [rnd(thin(r, .05)) for r in lines(f['geometry']) if len(r) > 30]
        g = shape(f['geometry'])
        if g.intersects(Polygon([(40, 36), (62, 36), (62, 52), (40, 52)])): land.append(g.buffer(0))
    land = unary_union(land).buffer(-.03)
    # land below sea level, Caspian lowland (z7, 32 px/deg)
    lon0, lon1, lat0, lat1, ppd = 44.0, 60.0, 40.0, 50.5, 32
    hm = mk.blur(mk.dem_grid(lon0, lon1, lat0, lat1, ppd, 7), 1.2)
    low = contour_poly(hm, 0, lon0, lat1, ppd).intersection(land).buffer(.04).buffer(-.04)
    out['low'] = rings(low, .04, .02)
    # the Karagiye bowl (z9)
    lon0, lon1, lat0, lat1, ppd = 50.9, 52.6, 42.9, 43.9, 120
    hm = mk.blur(mk.dem_grid(lon0, lon1, lat0, lat1, ppd, 9), 1.5)
    bowl = contour_poly(hm, -40, lon0, lat1, ppd).intersection(land)
    polys = [bowl] if bowl.geom_type == 'Polygon' else list(bowl.geoms)
    from shapely.geometry import Point
    bowl = max([p for p in polys if p.distance(Point(*KARA)) < .3], key=lambda p: p.area)
    out['bowl'] = rings(bowl.buffer(.01).buffer(-.01), .01, .0005)
    # height profile Karagiye -> Khan Tengri: max height across a 0.25 deg strip, 240 samples
    lon0, lon1, lat0, lat1, ppd = 44.0, 82.0, 40.0, 50.5, 16
    hm = mk.dem_grid(lon0, lon1, lat0, lat1, ppd, 7)
    prof = []
    for i in range(240):
        u = i / 239; lon = KARA[0] + (KT[0] - KARA[0]) * u; lat = KARA[1] + (KT[1] - KARA[1]) * u
        x = int((lon - lon0) * ppd); y = int((lat1 - lat) * ppd); w = 2
        prof.append(float(hm[max(0, y - w):y + w + 1, max(0, x - w):x + w + 1].max() if 0 < u < 1 else 0))
    prof[0] = -132; prof[-1] = 7010
    out['prof'] = [round(v) for v in prof]
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: len(v) for k, v in out.items()}, 'low area', round(low.area, 2), 'bowl', round(bowl.area, 4), bowl.bounds)


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
