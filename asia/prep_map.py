"""Natural Earth II raster (21600x10800, equirectangular, public domain) -> Miller-projected satellite-look maps
map_hi.jpg (40 px/deg) and map_lo.jpg (16 px/deg), lon -30..190 (wraps past 180 for Chukotka), lat -50..85."""
import numpy as np, math
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src = np.asarray(Image.open('data/NE2_HR_LC_SR_W.tif').convert('RGB'))
H0, W0 = src.shape[:2]; ppd = W0 / 360
LON0, LON1, LAT0, LAT1 = -30, 190, -50, 88
my = lambda lat: 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * lat * math.pi / 180)) * 180 / math.pi
Y0, Y1 = my(LAT0), my(LAT1)
print('miller y range', Y0, Y1)
for name, s in [('map_hi.jpg', 40), ('map_lo.jpg', 16)]:
    w, h = int((LON1 - LON0) * s), int((Y1 - Y0) * s)
    xs = ((LON0 + (np.arange(w) + .5) / s + 180) % 360 * ppd).astype(int).clip(0, W0 - 1)
    yv = Y1 - (np.arange(h) + .5) / s
    lat = (np.arctan(np.exp(yv * math.pi / 180 / 1.25)) - math.pi / 4) / 0.4 * 180 / math.pi
    ys = ((90 - lat) * ppd).astype(int).clip(0, H0 - 1)
    out = src[ys][:, xs].astype(np.float32) / 255
    # grade towards a darker 'satellite' look: deeper teal ocean, richer and darker land
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    ocean = np.clip((b - r - .08) / .12, 0, 1)[..., None]
    lum = out.mean(-1, keepdims=True)
    land = (np.clip(lum + (out - lum) * 1.15, 0, 1) ** 1.9) * np.array([1.0, .9, .82])
    deep = np.array([.05, .20, .27]); shallow = np.array([.16, .42, .48])
    sea = deep + (shallow - deep) * np.clip((lum - .45) / .35, 0, 1) ** 1.5
    out = land * (1 - ocean) + sea * ocean
    out = (np.clip(out, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out).save(name, quality=88)
    print(name, w, h)
