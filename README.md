# zelar-site

The website for Zélar at **https://zelar.whaaat.co**: home, privacy policy,
support and the AI guide. **English is the core language, at the root**
(`/`, `/privacy/` …); every other language lives under its own folder
(`/da/`, `/da/privacy/` …). It is plain HTML with one shared stylesheet,
published to GitHub Pages by a GitHub Actions workflow. The pages are built
from `site-src/` by a small standard-library Python script and committed,
so the repo still previews as is (icy-pork/zelar#212).

This repo holds only the website. The app lives in `icy-pork/zelar`.

## Pages

| Page | English | Danish | What |
| --- | --- | --- | --- |
| `home` | `/` | `/da/` | Home |
| `privacy` | `/privacy/` | `/da/privacy/` | Privacy policy |
| `support` | `/support/` | `/da/support/` | Support and user guide |
| `ai` | `/ai/` | `/da/ai/` | "Your own AI in Zélar": Shortcuts, sharing, drafts, first load (icy-pork/zelar#265) |
| | `/404.html` | | Not found, with a link to each language |

`/en/`, `/en/privacy/`, `/en/support/` and `/en/ai/` are redirect pages to
the root, kept so links from before the English root still land. Until
icy-pork/zelar#212, Danish was at the root: `/privacy/` and friends now show
English. The app links to the old `icy-pork.github.io/zelar-privacy/`
pages until its next release switches to this site.

The site is set up for the app's 12 locales (`site-src/locales.json`):
`en`, `en-GB`, `da`, `sv`, `nb`, `de`, `fr`, `it`, `es`, `pt-PT`, `pt-BR`
and `nl`. A locale is published once its `ready` flag is on. A page a ready
locale hasn't translated yet is built from the English text, with a notice
in that language and its canonical pointing to the English page, and is
left out of `hreflang` and the sitemap. Every built page carries
`<html lang>`, `hreflang` alternates with `x-default` (English), its own
title, description and Open Graph tags; `sitemap.xml` lists them all.

```
├─ site-src/                 the source of every page (not published)
│  ├─ locales.json           locales, UI strings (menu, footer…), pages, moved URLs
│  ├─ page.html              the one layout: head, header, language menu, footer
│  └─ content/<locale>/<page>.html   title, description and <main> of each page
├─ assets/
│  ├─ css/site.css     theme (:root) + shared components
│  ├─ fonts/           self-hosted Fraunces and Inter (OFL, licences beside them)
│  └─ img/             app icon, favicons, Open Graph images (og-en, og-da)
├─ scripts/build-site.py   builds the pages from site-src/
├─ scripts/check-site.py   runs before every deploy
├─ docs/DOMAIN-SETUP.md    DNS and GitHub Pages setup
└─ .github/workflows/pages.yml
```

`docs/`, `scripts/`, `site-src/` and this README are not published.

## Editing

- **Never edit a built page** (`index.html`, `da/…`, `sitemap.xml`,
  `404.html`). Edit `site-src/` and run `python3 scripts/build-site.py`;
  commit both. The workflow fails if a built page is out of date.
- **Page text:** `site-src/content/<locale>/<page>.html`. The two comments at
  the top are the page's title and meta description (also used for Open
  Graph). Write internal links as `{{root}}privacy/`; the build turns that
  into `/privacy/` or `/da/privacy/`.
- **Header, footer and language menu:** `site-src/page.html` and the `ui`
  strings in `site-src/locales.json`, once for every page.
- **A new language:** add its `ui` strings in `locales.json`, translate the
  pages into `site-src/content/<locale>/`, set `ready` to true and rebuild.
  Wine and app terms follow the glossary in `icy-pork/zelar`
  (`docs/localization/GLOSSARY.md`), so the site says what the app says.
  Its Open Graph image (`ogImage`) falls back to the English one.
- **Every language:** when you change a page, change its translations in
  the same commit.
- **Look:** change the tokens in `:root` at the top of
  `assets/css/site.css`. The rest of that file is the shared component CSS
  from `app-site-template`. The fonts' `unicode-range` covers Latin-1 plus
  Œ/œ, which is every letter the 12 locales use.
- **Privacy policy:** the text must match the app's privacy manifest
  (`PrivacyInfo.xcprivacy`) and its App Store privacy label, and say the
  same thing in every language: translate it faithfully, never for style.
  Update the "Last updated" date in every language with every change. The
  text was moved word for word from `icy-pork/zelar-privacy` on
  2026-10-29. On 2026-11-01 it gained the Zélar AI, server-settings,
  exchange rates and cellar-sharing sections, from the drafts in
  `icy-pork/zelar` `docs/compliance/` (icy-pork/zelar#174).
- **No third-party requests:** fonts, images and styles are all served from
  this site. No analytics, cookies, scripts or embeds; the language menu is
  a plain `<details>`. The check fails if a page loads anything from
  another origin.

## Preview and check locally

```sh
python3 scripts/build-site.py   # build the pages from site-src/
python3 -m http.server 8000     # then open http://localhost:8000
python3 scripts/check-site.py   # links, one h1 per page, meta tags, no third-party loads
```

Links start with `/`, so preview from the repo root as above, not by
opening the files directly.

## Deploy

Push to `main`. The workflow checks that the built pages are current and
valid, then publishes everything except `docs/`, `scripts/`, `site-src/`,
dotfiles and this README. Pull requests run the
check only.

## Still to do

- **App Store button:** hidden in an HTML comment on both home pages until
  the app is live. Add the real App Store URL in `site-src/content/*/home.html`
  and remove the comment. Then
  also add the Smart App Banner meta tag (comment in `site-src/page.html`).
- **Screenshots:** none yet. Add real App Store screenshots to the home
  pages when they exist (marked with a comment); no mock-ups.
- **Shortcut links:** the AI guide (`site-src/content/*/ai.html`) has a "Links coming"
  box and a build-it-yourself recipe until the owner has built the two
  Shortcuts on a device. Add their iCloud links where the HTML comment says
  (icy-pork/zelar#265).
- **App links:** the app still opens `icy-pork.github.io/zelar-privacy/`
  (privacy) and `…/zelar-privacy/ai.html` (AI guide). The owner switches
  them to `/privacy/` and `/ai/` here (English, with the language menu) at
  the app's next release (icy-pork/zelar#212).

## Template

This site started from `icy-pork/app-site-template`. Changes to the
template do not flow here automatically; copy them across by hand when
needed (usually the shared part of `site.css`, `scripts/check-site.py` and
the workflow).
