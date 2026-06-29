#!/usr/bin/env python3
"""
Render a SpaceX-style deck (one deck.html with many <section class="slide">)
into per-slide PNGs and a combined PDF, using headless Chrome.

Usage:
    python render_deck.py deck.html [--out output_dir] [--scale 2] [--png-only]

Contract for deck.html:
    - Links ../assets/css/deck.css (or inline <style>) in <head>.
    - Each slide is a TOP-LEVEL <section class="slide"> ... </section>.
      Do NOT nest <section> tags inside a slide (use <div>).
    - All <img> use LOCAL relative paths (download images first).
"""
import argparse, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

def find_chrome():
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    found = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
    if found:
        return found
    sys.exit("ERROR: Chrome/Edge not found. Set CHROME_PATH env var to the browser executable.")

def split_slides(html):
    # Strip HTML comments first so commented-out examples (which may themselves
    # contain <section class="slide">) can't leak into a real slide.
    clean = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    head = ""
    m = re.search(r"<head\b[^>]*>(.*?)</head>", clean, re.S | re.I)
    if m:
        head = m.group(1)
    slides = re.findall(r"<section class=\"slide.*?</section>", clean, re.S)
    if not slides:
        sys.exit("ERROR: no <section class=\"slide\"> found in the HTML.")
    return head, slides

SLIDE_DOC = """<!doctype html><html><head><meta charset="utf-8">{head}
<style>html,body{{margin:0;padding:0;background:#000;width:1920px;height:1080px;overflow:hidden}}
.slide{{position:relative !important;margin:0 !important}}</style></head>
<body>{slide}
<script>
(function(){{
  var nodes=[document.querySelector('.slide'),document.querySelector('.pad')].filter(Boolean);
  if(!nodes.length){{document.documentElement.setAttribute('data-ovf','noslide');return;}}
  var y=0,x=0;
  nodes.forEach(function(e){{ y=Math.max(y,e.scrollHeight-e.clientHeight); x=Math.max(x,e.scrollWidth-e.clientWidth); }});
  document.documentElement.setAttribute('data-ovf',(y>2||x>2)?('over;y='+y+';x='+x):'ok');
}})();
</script></body></html>"""

OVF_RE = re.compile(r'data-ovf="([^"]*)"')

def check_overflow(chrome, uri):
    # Return (overflow_y, overflow_x) in px via a fast dump-dom pass.
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--window-size=1920,1080", "--virtual-time-budget=1500", "--dump-dom", uri]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    m = OVF_RE.search(r.stdout or "")
    if not m or m.group(1) in ("ok", "noslide", ""):
        return (0, 0)
    try:
        parts = dict(p.split("=") for p in m.group(1).split(";")[1:])
        return (int(parts.get("y", 0)), int(parts.get("x", 0)))
    except Exception:
        return (0, 0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--out", default=None)
    ap.add_argument("--scale", type=float, default=2.0,
                    help="device pixel ratio: 2 = 4K/crisp (default), 3 = print")
    ap.add_argument("--png-only", action="store_true")
    ap.add_argument("--pdf-quality", type=int, default=92,
                    help="JPEG quality for PDF pages, 1-95 (default 92)")
    ap.add_argument("--no-check", action="store_true", help="skip overflow detection")
    args = ap.parse_args()

    deck = Path(args.deck).resolve()
    if not deck.exists():
        sys.exit(f"ERROR: {deck} not found")
    work = deck.parent
    out = Path(args.out).resolve() if args.out else work / "out"
    out.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome()
    head, slides = split_slides(deck.read_text(encoding="utf-8"))
    print(f"Found {len(slides)} slides. Browser: {chrome}")

    png_paths = []
    tmp_files = []
    overflows = []   # (slide_index, y_px, x_px)
    try:
        for i, slide in enumerate(slides, 1):
            # temp slide file lives NEXT TO deck.html so relative asset paths resolve
            tmp = work / f"__render_{i:03d}.html"
            tmp.write_text(SLIDE_DOC.format(head=head, slide=slide), encoding="utf-8")
            tmp_files.append(tmp)

            if not args.no_check:
                oy, ox = check_overflow(chrome, tmp.as_uri())
                if oy > 2 or ox > 2:
                    overflows.append((i, oy, ox))

            png = out / f"slide_{i:03d}.png"
            cmd = [
                chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--no-sandbox", "--default-background-color=000000ff",
                f"--force-device-scale-factor={args.scale}",
                "--window-size=1920,1080",
                "--virtual-time-budget=4000",
                f"--screenshot={png}", tmp.as_uri(),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if not png.exists():
                print(r.stderr[-800:])
                sys.exit(f"ERROR: failed to render slide {i}")
            png_paths.append(png)
            flag = ""
            for (oi, oy, ox) in overflows:
                if oi == i:
                    flag = f"   ⚠ OVERFLOW (content past edge: {oy}px down, {ox}px wide)"
            print(f"  rendered slide {i:>2}  ->  {png.name}{flag}")
    finally:
        for t in tmp_files:
            try: t.unlink()
            except OSError: pass

    if not args.png_only:
        try:
            from PIL import Image
        except ImportError:
            sys.exit("Pillow needed for PDF. pip install pillow  (or use --png-only)")
        imgs = [Image.open(p).convert("RGB") for p in png_paths]
        pdf = out / (deck.stem + ".pdf")
        # PDF pages are JPEG-encoded; keep quality high so the PDF stays nearly
        # as crisp as the lossless PNGs (the PNGs remain the master output).
        imgs[0].save(pdf, save_all=True, append_images=imgs[1:],
                     resolution=144.0, quality=args.pdf_quality)
        print(f"\nPDF: {pdf}  (q{args.pdf_quality}; PNGs are lossless masters)")
    print(f"PNGs: {out}")

    if overflows:
        print("\n" + "="*64)
        print("⚠  CONTENT OVERFLOW — these slides are CLIPPED (text/elements run")
        print("   past the slide edge and were silently cut off):")
        for (i, oy, ox) in overflows:
            bits = []
            if oy > 2: bits.append(f"{oy}px below the bottom")
            if ox > 2: bits.append(f"{ox}px past the right")
            print(f"     slide {i:>2}:  {', '.join(bits)}")
        print("   FIX before delivering: cut words, split across more columns,")
        print("   switch to the product-card layout, or move content to a new slide.")
        print("   Do NOT ship a clipped deck.")
        print("="*64)

if __name__ == "__main__":
    main()
