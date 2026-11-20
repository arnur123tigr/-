"""Mapzen/AWS Terrarium tiles (zoom 6, in /home/user/data/terr) -> tex/shelf_<d>.png: sea floor shallower than d m
(d = 20..120) as dry olive land with alpha, for the ice-age sea-level drop. Region lon 94..132, lat -12..8, 45 px/deg."""
import numpy as np, math
from PIL import Image
Z, L0, L1, B0, B1, PPD = 6, 94, 132, -12, 8, 45
def tile_xy(lon, lat):
    n = 2 ** Z; x = (lon + 180) / 360 * n; y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n; return x, y
W, H = (L1 - L0) * PPD, (B1 - B0) * PPD
lons = L0 + (np.arange(W) + .5) / PPD; lats = B1 - (np.arange(H) + .5) / PPD
X = (lons + 180) / 360 * 2 ** Z; Y = (1 - np.arcsinh(np.tan(np.radians(lats))) / np.pi) / 2 * 2 ** Z
cache = {}
def tile(x, y):
    if (x, y) not in cache:
        a = np.asarray(Image.open(f'/home/user/data/terr/{Z}_{x}_{y}.png').convert('RGB')).astype(np.float32)
        cache[(x, y)] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    return cache[(x, y)]
E = np.zeros((H, W), np.float32)
for j in range(H):
    ty = int(Y[j]); py = min(255, int((Y[j] - ty) * 256))
    for i in range(W):
        tx = int(X[i]); E[j, i] = tile(tx, ty)[py, min(255, int((X[i] - tx) * 256))]
np.save('/home/user/data/elev.npy', E)
rng = np.random.default_rng(1); nz = rng.normal(0, 1, (H, W)).astype(np.float32)
from PIL import ImageFilter
nzi = Image.fromarray(((nz * 30) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)); nz = (np.asarray(nzi).astype(np.float32) - 128) / 30
for d in range(20, 121, 20):
    m = ((E < -1) & (E > -d)).astype(np.float32)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    depth = np.clip(-E / 120, 0, 1)
    base = np.stack([112 - 30 * depth + 10 * nz, 118 - 34 * depth + 8 * nz, 62 - 12 * depth + 5 * nz], -1)  # olive lowland, darker where deeper
    o = np.dstack([base.clip(0, 255), m[..., None] * 235]).astype(np.uint8)
    Image.fromarray(o, 'RGBA').save(f'tex/shelf_{d}.png', optimize=True); print('shelf', d, m.mean().round(3))
