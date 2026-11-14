"""Satellite terrain texture for the 4-capitals reel -> terrain.jpg (equirectangular, lon 20..112, lat 16..74, 60 px/deg = NE2 native).
Source: Natural Earth II raster NE2_HR_LC_SR_W.tif (naciscdn.org, public domain) in data/ (or NE2 env path).
Graded dark & cinematic (ref IMG_8232); thin white country borders baked in from shapes.json (Kazakhstan incl. Baikonur)."""
import json, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
Image.MAX_IMAGE_PIXELS = None
LON0, LON1, LAT0, LAT1, S = 20, 112, 16, 74, 60
src = Image.open(os.environ.get('NE2', 'data/NE2_HR_LC_SR_W.tif'))
W0, H0 = src.size; ppd = W0 / 360
box = (int((LON0 + 180) * ppd), int((90 - LAT1) * ppd), int((LON1 + 180) * ppd), int((90 - LAT0) * ppd))
img = src.crop(box).convert('RGB').resize(((LON1 - LON0) * S, (LAT1 - LAT0) * S), Image.LANCZOS)
a = np.asarray(img).astype(np.float32) / 255
r, g, b = a[..., 0], a[..., 1], a[..., 2]
water = np.clip((b - r - .04) / .10, 0, 1)[..., None]
lum = a.mean(-1, keepdims=True)
# NE2 land-cover colours are too "atlas green": pull greens toward olive/khaki, desaturate, darken -> satellite look
import colorsys
hsv = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).convert('HSV')).astype(np.float32) / 255
h, s_, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
gr = np.clip((h - .12) / .12, 0, 1)                  # 0 = tan/brown, 1 = green
h2 = h - gr * (h - .17) * .55                        # greens -> olive
s2 = np.clip(s_ * (1.25 - .25 * gr) + .06, 0, 1)
v2 = (v ** 2.3) * (.95 - .2 * gr)
land = np.asarray(Image.fromarray((np.stack([h2, s2, v2], -1) * 255).clip(0, 255).astype(np.uint8), 'HSV').convert('RGB')).astype(np.float32) / 255
land = np.clip(land * np.array([1.08, .96, .82]), 0, 1)
lake = np.array([.08, .55, .56]) * (.6 + .5 * lum)                                  # turquoise lakes
out = land * (1 - water) + lake * water
# fine relief texture so the map stays crisp when the camera is close
rng = np.random.default_rng(1); n = rng.standard_normal(out.shape[:2]).astype(np.float32)
n = np.asarray(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255 - .5
out = np.clip(out * (1 + n[..., None] * .18), 0, 1)
img = Image.fromarray((out * 255).astype(np.uint8))
# borders
sh = json.load(open('shapes.json'))
ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
P = lambda lo, la: ((lo - LON0) * S, (LAT1 - la) * S)
for c in ['RUS', 'CHN', 'MNG', 'UZB', 'KGZ', 'TKM', 'TJK', 'AFG', 'IRN', 'AZE', 'GEO', 'ARM', 'TUR', 'UKR']:
    for ring in sh[c]: d.line([P(*p) for p in ring], fill=(235, 235, 230, 120), width=2, joint='curve')
for ring in sh['KAZ']: d.line([P(*p) for p in ring], fill=(255, 255, 250, 210), width=4, joint='curve')
img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
img.save('terrain.jpg', quality=90); print(img.size)
