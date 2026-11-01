#!/usr/bin/env python3
"""Builds the site's pages from site-src/ (icy-pork/zelar#212). Standard
library only.

site-src/locales.json   the locales, the pages and the moved URLs
site-src/page.html      the one layout: head, header with the language menu, footer
site-src/content/<locale>/<page>.html
                        each page's text: a title and description comment,
                        then its <main>. Internal links are written {{root}}…

English is the core language and is built at the root (/, /privacy/ …);
every other ready locale under its own folder (/da/, /da/privacy/ …). A
ready locale without its own copy of a page gets the English text with a
notice, canonical to the English page and no hreflang of its own. The old
/en/… URLs become small redirect pages. sitemap.xml and 404.html are built
too.

The built pages are committed, so the site previews straight from the repo.

  python3 scripts/build-site.py           # write the pages
  python3 scripts/build-site.py --check   # fail if a committed page is out of date
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "site-src"
SITE = "https://zelar.whaaat.co"
META = re.compile(r"<!--\s*(\w+):\s*(.*?)\s*-->")


def load():
    config = json.loads((SRC / "locales.json").read_text(encoding="utf-8"))
    locales = [l for l in config["locales"] if l.get("ready")]
    return config, locales


def read_content(code, page_id):
    path = SRC / "content" / code / f"{page_id}.html"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    meta = dict(META.findall(text.split("<main", 1)[0]))
    main = text[text.index("<main"):].rstrip() + "\n"
    return {"title": meta["title"], "description": meta["description"], "main": main}


def url(locale, page):
    return f"{SITE}/{locale['path']}{page['path']}"


def language_menu(current, locales, page):
    if len(locales) < 2:
        return ""
    items = []
    for loc in locales:
        here = ' aria-current="true"' if loc is current else ""
        items.append(f'          <li><a href="/{loc["path"]}{page["path"]}" hreflang="{loc["lang"]}" lang="{loc["lang"]}"{here}>{loc["name"]}</a></li>')
    return (
        '      <details class="lang-menu">\n'
        f'        <summary aria-label="{current["ui"]["language"]}: {current["name"]}">{current["name"]}</summary>\n'
        '        <ul>\n' + "\n".join(items) + "\n        </ul>\n      </details>"
    )


def fill(template, values):
    def sub(match):
        key = match.group(1)
        value = values
        for part in key.split("."):
            value = value[part]
        return value
    return re.sub(r"\{\{([\w.]+)\}\}", sub, template)


def build_page(template, config, locales, locale, page):
    default = next(l for l in locales if l["code"] == config["default"])
    content = read_content(locale["code"], page["id"])
    translated = content is not None
    if not translated:
        content = read_content(default["code"], page["id"])
    # Pages that exist in a locale, for hreflang: only real translations.
    present = [l for l in locales if read_content(l["code"], page["id"]) is not None]
    canonical = url(locale, page) if translated else url(default, page)
    alternates = ""
    if translated:
        lines = [f'<link rel="alternate" hreflang="{l["lang"]}" href="{url(l, page)}">' for l in present]
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{url(default, page)}">')
        alternates = "\n".join(lines) + "\n"
    notice = ""
    if not translated:
        notice = f'\n<p class="notice" role="note"><span class="wrap">{html.escape(locale["ui"]["untranslated"])}</span></p>\n'
    root = "/" + locale["path"]
    main = content["main"].replace("{{root}}", root)
    page_lang = locale["lang"] if translated else default["lang"]
    values = {
        "lang": locale["lang"],
        "title": content["title"],
        "description": content["description"],
        "canonical": canonical,
        "alternates": alternates,
        "og_locale": locale["og"],
        "og_image": locale.get("ogImage") or default["ogImage"],
        "site": SITE,
        "root": root,
        "ui": locale["ui"],
        "language_menu": language_menu(locale, locales, page),
        "notice": notice,
        "current": {pid: (' aria-current="page"' if pid == page["id"] else "") for pid in ("privacy", "support", "ai")},
        "main": main if translated else main.replace('<main id="main">', f'<main id="main" lang="{page_lang}">', 1),
    }
    return fill(template, values)


def redirect_page(target):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Zélar — moved</title>
<meta name="description" content="This page has moved to {SITE}{target}">
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE}{target}">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<main id="main">
<div class="wrap wrap--narrow">
  <h1>This page has moved</h1>
  <p><a href="{target}">Go to the new page</a></p>
</div>
</main>
</body>
</html>
"""


def not_found(template_locales):
    en = next(l for l in template_locales if l["code"] == "en")
    others = [l for l in template_locales if l["code"] != "en"]
    links = "\n".join(
        f'    <a class="btn btn--ghost" href="/{l["path"]}" hreflang="{l["lang"]}" lang="{l["lang"]}">{l["name"]}</a>'
        for l in others)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found — Zélar</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#15100a">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<a class="skip-link" href="#main">{en["ui"]["skip"]}</a>

<header class="site-header">
  <div class="wrap">
    <a class="wordmark" href="/" aria-label="{en["ui"]["home"]}">zélar</a>
  </div>
</header>

<main id="main">
<div class="wrap wrap--narrow">
  <div class="page-head">
    <p class="eyebrow">404</p>
    <h1>Page not found</h1>
  </div>
  <div class="actions">
    <a class="btn btn--primary" href="/">Go to the home page</a>
{links}
  </div>
</div>
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>© 2026 Whaaat Company · CVR 46838068</p>
    <nav aria-label="{en["ui"]["footer"]}">
      <a href="/privacy/">{en["ui"]["privacy"]}</a>
      <a href="/support/">{en["ui"]["support"]}</a>
      <a href="/ai/">{en["ui"]["ai"]}</a>
      <a href="https://whaaat.co/">whaaat.co</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def sitemap(config, locales):
    default = next(l for l in locales if l["code"] == config["default"])
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page in config["pages"]:
        present = [l for l in locales if read_content(l["code"], page["id"]) is not None]
        for loc in present:
            out.append("  <url>")
            out.append(f"    <loc>{url(loc, page)}</loc>")
            for alt in present:
                out.append(f'    <xhtml:link rel="alternate" hreflang="{alt["lang"]}" href="{url(alt, page)}"/>')
            out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url(default, page)}"/>')
            out.append("  </url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def outputs():
    config, locales = load()
    template = (SRC / "page.html").read_text(encoding="utf-8")
    files = {}
    for locale in locales:
        for page in config["pages"]:
            files[f"{locale['path']}{page['path']}index.html"] = build_page(template, config, locales, locale, page)
    for old, new in config["moved"].items():
        if old.startswith("_"):
            continue
        files[f"{old}index.html"] = redirect_page("/" + new)
    files["404.html"] = not_found(locales)
    files["sitemap.xml"] = sitemap(config, locales)
    return files


def main():
    check = "--check" in sys.argv
    stale = []
    for rel, text in outputs().items():
        path = ROOT / rel
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if check:
        for rel in stale:
            print(f"out of date: {rel} (run python3 scripts/build-site.py)")
        print("Built pages: " + ("OK" if not stale else f"{len(stale)} out of date"))
        return 1 if stale else 0
    print("Built the site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
