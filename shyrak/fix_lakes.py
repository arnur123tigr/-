"""Water as it was in 519 BC on our Blue Marble textures (2004): the Aral Sea is filled back to its 1960 shoreline (Natural Earth historic lakes),
the reservoirs of the 20th century (Aydarkul, Shardara) and Sarykamysh (dry in antiquity most of the time) are painted over with the land around them.
Usage: python3 fix_lakes.py   (rewrites tex/main.jpg and tex/detail.jpg in place; run once after prep_map.py)"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
Image.MAX_IMAGE_PIXELS = None
WINS = {'tex/main.jpg': (10.0, 146.5, 12.0, 78.0, 60), 'tex/detail.jpg': (50.0, 74.0, 35.0, 47.0, 160)}
ARAL = [r for f in json.load(open('data/ne_10m_lakes_historic.geojson'))['features'] if f['properties'].get('name') == 'Aral Sea'
        for r in ([f['geometry']['coordinates'][0]] if f['geometry']['type'] == 'Polygon' else [p[0] for p in f['geometry']['coordinates']])]
DRY = []
for f in json.load(open('data/ne_10m_lakes.geojson'))['features']:
    if f['properties'].get('name') in ('Aydar Ko‘l', 'Shardara Bgeni', 'Sarygamysh Köli'):
        g = f['geometry']; DRY += [g['coordinates'][0]] if g['type'] == 'Polygon' else [p[0] for p in g['coordinates']]


def mask(rings, size, win, grow=0):
    lon0, lon1, lat0, lat1, ppd = win; m = Image.new('L', size, 0); d = ImageDraw.Draw(m)
    for r in rings: d.polygon([((x - lon0) * ppd, (lat1 - y) * ppd) for x, y in r], fill=255)
    if grow: m = m.filter(ImageFilter.MaxFilter(grow | 1))
    return np.asarray(m).astype(np.float32) / 255


for path, win in WINS.items():
    im = Image.open(path); a = np.asarray(im).astype(np.float32) / 255; ppd = win[4]
    # 1) dry the reservoirs: fill with the land around them (normalised blur that ignores the water)
    md = mask(DRY, im.size, win, grow=int(ppd * .12)); keep = 1 - md
    s = ppd * .35; num = np.stack([gaussian_filter(a[..., c] * keep, s) for c in range(3)], -1); den = gaussian_filter(keep, s)[..., None] + 1e-6
    fill = num / den; rng = np.random.default_rng(3); grain = gaussian_filter(rng.standard_normal(md.shape), 1.2)[..., None] * .025
    soft = gaussian_filter(md, ppd * .02)[..., None]; a = a * (1 - soft) + np.clip(fill + grain, 0, 1) * soft
    # 2) the full Aral: deep water inside, a lighter turquoise rim of shallows along its shore
    ma = mask(ARAL, im.size, win); inner = gaussian_filter(ma, ppd * .18)
    deep = np.array([.025, .085, .13], np.float32); shallow = np.array([.06, .25, .28], np.float32)
    depth = np.clip((inner - .5) * 2.2, 0, 1)[..., None]; sea = shallow + (deep - shallow) * depth ** .7
    edge = gaussian_filter(ma, ppd * .015)[..., None]; a = a * (1 - edge) + sea * edge
    Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)).save(path, quality=88, subsampling=0); print(path, 'done')
