"""Satellite map texture for scenes 2 and 4 -> tex/sat.jpg (lon 42..90 E, lat 36..60 N, linear lon/lat = the plane in scene.html).
Source: NASA Blue Marble Next Generation topo+bathy July, tile C1 (public domain), 21600 px, in ../../data/C1.jpg
(https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july/world.topo.bathy.200407.3x21600x21600.C1.jpg).
Graded like the geography reels: a little darker and warmer, greens to olive, teal water; outside Kazakhstan darker so the country reads.
Kazakhstan (with the Baikonur lease filled) comes from geo.json source data/adm0.geojson.
Usage: python3 prep_tex.py"""
import json, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape
from shapely.ops import unary_union
Image.MAX_IMAGE_PIXELS = None
L0, L1, B0, B1, PPD = 42, 90, 36, 60, 60
T = Image.open('../../data/C1.jpg'); s = 240
im = T.crop((L0 * s, (90 - B1) * s, L1 * s, (90 - B0) * s)).resize(((L1 - L0) * PPD, (B1 - B0) * PPD), Image.LANCZOS)
a = np.asarray(im).astype(np.float32); r, g, b = a[..., 0], a[..., 1], a[..., 2]
water = np.clip((b - np.maximum(r, g) - 6) / 30, 0, 1)[..., None]
t = np.clip((b - 35) / 140, 0, 1)[..., None] ** .9
sea = np.array([18, 44, 62], np.float32) + (np.array([60, 128, 138], np.float32) - [18, 44, 62]) * t
lum = a.mean(-1, keepdims=True)
land = lum + (a - lum) * .85                                   # a little less saturated
land = land * np.array([1.04, .98, .86]) * .78                 # warmer, darker
green = np.clip((g - r) / 25, 0, 1)[..., None]; land = land * (1 - green * .25) + green * .25 * land * np.array([1.08, 1.0, .7])
o = land * (1 - water) + sea * water
# Kazakhstan mask: outside darker
F = {f['properties']['ADMIN']: shape(f['geometry']) for f in json.load(open('data/adm0.geojson'))['features']}
kz = unary_union([F['Kazakhstan'], F['Baykonur Cosmodrome']])
mk = Image.new('L', (o.shape[1], o.shape[0]), 0); d = ImageDraw.Draw(mk)
for p in getattr(kz, 'geoms', [kz]):
    d.polygon([((x - L0) * PPD, (B1 - y) * PPD) for x, y in p.exterior.coords], fill=255)
m = np.asarray(mk.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)[..., None] / 255
o = o * (.55 + .45 * m) * np.array([1, 1, 1.04])
yy, xx = np.mgrid[0:o.shape[0], 0:o.shape[1]]; e = np.minimum.reduce([xx, yy, o.shape[1] - 1 - xx, o.shape[0] - 1 - yy]) / (6 * PPD)
o = o * np.clip(e, 0, 1)[..., None] ** 1.5      # edges fade to black
Image.fromarray(o.clip(0, 255).astype(np.uint8)).save('tex/sat.jpg', quality=88)
print('tex/sat.jpg', o.shape)
