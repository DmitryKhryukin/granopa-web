#!/usr/bin/env python3
"""Собирает один самодостаточный файл для отправки на просмотр.

Вшивает styles.css и main.js прямо в HTML, чтобы получился ОДИН файл,
который можно просто открыть двойным кликом (или переслать жене).

Запуск:  python3 build-single.py
Результат:  таисия-сайт.html
"""
import base64
import re
from pathlib import Path

here = Path(__file__).parent
html = (here / "index.html").read_text(encoding="utf-8")
css = (here / "styles.css").read_text(encoding="utf-8")
js = (here / "main.js").read_text(encoding="utf-8")

html = html.replace(
    '<link rel="stylesheet" href="styles.css" />',
    f"<style>\n{css}\n</style>",
)
html = html.replace(
    '<script src="main.js" defer></script>',
    f"<script>\n{js}\n</script>",
)

# Вшиваем фото из assets/ как data-URI, чтобы файл был полностью самодостаточным
def inline_asset(match):
    path = here / match.group(1)
    if not path.exists():
        return match.group(0)
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'src="data:image/jpeg;base64,{data}"'

html = re.sub(r'src="(assets/[^"]+)"', inline_asset, html)

out = here / "таисия-сайт.html"
out.write_text(html, encoding="utf-8")
print(f"Готово: {out.name}  ({out.stat().st_size // 1024} КБ)")
