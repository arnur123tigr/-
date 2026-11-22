# procedural grounds for the collage: wood table, cork board, paper, grain tiles -> tex/*.jpg|png
import numpy as np
from PIL import Image, ImageFilter
rng = np.random.default_rng(7)
def noise(h, w, s):
    n = rng.standard_normal((h // s + 2, w // s + 2)); im = Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8))
    return np.asarray(im.resize((w, h), Image.BICUBIC)).astype(float) / 255
H, W = 1920, 1080
# wood: planks with grain
y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
g = noise(H, W, 6) * .5 + noise(H, W, 40) * .5
ring = np.sin((x * .9 + g * 60 + noise(H, W, 120) * 120) * .09) * .5 + .5
plank = ((x // 270) % 2) * .06
v = .55 + .25 * ring * .6 + .15 * noise(H, W, 3) - plank
col = np.stack([v * 120, v * 72, v * 40], -1)
col[:, ::270] *= .45
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save('tex/wood.jpg', quality=88)
# cork
c = noise(H, W, 2) * .5 + noise(H, W, 5) * .3 + noise(H, W, 30) * .2
col = np.stack([150 + c * 70, 105 + c * 55, 60 + c * 40], -1) * (.85 + .3 * (rng.random((H, W, 1)) > .97))
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save('tex/cork.jpg', quality=88)
# paper (off-white with fibres)
p = noise(H, W, 2) * .4 + noise(H, W, 60) * .6
col = np.stack([238 + p * 14, 232 + p * 14, 220 + p * 12], -1)
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6)).save('tex/paper.jpg', quality=90)
# grain tiles (gray noise, used with overlay alpha)
for i in range(4):
    n = rng.normal(128, 40, (480, 270)).clip(0, 255).astype(np.uint8)
    Image.fromarray(n).resize((540, 960), Image.NEAREST).save(f'tex/grain{i}.png')
print('ok')
