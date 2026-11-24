"""Make a Sentinel-2 texture sit on the graded Blue Marble: its dark sea (patchy between scene dates) is replaced by the
smooth teal sea of a reference texture (same lon/lat crop, upsampled) or by a fixed teal; bright shallows and land stay.
Usage: python3 grade_s2.py s2.jpg lon0 lon1 lat0 lat1 [ref.jpg rlon0 rlon1 rlat0 rlat1]"""
import sys, numpy as np
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS = None
f = sys.argv[1]; l0, l1, b0, b1 = map(float, sys.argv[2:6])
im = Image.open(f).convert('RGB'); a = np.asarray(im).astype(np.float32); H, W = a.shape[:2]
if len(sys.argv) > 6:
    R = Image.open(sys.argv[6]).convert('RGB'); r0, r1, s0, s1 = map(float, sys.argv[7:11]); rw, rh = R.size
    box = ((l0 - r0) / (r1 - r0) * rw, (s1 - b1) / (s1 - s0) * rh, (l1 - r0) / (r1 - r0) * rw, (s1 - b0) / (s1 - s0) * rh)
    ref = np.asarray(R.resize((W, H), Image.BICUBIC, box=box).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    # keep only the sea colour of the reference: where the reference is land, use its mean sea colour
    rsea = (ref[..., 2] > ref[..., 0] + 15)
    mean = ref[rsea].mean(0) if rsea.any() else np.array([30, 75, 95], np.float32)
    ref[~rsea] = mean
else:
    ref = np.zeros_like(a) + np.array([34, 80, 100], np.float32)
    # colour transfer on land: match the Sentinel land's mean/spread per channel to the reference land (Blue Marble look)
    Rl = np.asarray(R.resize((W, H), Image.BICUBIC, box=box)).astype(np.float32); land = (Rl[..., 2] <= Rl[..., 0] + 15)
    sl = land & (a.sum(2) > 150)
    for c in range(3):
        ms, ss, mr, sr = a[..., c][sl].mean(), a[..., c][sl].std(), Rl[..., c][land].mean(), Rl[..., c][land].std()
        a[..., c] = (a[..., c] - ms) * (sr / ss * .9 + .1) + mr
lum = a @ np.array([.3, .59, .11], np.float32)
m = np.clip((62 - lum) / 26, 0, 1)
m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)[..., None] / 255
detail = (lum - lum.mean())[..., None] * .25 * m       # a little of the original texture (waves) shows through
o = a * (1 - m) + (ref + detail) * m
Image.fromarray(o.clip(0, 255).astype(np.uint8)).save(f, quality=90); print('graded', f)
