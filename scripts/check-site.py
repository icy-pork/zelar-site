#!/usr/bin/env python3
"""Checks every page before deploy. Standard library only.

- internal links and assets resolve to a file in the site
- each page has lang, title, meta description, canonical and exactly one h1
- nothing loads from another origin (fonts, scripts, styles, images)
- no [[PLACEHOLDER]] text is left (pass --allow-placeholders in the template)

Run from the repo root: python3 scripts/check-site.py
"""
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "docs", "scripts", "site-src", "_site", "node_modules"}
LOADING = {("link", "href"), ("script", "src"), ("img", "src"), ("source", "src"),
           ("source", "srcset"), ("img", "srcset"), ("iframe", "src"), ("video", "src"), ("audio", "src")}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.loads, self.h1, self.meta, self.lang = [], [], 0, set(), None
        self.in_title, self.title = False, ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.meta.add("description")
        if tag == "link" and a.get("rel") == "canonical":
            self.meta.add("canonical")
        rel = a.get("rel") or ""
        for key in ("href", "src"):
            if key in a and a[key]:
                self.refs.append(a[key])
                if (tag, key) in LOADING and not (tag == "link" and rel in ("canonical", "alternate")):
                    self.loads.append(a[key])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def resolve(page, ref):
    ref = ref.split("#")[0].split("?")[0]
    if not ref:
        return True
    base = ROOT if ref.startswith("/") else page.parent
    target = (base / ref.lstrip("/")).resolve()
    if ref.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.is_file()


def main():
    errors = []
    allow_placeholders = "--allow-placeholders" in sys.argv
    if not allow_placeholders:
        for f in ROOT.rglob("*"):
            if f.suffix in (".html", ".xml", ".txt", ".css") and not SKIP_DIRS & set(f.relative_to(ROOT).parts):
                for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                    if "[[" in line:
                        errors.append(f"{f.relative_to(ROOT)}:{n}: placeholder left: {line.strip()[:80]}")
    pages = [p for p in ROOT.rglob("*.html") if not SKIP_DIRS & set(p.relative_to(ROOT).parts)]
    for page in sorted(pages):
        rel = page.relative_to(ROOT)
        doc = Page()
        doc.feed(page.read_text(encoding="utf-8"))
        if not doc.lang:
            errors.append(f"{rel}: <html> has no lang")
        if not doc.title.strip():
            errors.append(f"{rel}: empty <title>")
        if doc.h1 != 1:
            errors.append(f"{rel}: {doc.h1} h1 elements (want 1)")
        if rel.name != "404.html":
            for m in ("description", "canonical"):
                if m not in doc.meta:
                    errors.append(f"{rel}: missing {m}")
        for ref in doc.loads:
            if re.match(r"^(https?:)?//", ref):
                errors.append(f"{rel}: loads from another origin: {ref}")
        for ref in doc.refs:
            if re.match(r"^([a-z]+:|//)", ref):
                continue
            if not resolve(page, ref):
                errors.append(f"{rel}: broken link {ref}")
    for css in ROOT.rglob("*.css"):
        if SKIP_DIRS & set(css.relative_to(ROOT).parts):
            continue
        text = re.sub(r"/\*.*?\*/", "", css.read_text(encoding="utf-8"), flags=re.S)
        for ref in re.findall(r"url\(\s*['\"]?([^'\")]+)", text):
            if re.match(r"^(https?:)?//", ref):
                errors.append(f"{css.relative_to(ROOT)}: loads from another origin: {ref}")
            elif not ref.startswith("data:") and not (css.parent / ref).resolve().is_file():
                errors.append(f"{css.relative_to(ROOT)}: missing file {ref}")
        if "@import" in text:
            errors.append(f"{css.relative_to(ROOT)}: @import is not allowed")
    for e in errors:
        print("ERROR", e)
    print(f"Checked {len(pages)} pages: {'OK' if not errors else f'{len(errors)} problem(s)'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
