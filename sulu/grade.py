"""Regrade the Blue Marble crops in tex/ to the darker cinematic look of the JAS map reels:
a little darker, more relief contrast, warmer, greens pulled toward olive. Usage: python3 grade.py tex/z.jpg tex/z2.jpg"""
import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
for f in sys.argv[1:]:
    a = np.asarray(Image.open(f).convert('RGB')).astype(np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gr = np.clip((g - np.maximum(r, b)) * 4, 0, 1)            # green-dominant pixels -> olive
    a[..., 0] += gr * .05; a[..., 2] -= gr * .03
    m = a.mean()
    a = (a - m) * 1.18 + m                                    # contrast
    a = np.clip(a, 0, 1) ** 1.12 * .86                                      # darker, deeper shadows
    a[..., 0] *= 1.03; a[..., 2] *= .95                        # warm
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(f, quality=90); print('graded', f)
