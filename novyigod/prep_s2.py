"""Sentinel-2 L2A true-colour (TCI) mosaic for a lon/lat box, warped to equirectangular at ppd px/deg.
Data: Copernicus Sentinel-2 (free, incl. commercial use) via the Element84 Earth Search STAC (AWS open data).
Usage: python3 prep_s2.py out.jpg lon0 lon1 lat0 lat1 ppd [dates]"""
import sys, json, urllib.request, numpy as np, rasterio, os
from rasterio.warp import reproject, transform_bounds
from rasterio.transform import from_origin
from rasterio.windows import Window
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
from PIL import Image
os.environ.setdefault('CURL_CA_BUNDLE', '/root/.ccr/ca-bundle.crt'); os.environ['GDAL_DISABLE_READDIR_ON_OPEN'] = 'EMPTY_DIR'; os.environ['AWS_NO_SIGN_REQUEST'] = 'YES'
out, l0, l1, b0, b1, ppd = sys.argv[1], *map(float, sys.argv[2:7]); dates = sys.argv[7] if len(sys.argv) > 7 else '2023-04-01T00:00:00Z/2024-10-31T00:00:00Z'
q = {"collections": ["sentinel-2-l2a"], "bbox": [l0, b0, l1, b1], "query": {"eo:cloud_cover": {"lt": 2}}, "datetime": dates, "limit": 100}
r = urllib.request.Request("https://earth-search.aws.element84.com/v1/search", json.dumps(q).encode(), {"Content-Type": "application/json"})
F = []
for _ in range(8):   # follow the pages: one page can be filled by a single tile's many scenes
    d = json.load(urllib.request.urlopen(r)); F += d['features']
    nx = [l for l in d.get('links', []) if l.get('rel') == 'next']
    if not nx: break
    r = urllib.request.Request(nx[0]['href'], json.dumps(nx[0].get('body', {})).encode() if nx[0].get('body') else None, {"Content-Type": "application/json"}, method=nx[0].get('method', 'GET'))
# candidates: full scenes first (little no-data), then least cloud; each one only fills pixels still empty
C = sorted(F, key=lambda f: (f['properties'].get('s2:nodata_pixel_percentage', 0) > 2, f['properties']['eo:cloud_cover']))
W, H = int((l1 - l0) * ppd), int((b1 - b0) * ppd); im = np.zeros((H, W, 3), np.uint8); filled = np.zeros((H, W), bool); seen = set()
for f in C:
    k = f['properties'].get('grid:code') or f['id'].split('_')[1]
    if filled.all(): break
    if (k, f['properties'].get('s2:nodata_pixel_percentage', 0) > 2) in seen and f['properties'].get('s2:nodata_pixel_percentage', 0) <= 2: continue
    url = f['assets']['visual']['href']; print(k, f['id'], f['properties']['eo:cloud_cover'], flush=True)
    mpp = 111320 / ppd * np.cos(np.radians((b0 + b1) / 2))          # target metres per pixel
    ov = max(-1, min(4, int(np.floor(np.log2(max(mpp / 10, 1)))) - 1))   # overview level (-1 = full 10 m)
    with rasterio.open(url, **({'overview_level': ov} if ov >= 0 else {})) as src:
        sb = transform_bounds('EPSG:4326', src.crs, l0, b0, l1, b1, densify_pts=21)
        win = from_bounds(*sb, src.transform).round_offsets().round_lengths()
        win = win.intersection(Window(0, 0, src.width, src.height))
        s = src.read(window=win); st = src.window_transform(win); crs = src.crs
    d = np.zeros((3, H, W), np.uint8)
    reproject(s, d, src_transform=st, src_crs=crs, dst_transform=from_origin(l0, b1, 1 / ppd, 1 / ppd), dst_crs='EPSG:4326', resampling=Resampling.average if mpp > 12 else Resampling.cubic, src_nodata=0, dst_nodata=0)
    a = d.transpose(1, 2, 0); m = (a.astype(int).sum(2) > 0) & ~filled
    if not m.any(): continue
    im[m] = a[m]; filled |= m; seen.add((k, f['properties'].get('s2:nodata_pixel_percentage', 0) > 2))
print('empty px', int((~filled).sum())); Image.fromarray(im).save(out, quality=90); print('saved', out, im.shape)
