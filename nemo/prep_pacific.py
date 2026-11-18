"""Pacific Ocean mask (amber glow overlay) from the graded world texture: ocean pixels flood-filled from a seed,
with walls at the conventional borders (Bering, Drake, Tasmania-Antarctica, Sunda islands). Output tex/pacmask.png covers lon 0..360."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
im = Image.open('tex/world.jpg').convert('RGB').resize((2160, 1080), Image.BILINEAR)
a = np.asarray(im).astype(np.float32); a = np.roll(a, 1080, axis=1)          # now lon 0..360
r, g, b = a[..., 0], a[..., 1], a[..., 2]
sea = (b > np.maximum(r, g) + 4) | ((b > 60) & (g > r + 25) & (b > r + 25))
ppd = 6
X = lambda lon: lon * ppd; Y = lambda lat: (90 - lat) * ppd
wall = Image.new('L', (2160, 1080), 0); d = ImageDraw.Draw(wall)
lines = [[(-170 + 360, 66.5), (-165 + 360, 66)], [(-180 + 360, 66.5), (-155 + 360, 66.5)],
         [(-67 + 360, -55), (-67 + 360, -90)], [(147, -43), (147, -90)], [(146.2, -38.2), (146.6, -39.6), (147.6, -42.6)],
         [(98, 16), (98, 8), (95, 5.5), (105, -6.5), (115, -8.8), (125, -10), (132, -10), (142, -10.5)], [(142.5, -10.7), (142, -11)]]
for L in lines: d.line([(X(x), Y(y)) for x, y in L], fill=255, width=7)
sea &= np.asarray(wall) == 0
lab, n = ndimage.label(sea)
k = lab[Y(-40), X(-130 + 360)]
m = (lab == k).astype(np.float32)
m = ndimage.gaussian_filter(m, 1.2)
out = np.zeros((1080, 2160, 4), np.uint8); out[..., 0] = 254; out[..., 1] = 179; out[..., 2] = 0; out[..., 3] = (m * 255).astype(np.uint8)
Image.fromarray(out, 'RGBA').save('tex/pacmask.png'); print('ok', m.mean())
