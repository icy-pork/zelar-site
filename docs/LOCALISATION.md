# Localisation (icy-pork/zelar#212)

The audit, the owner's decisions and the glossary live in the app repo, so
one copy covers both: `icy-pork/zelar` → `docs/localization/` (`AUDIT.md`,
`GLOSSARY.md`). Section 2 of the audit is about this site.

What this repo does about it:

- English is the core language at the root; every other locale lives under
  `/<locale>/` (`/da/` today). The old `/en/…` URLs redirect to the root.
- The pages are built from `site-src/` by `scripts/build-site.py`: one
  layout, one language menu, a sitemap with `hreflang` and `x-default`, and
  an English fallback with a notice for a page a language hasn't
  translated yet. See the README.
- Site text uses the same glossary as the app, so a UI label quoted on the
  support or AI page matches the app in every language.
- The Open Graph images have text baked in; each new locale needs its own
  (until then it uses the English one).
