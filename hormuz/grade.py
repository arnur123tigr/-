"""Regrade Blue Marble textures: deep saturated blue ocean -> teal like the reference reels; land slightly brighter/warmer."""
import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
for f in sys.argv[1:]:
    a = np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.clip((b - np.maximum(r, g) - 8) / 30, 0, 1)[..., None]
    t = np.clip((b - 35) / 140, 0, 1)[..., None] ** 0.9
    deep = np.array([24, 58, 78], np.float32); shal = np.array([78, 150, 158], np.float32)
    sea = deep + (shal - deep) * t
    land = np.clip(a * 1.12 + np.array([6, 4, 0]), 0, 255)
    o = land * (1 - m) + sea * m
    Image.fromarray(o.clip(0, 255).astype(np.uint8)).save(f, quality=90); print('graded', f)
