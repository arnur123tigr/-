"""Mercator texture (from the equirectangular Blue Marble world.jpg) + shapes.json (Natural Earth 10m, public domain)."""
import json, sys, numpy as np
from PIL import Image
sys.path.insert(0, '../_shared'); from geo import *
Image.MAX_IMAGE_PIXELS = None
M = lambda lat: np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))
src = np.asarray(Image.open('../uk/tex/world.jpg').convert('RGB')); h0, w0 = src.shape[:2]
PX = 10; LAT0, LAT1 = -80, 84; y0, y1 = M(LAT0), M(LAT1)
Wd, Hd = 360 * PX, int((y1 - y0) * PX)
yy = y1 - (np.arange(Hd) + .5) / PX; lat = np.degrees(2 * np.arctan(np.exp(np.radians(yy))) - np.pi / 2)
rows = np.clip(((90 - lat) / 180 * h0).astype(int), 0, h0 - 1)
cols = np.clip(((np.arange(Wd) + .5) / Wd * w0).astype(int), 0, w0 - 1)
Image.fromarray(src[rows][:, cols]).save('tex/merc.jpg', quality=90); print('merc', Wd, Hd, 'y', y0, y1)
feats_ = feats('ne_10m_admin_0_countries')
C = {f['properties']['ADM0_A3']: shape(f['geometry']).buffer(0) for f in feats_}
afr = unary_union([shape(f['geometry']).buffer(0) for f in feats_ if f['properties']['CONTINENT'] == 'Africa'])
S = {'AFR': rings(afr.buffer(.15).buffer(-.15), .08, .5)}
for k in ['GRL', 'RUS', 'CAN', 'USA', 'KAZ', 'BRA', 'AUS', 'IND', 'CHN']:
    g = C[k]
    if k == 'RUS': g = g.intersection(box(19, 40, 180, 82))
    S[k] = rings(g, .06, .3)
S['meta'] = {'y0': float(y0), 'y1': float(y1)}
for k in ['GRL', 'RUS', 'CAN', 'USA', 'KAZ', 'BRA', 'AUS', 'IND', 'CHN', 'AFR']:
    g = afr if k == 'AFR' else C[k]
    if k == 'RUS': g = g.intersection(box(19, 40, 180, 82))
    c = g.centroid; S['meta'][k] = [round(c.x, 2), round(c.y, 2)]
S['all'] = []
for k, g in C.items(): S['all'] += rings(g, .08, .3)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
