#!/usr/bin/env python3
"""Скачивает самохостинг-шрифты в assets/fonts/ и печатает @font-face блок.

Берёт с Google Fonts только нужные подмножества (cyrillic + latin) и только те
начертания, что реально используются в styles.css:
    Lora    — 400 (normal, italic)
    Manrope — 400, 500, 600

Запуск:  python3 fetch-fonts.py
Дальше:  скопировать вывод faces в начало styles.css (если менялись начертания)
         и ./deploy.sh (шрифты заливаются вместе с assets/).
"""
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
FONTS = HERE / "assets" / "fonts"
FONTS.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
CSS_URL = ("https://fonts.googleapis.com/css2?"
           "family=Lora:ital,wght@0,400;1,400&"
           "family=Manrope:wght@400;500;600&display=swap")
WANT_SUBSETS = {"cyrillic", "latin"}


def fetch(url):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA})).read()


css = fetch(CSS_URL).decode("utf-8")
blocks = re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)

faces = []
for subset, block in blocks:
    if subset not in WANT_SUBSETS:
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", block).group(1).lower()
    weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
    style = re.search(r"font-style:\s*(\w+)", block).group(1)
    url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
    urange = re.search(r"unicode-range:\s*([^;]+);", block).group(1).strip()

    sty = "" if style == "normal" else f"-{style}"
    name = f"{fam}-{weight}{sty}-{subset}.woff2"
    (FONTS / name).write_bytes(fetch(url))
    print(f"  {name}")

    faces.append(
        f"@font-face {{\n"
        f"  font-family: '{fam.capitalize()}';\n"
        f"  font-style: {style};\n"
        f"  font-weight: {weight};\n"
        f"  font-display: swap;\n"
        f"  src: url('assets/fonts/{name}') format('woff2');\n"
        f"  unicode-range: {urange};\n"
        f"}}")

print(f"\nГотово: {len(faces)} файлов в assets/fonts/")
print("Если менялись начертания — обнови @font-face в styles.css:\n")
print("\n".join(faces))
