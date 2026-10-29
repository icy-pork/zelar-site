# Domain setup: whaaat.co on GitHub Pages

This guide puts the Whaaat sites on their own domains. The same file is in
every site repo.

| Domain | Repo | What it is |
| --- | --- | --- |
| `whaaat.co` (and `www.whaaat.co`, which redirects) | `icy-pork/whaaat-site` | Company page |
| `zelar.whaaat.co` | `icy-pork/zelar-site` | Zélar: home, `/privacy/`, `/support/`, English under `/en/` |
| `<app>.whaaat.co` | `icy-pork/<app>-site`, created from `icy-pork/app-site-template` | Future apps |

The GitHub owner is the personal account `icy-pork`, so every DNS record
points at `icy-pork.github.io`. DNS for `whaaat.co` is at Namecheap.

> **Keep the old Zélar URL working.** The released app links to
> `https://icy-pork.github.io/zelar-privacy/` (`ProLinks.privacyPolicy` in
> the app). Leave the `icy-pork/zelar-privacy` repo and its Pages site
> exactly as they are until a released app version points at
> `https://zelar.whaaat.co/privacy/`. **Never create a repo named
> `icy-pork.github.io` with a custom domain**: GitHub would then move every
> project site without its own domain, including `zelar-privacy`, under
> that domain.

## Order matters

Verify the domain and add it in GitHub **before** you change DNS.
Otherwise someone else could point a `whaaat.co` subdomain at their own
GitHub Pages site.

### 1. Verify `whaaat.co` in GitHub

1. Open <https://github.com/settings/pages> (your account settings, Pages).
2. Click **Add a domain** and enter `whaaat.co`.
3. GitHub shows a TXT record: host `_github-pages-challenge-icy-pork`,
   plus a value. Add it in step 3 below, then come back and click
   **Verify**. Verifying the apex also protects every subdomain.

### 2. Turn on Pages in each repo

In each repo: **Settings → Pages → Build and deployment → Source: GitHub
Actions**, then fill in **Custom domain**:

| Repo | Custom domain |
| --- | --- |
| `whaaat-site` | `whaaat.co` |
| `zelar-site` | `zelar.whaaat.co` |

With the GitHub Actions source, the domain lives in the repo settings. Do
not add a `CNAME` file.

The same from a terminal (with `gh` logged in as `icy-pork`):

```sh
gh api -X POST repos/icy-pork/zelar-site/pages -f build_type=workflow
gh api -X PUT  repos/icy-pork/zelar-site/pages -f cname=zelar.whaaat.co

gh api -X POST repos/icy-pork/whaaat-site/pages -f build_type=workflow
gh api -X PUT  repos/icy-pork/whaaat-site/pages -f cname=whaaat.co
```

Then run the **Deploy to GitHub Pages** workflow once (Actions tab, or push
to `main`).

### 3. Add the DNS records in Namecheap

Namecheap → **Domain List** → `whaaat.co` → **Manage** → **Advanced DNS**.
The domain must use Namecheap's own nameservers (Namecheap BasicDNS).

| Type | Host | Value | Note |
| --- | --- | --- | --- |
| A | `@` | `185.199.108.153` | Four A records for the apex |
| A | `@` | `185.199.109.153` | |
| A | `@` | `185.199.110.153` | |
| A | `@` | `185.199.111.153` | |
| AAAA | `@` | `2606:50c0:8000::153` | Optional IPv6; also `8001`, `8002`, `8003` |
| CNAME | `www` | `icy-pork.github.io.` | No repo name in the value |
| CNAME | `zelar` | `icy-pork.github.io.` | One CNAME per app subdomain |
| TXT | `_github-pages-challenge-icy-pork` | the value GitHub showed in step 1 | Domain verification |

TTL: Automatic is fine. Re-check the IP addresses against
[GitHub's custom domain docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
before you enter them; they rarely change, but the docs are the source of
truth.

### 4. Clean up Namecheap's defaults

Delete the parking records Namecheap adds to a new domain:

- the **URL Redirect Record** for `@`
- the **CNAME** for `www` pointing at `parkingpage.namecheap.com`

**Keep every MX, SPF, DKIM and other TXT record.** They carry email for
`anders@whaaat.co`.

### 5. Never add a wildcard record

No `*.whaaat.co` record, ever. GitHub warns that a wildcard makes
subdomain takeover possible.

### 6. Turn on HTTPS

Once GitHub's DNS check passes (Settings → Pages shows a green tick), tick
**Enforce HTTPS** in each repo. The certificate can take up to 24 hours. If
the box stays greyed out, remove the custom domain, save, and add it again.

```sh
gh api -X PUT repos/icy-pork/zelar-site/pages  -F https_enforced=true
gh api -X PUT repos/icy-pork/whaaat-site/pages -F https_enforced=true
```

### 7. Check from a terminal

```sh
dig +short whaaat.co A                # the four 185.199.x.153 addresses
dig +short www.whaaat.co CNAME        # icy-pork.github.io.
dig +short zelar.whaaat.co CNAME      # icy-pork.github.io.
curl -sI https://whaaat.co | head -1          # HTTP/2 200
curl -sI https://www.whaaat.co | head -1      # 301 to https://whaaat.co/
curl -sI https://zelar.whaaat.co | head -1    # HTTP/2 200
curl -sI https://icy-pork.github.io/zelar-privacy/ | head -1   # still 200
```

## Zélar: App Store Connect

Do **not** change any URL in App Store Connect or in the app while a
version is in review. Once `https://zelar.whaaat.co` is live with HTTPS,
and the next version is ready to submit:

| App Store Connect field | URL |
| --- | --- |
| Marketing URL | `https://zelar.whaaat.co/` |
| Support URL | `https://zelar.whaaat.co/support/` |
| Privacy Policy URL | `https://zelar.whaaat.co/privacy/` |

In the app, change `ProLinks.privacyPolicy` to
`https://zelar.whaaat.co/privacy/` in the same release. After that release
is live, add `<link rel="canonical" href="https://zelar.whaaat.co/privacy/">`
to the old `zelar-privacy` pages and leave their content in place, so
older app versions keep working.

## Adding a new app site

1. On GitHub, open `icy-pork/app-site-template` and click **Use this
   template → Create a new repository**. Name it `<app>-site`, **public**
   (Pages on a private repo needs a paid plan).
2. Clone it, run `python3 scripts/new-app.py "<App name>" <app>.whaaat.co`,
   then write the content the script lists as still missing. The deploy
   refuses to publish while any `[[PLACEHOLDER]]` is left.
3. Step 2 above for the new repo, with custom domain `<app>.whaaat.co`.
4. In Namecheap, add one record: CNAME, host `<app>`, value
   `icy-pork.github.io.`
5. Step 6 (Enforce HTTPS) and step 7 (check).

**When an app site is retired**, delete its CNAME in Namecheap at the same
time as the repo or its Pages site, so nobody can take over the subdomain.
