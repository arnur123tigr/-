"""Text overlays (scene titles, one-word captions, CTA) as an RGBA PNG sequence."""
import json, os, sys, math, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, "timeline.json")))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "build", "ovl")
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
TOTAL = TL["total"]
OFF = TL["vo_offset"]
FB = os.path.join(HERE, "fonts", "Montserrat-Black.ttf")
FE = os.path.join(HERE, "fonts", "Montserrat-ExtraBold.ttf")
GOLD = (255, 196, 60)

# words with corrected spelling, mapped onto whisper timings
raw = json.load(open(os.path.join(HERE, "audio", "vo_a.words.json")))
fix = {"1218.": "1218", "Номестник": "Наместник", "харезма": "Хорезма", "казнить": "казнит",
       "25.": "«25»", "ЕНТ.": "ЕНТ"}
words = []
i = 0
while i < len(raw):
    s, e, w = raw[i]
    if w == "от" and i + 1 < len(raw) and raw[i + 1][2] == "Рара":
        words.append([s, raw[i + 1][1], "Отрара"]); i += 2; continue
    if w == "и" and i + 1 < len(raw) and raw[i + 1][2] == "Нолчук":
        words.append([s, raw[i + 1][1], "Иналчук"]); i += 2; continue
    w = fix.get(w, w)
    words.append([s, e, w.strip(".,!?")])
    i += 1
for w in words:
    w[0] += OFF; w[1] += OFF

titles = {
    "s1": ("POV:", "ты купец Чингисхана"),
    "s2": ("500", "верблюдов"),
    "s3": ("Наместник", "Иналчук"),
    "s4": ("«Вы", "шпионы!»"),
    "s5": ("Спасся", "один"),
    "s6": ("Чингисхан", "узнаёт"),
    "s7": ("Посла", "казнили"),
}

def font(p, s):
    return ImageFont.truetype(p, s)

def shadow_text(img, xy, text, fnt, fill, anchor="mm", stroke=0, shadow=10, alpha=1.0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((xy[0], xy[1] + 6), text, font=fnt, fill=(0, 0, 0, int(170 * alpha)), anchor=anchor,
           stroke_width=stroke + 4, stroke_fill=(0, 0, 0, int(170 * alpha)))
    lay = lay.filter(ImageFilter.GaussianBlur(shadow))
    d = ImageDraw.Draw(lay)
    d.text(xy, text, font=fnt, fill=fill[:3] + (int(255 * alpha),), anchor=anchor,
           stroke_width=stroke, stroke_fill=(20, 12, 6, int(255 * alpha)))
    img.alpha_composite(lay)

_fc = {}
def fit(text, size, maxw=940, path=None):
    path = path or FB
    k = (text, size)
    if k in _fc:
        return _fc[k]
    while size > 20:
        f = ImageFont.truetype(path, size)
        if f.getlength(text) <= maxw:
            break
        size -= 2
    _fc[k] = f
    return f

def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

f_title1 = font(FB, 64)
f_title2 = font(FB, 78)
f_cap = font(FB, 96)
f_cta = font(FB, 70)
f_cta2 = font(FE, 44)

def title_layer(img, t):
    for name, (a, b) in titles.items():
        s, e = TL["shots"][name]
        if not (s <= t < e):
            continue
        k = ease((t - s - 0.05) / 0.35)
        out = min(1.0, (e - t) / 0.15)
        al = k * out
        dy = (1 - k) * 30
        y0 = 300
        txt1 = a.upper()
        txt2 = b.upper()
        shadow_text(img, (W // 2, y0 + dy), txt1, fit(txt1, 64), GOLD, stroke=0, alpha=al)
        shadow_text(img, (W // 2, y0 + 92 + dy), txt2, fit(txt2, 78), (255, 255, 255), alpha=al)

def caption_layer(img, t):
    cur = None
    for s, e, w in words:
        if s - 0.02 <= t < max(e, s + 0.22) + 0.05:
            cur = (s, w)
    if cur is None:
        return
    s, w = cur
    k = ease((t - s) / 0.10)
    sc = 0.85 + 0.15 * k
    fnt = fit(w, int(96 * sc), 980)
    shadow_text(img, (W // 2, 1230), w, fnt, (255, 255, 255), stroke=7, shadow=8, alpha=min(1, k * 1.5))

def cta_layer(img, t):
    s = 27.4 + OFF
    if t < s:
        return
    k = ease((t - s) / 0.4)
    # green comment bubble
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bw, bh = 820, 230
    x0, y0 = (W - bw) // 2, int(380 + (1 - k) * 40)
    d.rounded_rectangle((x0 + 6, y0 + 10, x0 + bw + 6, y0 + bh + 10), 46, fill=(0, 0, 0, int(110 * k)))
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 46, fill=(37, 184, 92, int(245 * k)))
    d.polygon([(x0 + 120, y0 + bh - 2), (x0 + 200, y0 + bh - 2), (x0 + 110, y0 + bh + 60)],
              fill=(37, 184, 92, int(245 * k)))
    d.text((W // 2, y0 + 78), "ПИШИ «25»", font=f_cta, fill=(255, 255, 255, int(255 * k)), anchor="mm")
    d.text((W // 2, y0 + 160), "получи гайд по истории к ЕНТ", font=f_cta2,
           fill=(255, 255, 255, int(255 * k)), anchor="mm")
    img.alpha_composite(lay)

n = int(round(TOTAL * FPS))
only = None
if len(sys.argv) > 2:
    only = [int(x) for x in sys.argv[2].split(",")]
for fr in range(n):
    if only and fr not in only:
        continue
    t = fr / FPS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    title_layer(img, t)
    cta_layer(img, t)
    caption_layer(img, t)
    img.save(os.path.join(OUT, f"o_{fr:04d}.png"), compress_level=1)
print("frames", n)
