# zelar-site

The website for Zélar at **https://zelar.whaaat.co**: home, privacy policy,
support and the AI guide, in Danish at `/` and English under `/en/`. It is plain HTML
with one shared stylesheet, published to GitHub Pages by a GitHub Actions
workflow. There is no build step.

This repo holds only the website. The app lives in `icy-pork/zelar`.

## Pages

| Danish | English | What |
| --- | --- | --- |
| `index.html` | `en/index.html` | Home |
| `privacy/index.html` | `en/privacy/index.html` | Privacy policy |
| `support/index.html` | `en/support/index.html` | Support and user guide |
| `ai/index.html` | `en/ai/index.html` | "Din egen AI i Zélar": Shortcuts, sharing, drafts, first load (icy-pork/zelar#265) |
| `404.html` | | Not found (both languages) |

Every page links to its other-language twin with `hreflang`, and
`sitemap.xml` lists both.

```
├─ assets/
│  ├─ css/site.css     theme (:root) + shared components
│  ├─ fonts/           self-hosted Fraunces and Inter (OFL, licences beside them)
│  └─ img/             app icon, favicons, Open Graph images
├─ scripts/check-site.py   runs before every deploy
├─ docs/DOMAIN-SETUP.md    DNS and GitHub Pages setup
└─ .github/workflows/pages.yml
```

`docs/`, `scripts/` and this README are not published.

## Editing

- **Look:** change the tokens in `:root` at the top of
  `assets/css/site.css`. The rest of that file is the shared component CSS
  from `app-site-template`.
- **Header and footer** are repeated in each of the nine HTML files. When
  you change one, change them all (search for `site-header` or
  `site-footer`).
- **Both languages:** when you change a Danish page, change its English twin
  in the same commit.
- **Privacy policy:** the text must match the app's privacy manifest
  (`PrivacyInfo.xcprivacy`) and its App Store privacy label. Update the
  "Senest opdateret / Last updated" date with every change. The text here
  was moved word for word from `icy-pork/zelar-privacy` on 2026-10-29.
  On 2026-11-01 it gained the Zélar AI (Worker), server-settings, exchange
  rates and cellar-sharing sections, from the drafts in `icy-pork/zelar`
  `docs/compliance/` (icy-pork/zelar#174).
- **No third-party requests:** fonts, images and styles are all served from
  this site. No analytics, cookies or embeds. The check fails if a page
  loads anything from another origin.

## Preview and check locally

```sh
python3 -m http.server 8000     # then open http://localhost:8000
python3 scripts/check-site.py   # links, one h1 per page, meta tags, no third-party loads
```

Links start with `/`, so preview from the repo root as above, not by
opening the files directly.

## Deploy

Push to `main`. The workflow checks the pages, then publishes everything
except `docs/`, `scripts/`, dotfiles and this README. Pull requests run the
check only.

## Still to do

- **App Store button:** hidden in an HTML comment on both home pages until
  the app is live. Add the real App Store URL and remove the comment. Then
  also add the Smart App Banner meta tag (comment in each page's `<head>`).
- **Screenshots:** none yet. Add real App Store screenshots to the home
  pages when they exist (marked with a comment); no mock-ups.
- **Shortcut links:** the AI guide (`ai/`, `en/ai/`) has a "Links coming"
  box and a build-it-yourself recipe until the owner has built the two
  Shortcuts on a device. Add their iCloud links where the HTML comment says
  (icy-pork/zelar#265).
- **App links:** the app still opens `icy-pork.github.io/zelar-privacy/`
  (privacy) and `…/zelar-privacy/ai.html` (AI guide). Point them at
  `/privacy/` and `/ai/` here, or redirect from the old repo.

## Template

This site started from `icy-pork/app-site-template`. Changes to the
template do not flow here automatically; copy them across by hand when
needed (usually the shared part of `site.css`, `scripts/check-site.py` and
the workflow).
