# Localisation (icy-pork/zelar#212)

The Phase 0 audit for adding 10 more languages to the app and this site lives
in the app repo, so one copy covers both:
`icy-pork/zelar` → `docs/localization/AUDIT.md` (on `dev` and
`feat/zelar-pro`). Section 2 is about this site.

The short version for this repo:

- Danish stays at `/` and English at `/en/`; new locales go beside them
  (`/sv/`, `/de/`, …), so no existing URL moves.
- With 12 locales, the hand-copied header, footer and `sitemap.xml` would
  need a small build-time generator (standard-library Python, run in the
  workflow before `scripts/check-site.py`). Still no JavaScript and no
  third-party requests.
- The Open Graph images have baked-in text, so each locale needs its own.
- The glossary (Phase 2) is shared with the app, so a UI label quoted on the
  support or AI page matches the app in every language.

Nothing is changed on the site until the owner answers the audit's open
questions.
