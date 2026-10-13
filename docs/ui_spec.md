# Netra-Hb — UI design spec

## Who and what
- **User in the story:** an ASHA worker screening a child during a home visit, often outdoors, on a phone.
- **User at the lab evaluation:** an examiner with a few minutes. They should screen a sample patient in under 30 seconds, then check the results and the methods.
- **Primary job:** photo in → quality check → "Refer for Hb test" or "Normal", with reasons a non-expert understands.
- **Scope:** only what the lab evaluation needs. English only, light mode only. No language toggle, dark mode, referral slip, visit register or multi-site combined estimate (removed after P10b).

## The concept: the haemoglobin colour scale
Health workers already know the WHO Haemoglobin Colour Scale: a paper strip of reds, from pale blush to deep crimson, that a blood drop is matched against. Netra-Hb is built around a digital version of that strip.
- The strip is the visual spine of the app: it sits on the home screen, it is the result display, and its reds are the only strong colour in the interface.
- **Signature moment (the one animation):** after analysis, a swatch of the patient's actual tissue colour lifts out of the photo, travels to the strip, and settles at its position. A thin marker drops to show the anaemia threshold. Everything else in the UI is calm and still.

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
- All text passes WCAG AA.

## Type
- **Display: Bricolage Grotesque** (Google Fonts), 600–700. Headings, the result word, big numbers.
- **Body and UI: Atkinson Hyperlegible** (Google Fonts), 400/700. Designed for low-vision readability, which fits a field health tool.
- Scale: 14 / 16 / 20 / 28 / 40 / 64 px. Result word at 64 px. Line length ≤ 70 characters. Sentence case everywhere.
- Avoid: all-caps labels, monospace labels, middle-dot meta strings, arrows in button text.

## Layout
Left-aligned, generous whitespace, one column on phone, two on laptop. Shapes follow meaning: the strip is a long rounded bar, photos are rounded 12 px, result panel is square-cornered with a thick left rule in its state colour. Not every block is a card; mix plain sections, the strip, and panels.

```
Home (laptop)
+--------------------------------------------------------------+
| Netra-Hb                                                     |
| Home  Screen  Results  Insights  About                       |
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
1. **Home**: short hero with two actions ("Start a screening", "Try a sample patient"), the colour strip, a 3-step how-it-works (a genuine sequence, so numbering is fine), and a short honest results summary read from `outputs/results/final.json` and `sites.json`.
2. **Screen**: one scrolling page in three numbered steps.
   - *Patient and site*: age band (6–59 months / 5–11 / 12–14 / 15+ woman / 15+ man) sets the WHO cut-off; site cards for eyelid, palm, nail, each with a line illustration of how to take the photo.
   - *Photo*: `st.camera_input`, upload, or one of 6 sample patients from `app/samples/` (2 per site, mixed results; shown with their out-of-fold score). Tissue is auto-detected from a transparent or black background, otherwise the user taps (region grow) or drags a box. A zoomed "Pixels measured" preview shows exactly which pixels count.
   - *Photo check*: light, glare, sharpness and, for the eye, makeup or lashes (dark, low-saturation pixels removed; more than 15% removed fails). Each failure gives one plain fix; "See result" stays disabled until all pass.
   - *Result*: the swatch-to-strip animation, the result word, probability with its uncertainty band (Wilson interval of out-of-fold children with similar scores), a severity line for the eye with its caveat, three plain-language reasons, a "Low confidence" note when the KNN unfamiliar-photo check fires or the age band is outside 6–59 months, the next step, and the Known limits box.
3. **Results**: model comparison table (mean over 25 folds, 95% corrected CI) for the tuned syllabus models and the final soft vote; a model picker and threshold slider driving the 100-child icon grid ("Out of 100 children screened: 42 anaemic, 35 caught, 7 missed; 58 healthy, 24 sent for a test they didn't need"); ROC with the operating point and the confusion matrix. Saved out-of-fold predictions only (`oof_tuned.csv`, first repeat pooled).
4. **Insights**, four tabs:
   - *Data*: class balance by severity, Hb distribution with the cut-off, feature vs Hb (feature picker), raw vs grey-world correlation with Hb.
   - *Eye vs palm vs nail*: site table, equal-size (n = 220) comparison, learning curves, with the different-children / folder-label caveat.
   - *Clusters*: K-means elbow and silhouette, centroid swatches with mean Hb and % anaemic, purity against the majority baseline, palm and nail purity.
   - *Search*: algorithm comparison table, convergence chart (best score vs evaluations), honest nested re-evaluation (inner vs held-out score).
5. **About**: problem, datasets with citations, method and syllabus mapping, honest results, known limits, disclaimer.

## Interaction and polish
- One orchestrated animation (the swatch). Other motion only responds to the user: the threshold slider updating the grid.
- `prefers-reduced-motion`: the swatch appears in place without travelling.
- Touch targets ≥ 44 px. Visible keyboard focus. Every chart has a one-line plain-language takeaway above it, computed from the data it shows.
- Empty and error states give the next action: "No photo yet. Take one, upload one or pick a sample patient."
- Footer on every page: "Screening aid for health workers. Not a diagnosis. Confirm with a blood Hb test."

## Tech
- Streamlit multipage (`app/Home.py`, `app/pages/`), a theme in `.streamlit/config.toml`, and `app/style.css` injected once.
- Shared UI helpers in `app/ui.py`: strip, quality chips, known limits, chart (with takeaway), page and section titles. Screening logic in `app/screen_core.py` and `src/netra/screening.py`.
- The strip and the swatch animation are a small custom HTML/CSS/JS block via `st.components.v1.html`.
- Plotly for every chart, with a shared template using the tokens above.
- The app only reads from `outputs/`; it never retrains. Missing files show a clear message naming the script that creates them.
