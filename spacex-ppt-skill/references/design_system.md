# Design System Reference

Detailed guide for building a faithful SpaceX-roadshow-style deck. Read this
before authoring `deck.html`. Layout snippets live in `assets/template.html`.

## Table of contents
- [The non-negotiable rules](#the-non-negotiable-rules)
- [Canvas & slide structure](#canvas--slide-structure)
- [The scrim (most important technique)](#the-scrim-most-important-technique)
- [Layout catalog — pick by content shape](#layout-catalog--pick-by-content-shape)
- [Image strategy & treatment](#image-strategy--treatment)
- [Typography classes](#typography-classes)
- [Rendering & troubleshooting](#rendering--troubleshooting)

## The non-negotiable rules
What makes the look work is restraint and consistency, not complexity.

1. **Pure black background** (`#000`). Never dark gray, never a color.
2. **Text is only white or gray.** No brand accent color, no colored highlights,
   no colored icons. All color in the deck comes from photographs.
3. **Headlines: UPPERCASE, light weight (300), wide tracking.** This single
   treatment is ~80% of the resemblance. Do not bold headlines.
4. **One photograph per slide, full-bleed**, faded into the black with a scrim
   so text sits on solid black. Never put text directly on a busy photo.
5. **Generous margins and negative space.** When unsure, remove an element.
6. **Thin 1px rules** (`rgba(255,255,255,.22)`) divide content — never boxes,
   borders, drop shadows, or rounded corners.
7. **Few words.** Short declarative phrases. Big numbers do the talking.

## Canvas & slide structure
- Canvas is **1920 × 1080** (16:9). One `<section class="slide">` = one page.
- Never nest `<section>` inside a slide (the renderer splits on that tag).
- Layer order inside a slide (by `z-index`):
  ```
  <section class="slide">
    <img class="bg ...">        <!-- z1: full-bleed photo -->
    <div class="scrim ...">     <!-- z2: black gradient over the photo -->
    <div class="pad"> ... </div><!-- z3: the content, in the margin box -->
    <div class="footer"> ... </div> <!-- z4: logo + page number -->
  </section>
  ```
- `.pad` is the content box with page margins; it's `flex-direction:column`.
  Constrain text slides with `style="max-width:46-52%"` so copy stays on the
  black side, opposite the photo's subject.

## The scrim (most important technique)
The scrim is a black gradient laid over the photo so white text stays readable.
Match the scrim direction to where the photo's subject sits and where text goes:

| Photo subject on… | Text on… | Use |
|---|---|---|
| right | left | `scrim--l` + `bg bg--right` |
| left | right | `scrim--r` + `bg bg--left` |
| bottom band | top | `scrim--b` (strengthen stops as needed) |
| whole frame, busy | over it | `scrim--full` and/or `scrim--vignette` |
| chart left / photo right | left | `scrim--seam` (hard vertical black panel) |

Stack scrims freely (e.g. `scrim--vignette` + `scrim--b` on a cover). To tune,
override inline: `style="background:linear-gradient(90deg,#000 0%,#000 30%,rgba(0,0,0,0) 70%)"`.
Rule of thumb: the text column must fall entirely within the solid-black part of
the gradient. If text looks muddy, push the solid stop further (e.g. 24%→34%).

## Layout catalog — pick by content shape
Each maps to a labeled section in `assets/template.html`. Copy, then swap text
and image paths.

| # | Layout | Use when the content is… |
|---|---|---|
| 1 | Cover | the title slide |
| 2 | Section divider | a chapter break between topics |
| 3 | Split text/photo | a narrative point, 1–3 short paragraphs |
| 4 | Stat stack + photo | 3–4 headline metrics, each with a caption |
| 5 | Metric columns | parallel pillars with **short** metric values (`cols-2/3/4/5/6`) |
| 5b | Product/spec cards | a matrix of items each with several **multi-word** specs |
| 6 | Label/value table | a spec sheet / summary of fields |
| 7 | Numbered list + photo | a process or ranked set of principles |
| 8 | Full-bleed + bullets | a punchy list of advantages over a hero photo |
| 9 | Image grid (6-up) | categories / use cases, one image each |
| 10 | Bar chart on black | one clean quantitative comparison |
| 11 | Chart + photo split | a chart that still wants a hero image |
| 12 | Closing | the final "thank you" slide |

Deck rhythm: alternate dense slides (tables, columns, charts) with airy ones
(section dividers, big-stat, full-bleed). Don't run three busy slides in a row.

**Columns vs cards** — the common mistake: a "product matrix" where each item has
several text specs. Do NOT cram multi-word values into `metric__val` (big,
right-aligned numbers) — they wrap mid-phrase and look broken. Use **layout 5b
(cards)** for text specs; reserve metric columns (layout 5) for short values
(numbers, percentages, ≤1 word). Set the column count to the item count:
`cols-4` for four products, etc. (counts 2–6 are defined).

## Capacity & overflow (avoid 吞字 / clipped text)
Slides are a fixed 1920×1080 with `overflow:hidden`, so anything past the edge is
**silently cut off**. The renderer now detects this and prints a
`⚠ CONTENT OVERFLOW` warning naming each clipped slide and by how many pixels —
**never deliver a deck with an overflow warning unresolved.** Rough capacity per
slide (at default sizes):
- Body copy: ≤ ~6 lines total. Stats: ≤ 4. Table rows: ≤ 6. Numbered items: ≤ 6.
- Metric columns: ≤ 4 metrics per column; pick the column count = item count.
- Cards (`cards-2`): ≤ 4 cards, ≤ 4 specs each.

When a slide overflows, fix it by (in order): cut words → split across more
columns → switch metric columns to cards → move content onto a second slide.
**Do not shrink the page margins** to fit more in.

## Chinese / CJK text
The bundled Latin fonts have no Chinese glyphs, so CJK falls back per-glyph to a
light Chinese face (`Noto Sans SC` / `Microsoft YaHei`, declared in the font
stack) to match the thin Latin headlines. Notes:
- Keep headlines short — Chinese characters are wide; a 6–8 character headline is
  plenty at the default 72px.
- Control line breaks: bind tokens that must stay together with `&nbsp;`
  (e.g. `3.5寸屏&nbsp;+&nbsp;OV2640`) or wrap them in `<span class="nowrap">`.
- For fully portable rendering on a machine without these fonts, bundle a light
  CJK font and add an `@font-face` — otherwise rely on the system fonts above.

## Image strategy & treatment
Cohesion comes from the image SET, not any single photo. Two levers:

**1. Pick ONE natural visual theme and stick to it** for the whole deck.
**Default to dramatic natural-world photography** — this is what creates the
cinematic look. Strong, proven themes:
- **ocean / sea / waves / aerial coastline** (a reliable favorite)
- **desert dunes**, **mountains / alpine**, **glaciers / ice**, **fog / clouds**
- **night sky / stars / aurora**, **aerial earth / topography**
- **canyons**, **forest canopy from above**, **storms**

Avoid generic corporate/office, abstract 3D renders, gradients, isolated product
shots, and busy stock photos — they break the aesthetic. If the deck's topic is
abstract (software, finance), still wrap it in a natural theme (e.g. ocean or
aerial earth) rather than reaching for literal tech imagery. Consistent subject +
consistent color family is what reads as "one deck."

**2. Let `fetch_images.py` manufacture cohesion in post.** It darkens + slightly
desaturates every photo and prefers darker candidates (room for white text).
```
python scripts/fetch_images.py --query "ocean horizon aerial" --count 6 --out images
```
Useful flags:
- `--orientation landscape|portrait` — portrait suits split/numbered layouts.
- `--darken 0.72` (lower = darker), `--saturation 0.85` (lower = more muted).
- `--duotone "#0c1622"` — maps the whole image toward one color for maximum
  cohesion (strong effect; try on a mixed-source set). Keep the SAME hex deck-wide.
- `--prefer dark` (default) vs `--prefer any`.

Query tips: add mood/lighting words — "dark", "aerial", "horizon", "minimal",
"fog", "dusk" — to pull moodier, emptier frames with negative space.

Credits land in `images/CREDITS.txt`. Pexels asks that attribution travel with
the deck; keep that file alongside the output or add a small credits line.

## Typography classes
- `.headline` / `.headline--xl` / `.headline--sm` — uppercase light titles.
- `.headline--sentence` — sentence-case variant (cover title, soft openers).
- `.eyebrow` — small tracked label above a headline (e.g. "N OF 1").
- `.body` / `.body--bright` — gray paragraph copy; cap at `max-width:46ch`.
- `.stat__num` + `.stat__label` + `.stat__rule` — big metric block.
- `.colhead` + `.metric`/`.metric__label`/`.metric__val` — column metrics.
- `.row`/`.row__label`/`.row__value` — table rows.
- `.numitem`/`.numitem__n`/`.numitem__txt` — numbered list.
- `.bullet` — large light bullet for the full-bleed list.
- `.footnote` — tiny gray source/notes line.
Fonts are bundled (`assets/fonts/Saira.ttf`, `Archivo.ttf`) and referenced by
`@font-face`; rendering is fully offline.

## Rendering & troubleshooting
```
python scripts/render_deck.py path/to/deck.html --out path/to/out --scale 2
```
- Outputs `slide_001.png …` plus a combined `<deck>.pdf`. `--png-only` skips PDF.
- `--scale` is the device pixel ratio: **2 = 3840×2160 (4K), the default** and
  right for screen/projector; 3 ≈ 5760×3240 for large-format print; 1.3 = lighter
  files for quick review.

**Resolution & output quality:**
- The **PNGs are the lossless master** output (sharpest). The **PDF embeds those
  same pixels but JPEG-encoded**, so it is marginally softer at the same
  resolution — control it with `--pdf-quality` (default 92; raise toward 95 for
  print, lower for smaller files). For the crispest possible artifact, hand out
  the PNGs.
- Pexels `original` photos are typically 6000–8000px and get **downscaled** into
  the 4K canvas, so there is no upscaling blur. Clarity problems almost always
  mean the wrong source size was used — `fetch_images.py` already uses `original`.
- Do not judge sharpness from a downscaled preview/thumbnail; open the full-size
  PNG.
- Renderer auto-finds Chrome/Edge; override with `CHROME_PATH` env var.

Common issues:
- **Text muddy over a photo** → strengthen/extend the scrim (see scrim section).
- **Photo subject cropped wrong** → set `bg--left`/`bg--right` or inline
  `object-position`.
- **Image too bright/clashing** → re-fetch with lower `--darken`, or add
  `--duotone`.
- **Content overflows the slide** (renderer prints `⚠ CONTENT OVERFLOW`) → see
  "Capacity & overflow" above; cut words, add columns, or split the slide. Never
  shrink margins. Re-render until no warning remains.
- **Long values wrap mid-phrase** → use cards (5b) instead of metric columns, and
  bind tokens with `&nbsp;` or `.nowrap`.
- **Photo looks low-res / soft** → `fetch_images.py` already saves the Pexels
  `original` (full resolution); just render at `--scale 2`. Don't downscale
  sources.
- **Black backgrounds render white** → already handled via
  `--default-background-color`; ensure the slide has `class="slide"`.
