"""Map assets for the Shyrak reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin are taken unchanged from the Turkic Khaganate reel (kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  Turan lowland (Kyzylkum, Syr Darya, Amu Darya, the Aral), lon 50..74, lat 35..47, 160 px/deg, relief from Terrarium z8
  shapes.json     modern borders (faint, for orientation), Syr Darya, Amu Darya, the Aral Sea as it was before the 1960s
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
import mapkit as mk
DETAIL = (50.0, 74.0, 35.0, 47.0, 160)
BOX = (38, 86, 22, 52)          # vectors are clipped to this lon/lat box


def make_tex():
    lon0, lon1, lat0, lat1, ppd = DETAIL
    img = np.asarray(mk.bm_region(*DETAIL)).astype(np.float32) / 255
    rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 8, 3.2, 10)
    Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/detail.jpg', quality=88, subsampling=0)
    print('detail.jpg', img.shape)


def lines(geom):
    if geom['type'] == 'LineString': return [geom['coordinates']]
    if geom['type'] == 'MultiLineString': return geom['coordinates']
    if geom['type'] == 'Polygon': return [geom['coordinates'][0]]
    if geom['type'] == 'MultiPolygon': return [p[0] for p in geom['coordinates']]
    return []


def inbox(r): return any(BOX[0] <= x <= BOX[1] and BOX[2] <= y <= BOX[3] for x, y in r)
def rnd(r, k=3): return [[round(x, k), round(y, k)] for x, y in r]


def make_vec():
    out = {'borders': [], 'syr': [], 'amu': [], 'aral': []}
    for f in json.load(open('data/ne_50m_admin_0_boundary_lines_land.geojson'))['features']:
        out['borders'] += [rnd(r) for r in lines(f['geometry']) if inbox(r)]
    for f in json.load(open('data/ne_10m_rivers_lake_centerlines.geojson'))['features']:
        n = (f['properties'].get('name') or '').replace('  ', ' ')
        key = {'Syr Darya': 'syr', 'Amu Darya': 'amu'}.get(n)
        if key: out[key] += [rnd(r) for r in lines(f['geometry'])]
    for f in json.load(open('data/ne_10m_lakes_historic.geojson'))['features']:
        if f['properties'].get('name') == 'Aral Sea': out['aral'] += [rnd(r) for r in lines(f['geometry'])]
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: (len(v), sum(len(r) for r in v)) for k, v in out.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
