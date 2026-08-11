#!/usr/bin/env python3
"""
Build the deployed thank-you page at repo-root/thank-you/index.html.

The thank-you page is defined by the HTML template in this script (there is no
separate source file). It is the post-booking / post-submit confirmation and
the Google Ads conversion anchor. Fonts + logos are inlined at build time.

Edit the HTML template below, then:  python3 build_thankyou.py
"""
import re, base64, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = HERE
OUT = os.path.join(HERE, "..", "thank-you", "index.html")
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
    css = _fetch(FONTS_URL).decode()
    cache, faces = {}, []
    for subset, block in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S):
        if subset != "latin":
            continue
        m = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        if not m:
            continue
        url = m.group(1)
        if url not in cache:
            cache[url] = base64.b64encode(_fetch(url)).decode()
        faces.append(block.replace(url, f"data:font/woff2;base64,{cache[url]}"))
    return "\n".join(faces)

def img_data_uri(rel):
    ext = rel.rsplit(".", 1)[1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    with open(os.path.join(ASSETS, rel), "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()

FONT_CSS = inline_fonts() if __name__ == "__main__" else ""
LOGO_MARK = img_data_uri("assets/logo-mark.png") if __name__ == "__main__" else ""
LOGO_WHITE = img_data_uri("assets/logo-white.png") if __name__ == "__main__" else ""

# --- Google Tag Manager (plain strings so JS braces don't collide with the f-string) ---
GTM_HEAD = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-W3DF6HM3');</script>
<!-- End Google Tag Manager -->"""

GTM_NOSCRIPT = """<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W3DF6HM3"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""

def render():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="robots" content="noindex, nofollow, noarchive" />
{GTM_HEAD}
<title>Thank You — We’ll Be In Touch | Serene Mental Health &amp; Sleep</title>
<style>
{FONT_CSS}
:root{{
  --navy:#075097;--navy-deep:#053a6e;--blue:#3288b9;--sky:#87c5e8;--sky-tint:#e4f1fa;
  --sand:#f7f4ec;--gold:#e6b23e;--gold-deep:#c99626;--ink:#1c2b3a;--slate:#5a6b7b;
  --line:#e3e9f0;--white:#ffffff;--shadow-sm:0 2px 8px rgba(7,80,151,.06);
  --shadow-lg:0 24px 60px rgba(7,80,151,.18);--maxw:1180px;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,-apple-system,sans-serif;color:var(--ink);background:
  radial-gradient(1200px 480px at 78% -10%,rgba(135,197,232,.35),transparent 60%),
  linear-gradient(180deg,#f4f9fd 0%,#eaf3fb 100%);min-height:100vh;line-height:1.6;
  -webkit-font-smoothing:antialiased;display:flex;flex-direction:column}}
h1,h2,h3{{font-family:'Poppins',sans-serif;color:var(--navy-deep);line-height:1.15;font-weight:700}}
a{{color:inherit;text-decoration:none}}
img{{max-width:100%;display:block}}
.wrap{{max-width:var(--maxw);margin:0 auto;padding:0 22px;width:100%}}
header{{background:rgba(255,255,255,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:12px 22px;max-width:var(--maxw);margin:0 auto;gap:16px}}
.brand{{display:flex;align-items:center;gap:12px}}
.brand-mark{{height:46px;width:auto}}
.brand-name{{font-family:'Poppins',sans-serif;font-weight:700;font-size:1.06rem;color:var(--navy-deep);line-height:1.1}}
.brand-name span{{display:block;font-size:.68rem;font-weight:500;letter-spacing:.16em;text-transform:uppercase;color:var(--blue)}}
.nav-phone{{display:flex;align-items:center;gap:8px;font-family:'Poppins',sans-serif;font-weight:600;color:var(--navy)}}
.nav-phone svg{{width:18px;height:18px}}
@media(max-width:560px){{.nav-phone .num{{display:none}}}}
main{{flex:1;display:flex;align-items:center;justify-content:center;padding:48px 0}}
.card{{background:#fff;border:1px solid var(--line);border-radius:24px;box-shadow:var(--shadow-lg);
  max-width:620px;width:100%;margin:0 auto;padding:48px 44px;text-align:center}}
.check{{width:84px;height:84px;border-radius:50%;margin:0 auto 24px;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--navy),var(--blue));box-shadow:0 12px 30px rgba(7,80,151,.28)}}
.check svg{{width:44px;height:44px;color:#fff}}
.card h1{{font-size:clamp(1.7rem,4vw,2.3rem);font-weight:800;letter-spacing:-.01em}}
.card .lead{{font-size:1.12rem;color:var(--slate);margin:16px auto 6px;max-width:44ch}}
.reassure{{display:inline-flex;align-items:center;gap:8px;margin-top:20px;background:var(--sky-tint);
  border:1px solid #d4e6f4;color:var(--navy);border-radius:999px;padding:8px 16px;font-size:.85rem;font-weight:600}}
.reassure svg{{width:15px;height:15px}}
.steps{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:34px 0 6px;text-align:left}}
.step{{background:#fbfdff;border:1px solid var(--line);border-radius:14px;padding:18px 16px}}
.step .n{{width:30px;height:30px;border-radius:50%;background:linear-gradient(180deg,#ecc05a,var(--gold));
  color:#4a3708;display:grid;place-items:center;font-family:'Poppins';font-weight:800;font-size:.95rem;margin-bottom:10px}}
.step h3{{font-size:.98rem;margin-bottom:3px}}
.step p{{font-size:.84rem;color:var(--slate);line-height:1.45}}
@media(max-width:560px){{.steps{{grid-template-columns:1fr}}}}
.call-row{{margin-top:30px;font-size:.98rem;color:var(--slate)}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:9px;font-family:'Poppins',sans-serif;
  font-weight:600;font-size:1rem;padding:14px 28px;border-radius:999px;margin-top:14px;
  background:linear-gradient(180deg,#0a5aa6,var(--navy));color:#fff;box-shadow:0 8px 20px rgba(7,80,151,.28)}}
.btn svg{{width:18px;height:18px}}
.crisis{{max-width:620px;margin:22px auto 0;background:rgba(230,178,62,.12);border:1px solid rgba(230,178,62,.4);
  border-radius:12px;padding:12px 18px;color:#7a5a12;font-size:.84rem;text-align:center}}
.crisis strong{{color:var(--gold-deep)}}
footer{{background:#0b2540;color:#94aecb;padding:26px 0;font-size:.82rem;text-align:center;margin-top:40px}}
footer img{{height:40px;width:auto;margin:0 auto 10px;opacity:.95}}
</style>
</head>
<body>
{GTM_NOSCRIPT}

<header>
  <div class="nav">
    <a class="brand" href="https://info.serenementalhealthandsleep.com" aria-label="Serene Mental Health and Sleep home">
      <img class="brand-mark" src="{LOGO_MARK}" alt="" aria-hidden="true" />
      <span class="brand-name">Serene<span>Mental Health &amp; Sleep</span></span>
    </a>
    <a class="nav-phone" href="tel:+17134659282">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
      <span class="num">(713) 465-9282</span>
    </a>
  </div>
</header>

<main>
  <div class="wrap">
    <div class="card">
      <div class="check">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
      </div>
      <h1>Thank you — your request is in.</h1>
      <p class="lead">A member of our care team will reach out <strong>within one business day</strong> to confirm your appointment time. Keep an eye on your phone and email.</p>
      <span class="reassure">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        Confidential &amp; secure
      </span>

      <div class="steps">
        <div class="step"><div class="n">1</div><h3>We review your request</h3><p>Our team confirms your details and verifies your insurance.</p></div>
        <div class="step"><div class="n">2</div><h3>We call to confirm</h3><p>We reach out to lock in a time that works for you — often the same week.</p></div>
        <div class="step"><div class="n">3</div><h3>Meet your provider</h3><p>Connect by secure video with a board-certified provider from home.</p></div>
      </div>

      <div class="call-row">
        Prefer to talk now?
        <div>
          <a class="btn" href="tel:+17134659282">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            Call (713) 465-9282
          </a>
        </div>
      </div>
    </div>

    <div class="crisis">
      <strong>In crisis?</strong> If you’re experiencing a mental health emergency or thoughts of self-harm, call or text <strong>988</strong> (Suicide &amp; Crisis Lifeline) or dial <strong>911</strong>. This site is not for emergencies.
    </div>
  </div>
</main>

<footer>
  <div class="wrap">
    <img src="{LOGO_WHITE}" alt="Serene Mental Health and Sleep" />
    <div>&copy; 2026 Serene Mental Health &amp; Sleep · Serving Texas via telehealth</div>
  </div>
</footer>

</body>
</html>
"""

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    html = render()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {os.path.normpath(OUT)}: {len(html):,} chars")
    print(f"  @font-face: {html.count('@font-face')} | logos: {html.count('data:image')}"
          f" | GTM: {html.count('GTM-W3DF6HM3')} | noindex: {html.count('noindex')}")

if __name__ == "__main__":
    main()
