#!/usr/bin/env python3
"""
Build the deployed landing page from build/src-index.html.

Reads the human-editable source (with asset paths + a Google Fonts <link>),
produces a single self-contained file at repo-root/index.html:
  - Poppins + Inter (latin subset) inlined as @font-face data URIs
  - all assets/ images inlined as data URIs
  - Google Fonts <link>/<preconnect> removed (fonts are now inlined)
  - all HTML comments stripped (keeps view-source clean)
  - <meta robots noindex> added (staging/ad LP must not be indexed)

Usage:  python3 build_pages.py
Edit the SOURCE at build/src-index.html, then re-run and commit the output.
"""
import re, base64, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src-index.html")
ASSETS = HERE  # asset paths in the source are like "assets/..."
OUT = os.path.join(HERE, "..", "index.html")
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800"
             "&family=Inter:wght@400;500;600;700&display=swap")

def _fetch(url):
    # Full Chrome UA is required: with a bare "Mozilla/5.0" Google Fonts returns a
    # format WITHOUT the latin-subset woff2 blocks, and no fonts get inlined.
    ua = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    return urllib.request.urlopen(req).read()

def inline_fonts():
    """Fetch the Google Fonts CSS, keep only the latin subset, inline each woff2."""
    css = _fetch(FONTS_URL).decode()
    cache, faces = {}, []
    for subset, block in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S):
        if subset != "latin":
            continue
        m = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        if not m:
            continue
        url = m.group(1)
        if url not in cache:                       # dedupe (Inter serves one file per weight)
            cache[url] = base64.b64encode(_fetch(url)).decode()
        faces.append(block.replace(url, f"data:font/woff2;base64,{cache[url]}"))
    return "\n".join(faces)

def img_data_uri(rel):
    ext = rel.rsplit(".", 1)[1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    with open(os.path.join(ASSETS, rel), "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()

def main():
    html = open(SRC, encoding="utf-8").read()

    # 1. inline every referenced image (src="assets/...")
    for rel in sorted(set(re.findall(r'src="(assets/[^"]+)"', html))):
        html = html.replace('"' + rel + '"', '"' + img_data_uri(rel) + '"')

    # 2. drop the Google Fonts network requests; inline the faces instead
    html = re.sub(r'\s*<link rel="preconnect"[^>]*/>', "", html)
    html = re.sub(r'\s*<link href="https://fonts\.googleapis\.com[^>]*/>', "", html)
    html = html.replace("<style>", "<style>\n/* --- inlined brand fonts (latin) --- */\n"
                        + inline_fonts() + "\n", 1)

    # 3. keep the ad LP out of the index (avoids duplicate content w/ the main site)
    html = html.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        '<meta name="robots" content="noindex, nofollow, noarchive" />')

    # 4. strip ALL html comments (internal notes must not reach view-source).
    #    NOTE: anchor future comment/section regexes to unique local markers — a
    #    generic <!--.*?--> with DOTALL once matched from the first comment and ate
    #    the whole <head>. This blanket strip is safe only because it removes every
    #    complete comment, never spanning into live markup.
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"\n{3,}", "\n\n", html)  # tidy blank runs left by stripped comments

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)

    ext = re.findall(r'src="https?://[^"]*"', html)
    print(f"wrote {os.path.normpath(OUT)}: {len(html):,} chars")
    print(f"  images inlined: {html.count('data:image')} | @font-face: {html.count('@font-face')}"
          f" | comments left: {html.count('<!--')}")
    print(f"  remaining external refs: {ext}")

if __name__ == "__main__":
    main()
