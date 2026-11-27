"""Map assets for the fortress-lines reel «Бізге қарсы салынған қалалар» (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from karagie/ (<- tyn/ <- kulja/ <- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  Almaty and the Zailiysky Alatau, lon 75.8..78.2, lat 42.7..44.0, 240 px/deg (Blue Marble native), relief from Terrarium z9
  tex/peak.jpg    north-east Kazakhstan (Irtysh, Ishim), lon 68..84.5, lat 48..56, 120 px/deg, relief from Terrarium z8
  shapes.json     borders, Kazakhstan outline, rivers (Natural Earth: Irtysh, Ishim, Ural, Tobol, Or, Ilek; the Uy and the Malaya Almatinka drawn by hand),
                  the right bank of the Ural (a 150 km band on the right side of the river, from Orsk down to the Caspian)
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, LineString, MultiLineString
from shapely.ops import linemerge, unary_union
import mapkit as mk
DETAIL = (75.8, 78.2, 42.7, 44.0, 240)
PEAK = (68.0, 84.5, 48.0, 56.0, 120)
BOX = (10, 150, 10, 78)


def make_tex():
    for name, win, z, zf in (('detail', DETAIL, 9, 2.4), ('peak', PEAK, 8, 4.0)):
        lon0, lon1, lat0, lat1, ppd = win
        img = np.asarray(mk.bm_region(*win)).astype(np.float32) / 255
        rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, z, zf, 6)
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


def river(names, files, start=None):
    """Natural Earth segments of one river merged into one line, oriented to begin near `start` (lon, lat)."""
    segs = []
    for fn in files:
        for f in json.load(open(f'data/{fn}.geojson'))['features']:
            if f['properties'].get('name') in names: segs += lines(f['geometry'])
    m = linemerge(MultiLineString(segs))
    if m.geom_type == 'MultiLineString': m = max(m.geoms, key=lambda g: g.length)
    c = list(m.coords)
    if start and np.hypot(c[-1][0] - start[0], c[-1][1] - start[1]) < np.hypot(c[0][0] - start[0], c[0][1] - start[1]): c = c[::-1]
    return c


def make_vec():
    out = {'borders': [], 'kz': [], 'riv': {}}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        if f['properties']['ADMIN'] == 'Kazakhstan': out['kz'] += [rnd(thin(r, .05)) for r in lines(f['geometry']) if len(r) > 30]
    R = 'ne_10m_rivers_lake_centerlines'; E = 'ne_10m_rivers_europe'
    # the Irtysh from the Chinese Altai down to Omsk and beyond (two Natural Earth features), source first
    irt = river(['Ertix', 'Irtysh'], [R], start=(90.3, 47.6))
    out['riv']['irtysh'] = rnd(thin([p for p in irt if p[1] < 58.5], .03))
    out['riv']['ishim'] = rnd(thin(river(['Ishim'], [R], start=(67, 53.3)), .03))
    ural = river(['Ural'], [R], start=(59.45, 54.7))                 # source in the Ural mountains -> Caspian
    out['riv']['ural'] = rnd(thin(ural, .03))
    out['riv']['tobol'] = rnd(thin(river(['Tobol'], [R], start=(60.9, 51.7)), .03))
    out['riv']['or'] = rnd(thin(river(['Or'], [E], start=(58.2, 49.35)), .03))
    out['riv']['ilek'] = rnd(thin(river(['Ilek'], [E], start=(57.98, 49.8)), .03))
    # the Uy (not in Natural Earth): from the Ural mountains east past Troitsk to the Tobol at Ust-Uysk (approximate, from the atlas)
    out['riv']['uy'] = [[59.0, 54.38], [59.6, 54.2], [60.3, 54.12], [61.0, 54.05], [61.57, 54.08], [62.2, 54.18], [62.9, 54.2], [63.6, 54.28], [64.3, 54.26], [64.75, 54.4]]
    # the Malaya Almatinka through Almaty (approximate): from Medeu down to the north
    out['riv']['malm'] = [[77.06, 43.15], [77.02, 43.2], [76.99, 43.235], [76.975, 43.26], [76.97, 43.29], [76.965, 43.33], [76.97, 43.38], [76.985, 43.43]]
    # right bank of the Ural, from Orsk to the sea: the band on the right of the flow direction (shapely: negative single-sided buffer)
    u = LineString(ural); i0 = int(np.argmin([abs(x - 58.6) + abs(y - 51.2) for x, y in ural]))
    seg = LineString(ural[i0:])
    band = seg.buffer(-1.6, single_sided=True, join_style=1).simplify(.02)
    band = band.intersection(unary_union([shape(f['geometry']) for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']
                                           if f['properties']['ADMIN'] in ('Kazakhstan', 'Russia')]).buffer(0))
    polys = [band] if band.geom_type == 'Polygon' else list(band.geoms)
    out['bank'] = [rnd(thin(list(p.exterior.coords), .03)) for p in polys if p.area > .05]
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: len(v) for k, v in out.items()}, {k: len(v) for k, v in out['riv'].items()}, 'bank area', round(band.area, 2))


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
