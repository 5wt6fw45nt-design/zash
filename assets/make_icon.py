"""Icono de Zash con el estilo de la familia (Tiper, Conie, Bru, Clutch):
degradado diagonal a sangre, símbolo grande en blanco e insignia redonda arriba a la derecha.
Zash: dorado de Zcash, Z blanca e insignia con candado (privacidad).
Uso: python3 make_icon.py [salida.png]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

C1, C2 = (0xF6, 0xB9, 0x2B), (0xD9, 0x6A, 0x0B)   # dorado → ámbar
NAVY = (0x1C, 0x22, 0x3F)
YELLOW = (0xFF, 0xD3, 0x58)
FONT = '/System/Library/Fonts/SFNSRounded.ttf'
S = 4
W = 1024 * S


def gradient():
    g = Image.new('RGB', (256, 256))
    px = g.load()
    for y in range(256):
        for x in range(256):
            t = (x + y) / 510
            px[x, y] = tuple(round(C1[i] + (C2[i] - C1[i]) * t) for i in range(3))
    return g.resize((W, W), Image.BICUBIC)


def font(size, weight=b'Black'):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(weight)
    return f


def badge(d):
    # moneda azul noche con candado amarillo: la privacidad
    cx, cy, r = 0.74 * W, 0.24 * W, 0.10 * W
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY)
    u = r / 100
    d.rounded_rectangle([cx - 36 * u, cy - 4 * u, cx + 36 * u, cy + 46 * u], radius=10 * u, fill=YELLOW)
    d.arc([cx - 25 * u, cy - 50 * u, cx + 25 * u, cy + 8 * u], start=180, end=360, fill=YELLOW, width=int(14 * u))
    for x in (-25, 25):
        d.line([(cx + x * u, cy - 22 * u), (cx + x * u, cy - 2 * u)], fill=YELLOW, width=int(14 * u))


def make(out):
    img = gradient()
    d = ImageDraw.Draw(img)
    d.text((0.47 * W, 0.54 * W), 'Z', font=font(int(640 * S)), fill='white', anchor='mm')
    badge(d)
    img = img.resize((1024, 1024), Image.LANCZOS)
    img.save(out)
    img.resize((512, 512), Image.LANCZOS).save(Path(out).with_name('avatar-zash-512.png'))
    print(out)


if __name__ == '__main__':
    make(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).with_name('avatar-zash.png')))
