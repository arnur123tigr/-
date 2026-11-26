"""Map assets for the Kulja 1881 reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from semey/ (<- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  the Ili valley and Zhetysu, lon 74..86, lat 41..47, 240 px/deg, relief from Terrarium z9
  shapes.json     modern borders, Kazakhstan / China outlines (Kazakhstan with Baikonur), the Ili, Tekes, Kunes, Balkhash, the KZ-CN border at Khorgos
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
import mapkit as mk
DETAIL = (74.0, 86.0, 41.0, 47.0, 240)
BOX = (10, 150, 10, 78)


def make_tex():
    lon0, lon1, lat0, lat1, ppd = DETAIL
    img = np.asarray(mk.bm_region(*DETAIL)).astype(np.float32) / 255
    rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 9, 3.0, 12)
    Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/detail.jpg', quality=88, subsampling=0)
    print('detail.jpg', img.shape)


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


def make_vec():
    out = {'borders': [], 'kz': [], 'cn': [], 'ru': [], 'ili': [], 'tekes': [], 'kunes': [], 'balkhash': [], 'kzcn': [], 'ak': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        k = {'Kazakhstan': 'kz', 'China': 'cn', 'Russia': 'ru'}.get(f['properties']['SOVEREIGNT'])
        if k and (k != 'cn' or f['properties']['ADMIN'] == 'China'):
            out[k] += [rnd(thin(r, .05 if k == 'kz' else .12)) for r in lines(f['geometry']) if len(r) > 30]
        if f['properties']['ADMIN'] == 'United States of America':
            out['ak'] += [rnd(thin(r, .1)) for r in lines(f['geometry']) if len(r) > 30 and max(p[1] for p in r) > 54 and min(p[0] for p in r) < -129]
    for f in json.load(open('data/ne_10m_rivers_lake_centerlines.geojson'))['features']:
        n = (f['properties'].get('name') or '').strip()
        key = {'Ile': 'ili', 'Ili': 'ili', 'Tekes': 'tekes', 'Künes': 'kunes', 'Kunes': 'kunes'}.get(n)
        if key: out[key] += [rnd(r) for r in lines(f['geometry'])]
    for f in json.load(open('data/ne_10m_lakes.geojson'))['features']:
        if f['properties'].get('name') == 'Lake Balkhash': out['balkhash'] += [rnd(r) for r in lines(f['geometry'])]
    # the Kazakhstan-China land border between the Dzungarian Alatau and the Tian Shan (along the Khorgos and further south)
    for r in out['borders']:
        seg = [p for p in r if 79.6 <= p[0] <= 81.0 and 42.6 <= p[1] <= 45.2]
        if len(seg) > 10: out['kzcn'].append(seg)
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: (len(v), sum(len(r) for r in v)) for k, v in out.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
