"""Reel de Zash (1080x1920, 30 fps, 25 s) con la música de los reels de la familia (reel/musica.wav).
Tono: el gran predicador de la privacidad. Solemne, contundente, con mandamientos. Sin imaginería religiosa.
Uso: python3 make_reel.py  → reel/zash-reel.mp4 + reel/portada.png
Los datos del móvil (precio, % blindado) son de la consulta real del 14/10/2026.
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).parent
OUT = HERE / 'reel'
ICON = HERE.parent / 'assets' / 'avatar-zash.png'
QR = OUT / 'qr.png'

W, H, FPS = 1080, 1920, 30
ROUNDED = '/System/Library/Fonts/SFNSRounded.ttf'
SANS = '/System/Library/Fonts/SFNS.ttf'
GOLD, AMBER = (0xF6, 0xB9, 0x2B), (0xD9, 0x6A, 0x0B)
DARK = (0x0B, 0x0C, 0x10)
GREY = (0x8A, 0x8D, 0x96)
LIGHT = (0xC9, 0xCB, 0xD1)
RED = (0xE5, 0x3E, 0x3E)
NAVY = (0x1C, 0x22, 0x3F)
WHITE = (255, 255, 255)

_fonts = {}


def font(size, weight='Black', path=ROUNDED):
    key = (path, size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(path, size)
        try:
            f.set_variation_by_name(weight.encode())
        except Exception:
            pass
        _fonts[key] = f
    return _fonts[key]


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def gradient(w, h, c1=GOLD, c2=AMBER):
    g = Image.new('RGB', (64, 64))
    px = g.load()
    for y in range(64):
        for x in range(64):
            t = x / 63 * 0.4 + y / 63 * 0.6
            px[x, y] = tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return g.resize((w, h), Image.BICUBIC)


GRAD = gradient(W, H)


def wrap(text, f, max_w):
    words, lines, cur = text.split(), [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if f.getlength(test) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def headline(img, text, y, size=104, fill=WHITE, alpha=1.0, dy=0, max_w=920, weight='Black'):
    if alpha <= 0:
        return y
    f = font(size, weight)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lh = int(size * 1.1)
    lines = wrap(text, f, max_w)
    for i, line in enumerate(lines):
        d.text((W / 2, y + dy + i * lh), line, font=f, fill=fill + (int(255 * alpha),), anchor='mt')
    img.alpha_composite(layer)
    return y + len(lines) * lh


def fade_in(t, start, dur=0.45):
    return ease((t - start) / dur)


# ---------------------------------------------------------------- 1. la llamada

def scene_call(t):
    img = Image.new('RGBA', (W, H), DARK + (255,))
    # halo dorado que crece despacio detrás de la palabra
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    r = 260 + 90 * ease(t / 3)
    ImageDraw.Draw(glow).ellipse([W / 2 - r, 760 - r, W / 2 + r, 760 + r], fill=GOLD + (int(70 * ease(t / 1.2)),))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    k = fade_in(t, 0.1, 0.6)
    s = 1.25 - 0.25 * k
    headline(img, 'Escuchad.', 690 - 40 * (s - 1), int(190 * s), fill=GOLD, alpha=k)
    headline(img, 'Tu dinero habla de ti.', 1180, 84, fill=LIGHT, alpha=fade_in(t, 1.5), dy=(1 - fade_in(t, 1.5)) * 30)
    return img


# ---------------------------------------------------------------- 2. bitcoin: todo a la vista

LEDGER = [
    ('bc1qx…9ab', 'bc1qk…22c', '2,4 BTC'),
    ('bc1qm…4ld', 'bc1qr…7fe', '0,35 BTC'),
    ('bc1qv…8np', 'bc1qx…9ab', '1,1 BTC'),
    ('bc1qs…0tq', 'bc1qh…3hk', '0,08 BTC'),
]


def ledger(img, y0, t, hidden=False, alpha=1.0):
    d = ImageDraw.Draw(img)
    f = font(42, 'Bold', SANS)
    for i, (a, b, amt) in enumerate(LEDGER):
        k = fade_in(t, 0.3 + i * 0.25, 0.3) * alpha
        if k <= 0:
            continue
        y = y0 + i * 130
        d.rounded_rectangle([90, y, W - 90, y + 104], 26, fill=(0x1B, 0x1D, 0x26, int(235 * k)))
        if hidden:
            for x0, x1 in ((130, 400), (470, 740), (800, 950)):
                d.rounded_rectangle([x0, y + 34, x1, y + 70], 12, fill=(0x3A, 0x3E, 0x4C, int(255 * k)))
        else:
            col = WHITE + (int(255 * k),)
            d.text((130, y + 52), a, font=f, fill=col, anchor='lm')
            d.text((430, y + 52), '→', font=f, fill=GREY + (int(255 * k),), anchor='lm')
            d.text((490, y + 52), b, font=f, fill=col, anchor='lm')
            d.text((W - 130, y + 52), amt, font=f, fill=GOLD + (int(255 * k),), anchor='rm')


def scene_exposed(t):
    img = Image.new('RGBA', (W, H), DARK + (255,))
    headline(img, 'En Bitcoin, todo el mundo lo ve:', 250, 76, alpha=fade_in(t, 0))
    headline(img, 'quién paga, a quién y cuánto.', 420, 64, fill=LIGHT, alpha=fade_in(t, 0.4))
    ledger(img, 720, t)
    if t > 2.1:
        k = ease((t - 2.1) / 0.25)
        s = 1.3 - 0.3 * k
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        f = font(int(170 * s), 'Black')
        d.text((W / 2, 1460), 'EXPUESTO', font=f, fill=RED + (int(255 * k),), anchor='mm')
        img.alpha_composite(layer.rotate(-8, center=(W / 2, 1460)))
    return img


# ---------------------------------------------------------------- 3. zcash: blindado

def scene_shielded(t):
    img = GRAD.copy().convert('RGBA')
    headline(img, 'En Zcash, nadie.', 250, 104, alpha=fade_in(t, 0))
    headline(img, 'Ni quién, ni a quién, ni cuánto.', 420, 62, fill=NAVY, alpha=fade_in(t, 0.4))
    dark = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ledger(dark, 720, t, hidden=True)
    img.alpha_composite(dark)
    if t > 2.0:
        k = ease((t - 2.0) / 0.3)
        headline(img, 'BLINDADO', 1400, int(150 * (1.2 - 0.2 * k)), fill=WHITE, alpha=k)
    return img


# ---------------------------------------------------------------- 4. Zash en el móvil

PHONE_W, PHONE_H = 760, 1180
CHAT_BG = (0x0F, 0x16, 0x1F)
BOT_BUBBLE = (0x1F, 0x2C, 0x3A)
ME_BUBBLE = (0x2B, 0x52, 0x78)


def bubble_img(text, mine, max_w=640):
    reg, bold = font(32, 'Regular', SANS), font(32, 'Bold', SANS)
    lines = []
    for i, raw in enumerate(text.split('\n')):
        f = bold if (i == 0 and not mine) else reg
        if not raw:
            lines.append(('', reg))
            continue
        for ln in wrap(raw, f, max_w - 50):
            lines.append((ln, f))
    lh = 42
    w = int(max(f.getlength(tx) for tx, f in lines)) + 50
    h = len(lines) * lh + 34
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=(ME_BUBBLE if mine else BOT_BUBBLE) + (255,))
    for i, (tx, f) in enumerate(lines):
        d.text((25, 17 + i * lh), tx, font=f, fill=WHITE)
    return im


MESSAGES = [
    (0.4, bubble_img('¿qué es zcash?', True)),
    (0.9, bubble_img('1. ¿Qué es Zcash?\nDinero digital, como bitcoin: nadie lo controla y como máximo habrá 21 millones.\nLa diferencia: puedes elegir que tus pagos sean privados.', False)),
    (3.0, bubble_img('precio', True)),
    (3.5, bubble_img('Zcash (ZEC)\n1.042 euros · 1.158 dólares\n29,2 % de los ZEC ya están blindados', False)),
]


def phone(t):
    ph = Image.new('RGBA', (PHONE_W, PHONE_H), (0, 0, 0, 0))
    ImageDraw.Draw(ph).rounded_rectangle([0, 0, PHONE_W - 1, PHONE_H - 1], 80, fill=(0x05, 0x05, 0x07, 255))
    sx0, sy0, sx1, sy1 = 22, 22, PHONE_W - 22, PHONE_H - 22
    screen = Image.new('RGBA', (sx1 - sx0, sy1 - sy0), CHAT_BG + (255,))
    shown = [(ts, b) for ts, b in MESSAGES if t >= ts]
    y = screen.height - 40
    for ts, b in reversed(shown):
        k = ease((t - ts) / 0.3)
        y -= b.height
        mine = b.getpixel((10, b.height // 2))[:3] == ME_BUBBLE
        x = screen.width - b.width - 30 if mine else 30
        lay = Image.new('RGBA', screen.size, (0, 0, 0, 0))
        lay.paste(b, (x, int(y + (1 - k) * 40)))
        if k < 1:
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * k)))
        screen.alpha_composite(lay)
        y -= 22
    sd = ImageDraw.Draw(screen)
    sd.rectangle([0, 0, screen.width, 150], fill=(0x17, 0x21, 0x2B, 255))
    icon = Image.open(ICON).convert('RGBA').resize((84, 84), Image.LANCZOS)
    m = Image.new('L', (84, 84), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 83, 83], fill=255)
    screen.paste(icon, (40, 50), m)
    sd.text((142, 60), 'Zash · Zcash en español', font=font(32, 'Bold', SANS), fill=WHITE)
    sd.text((142, 102), 'bot', font=font(26, 'Regular', SANS), fill=GREY)
    mask = Image.new('L', screen.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, screen.width - 1, screen.height - 1], 60, fill=255)
    ph.paste(screen, (sx0, sy0), mask)
    return ph


def scene_zash(t):
    img = GRAD.copy().convert('RGBA')
    y = headline(img, 'Zash te lo enseña desde cero.', 120, 74, alpha=fade_in(t, 0))
    headline(img, 'En español. Gratis.', y + 10, 70, fill=NAVY, alpha=fade_in(t, 2.6))
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([170, 560, 170 + PHONE_W, 560 + PHONE_H], 80, fill=(60, 30, 0, 110))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(30)))
    rise = (1 - ease(t / 0.5)) * 200
    img.alpha_composite(phone(t), ((W - PHONE_W) // 2, int(470 + rise)))
    headline(img, 'Datos reales del 14/10/2026.', 1800, 28, alpha=0.8 * fade_in(t, 0.6), weight='Semibold')
    return img


# ---------------------------------------------------------------- 5. los mandamientos

COMMANDMENTS = [
    ('I', 'Tu frase secreta no se comparte. Jamás.'),
    ('II', 'Lo que recibas, blíndalo.'),
    ('III', 'Aprende antes de mover un céntimo.'),
]


def scene_law(t):
    img = Image.new('RGBA', (W, H), DARK + (255,))
    y = headline(img, 'LOS TRES MANDAMIENTOS', 240, 66, fill=GOLD, alpha=fade_in(t, 0), max_w=980)
    headline(img, 'de la privacidad', y + 12, 54, fill=LIGHT, alpha=fade_in(t, 0.2))
    d = ImageDraw.Draw(img)
    for i, (num, text) in enumerate(COMMANDMENTS):
        k = fade_in(t, 0.7 + i * 1.0, 0.4)
        if k <= 0:
            continue
        y = 640 + i * 330
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((150, y + 10 + (1 - k) * 30), num, font=font(120, 'Black'), fill=GOLD + (int(255 * k),), anchor='lt')
        f = font(60, 'Heavy')
        for j, line in enumerate(wrap(text, f, 620)):
            ld.text((350, y + 20 + j * 70 + (1 - k) * 30), line, font=f, fill=WHITE + (int(255 * k),), anchor='lt')
        img.alpha_composite(layer)
    return img


# ---------------------------------------------------------------- 6. cierre

def end_card(t=9.0):
    img = GRAD.copy().convert('RGBA')
    k = ease(t / 0.5)
    icon = Image.open(ICON).convert('RGBA').resize((300, 300), Image.LANCZOS)
    m = Image.new('L', (300, 300), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 299, 299], fill=255)
    ring = Image.new('RGBA', (330, 330), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, 329, 329], fill=WHITE + (255,))
    ring.paste(icon, (15, 15), m)
    img.alpha_composite(ring, ((W - 330) // 2, int(200 + (1 - k) * 60)))
    headline(img, 'Zash', 560, 150, alpha=k)
    headline(img, 'Zcash desde cero · gratis', 730, 62, fill=NAVY, alpha=fade_in(t, 0.2, 0.4))
    k2 = fade_in(t, 0.5, 0.5)
    card = Image.new('RGBA', (720, 760), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, 719, 759], 50, fill=WHITE + (255,))
    qr = Image.open(QR).convert('RGBA').resize((440, 440), Image.NEAREST)
    card.alpha_composite(qr, (140, 50))
    cd.text((360, 540), '@ZashCash_bot', font=font(52, 'Heavy'), fill=DARK, anchor='mm')
    cd.text((360, 615), 'Búscalo en Telegram', font=font(38, 'Semibold'), fill=GREY, anchor='mm')
    cd.text((360, 680), 'Precio · curso · privacidad · alertas', font=font(32, 'Heavy'), fill=AMBER, anchor='mm')
    if k2 > 0:
        card.putalpha(card.getchannel('A').point(lambda v: int(v * k2)))
        img.alpha_composite(card, ((W - 720) // 2, int(870 + (1 - k2) * 80)))
    headline(img, 'Información y formación, no consejo de inversión.', 1690, 30, alpha=fade_in(t, 0.8), weight='Semibold')
    return img


SCENES = [(scene_call, 3.3), (scene_exposed, 3.4), (scene_shielded, 3.2), (scene_zash, 6.2), (scene_law, 4.0), (end_card, 4.9)]
XFADE = 6


def frames():
    prev_last = None
    for fn, dur in SCENES:
        n = int(dur * FPS)
        for i in range(n):
            fr = fn(i / FPS).convert('RGB')
            if prev_last is not None and i < XFADE:
                fr = Image.blend(prev_last, fr, (i + 1) / (XFADE + 1))
            yield fr
        prev_last = fn((n - 1) / FPS).convert('RGB')


def main():
    OUT.mkdir(exist_ok=True)
    mp4 = OUT / 'zash-reel.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', str(OUT / 'musica.wav'), '-shortest',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(mp4)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames():
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    p.wait()
    end_card().convert('RGB').save(OUT / 'portada.png')
    print(mp4)


if __name__ == '__main__':
    main()
