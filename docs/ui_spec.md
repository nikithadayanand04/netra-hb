# Netra-Hb — UI design spec

## Who and what
- **User in the story:** an ASHA worker screening a child during a home visit, often outdoors, on a phone.
- **User at the lab evaluation:** an examiner with a few minutes. They should screen a sample patient in under 30 seconds, then check the results and the methods.
- **Primary job:** photo in → quality check → "Refer for Hb test" or "Normal", with reasons a non-expert understands.
- **Scope:** five pages for the lab evaluation, in English, ಕನ್ನಡ and हिंदी, in light (default) and dark mode. No referral slip, visit register or multi-site combined estimate (removed after P10b).

## The concept: the haemoglobin colour scale
Health workers already know the WHO Haemoglobin Colour Scale: a paper strip of reds, from pale blush to deep crimson, that a blood drop is matched against. Netra-Hb is built around a digital version of that strip.
- The strip is the visual spine of the app: it sits on the home screen, it is the result display, and its reds are the only strong colour in the interface.
- **Signature moment:** after analysis, a swatch of the patient's actual tissue colour lifts out of the photo, travels to the strip, and settles at its position, while the risk gauge fills; a thin marker drops to show the anaemia threshold.
- **One main animation per page:** Home, the strip in the hero illustration glows once; Screen, a scan line sweeps the measured area once per guided crop, then the result moment above. Everything else is still, and `prefers-reduced-motion` shows the final state with no motion.

## Colour tokens
| Token | Hex | Use |
|---|---|---|
| porcelain | `#F3F5F7` | page background (cool, clinical; never cream) |
| ink | `#1B2340` | text, headings, primary buttons (deep register-pen indigo) |
| slate | `#5B6475` | secondary text, axes, borders |
| pallor | `#F2C4C9` | pale tissue, soft highlights |
| haem | `#B3123A` | "Refer" state, anaemic class in charts, the strip's deep end |
| clear | `#1F7A6D` | "Normal" state, non-anaemic class in charts |

Hb strip gradient (low Hb → high Hb): `#F7E1E1 → #E9A3A8 → #CF5B6B → #A3153A → #6E0B24`.

Rules:
- Red appears only for blood and for the refer state. No red buttons, no red decoration.
- Charts use exactly two class colours: haem = anaemic, clear = normal. Everything else is slate.
- All text passes WCAG AA in both modes.
- Dark mode: background `#121624`, surface `#1B2133`, text `#E6E9F0`; haem and clear text are lightened (`#D17189`, `#4C958A`) because the base hues fail AA on the dark surface. Tokens live in the `.nh-dark` block of `app/style.css`; Streamlit widgets (inputs, tabs, slider, camera, uploader) are repainted from the tokens because the theme config is light.

## Type
- **Display: Bricolage Grotesque**, 600–700. Headings, the result word, big numbers.
- **Body and UI: Atkinson Hyperlegible**, 400/700. Designed for low-vision readability, which fits a field health tool.
- **Regional scripts:** Noto Sans Kannada and Noto Sans Devanagari as fallbacks in every font stack.
- All fonts are served locally from `app/static/fonts` (OFL); the app makes no network requests.
- Scale: 14 / 16 / 20 / 28 / 40 / 64 px. Result word at 64 px. Line length ≤ 70 characters. Sentence case everywhere.
- Avoid: all-caps labels, monospace labels, middle-dot meta strings, arrows in button text.

## Layout
Left-aligned, generous whitespace, one column on phone, two on laptop. Shapes follow meaning: the strip is a long rounded bar, photos are rounded 12 px, result panel is square-cornered with a thick left rule in its state colour. Not every block is a card; mix plain sections, the strip, and panels.

```
Home (laptop)
+--------------------------------------------------------------+
| Netra-Hb                          English | ಕನ್ನಡ | हिंदी  [Dark] |
| Home  Screen  Results  Insights  About  (each with a line icon) |
|                                                              |
| Needle-free anaemia screening     [ Start a screening ]      |
| from a photo of the eyelid,       [ Try a sample patient ]   |
| palm or nail.                                                |
|                                                              |
| [=========== Hb colour strip, gently lit ================]  |
|  6 g/dL                                          15 g/dL     |
|                                                              |
| How it works (a real 3-step sequence)                         |
|  1 Photograph   2 Quality check   3 Result + reasons          |
|                                                              |
| Results in brief (from outputs/results, honest numbers)       |
+--------------------------------------------------------------+

Screen: result (laptop)
+----------------------------+---------------------------------+
| [photo with tissue mask]   | Refer for Hb test               |
|  quality: light ok,        | (64px, haem rule on the left)   |
|  glare ok, sharp ok        | Likely anaemic · 78% (wide band)|
|                            | [strip with swatch + threshold] |
|                            | Why: eyelid is paler and less   |
|                            | red than most healthy children  |
|                            | Known limits                    |
+----------------------------+---------------------------------+
```

