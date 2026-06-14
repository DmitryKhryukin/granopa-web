# AGENTS.md

Concise reference for AI agents working on this repo. Read this before touching code.

## Overview

`granopa-web` — a single-page brochure site for **Таисия Галицкая**, a psychologist
working online (psychoanalytic approach, adults only). Plain **HTML/CSS + a little
vanilla JS**. No build step, no framework, no dependencies. Hosted as static files on
**Yandex Object Storage** (RF). Russian-language; audience is in Russia.

## Project structure

| Path | What |
|---|---|
| `index.html` | The whole page — markup and all copy |
| `styles.css` | All styling (design system in `:root`, tokens for palette/type/rhythm) |
| `main.js` | Optional progressive enhancement: scroll-reveal + mobile menu. Site fully works without it |
| `build-single.py` | Inlines CSS+JS into one self-contained `таисия-сайт.html` for review/sharing |
| `assets/` | Photos and diploma scans (create it; not yet populated) |
| `README.md` | Human-facing docs |
| `RESEARCH.md` | Deep background: structure, Yandex SEO, 152-ФЗ, B17. ⚠️ platform section is outdated (recommends Tilda; we went custom) |

## Commands

```sh
# Preview locally
python3 -m http.server 8000        # then open http://localhost:8000

# Build the single-file version (after editing html/css/js)
python3 build-single.py            # → таисия-сайт.html
```

There is no test/lint/build pipeline — it's static files.

## Constraints (read before editing)

- **No phone number, no contact form, no Yandex.Metrika** — deliberate. The site collects
  zero personal data (keeps it out of scope for 152-ФЗ). Don't add any of these without
  asking. Contacts are Telegram + email + VK only.
- **The copy was written by Таисия herself** (brief was in `сайт-мой.pdf`). Do not rewrite
  or paraphrase her text without asking — preserve it verbatim.
- **Plain HTML/CSS by choice** — chosen over Astro/Tilda for zero-maintenance longevity.
  Don't introduce a framework, bundler, or npm dependencies.
- **Placeholders to fill before launch** — search `index.html` for `ЗАПОЛНИТЬ`: real links
  (Telegram/email/VK/channel/Dzen), photos in `assets/`, og:url/og:image.
- **Fonts** load from Google Fonts for now (Lora + Manrope, both Cyrillic). Self-host
  before production (see README → Fonts).
- `таисия-сайт.html` is a generated artifact — don't hand-edit it; regenerate with
  `build-single.py`.

## Deploy

Static files → Yandex Object Storage bucket with static-website hosting; HTTPS via
Certificate Manager + Cloud CDN. See README → Deploy.

## More context

- `README.md` — setup, usage, deploy for humans
- `RESEARCH.md` — niche/SEO/legal background (platform section stale)
