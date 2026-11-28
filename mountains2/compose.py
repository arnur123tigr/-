"""Plates -> mountains remake: Higgsfield clip (clip.mp4, 720p) upscaled to 1080x1920 + RU labels + JAS logo.
Usage: python3 compose.py clip.mp4 out_silent.mp4"""
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30
src, out = sys.argv[1], sys.argv[2]
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
N = int(dur * FPS)
F = lambda s, w='Black': ImageFont.truetype(f'fonts/Montserrat-{w}.ttf', s)
logo = Image.open('brand/logo_white_transparent.png').convert('RGBA'); lh = 122; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
la = logo.split()[3].point(lambda v: int(v * .9)); logo.putalpha(la)
def label(text, size=58, col=(255, 255, 255), bg=(19, 11, 84, 215), line=(254, 179, 0, 160)):
    f = F(size, 'ExtraBold'); w = int(f.getlength(text)) + size; h = int(size * 1.75)
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 24, 20 + w, 24 + h), h * .32, fill=(0, 0, 0, 140)); im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, 20 + w, 20 + h), h * .32, fill=bg, outline=line, width=3)
    d.text((20 + w / 2, 20 + h / 2 + 2), text, font=f, fill=col, anchor='mm'); return im
L = [  # text, centre x, centre y, t_in, t_out
    (label('Плита А'), 270, 760, .3, 4.2), (label('Плита Б'), 810, 760, .6, 4.2),
    (label('Литосфера', 50), 540, 1330, 1.0, 5.0), (label('Магма', 50, bg=(232, 80, 47, 220), line=(255, 255, 255, 180)), 540, 1700, 1.4, 6.0),
    (label('Плиты сталкиваются', 54, col=(254, 179, 0)), 540, 330, 3.2, 6.6), (label('и рождаются горы', 62, col=(254, 179, 0)), 540, 330, 6.8, dur - .2),
]
def alpha(t, a, b, f=.35): return max(0, min(1, (t - a) / f, (b - t) / f))
dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-vf', f'scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', out], stdin=subprocess.PIPE)
i = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    t = i / FPS; fr = Image.frombuffer('RGB', (W, H), buf).convert('RGBA')
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(0, 300, 6): gd.rectangle((0, y, W, y + 6), fill=(0, 0, 0, int(110 * (1 - y / 300))))
    fr = Image.alpha_composite(fr, g)
    for im, x, y, a, b in L:
        k = alpha(t, a, b)
        if k <= 0: continue
        s = im.copy(); s.putalpha(s.split()[3].point(lambda v: int(v * k))); dy = int((1 - k) * 25)
        fr.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2 + dy)))
    fr.alpha_composite(logo, (W - 48 - logo.width, 48))
    enc.stdin.write(fr.convert('RGB').tobytes()); i += 1
enc.stdin.close(); enc.wait(); print('frames', i, 'dur', dur)
