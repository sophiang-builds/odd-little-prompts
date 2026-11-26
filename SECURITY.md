# Security notes

## What protects the site

- **HTTPS** is issued and renewed by GitHub Pages (Let's Encrypt). Keep "Enforce HTTPS" ticked under Settings > Pages.
- **Content Security Policy** (a `<meta>` tag at the top of each page) lists the only places code, styles, fonts and images may come from:
  - `index.html`: this site, Google Fonts, and Buy Me a Coffee (`cdnjs.buymeacoffee.com` for the button script, `cdn.buymeacoffee.com` for its images).
  - `app.html`: this site and Google Fonts. No outside scripts.
  - `sketchbook-warm-ups/index.html`: no scripts at all.
- **No inline JavaScript.** Page code lives in `assets/site.js` and `assets/app.js`, so the policy can refuse any script that isn't one of ours.
- **Referrer policy** `strict-origin-when-cross-origin`: other sites see only `oddlittleprompts.com`, never the full page address.
- If the Buy Me a Coffee script is blocked or fails, `assets/site.js` shows the plain backup coffee link instead.

## Adding a new outside service

Add its exact host to the matching directive in that page's Content-Security-Policy tag (`script-src` for scripts, `img-src` for images, `connect-src` for data requests, `frame-src` for embeds). Test in a browser and watch the console for "Refused to load". Never add `'unsafe-inline'` or `'unsafe-eval'` to `script-src`.

## What GitHub Pages can't do

It doesn't allow custom response headers, so there is no HSTS, `frame-ancestors` or `X-Frame-Options` (meta tags can't set these). For a static site with no logins this is acceptable. Full header control needs a proxy such as Cloudflare in front.

## Domain and account checklist

- DNS at Porkbun: four GitHub A records, four AAAA records, `www` CNAME to `sophiang-builds.github.io`, no wildcard record.
- DNSSEC on. Registrar lock and auto-renew on.
- CAA `0 issue "letsencrypt.org"` (only after HTTPS works).
- DMARC `_dmarc` TXT `v=DMARC1; p=reject` (the domain never sends mail).
- Domain verified in GitHub profile Settings > Pages.
- Two-factor sign-in (passkey or app) on GitHub, Porkbun and Buy Me a Coffee.
- Occasionally check crt.sh for certificates you didn't expect, and re-test at ssllabs.com and securityheaders.com after big changes.
