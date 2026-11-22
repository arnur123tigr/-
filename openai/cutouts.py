# background removal (rembg, u2net_human_seg / isnet) -> cut/<name>.png, cropped to content
import sys, os
from rembg import remove, new_session
from PIL import Image
os.makedirs('cut', exist_ok=True)
S = new_session('isnet-general-use')
for n in sys.argv[1:]:
    im = Image.open(f'photos/{n}.jpg').convert('RGB')
    o = remove(im, session=S, alpha_matting=False)
    bb = o.getbbox(); o = o.crop(bb); o.save(f'cut/{n}.png'); print(n, o.size, flush=True)
