---
name: spacex-ppt-skill
description: >-
  Create minimalist, cinematic presentation decks in the style of the SpaceX IPO
  roadshow — pure-black slides, full-bleed photography faded into black with
  gradient scrims, uppercase light-weight headlines, and big white stat numbers.
  Use whenever the user wants a presentation/slide deck/pitch deck in a "SpaceX
  style", "minimalist black", "cinematic", "roadshow", or "Apple-keynote-like"
  aesthetic, or asks to turn an outline, topic, or content into such slides. The
  skill fetches and color-grades cohesive theme photography from Pexels and
  renders the deck to PDF + PNGs via headless Chrome.
---

# SpaceX-Style Deck

Turn a topic or outline into a cinematic, minimalist black deck. The output is an
HTML deck rendered to **PDF + per-slide PNGs** (not an editable .pptx — by design,
for pixel-perfect fidelity).

## How the look works (read this first)
The aesthetic is **restraint + consistency**: pure-black slides, one full-bleed
photo per slide faded into black with a **gradient scrim**, **UPPERCASE light
headlines** with wide tracking, white stat numbers, thin 1px rules, lots of
negative space, and **no accent color** (all color comes from the photos). Full
rules, the scrim technique, and the layout catalog are in
**`references/design_system.md`** — read it before authoring slides.

## Workflow

### 1. Establish content + ONE visual theme
Get the deck's content (topic, outline, or raw notes) and pick a **single photo
theme** that runs through the whole deck. **Default to dramatic natural-world
photography** — ocean/coastline, desert, mountains, glaciers, fog, night sky,
aerial earth — which is what produces the cinematic look. Avoid generic
corporate/office and abstract 3D stock (it breaks the aesthetic); even for an
abstract topic, wrap it in a natural theme. One theme + one color family is what
makes it cohere. If the theme isn't obvious, propose one (ocean is a safe pick)
and confirm.

### 2. Outline the slides and assign layouts
Draft the slide sequence. For each slide, choose a layout from the catalog in
`references/design_system.md` (cover, section divider, split text/photo, stat
stack, metric columns, **product cards**, table, numbered list, full-bleed
bullets, image grid, bar chart, chart+photo, closing). For a "matrix" of items
with multi-word specs, use **product cards** (not metric columns — long values
wrap badly there). Alternate dense and airy slides; keep words few.

### 3. Fetch cohesive imagery
Count how many photos the deck needs, then fetch them in one theme. The script
darkens + desaturates and prefers darker frames so white text reads:
```
python scripts/fetch_images.py --query "<theme + mood words>" --count <n> \
    --orientation landscape --out <deckdir>/images
```
Use `--orientation portrait` for split/numbered layouts, and `--duotone "#0c1622"`
(same hex deck-wide) if a mixed set needs stronger unification. See the
"Image strategy" section of the reference for query and treatment tips.

**API key (first run):** the script needs a Pexels key. If none is configured it
exits with instructions. When that happens, tell the user to create a **free**
key at **https://www.pexels.com/api/** (instant, ~1 min) and paste it into
`scripts/pexels_key.txt` (or set the `PEXELS_API_KEY` env var). The key is a
secret — never commit it or share a packaged `.skill` that contains a real key;
distribute with the placeholder `pexels_key.txt` and let each user add their own.

### 4. Assemble the deck
Copy `assets/template.html` to `<deckdir>/deck.html` and adjust the stylesheet
link so it resolves (e.g. point `<link>` at this skill's `assets/css/deck.css`,
or copy the `assets/` folder next to the deck). Keep `images/` and `logo.svg`
paths resolvable. Then, for each planned slide, copy the matching
`<section class="slide">` from the template and swap in real text and image
paths. Delete unused layouts; duplicate the ones you reuse. **Never nest
`<section>` inside a slide.** Obey the non-negotiable rules — if tempted to add a
color, a box, or a third paragraph, don't.

### 5. Render
```
python scripts/render_deck.py <deckdir>/deck.html --out <deckdir>/out --scale 2
```
Produces `out/slide_*.png` and `out/deck.pdf`. The renderer auto-detects clipped
content and prints `⚠ CONTENT OVERFLOW` for any slide whose text/elements run
past the edge — **you must resolve every overflow warning before delivering**
(cut words, add columns, switch to cards, or split the slide). Then inspect the
PNGs and fix any muddy-text issues (strengthen the scrim, re-crop the photo) —
see the troubleshooting section of the reference.

### 6. Deliver
Give the user the PDF and PNG folder. Keep `images/CREDITS.txt` with the output
(Pexels attribution).

## Bundled resources
- `assets/css/deck.css` — the complete design system (compose with its classes; don't fight it).
- `assets/template.html` — renderable gallery of all 12 layouts; the copy-paste source.
- `assets/fonts/`, `assets/logo.svg` — bundled fonts (offline) and corner mark.
- `scripts/fetch_images.py` — Pexels fetch + color-grade for cohesion.
- `scripts/render_deck.py` — HTML → PNG/PDF via headless Chrome.
- `references/design_system.md` — rules, scrim guide, layout catalog, troubleshooting.