## Pages and features (5, top nav in this order)
1. **Home**: short hero with two actions ("Start a screening", "Try a sample patient"), the hero illustration with the colour strip, a 3-step illustrated how-it-works (a genuine sequence, so numbering is fine), and a link to the Results page. No numbers on Home.
2. **Screen**, sample patients first:
   - *Try a sample patient*: 6 cards (2 per site, mixed results) with thumbnail, site icon and age band; one click shows the result directly below the gallery.
   - *Or screen with your own photo* (secondary): age band (sets the WHO cut-off), then the sites in recommended order with a rank and photo guide each: 1 eyelid (most skin-tone robust), 2 nail, 3 palm. Camera or upload.
   - *Guided crop*: the user drags a tight box over only the pink inner eyelid, one nail bed or the palm centre; only the oval inscribed in the box is measured (an oval guide is drawn), and the crop is rescaled to the training images' scale. Photos with a clear background are found automatically.
   - *Silent checks*: makeup filter, light, glare, sharpness and the KNN unfamiliar-photo check run without showing numbers. A failed check shows one friendly line ("Please retake: daylight, no eye makeup, show only the inner eyelid.", per site) and keeps "See result" disabled. An unfamiliar photo or an age band outside 6–59 months shows a small "Low confidence" tag only.
   - *Result*: only the result word, the animated risk gauge, the swatch on the colour strip, 2–3 plain reasons with icons, and "Screening aid only. Confirm with a blood Hb test."
   - No dataset sizes, model names or interval numbers on Home or Screen; they live on Results, Insights and About.
3. **Results**: model comparison table (mean over 25 folds, 95% corrected CI) for the tuned syllabus models and the final soft vote; a model picker and threshold slider driving the 100-child icon grid ("Out of 100 children screened: 42 anaemic, 35 caught, 7 missed; 58 healthy, 24 sent for a test they didn't need"); ROC with the operating point and the confusion matrix. Saved out-of-fold predictions only (`oof_tuned.csv`, first repeat pooled).
4. **Insights**, four tabs:
   - *Data*: class balance by severity, Hb distribution with the cut-off, feature vs Hb (feature picker), raw vs grey-world correlation with Hb.
   - *Eye vs palm vs nail*: site table, equal-size (n = 220) comparison, learning curves, with the different-children / folder-label caveat.
   - *Clusters*: K-means elbow and silhouette, centroid swatches with mean Hb and % anaemic, purity against the majority baseline, palm and nail purity.
   - *Search*: algorithm comparison table, convergence chart (best score vs evaluations), honest nested re-evaluation (inner vs held-out score).
5. **About**: problem, datasets with citations, method and syllabus mapping, honest results, known limits, disclaimer.

## Visual language
- **Original SVG artwork only**, drawn in code in `app/art.py` (no stock images, no network): the Home hero (eye, palm and fingernail line art joined by the Hb strip), the three how-it-works steps (phone camera, quality check, result), the photo guides per site (finger pulling the lower eyelid, open palm, fingernails), a header illustration per Insights tab and for About, the About pipeline nodes and the tissue swatches.
- Illustrations are drawn per mode with the palette baked in and hold no text (an SVG image cannot use the page fonts); labels sit in the HTML around them.
- **One icon set:** 24 × 24, 1.8 stroke, round caps, used as CSS masks so icons follow the text colour (sites, steps, checks, tips, reasons, nav).
- A soft two-glow gradient and a faint paper grain sit behind every page, in both modes.

## Interaction and polish
- One orchestrated animation (the swatch). Other motion only responds to the user: the threshold slider updating the grid.
- `prefers-reduced-motion`: the swatch appears in place without travelling.
- Touch targets ≥ 44 px. Visible keyboard focus. Every chart has a one-line plain-language takeaway above it, computed from the data it shows.
- Every user-facing string lives in `app/strings.py` (`STRINGS`) in all three languages, with the same `{placeholders}`; a test enforces it. Home, the whole Screen flow, the nav and every page title and chart takeaway are translated; chart content, model names and the About prose stay English.
- Empty and error states give the next action: "No photo yet. Take one, upload one or pick a sample patient."
- Footer on every page: "Screening aid for health workers. Not a diagnosis. Confirm with a blood Hb test."

## Tech
- Streamlit multipage (`app/Home.py`, `app/pages/`), a theme in `.streamlit/config.toml`, and `app/style.css` injected once.
- Shared UI helpers in `app/ui.py`: strip, quality chips, known limits, chart (with takeaway), page and section titles. Screening logic in `app/screen_core.py` and `src/netra/screening.py`.
- The strip and the swatch animation are a small custom HTML/CSS/JS block via `st.components.v1.html`.
- Plotly for every chart, with a shared template using the tokens above.
- The app only reads from `outputs/`; it never retrains. Missing files show a clear message naming the script that creates them.
