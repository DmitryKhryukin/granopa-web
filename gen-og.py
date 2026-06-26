#!/usr/bin/env python3
"""Генерирует OG-карточку assets/og.jpg — превью ссылки в Телеграме/соцсетях.

Текст превью «вшит» в саму картинку (не в мета-теги!). Чтобы поменять —
правишь константы ниже и запускаешь:

    python3 gen-og.py        # → assets/og.jpg
    ./deploy.sh              # залить
    # затем: сбросить кэш CDN (картинки кэшируются неделю!) и обновить
    #        кэш Телеграма — отправить https://granopa.ru боту @WebpageBot

Шрифты — пути macOS; на другой ОС поправь FONTS_DIR.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).parent
PORTRAIT = HERE / "assets" / "hero.jpg"   # фото справа на карточке
OUTPUT   = HERE / "assets" / "og.jpg"

# ── ЧТО НАПИСАНО НА КАРТОЧКЕ (правь здесь) ──────────────────────────────
EYEBROW = "ПСИХОЛОГ · ПСИХОАНАЛИТИЧЕСКИЙ ПОДХОД"
NAME    = ["Таисия", "Галицкая"]          # по строкам
TAGLINE = ["Бережно всматриваемся в то,",  # курсивная подпись, по строкам
           "что беспокоит, — в вашем темпе."]
# ────────────────────────────────────────────────────────────────────────

# Палитра сайта
PAPER=(245,239,230); INK=(44,40,35); INK_SOFT=(93,84,74); CLAY=(154,93,55); LINE=(221,208,189)
W, H, PANEL = 1200, 630, 470   # размер карточки + ширина фото-панели справа

FONTS_DIR = "/System/Library/Fonts/Supplemental"
def georgia(s):   return ImageFont.truetype(f"{FONTS_DIR}/Georgia.ttf", s)
def georgia_i(s): return ImageFont.truetype(f"{FONTS_DIR}/Georgia Italic.ttf", s)
def arial(s):     return ImageFont.truetype(f"{FONTS_DIR}/Arial.ttf", s)

def cover_crop(img, w, h):
    """Кадрирует под соотношение w:h (как object-fit: cover)."""
    iw, ih = img.size; target = w / h
    if iw / ih > target:
        nw = int(ih * target); x = (iw - nw) // 2; return img.crop((x, 0, x + nw, ih))
    nh = int(iw / target); y = (ih - nh) // 2; return img.crop((0, y, iw, y + nh))

def draw_tracked(draw, pos, text, font, fill, track):
    """Текст с межбуквенным интервалом (для надзаголовка)."""
    cx, cy = pos
    for ch in text:
        draw.text((cx, cy), ch, font=font, fill=fill)
        cx += draw.textlength(ch, font=font) + track

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# Фото справа
port = ImageOps.exif_transpose(Image.open(PORTRAIT)).convert("RGB")
port = cover_crop(port, PANEL, H).resize((PANEL, H), Image.LANCZOS)
img.paste(port, (W - PANEL, 0))
d.line([(W - PANEL, 0), (W - PANEL, H)], fill=LINE, width=2)

# Текст слева
x = 80
draw_tracked(d, (x, 118), EYEBROW, arial(20), CLAY, 2.5)
y = 165
for line in NAME:
    d.text((x, y), line, font=georgia(82), fill=INK); y += 90
y = 392
for line in TAGLINE:
    d.text((x, y), line, font=georgia_i(30), fill=INK_SOFT); y += 44

img.save(OUTPUT, "JPEG", quality=88, optimize=True, progressive=True)
print(f"OK: {OUTPUT.relative_to(HERE)} ({OUTPUT.stat().st_size // 1024} KB)")
