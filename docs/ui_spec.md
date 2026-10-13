# Netra-Hb — UI design spec

## Who and what
- **User in the story:** an ASHA worker screening children and women during a home visit, often outdoors, on a phone.
- **User at the exhibition:** a judge with 3 minutes. They should screen a sample patient in under 30 seconds, then explore the science.
- **Primary job:** photo in → quality check → "Refer for Hb test" or "Normal", with reasons a non-expert understands.

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
- Dark mode: background `#121624`, text `#E6E9F0`; keep haem and clear and lighten them 10% only if contrast needs it.
- All text passes WCAG AA.

## Type
- **Display: Bricolage Grotesque** (Google Fonts), 600–700. Headings, the result word, big numbers.
- **Body and UI: Atkinson Hyperlegible** (Google Fonts), 400/700. Designed for low-vision readability, which fits a field health tool.
- **Regional scripts:** Noto Sans Kannada and Noto Sans Devanagari for the language toggle.
- Scale: 14 / 16 / 20 / 28 / 40 / 64 px. Result word at 64 px. Line length ≤ 70 characters. Sentence case everywhere.
- Avoid: all-caps labels, monospace labels, middle-dot meta strings, arrows in button text.

## Layout
Left-aligned, generous whitespace, one column on phone, two on laptop. Shapes follow meaning: the strip is a long rounded bar, photos are rounded 12 px, result panel is square-cornered with a thick left rule in its state colour. Not every block is a card; mix plain sections, the strip, and panels.

```
Home (laptop)
+--------------------------------------------------------------+
| Netra-Hb                          English | ಕನ್ನಡ | हिंदी  [Dark] |
|                                                              |
| Needle-free anaemia screening     [ Start a screening ]      |
| from a photo of the eyelid,       [ Try a sample patient ]   |
| palm or nail.                                                |
|                                                              |
| [=========== Hb colour strip, gently lit ================]  |
|  6 g/dL                                          15 g/dL     |
|                                                              |
| How it works (a real 3-step sequence)                         |
|  1 Photograph   2 Quality check   3 Result + referral slip    |
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
|                            | [ Add a palm photo ] [ Slip ]   |
+----------------------------+---------------------------------+
```

## Pages and features
1. **Home**: hero with the live strip, two actions, a 3-step how-it-works (a genuine sequence, so numbering is fine), a short honest results summary read from `outputs/results`.
2. **Screen (the core flow)**, as a guided visit:
   - Patient: optional name, age band (6–59 months / 5–11 / 12–14 / 15+ woman / 15+ man), which sets the WHO cut-off.
   - Choose site: eye, palm or nail, each with a simple line illustration showing how to take the photo (for the eye: gently pull down the lower eyelid, daylight, no flash).
   - Capture: `st.camera_input` or upload. Then click-to-select the tissue region with streamlit-image-coordinates (auto-detected if the image already has a transparent background).
   - **Photo quality gate**: three live checks using our cleaning module: light, glare and sharpness, each with a pass or retake state and one plain fix ("Too much glare. Turn away from the window and retake.").
   - **Result**: the signature swatch-to-strip moment, the result word, probability with its uncertainty band, severity band (with a caveat), and three plain-language reasons from feature contributions.
   - **Add another site**: adding palm or nail updates the combined estimate (label it "combined estimate, experimental").
   - **Referral slip**: a one-page PDF (fpdf2) with patient band, date, sites used, result, next step ("Visit the PHC for a finger-prick Hb test within 7 days"), and the disclaimer. Button text: "Download referral slip"; toast: "Referral slip downloaded".
   - **Visit register**: the session's screenings in a table (time, age band, site, result) with totals and "Export register (CSV)". In-session state only.
3. **How sure is it?** (the model lab): pick a model and drag the threshold. Show the trade-off as a **100-child icon grid**: "Out of 100 children screened: 42 anaemic, 34 caught, 8 missed; 58 healthy, 30 sent for a test they didn't need." Plus ROC with the operating point, and the confusion matrix. Uses saved out-of-fold predictions only.
4. **Eye, palm or nail?**: the site comparison and the equal-sample comparison, learning curves, and the simulated fusion result with its caveat.
5. **Lighting**: the same photo with raw colour vs grey-world-corrected colour, showing how correction erases redness (our finding), and an explanation of why we keep raw ratios.
6. **Patterns** (clustering): K-means clusters on a 2D projection; click a cluster to see its centroid swatch on the strip and its mean Hb.
7. **Protocol finder** (search): animate the search traces. Each algorithm's states as points on cost vs specificity, the path lighting up step by step; a table of best protocol, evaluations used and runtime per algorithm.
8. **About and limits**: data sources with citations, label noise, the 0.71 honest result, no Indian data yet, not a diagnosis.

## Interaction and polish
- One orchestrated animation (the swatch). Other motion only responds to the user: the slider updating the grid, a toast confirming the slip.
- `prefers-reduced-motion`: the swatch appears in place without travelling.
- Touch targets ≥ 44 px. Visible keyboard focus. Every chart has a one-line plain-language takeaway above it.
- Language toggle: all screening-flow strings in a dict for English, Kannada and Hindi. Science pages may stay in English.
- Empty and error states give the next action: "No photo yet. Take one or pick a sample patient."
- Preload 6 sample patients (2 eye, 2 palm, 2 nail; mixed results) in `app/samples/` so the demo never depends on a live camera.
- Footer on every page: "Screening aid for health workers. Not a diagnosis. Confirm with a blood Hb test."

## Tech
- Streamlit multipage (`app/Home.py`, `app/pages/`), a theme in `.streamlit/config.toml`, and `app/style.css` injected once.
- Shared UI helpers in `app/ui.py`: strip, result panel, quality chips, icon grid, toast, language strings.
- The strip and the swatch animation are a small custom HTML/CSS/JS block via `st.components.v1.html`.
- Plotly for every chart, with a shared template using the tokens above.
- The app only reads from `outputs/`; it never retrains. Missing files show a clear message naming the script that creates them.
