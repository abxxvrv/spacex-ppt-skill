#!/usr/bin/env python3
"""
Fetch + normalize photos from Pexels into a cohesive, on-brand set.

The cohesion is MANUFACTURED in post: every image is darkened + slightly
desaturated (and optionally duotoned toward one color), so even mixed source
photos read like one deck. Darker candidates are preferred because they leave
room for white text and scrims.

Usage:
    python fetch_images.py --query "ocean horizon" --count 6 --out images/
    python fetch_images.py --query "desert dunes" --count 4 --orientation landscape \\
        --darken 0.65 --saturation 0.8 --duotone "#0c1622"

Key resolution order: $PEXELS_API_KEY  ->  scripts/pexels_key.txt
Credits are written to <out>/CREDITS.txt and <out>/credits.json (Pexels asks
for attribution; keep it with the deck).
"""
import argparse, json, os, sys
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ImageOps

API = "https://api.pexels.com/v1/search"

def _is_placeholder(k):
    # treat empty / unfilled template text as "no key"
    return (not k) or k.upper().startswith(("YOUR", "PASTE", "REPLACE", "<", "#"))

def load_key():
    env = (os.environ.get("PEXELS_API_KEY") or "").strip()
    if not _is_placeholder(env):
        return env
    f = Path(__file__).parent / "pexels_key.txt"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):   # skip blanks / comment lines
                continue
            if not _is_placeholder(line):
                return line
            break
    sys.exit(
        "ERROR: No Pexels API key found.\n"
        "  Pexels issues free API keys instantly. Tell the user to:\n"
        "    1. create a free key at  https://www.pexels.com/api/  (~1 min)\n"
        "    2. paste it into  scripts/pexels_key.txt   (or set the\n"
        "       PEXELS_API_KEY environment variable)\n"
        "  Keep the key private; never share a skill package that contains it.")

def luminance(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return 0.2126*r + 0.7152*g + 0.0722*b

def search(key, query, orientation, want):
    # over-fetch candidates so we can pick the darkest / best-fit
    per_page = min(80, max(want * 4, 15))
    r = requests.get(API, headers={"Authorization": key},
                     params={"query": query, "orientation": orientation,
                             "per_page": per_page, "size": "large"}, timeout=30)
    r.raise_for_status()
    return r.json().get("photos", [])

def duotone(img, dark_hex, light_hex="#f2f2f2"):
    g = ImageOps.grayscale(img)
    return ImageOps.colorize(g, black=dark_hex, white=light_hex).convert("RGB")

def treat(img, darken, saturation, contrast, duo):
    img = img.convert("RGB")
    if duo:
        img = duotone(img, duo)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if darken != 1.0:
        img = ImageEnhance.Brightness(img).enhance(darken)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--orientation", default="landscape",
                    choices=["landscape", "portrait", "square"])
    ap.add_argument("--out", default="images")
    ap.add_argument("--prefer", default="dark", choices=["dark", "any"],
                    help="dark = prefer darker photos (better for white text)")
    ap.add_argument("--darken", type=float, default=0.72)
    ap.add_argument("--saturation", type=float, default=0.85)
    ap.add_argument("--contrast", type=float, default=1.04)
    ap.add_argument("--duotone", default=None, help='hex like "#0c1622" (optional)')
    ap.add_argument("--prefix", default=None, help="filename prefix (default: slug of query)")
    args = ap.parse_args()

    key = load_key()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or "".join(c if c.isalnum() else "-" for c in args.query.lower()).strip("-")

    photos = search(key, args.query, args.orientation, args.count)
    if not photos:
        sys.exit(f"No results for '{args.query}'.")
    if args.prefer == "dark":
        photos.sort(key=lambda p: luminance(p.get("avg_color", "#808080")))
    photos = photos[:args.count]

    credits = []
    for i, p in enumerate(photos, 1):
        url = p["src"]["original"]
        raw = requests.get(url, timeout=60).content
        tmp = out / f".__raw_{i}.jpg"; tmp.write_bytes(raw)
        try:
            img = Image.open(tmp)
            img = treat(img, args.darken, args.saturation, args.contrast, args.duotone)
            name = f"{prefix}-{i:02d}.jpg"
            img.save(out / name, "JPEG", quality=88)
        finally:
            tmp.unlink(missing_ok=True)
        credits.append({"file": name, "photographer": p.get("photographer"),
                        "url": p.get("url"), "pexels_id": p.get("id"),
                        "avg_color": p.get("avg_color")})
        print(f"  {name}  <-  {p.get('photographer')}  ({p.get('avg_color')})")

    (out / "credits.json").write_text(json.dumps(credits, indent=2), encoding="utf-8")
    with (out / "CREDITS.txt").open("a", encoding="utf-8") as f:
        f.write(f"\n# query: {args.query}\n")
        for c in credits:
            f.write(f"{c['file']}: Photo by {c['photographer']} on Pexels — {c['url']}\n")
    print(f"\nSaved {len(credits)} images to {out}/  (credits in CREDITS.txt)")

if __name__ == "__main__":
    main()
