"""Map assets for the Africa rift reel (run once after fetch_data.sh). Uses mapkit.py (Blue Marble grading, Terrarium relief).
  tex/main.jpg    Africa + Arabia, lon -20..60, lat -36..40, 40 px/deg (NASA Blue Marble NG tiles B1 B2 C1 C2), relief Terrarium z6
  tex/detail.jpg  East African Rift, lon 28..50, lat -12..18, 120 px/deg, relief Terrarium z8
  dem.bin         Int16 heights (m) for the main window, 8 samples/deg
  shapes.json     borders, Kazakhstan outline, Nubian / Somali plates on land (PB2002), all plate boundaries (PB2002),
                  the rift branches (hand-drawn after USGS / Wikipedia maps), the Mai Mahiu road (Natural Earth roads)
tex/world.jpg comes from tyn/.  Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, box, LineString
from shapely.ops import unary_union
import mapkit as mk
Image.MAX_IMAGE_PIXELS = None
MAIN = (-20.0, 60.0, -36.0, 40.0, 40)
DETAIL = (28.0, 50.0, -12.0, 18.0, 120)
TILES = {'B1.jpg': (-90, 0), 'B2.jpg': (-90, -90), 'C1.jpg': (0, 0), 'C2.jpg': (0, -90)}     # (lon0, lat0) of each 90° tile


def bm(lon0, lon1, lat0, lat1, ppd):
    w, h = int(round((lon1 - lon0) * ppd)), int(round((lat1 - lat0) * ppd)); out = Image.new('RGB', (w, h))
    for name, (a0, b0) in TILES.items():
        l0, l1, t0, t1 = max(lon0, a0), min(lon1, a0 + 90), max(lat0, b0), min(lat1, b0 + 90)
        if l1 <= l0 or t1 <= t0: continue
        im = Image.open('data/' + name)
        part = im.crop((round((l0 - a0) * 240), round((b0 + 90 - t1) * 240), round((l1 - a0) * 240), round((b0 + 90 - t0) * 240)))
        x0, x1 = round((l0 - lon0) * ppd), round((l1 - lon0) * ppd); y0, y1 = round((lat1 - t1) * ppd), round((lat1 - t0) * ppd)
        out.paste(part.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0)); print('  ', name, flush=True)
    return out


def make_tex():
    lon0, lon1, lat0, lat1, ppd = MAIN
    img = np.asarray(bm(*MAIN)).astype(np.float32) / 255
    rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 6, 5.0, 4)
    Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/main.jpg', quality=88, subsampling=0); print('main', img.shape)
    k = ppd // 8; hh = np.maximum(hm, 0)[:hm.shape[0] // k * k, :hm.shape[1] // k * k]
    dm = hh.reshape(hh.shape[0] // k, k, hh.shape[1] // k, k).mean((1, 3))
    np.clip(dm, 0, 9000).astype('<i2').tofile('dem.bin'); print('dem.bin', dm.shape)
    lon0, lon1, lat0, lat1, ppd = DETAIL
    img = np.asarray(bm(*DETAIL)).astype(np.float32) / 255
    rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 8, 3.5, 8)
    Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/detail.jpg', quality=88, subsampling=0); print('detail', img.shape)


rnd = lambda r, k=3: [[round(x, k), round(y, k)] for x, y in r]
def rings(g, tol=.03, amin=.05):
    g = g.simplify(tol, preserve_topology=True)
    ps = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
    return [rnd(p.exterior.coords) for p in ps if p.area > amin]
def lines(g):
    t = g.geom_type
    return [list(g.coords)] if t == 'LineString' else [list(l.coords) for l in g.geoms if l.geom_type == 'LineString'] if hasattr(g, 'geoms') else []
# rift branches (north -> south)
EAST = [(43.2, 11.6), (42.4, 11.55), (41.6, 11.2), (40.9, 10.6), (40.2, 9.6), (39.4, 8.4), (38.6, 7.3), (37.9, 6.1), (37.2, 5.0), (36.5, 4.1),
        (36.15, 3.0), (36.05, 1.8), (35.95, .6), (36.2, -.5), (36.35, -1.2), (36.1, -2.2), (35.85, -3.4), (35.6, -4.6), (35.4, -5.6)]
WEST = [(31.3, 2.6), (30.7, 1.6), (30.0, .3), (29.6, -.6), (29.3, -1.6), (29.1, -2.6), (29.25, -3.6), (29.5, -5.0), (29.9, -6.6), (30.6, -7.9),
        (31.6, -8.5), (32.6, -8.9), (33.6, -9.7), (34.15, -10.8), (34.4, -12.0), (34.7, -13.4), (35.2, -14.6)]
RED = [(32.6, 29.9), (33.6, 28.0), (34.9, 26.0), (36.4, 23.0), (38.0, 20.5), (39.3, 18.0), (40.6, 15.6), (42.0, 13.6), (43.3, 12.6)]
ADEN = [(43.3, 12.0), (44.6, 12.2), (46.5, 12.7), (48.5, 13.4), (50.5, 14.0), (52.0, 14.4)]


def make_vec():
    out = {'east': EAST, 'west': WEST, 'red': RED, 'aden': ADEN, 'borders': []}
    bb = box(-25, -40, 65, 45)
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for l in lines(shape(f['geometry']).intersection(bb).simplify(.03)):
            if len(l) > 1: out['borders'].append(rnd(l))
    land = []
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        p = f['properties']; g = shape(f['geometry']).buffer(0)
        if p['ADMIN'] == 'Kazakhstan': out['kz'] = rings(g, .05, .5)
        if p['CONTINENT'] == 'Africa' or p['ADMIN'] in ('Yemen', 'Saudi Arabia', 'Oman'): land.append(g)
    land = unary_union(land).buffer(.02).buffer(-.02)
    out['africa'] = rings(land.intersection(box(-20, -36, 60, 38)), .04, .3)
    P = {}
    for f in json.load(open('data/pb_plates.json'))['features']:
        c = f['properties']['Code']; g = shape(f['geometry']).buffer(0); P[c] = unary_union([P[c], g]) if c in P else g
    out['nubia'] = rings(P['AF'].intersection(land), .04, .2); out['somalia'] = rings(P['SO'].intersection(land), .04, .2)
    pb = []
    for f in json.load(open('data/pb_boundaries.json'))['features']:
        for l in lines(shape(f['geometry']).simplify(.15)):
            if len(l) > 1: pb.append(rnd(l, 2))
    out['plates'] = pb
    road = []
    for f in json.load(open('data/ne_10m_roads.geojson'))['features']:
        g = shape(f['geometry']).intersection(box(35.6, -1.8, 37.2, -.6))
        for l in lines(g):
            if len(l) > 1: road.append(rnd(l, 4))
    out['road'] = road
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: len(v) for k, v in out.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
