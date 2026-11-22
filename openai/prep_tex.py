"""Crop NASA Blue Marble (topo+bathy, July) tiles into equirectangular textures.
Usage: python3 prep_tex.py out_dir name lon0 lon1 lat0 lat1 ppd [name ...]  (groups of 7 args after out_dir)"""
import sys, os
from PIL import Image, ImageEnhance
Image.MAX_IMAGE_PIXELS = None
D = '/home/user/data/'
TILES = {'A1': (-180, -90, 0, 90), 'B1': (-90, 0, 0, 90), 'C1': (0, 90, 0, 90), 'D1': (90, 180, 0, 90), 'C2': (0, 90, -90, 0)}
out = sys.argv[1]; a = sys.argv[2:]; jobs = [a[i:i + 6] for i in range(0, len(a), 6)]
cache = {}
def tile(k):
    if k not in cache:
        cache.clear(); cache[k] = Image.open(D + k + '.jpg'); cache[k].load()
    return cache[k]
res = {}
for name, *v in jobs:
    l0, l1, b0, b1, ppd = map(float, v)
    W, H = int((l1 - l0) * ppd), int((b1 - b0) * ppd)
    res[name] = Image.new('RGB', (W, H), (8, 20, 45))
for k, (tl0, tl1, tb0, tb1) in TILES.items():
    for name, *v in jobs:
        l0, l1, b0, b1, ppd = map(float, v)
        x0, x1, y0, y1 = max(l0, tl0), min(l1, tl1), max(b0, tb0), min(b1, tb1)
        if x0 >= x1 or y0 >= y1: continue
        T = tile(k); s = 240
        box = (int((x0 - tl0) * s), int((tb1 - y1) * s), int((x1 - tl0) * s), int((tb1 - y0) * s))
        c = T.crop(box).resize((round((x1 - x0) * ppd), round((y1 - y0) * ppd)), Image.LANCZOS)
        res[name].paste(c, (round((x0 - l0) * ppd), round((b1 - y1) * ppd)))
        print(name, k, flush=True)
for name, im in res.items():
    im = ImageEnhance.Color(im).enhance(1.05)
    im.save(os.path.join(out, name + '.jpg'), quality=90); print('saved', name, im.size)
