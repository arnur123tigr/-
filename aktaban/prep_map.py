"""Map assets for the Aktaban 1723 reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from kulja/ (<- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  Kazakhstan + Central Asia, lon 50..90, lat 35..52, 100 px/deg, relief from Terrarium z8;
                  the Aral Sea is filled back to its historic shore (Natural Earth lakes_historic): in 1723 it was full
  shapes.json     modern borders, Kazakhstan outline, rivers (Syr Darya, Amu Darya, Ili, Ural, Chu, Talas), Balkhash, historic Aral
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import mapkit as mk
DETAIL = (50.0, 90.0, 35.0, 52.0, 100)
BOX = (10, 150, 10, 78)


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
def aral():
    for f in json.load(open('data/ne_10m_lakes_historic.geojson'))['features']:
        if f['properties'].get('name') == 'Aral Sea': return [r for r in lines(f['geometry'])]


def make_tex():
    lon0, lon1, lat0, lat1, ppd = DETAIL
    bm = mk.bm_region(*DETAIL); img = np.asarray(bm).astype(np.float32) / 255
    # the full Aral: water colour sampled from the open Caspian, soft shore
    h, w = img.shape[:2]; m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for r in aral(): d.polygon([((x - lon0) * ppd, (lat1 - y) * ppd) for x, y in r], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32)[..., None] / 255
    cy, cx = int((lat1 - 42.0) * ppd), int((51.0 - lon0) * ppd); water = img[cy - 20:cy + 20, cx - 20:cx + 20].reshape(-1, 3).mean(0)
    img = img * (1 - m) + water * m
    rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 8, 3.0, 10)
    hm = np.where(m[..., 0] > .5, -20, hm); rel = rel * (1 - m[..., 0]) + rel.mean() * m[..., 0]
    Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/detail.jpg', quality=88, subsampling=0)
    print('detail.jpg', img.shape, 'water', water)


def make_vec():
    out = {'borders': [], 'kz': [], 'rivers': [], 'balkhash': [], 'aral': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        if f['properties']['ADMIN'] == 'Kazakhstan': out['kz'] += [rnd(thin(r, .05)) for r in lines(f['geometry']) if len(r) > 30]
    riv = {}
    for f in json.load(open('data/ne_10m_rivers_lake_centerlines.geojson'))['features']:
        n = ' '.join((f['properties'].get('name') or '').split())
        if n in ('Syr Darya', 'Amu Darya', 'Ile', 'Ural', 'Naryn'):
            riv.setdefault(n, []).extend(rnd(r) for r in lines(f['geometry']) if inbox(r, (45, 92, 35, 56)))
    # Chu and Talas are not in Natural Earth: drawn by hand (approximate courses)
    riv['Chu'] = [[[76.2, 42.55], [75.6, 42.75], [75.0, 42.85], [74.4, 43.1], [73.7, 43.6], [72.6, 44.2], [71.4, 44.6], [70.2, 44.9], [69.0, 45.0]]]
    riv['Talas'] = [[[72.6, 42.45], [71.9, 42.6], [71.4, 42.9], [71.0, 43.4], [70.5, 44.0], [70.1, 44.4]]]
    out['rivers'] = [r for v in riv.values() for r in v]
    for f in json.load(open('data/ne_10m_lakes.geojson'))['features']:
        if f['properties'].get('name') == 'Lake Balkhash': out['balkhash'] += [rnd(r) for r in lines(f['geometry'])]
    out['aral'] = [rnd(thin(r, .03)) for r in aral()]
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: (len(v), sum(len(r) for r in v)) for k, v in out.items()}, list(riv))


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
