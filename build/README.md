# Build pipeline — Serene landing page

This repo is deployed by **Cloudflare Pages** (project `serene-lp`, connected to
`PracticeGrowthCo/serene-lp`, output dir `/`). Every push to `main` auto-deploys.

## What's served
- `../index.html` — the landing page (`https://info.serenementalhealthandsleep.com`)
- `../thank-you/index.html` — the post-booking / thank-you page + Google Ads conversion anchor

Both are **generated** — don't hand-edit them. Edit the source here, rebuild, commit.

## Files here
| File | Role |
|---|---|
| `src-index.html` | **Source** for the landing page. Human-readable: `assets/…` image paths + a Google Fonts `<link>`. **Edit this** for LP changes. |
| `assets/` | Logos + provider headshots used by the LP. |
| `build_pages.py` | Builds `../index.html` from `src-index.html`. |
| `build_thankyou.py` | Builds `../thank-you/index.html`. The thank-you HTML lives **in the script** (no separate source file) — edit the template inside it. |

## How to build
```bash
cd build
python3 build_pages.py       # → ../index.html
python3 build_thankyou.py    # → ../thank-you/index.html
git add -A && git commit -m "…" && git push   # Cloudflare auto-deploys
```
No dependencies beyond Python 3 stdlib. The scripts fetch Google Fonts at build
time (needs internet) and inline everything, so the output has **zero external
asset dependencies**.

## What the build does
1. Inlines Poppins + Inter (latin subset woff2) as `@font-face` data URIs.
2. Inlines every `assets/…` image as a data URI.
3. Removes the Google Fonts `<link>`/`<preconnect>` (fonts are now inlined).
4. Strips **all** HTML comments (keeps internal notes out of view-source).
5. Adds `<meta robots noindex>` (ad LP must not compete with the main site).

## Gotchas
- **Google Fonts needs a full Chrome User-Agent** or it returns a format with no
  latin woff2 and **no fonts get inlined**. `_fetch()` already sets one — don't
  weaken it.
- **Never** write a blanket `<!--.*?-->` (DOTALL) regex that isn't the final
  strip-all step — a version of it once matched from the first comment in the
  file and deleted the entire `<head>`. Anchor comment edits to unique markers.
- The landing page embeds the **GHL booking calendar** (`6wkTyIqhxeW4x6DDBuWu`);
  set its post-booking redirect to `…/thank-you` in GHL. GTM `GTM-W3DF6HM3` is on
  both pages; the Google Ads conversion tag lives in the GTM container (not here).
