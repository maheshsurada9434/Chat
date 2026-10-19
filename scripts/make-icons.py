# Generates the PWA icons (run: python3 scripts/make-icons.py)
from PIL import Image, ImageDraw, ImageFilter
import os
S = 1024
def grad(size):
    a, b = (109, 74, 255), (22, 119, 214)
    im = Image.new('RGB', (size, size))
    px = im.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size - 2)
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return im
def draw(full_bleed, scale):
    bg = grad(S).convert('RGBA')
    glow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((S*.05, S*-.25, S*.85, S*.55), fill=(255, 255, 255, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    bg.alpha_composite(glow)
    ov = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c = S / 2
    w, h = S * .56 * scale, S * .44 * scale
    x0, y0 = c - w / 2, c - h / 2 - S * .03 * scale
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=h * .34, fill=(255, 255, 255, 245))
    tail = [(x0 + w * .2, y0 + h - 4), (x0 + w * .12, y0 + h + h * .26), (x0 + w * .42, y0 + h - 4)]
    d.polygon(tail, fill=(255, 255, 255, 245))
    # lock
    lw, lh = w * .26, h * .30
    lx, ly = c - lw / 2, y0 + h * .46
    d.rounded_rectangle((lx, ly, lx + lw, ly + lh), radius=lw * .2, fill=(66, 52, 190, 255))
    r = lw * .30
    d.arc((c - r, ly - r * 1.35, c + r, ly + r * .65), 180, 360, fill=(66, 52, 190, 255), width=int(lw * .13))
    d.ellipse((c - lw*.08, ly + lh*.28, c + lw*.08, ly + lh*.28 + lw*.16), fill=(255, 255, 255, 255))
    bg.alpha_composite(ov)
    if not full_bleed:
        m = Image.new('L', (S, S), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, S, S), radius=int(S * .22), fill=255)
        out = Image.new('RGBA', (S, S), (0, 0, 0, 0)); out.paste(bg, mask=m); return out
    return bg
os.makedirs('icons', exist_ok=True)
std = draw(False, 1.0); mask = draw(True, .78); full = draw(True, 1.0)
std.resize((512, 512), Image.LANCZOS).save('icons/icon-512.png')
std.resize((192, 192), Image.LANCZOS).save('icons/icon-192.png')
mask.resize((512, 512), Image.LANCZOS).save('icons/maskable-512.png')
full.convert('RGB').resize((180, 180), Image.LANCZOS).save('icons/apple-touch-icon.png')
print('ok')
