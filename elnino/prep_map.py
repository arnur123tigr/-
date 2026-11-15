"""Natural Earth II raster (21600x10800, equirectangular, public domain) -> Miller-projected satellite-look maps
map_hi.jpg (40 px/deg) and map_lo.jpg (16 px/deg), lon 60E..15W across the Pacific, lat -85..85."""
import numpy as np, math
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src = np.asarray(Image.open('data/NE2_HR_LC_SR_W.tif').convert('RGB'))
H0, W0 = src.shape[:2]; ppd = W0 / 360
LON0, LON1, LAT0, LAT1 = 60, 345, -85, 85
my = lambda lat: 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * lat * math.pi / 180)) * 180 / math.pi
Y0, Y1 = my(LAT0), my(LAT1)
print('miller y range', Y0, Y1)
for name, s in [('map_hi.jpg', 24)]:
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
    land = (np.clip(lum + (out - lum) * 1.05, 0, 1) ** 2.6) * np.array([.88, .95, .74])
    deep = np.array([.05, .20, .27]); shallow = np.array([.16, .42, .48])
    sea = deep + (shallow - deep) * np.clip((lum - .45) / .35, 0, 1) ** 1.5
    out = land * (1 - ocean) + sea * ocean
    out = (np.clip(out, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out).save(name, quality=88)
    print(name, w, h)

# ---- sea-surface-temperature anomaly overlay (sst.png, 6 px/deg, RGBA) on the same grid: hot tongue along the equator, strongest in the east
s = 6; w, h = int((LON1 - LON0) * s), int((Y1 - Y0) * s)
lo = Image.open('map_hi.jpg').resize((w, h), Image.BILINEAR); a = np.asarray(lo).astype(np.float32) / 255
ocean = (np.abs(a - np.array([.05, .20, .27])).sum(-1) < .28) | ((a[..., 2] > a[..., 0] + .06) & (a.mean(-1) < .55))
from PIL import ImageFilter
ocean = np.asarray(Image.fromarray((ocean * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.5))) / 255
lon = LON0 + (np.arange(w) + .5) / s; yv = Y1 - (np.arange(h) + .5) / s
lat = (np.arctan(np.exp(yv * math.pi / 180 / 1.25)) - math.pi / 4) / 0.4 * 180 / math.pi
LON, LAT = np.meshgrid(lon, lat)
rng = np.random.default_rng(5)
def noise(sc):
    n = rng.standard_normal((h // sc + 2, w // sc + 2)).astype(np.float32)
    return np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
nz = .5 * noise(40) + .3 * noise(12) + .25 * noise(4) + .15 * noise(2)
east = np.clip((LON - 160) / 110, 0, 1)
tongue = np.exp(-(LAT / (6 + 6 * (1 - east))) ** 2) * (.2 + 1.0 * east) * (LON < 290)
v = np.clip(.68 + tongue * .6 + nz * .2 - np.abs(LAT) / 140, 0, 1.3)   # 0 cold .. 1+ very hot
stops = [(0, (.15, .45, .95)), (.25, (.3, .85, .9)), (.42, (.95, .97, .85)), (.55, (1, .9, .35)), (.72, (.98, .45, .1)), (.88, (.85, .08, .08)), (1.1, (.45, 0, .05))]
col = np.zeros((h, w, 3), np.float32)
for (x0, c0), (x1, c1) in zip(stops, stops[1:]):
    m = (v >= x0) & (v < x1) if x1 < 1.1 else (v >= x0)
    k = np.clip((v - x0) / (x1 - x0), 0, 1)[..., None]
    col = np.where(m[..., None], np.array(c0) + (np.array(c1) - np.array(c0)) * k, col)
alpha = ocean * np.clip(1 - (np.abs(LAT) - 55) / 10, 0, 1) * .92
Image.fromarray(np.dstack([col * 255, alpha * 255]).clip(0, 255).astype(np.uint8), 'RGBA').save('sst.png')
print('sst', w, h)
