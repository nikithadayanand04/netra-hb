from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
RESULTS_DIR = ROOT / "outputs" / "results"

PORCELAIN, INK, SLATE, PALLOR, HAEM, CLEAR = "#F3F5F7", "#1B2340", "#5B6475", "#F2C4C9", "#B3123A", "#1F7A6D"
STRIP_STOPS = ["#F7E1E1", "#E9A3A8", "#CF5B6B", "#A3153A", "#6E0B24"]
HB_MIN, HB_MAX = 6.0, 15.0

LIGHT = {"bg": PORCELAIN, "surface": "#FFFFFF", "text": INK, "muted": SLATE, "line": "#D3D8E0",
         "refer": HAEM, "normal": CLEAR, "grid": "#E1E5EB"}
DARK = {"bg": "#121624", "surface": "#1B2133", "text": "#E6E9F0", "muted": "#9AA3B5", "line": "#2E3650",
        "refer": "#D17189", "normal": "#4C958A", "grid": "#262D44"}

FONTS_URL = ("https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700"
             "&family=Bricolage+Grotesque:opsz,wght@12..96,600..700"
             "&family=Noto+Sans+Devanagari:wght@400;700&family=Noto+Sans+Kannada:wght@400;700&display=swap")
DISPLAY_FONT = "Bricolage Grotesque, Noto Sans Kannada, Noto Sans Devanagari, sans-serif"
BODY_FONT = "Atkinson Hyperlegible, Noto Sans Kannada, Noto Sans Devanagari, sans-serif"

LANGS = {"en": "English", "kn": "ಕನ್ನಡ", "hi": "हिंदी"}

# Screening-flow strings in all three languages. Science-page strings may be English only: t() falls back to "en".
STRINGS: dict[str, dict[str, str]] = {
    "dark": {"en": "Dark", "kn": "ಡಾರ್ಕ್", "hi": "डार्क"},
    "language": {"en": "Language", "kn": "ಭಾಷೆ", "hi": "भाषा"},
    "hero_title": {"en": "Needle-free anaemia screening", "kn": "ಸೂಜಿ ಇಲ್ಲದೆ ರಕ್ತಹೀನತೆ ತಪಾಸಣೆ",
                   "hi": "बिना सुई के एनीमिया जाँच"},
    "hero_lede": {
        "en": "From one phone photo of the inner eyelid, palm or nail bed, Netra-Hb tells a health worker "
              "whether to refer for a blood Hb test.",
        "kn": "ಕಣ್ಣಿನ ಒಳರೆಪ್ಪೆ, ಅಂಗೈ ಅಥವಾ ಉಗುರಿನ ಒಂದು ಫೋನ್ ಫೋಟೋದಿಂದ, ರಕ್ತದ Hb ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಬೇಕೇ "
              "ಎಂದು Netra-Hb ಆರೋಗ್ಯ ಕಾರ್ಯಕರ್ತರಿಗೆ ತಿಳಿಸುತ್ತದೆ.",
        "hi": "आँख की भीतरी पलक, हथेली या नाखून की एक फ़ोन फ़ोटो से Netra-Hb स्वास्थ्य कार्यकर्ता को "
              "बताता है कि खून की Hb जाँच के लिए भेजना है या नहीं।",
    },
    "start": {"en": "Start a screening", "kn": "ತಪಾಸಣೆ ಆರಂಭಿಸಿ", "hi": "जाँच शुरू करें"},
    "try_sample": {"en": "Try a sample patient", "kn": "ಮಾದರಿ ರೋಗಿಯೊಂದಿಗೆ ಪ್ರಯತ್ನಿಸಿ",
                   "hi": "नमूना मरीज़ के साथ आज़माएँ"},
    "actions_note": {"en": "No needle, no test strips. About a minute per child.",
                     "kn": "ಸೂಜಿ ಇಲ್ಲ, ಪರೀಕ್ಷಾ ಪಟ್ಟಿ ಇಲ್ಲ. ಪ್ರತಿ ಮಗುವಿಗೆ ಸುಮಾರು ಒಂದು ನಿಮಿಷ.",
                     "hi": "न सुई, न टेस्ट स्ट्रिप। हर बच्चे के लिए लगभग एक मिनट।"},
    "strip_caption": {
        "en": "The haemoglobin colour scale. Paler tissue sits to the left, richer red to the right.",
        "kn": "ಹಿಮೋಗ್ಲೋಬಿನ್ ಬಣ್ಣದ ಮಾಪಕ. ಬಿಳಿಚಿದ ಅಂಗಾಂಶ ಎಡಕ್ಕೆ, ಗಾಢ ಕೆಂಪು ಬಲಕ್ಕೆ.",
        "hi": "हीमोग्लोबिन रंग पैमाना। फीका ऊतक बाईं ओर, गहरा लाल दाईं ओर।",
    },
    "cutoff": {"en": "Anaemia cut-off", "kn": "ರಕ್ತಹೀನತೆ ಮಿತಿ", "hi": "एनीमिया सीमा"},
    "this_photo": {"en": "This photo", "kn": "ಈ ಫೋಟೋ", "hi": "यह फ़ोटो"},
    "strip_aria": {"en": "Haemoglobin colour scale from 6 to 15 g/dL",
                   "kn": "6 ರಿಂದ 15 g/dL ವರೆಗಿನ ಹಿಮೋಗ್ಲೋಬಿನ್ ಬಣ್ಣದ ಮಾಪಕ",
                   "hi": "6 से 15 g/dL तक हीमोग्लोबिन रंग पैमाना"},
    "how_title": {"en": "How it works", "kn": "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ", "hi": "यह कैसे काम करता है"},
    "step1_name": {"en": "Photograph", "kn": "ಫೋಟೋ ತೆಗೆಯಿರಿ", "hi": "फ़ोटो लें"},
    "step1_text": {
        "en": "Gently pull down the lower eyelid, or show the palm or a nail, in daylight without flash.",
        "kn": "ಕೆಳ ರೆಪ್ಪೆಯನ್ನು ನಿಧಾನವಾಗಿ ಕೆಳಗೆ ಎಳೆಯಿರಿ, ಅಥವಾ ಅಂಗೈ ಅಥವಾ ಉಗುರನ್ನು ತೋರಿಸಿ. ಹಗಲು ಬೆಳಕು, ಫ್ಲ್ಯಾಶ್ ಬೇಡ.",
        "hi": "निचली पलक को धीरे से नीचे खींचें, या हथेली या नाखून दिखाएँ। दिन की रोशनी, फ़्लैश नहीं।",
    },
    "step2_name": {"en": "Quality check", "kn": "ಗುಣಮಟ್ಟ ಪರಿಶೀಲನೆ", "hi": "गुणवत्ता जाँच"},
    "step2_text": {
        "en": "Light, glare and sharpness are checked at once. If one fails, you get one plain fix and retake.",
        "kn": "ಬೆಳಕು, ಹೊಳಪು ಮತ್ತು ಸ್ಪಷ್ಟತೆಯನ್ನು ತಕ್ಷಣ ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ. ಒಂದು ವಿಫಲವಾದರೆ, ಸರಳ ಸಲಹೆಯೊಂದಿಗೆ ಮತ್ತೆ ತೆಗೆಯಿರಿ.",
        "hi": "रोशनी, चमक और साफ़पन तुरंत जाँचे जाते हैं। कोई जाँच विफल हो तो एक आसान सुझाव मिलता है, फिर दोबारा लें।",
    },
    "step3_name": {"en": "Result and slip", "kn": "ಫಲಿತಾಂಶ ಮತ್ತು ಚೀಟಿ", "hi": "नतीजा और पर्ची"},
    "step3_text": {
        "en": "Refer for Hb test or Normal, with three reasons, and a referral slip to hand to the family.",
        "kn": "Hb ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಿ ಅಥವಾ ಸಾಮಾನ್ಯ, ಮೂರು ಕಾರಣಗಳೊಂದಿಗೆ, ಮತ್ತು ಕುಟುಂಬಕ್ಕೆ ನೀಡಲು ಶಿಫಾರಸು ಚೀಟಿ.",
        "hi": "Hb जाँच के लिए भेजें या सामान्य, तीन कारणों के साथ, और परिवार को देने के लिए रेफ़रल पर्ची।",
    },
    "refer": {"en": "Refer for Hb test", "kn": "Hb ಪರೀಕ್ಷೆಗೆ ಕಳುಹಿಸಿ", "hi": "Hb जाँच के लिए भेजें"},
    "normal": {"en": "Normal", "kn": "ಸಾಮಾನ್ಯ", "hi": "सामान्य"},
    "likely_anaemic": {"en": "Likely anaemic", "kn": "ರಕ್ತಹೀನತೆ ಇರುವ ಸಾಧ್ಯತೆ", "hi": "एनीमिया की संभावना"},
    "likely_normal": {"en": "Likely not anaemic", "kn": "ರಕ್ತಹೀನತೆ ಇಲ್ಲದಿರುವ ಸಾಧ್ಯತೆ",
                      "hi": "एनीमिया न होने की संभावना"},
    "prob_line": {"en": "{word}, {p}% chance", "kn": "{word}, {p}% ಸಾಧ್ಯತೆ", "hi": "{word}, {p}% संभावना"},
    "band_line": {"en": "Likely range {lo}–{hi}%", "kn": "ಸಂಭವನೀಯ ವ್ಯಾಪ್ತಿ {lo}–{hi}%",
                  "hi": "संभावित दायरा {lo}–{hi}%"},
    "why": {"en": "Why", "kn": "ಏಕೆ", "hi": "क्यों"},
    "severity_caveat": {
        "en": "Severity is a rough guide from colour only. Only a blood test gives the Hb level.",
        "kn": "ತೀವ್ರತೆ ಬಣ್ಣದಿಂದ ಮಾತ್ರ ಅಂದಾಜು. ರಕ್ತ ಪರೀಕ್ಷೆ ಮಾತ್ರ Hb ಮಟ್ಟವನ್ನು ನೀಡುತ್ತದೆ.",
        "hi": "गंभीरता केवल रंग से एक मोटा अनुमान है। Hb स्तर केवल खून की जाँच से पता चलता है।",
    },
    "q_light": {"en": "Light", "kn": "ಬೆಳಕು", "hi": "रोशनी"},
    "q_glare": {"en": "Glare", "kn": "ಹೊಳಪು", "hi": "चमक"},
    "q_sharp": {"en": "Sharpness", "kn": "ಸ್ಪಷ್ಟತೆ", "hi": "साफ़पन"},
    "q_ok": {"en": "ok", "kn": "ಸರಿ", "hi": "ठीक"},
    "q_retake": {"en": "retake", "kn": "ಮತ್ತೆ ತೆಗೆಯಿರಿ", "hi": "दोबारा लें"},
    "fix_light": {"en": "Too dark. Move into daylight and retake.",
                  "kn": "ತುಂಬಾ ಕತ್ತಲು. ಹಗಲು ಬೆಳಕಿಗೆ ಬನ್ನಿ ಮತ್ತು ಮತ್ತೆ ತೆಗೆಯಿರಿ.",
                  "hi": "बहुत अँधेरा है। दिन की रोशनी में आएँ और दोबारा लें।"},
    "fix_glare": {"en": "Too much glare. Turn away from the window and retake.",
                  "kn": "ಹೆಚ್ಚು ಹೊಳಪು. ಕಿಟಕಿಯಿಂದ ದೂರ ತಿರುಗಿ ಮತ್ತೆ ತೆಗೆಯಿರಿ.",
                  "hi": "बहुत चमक है। खिड़की से मुँह फेरें और दोबारा लें।"},
    "fix_sharp": {"en": "Blurred. Hold the phone still, tap to focus and retake.",
                  "kn": "ಮಸುಕಾಗಿದೆ. ಫೋನನ್ನು ಸ್ಥಿರವಾಗಿ ಹಿಡಿದು, ಫೋಕಸ್‌ಗೆ ತಟ್ಟಿ ಮತ್ತೆ ತೆಗೆಯಿರಿ.",
                  "hi": "धुंधला है। फ़ोन स्थिर रखें, फ़ोकस के लिए टैप करें और दोबारा लें।"},
    "no_photo": {"en": "No photo yet. Take one or pick a sample patient.",
                 "kn": "ಇನ್ನೂ ಫೋಟೋ ಇಲ್ಲ. ಒಂದನ್ನು ತೆಗೆಯಿರಿ ಅಥವಾ ಮಾದರಿ ರೋಗಿಯನ್ನು ಆರಿಸಿ.",
                 "hi": "अभी कोई फ़ोटो नहीं। एक फ़ोटो लें या नमूना मरीज़ चुनें।"},
    "screen_title": {"en": "Screen a patient", "kn": "ರೋಗಿಯ ತಪಾಸಣೆ", "hi": "मरीज़ की जाँच"},
    "slip_button": {"en": "Download referral slip", "kn": "ಶಿಫಾರಸು ಚೀಟಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
                    "hi": "रेफ़रल पर्ची डाउनलोड करें"},
    "slip_toast": {"en": "Referral slip downloaded", "kn": "ಶಿಫಾರಸು ಚೀಟಿ ಡೌನ್‌ಲೋಡ್ ಆಯಿತು",
                   "hi": "रेफ़रल पर्ची डाउनलोड हो गई"},
    "next_step": {"en": "Visit the PHC for a finger-prick Hb test within 7 days.",
                  "kn": "7 ದಿನಗಳ ಒಳಗೆ ಬೆರಳು ಚುಚ್ಚುವ Hb ಪರೀಕ್ಷೆಗಾಗಿ PHCಗೆ ಭೇಟಿ ನೀಡಿ.",
                  "hi": "7 दिनों के भीतर उँगली से Hb जाँच के लिए PHC जाएँ।"},
    "age_band": {"en": "Age band", "kn": "ವಯಸ್ಸಿನ ಗುಂಪು", "hi": "आयु वर्ग"},
    "age_6_59m": {"en": "6–59 months", "kn": "6–59 ತಿಂಗಳು", "hi": "6–59 महीने"},
    "age_5_11": {"en": "5–11 years", "kn": "5–11 ವರ್ಷ", "hi": "5–11 वर्ष"},
    "age_12_14": {"en": "12–14 years", "kn": "12–14 ವರ್ಷ", "hi": "12–14 वर्ष"},
    "age_15_woman": {"en": "15+ woman", "kn": "15+ ಮಹಿಳೆ", "hi": "15+ महिला"},
    "age_15_man": {"en": "15+ man", "kn": "15+ ಪುರುಷ", "hi": "15+ पुरुष"},
    "site_eye": {"en": "Eyelid", "kn": "ಕಣ್ಣಿನ ರೆಪ್ಪೆ", "hi": "पलक"},
    "site_palm": {"en": "Palm", "kn": "ಅಂಗೈ", "hi": "हथेली"},
    "site_nail": {"en": "Nail", "kn": "ಉಗುರು", "hi": "नाखून"},
    "combined": {"en": "Combined estimate, experimental", "kn": "ಸಂಯೋಜಿತ ಅಂದಾಜು, ಪ್ರಾಯೋಗಿಕ",
                 "hi": "संयुक्त अनुमान, प्रायोगिक"},
    "register": {"en": "Visit register", "kn": "ಭೇಟಿ ದಾಖಲೆ", "hi": "भ्रमण रजिस्टर"},
    "export_register": {"en": "Export register (CSV)", "kn": "ದಾಖಲೆ ರಫ್ತು ಮಾಡಿ (CSV)",
                        "hi": "रजिस्टर निर्यात करें (CSV)"},
    "footer": {
        "en": "Screening aid for health workers. Not a diagnosis. Confirm with a blood Hb test.",
        "kn": "ಆರೋಗ್ಯ ಕಾರ್ಯಕರ್ತರಿಗೆ ತಪಾಸಣಾ ಸಹಾಯಕ. ಇದು ರೋಗನಿರ್ಣಯವಲ್ಲ. ರಕ್ತದ Hb ಪರೀಕ್ಷೆಯಿಂದ ಖಚಿತಪಡಿಸಿ.",
        "hi": "स्वास्थ्य कार्यकर्ताओं के लिए जाँच सहायक। यह निदान नहीं है। खून की Hb जाँच से पुष्टि करें।",
    },
}

AGE_BANDS = {"age_6_59m": 11.0, "age_5_11": 11.5, "age_12_14": 12.0, "age_15_woman": 12.0, "age_15_man": 13.0}


def lang() -> str:
    return st.session_state.get("lang") or "en"


def is_dark() -> bool:
    return bool(st.session_state.get("dark", False))


def tokens() -> dict[str, str]:
    return DARK if is_dark() else LIGHT


def t(key: str, **fmt: Any) -> str:
    entry = STRINGS.get(key, {})
    text = entry.get(lang()) or entry.get("en") or key
    return text.format(**fmt) if fmt else text


def inject_css() -> None:
    css = (APP_DIR / "style.css").read_text(encoding="utf-8")
    if is_dark():
        css = css.replace(".nh-dark {", ":root {")
    st.html(f"<style>{css}</style>")


def setup_page(title: str) -> None:
    st.set_page_config(page_title=f"{title} | Netra-Hb", page_icon=":material/opacity:", layout="wide",
                       initial_sidebar_state="collapsed")
    st.session_state.setdefault("dark", st.context.theme.type == "dark")
    st.session_state.setdefault("lang", "en")
    inject_css()
    pio.templates.default = "netra_dark" if is_dark() else "netra"
    header()


def header() -> None:
    with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute",
                      key="nh_header"):
        st.html('<p class="nh-brand"><span class="nh-brand-mark" aria-hidden="true"></span>Netra-Hb</p>')
        with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="right",
                          width="content", gap="medium"):
            st.segmented_control(t("language"), list(LANGS), format_func=LANGS.get, key="lang", required=True,
                                 label_visibility="collapsed", persist_state="session")
            st.toggle(t("dark"), key="dark", persist_state="session")


def footer() -> None:
    st.html(f'<footer class="nh-footer">{html.escape(t("footer"))}</footer>')


def section(title: str, lede: str | None = None) -> None:
    body = f'<h2 class="nh-section-title">{html.escape(title)}</h2>'
    if lede:
        body += f'<p class="nh-section-lede">{html.escape(lede)}</p>'
    st.html(body)


def spacer(small: bool = False) -> None:
    st.html(f'<div class="{"nh-spacer-sm" if small else "nh-spacer"}"></div>')


def read_result(name: str) -> dict | None:
    path = RESULTS_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def missing(name: str, script: str) -> None:
    st.html(f'<p class="nh-missing">No results yet: <code>outputs/results/{html.escape(name)}</code> is missing. '
            f'Create it with <code>python -m scripts.{html.escape(script)}</code>.</p>')


def _hb_frac(hb: float) -> float:
    return min(max((hb - HB_MIN) / (HB_MAX - HB_MIN), 0.0), 1.0)


_STRIP_HTML = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="__FONTS__">
<style>
:root { --text: __TEXT__; --muted: __MUTED__; --bg: __BG__; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: transparent; color: var(--text);
  font-family: "Atkinson Hyperlegible", "Noto Sans Kannada", "Noto Sans Devanagari", sans-serif; }
.wrap { display: flex; align-items: flex-end; gap: 20px; padding: 4px 1px 0; }
.photo { position: relative; flex: none; width: var(--pw); }
.photo img { display: block; width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 12px; }
.photo .ring { position: absolute; width: 22px; height: 22px; margin: -11px 0 0 -11px; border-radius: 50%;
  border: 2px solid #fff; box-shadow: 0 0 0 1px rgba(27,35,64,.5); }
.scale { position: relative; flex: 1; min-width: 0; padding-top: var(--top); }
.bar { position: relative; height: var(--bh); border-radius: 999px; background: linear-gradient(90deg, __STOPS__);
  box-shadow: inset 0 0 0 1px rgba(27,35,64,.08); overflow: hidden; }
.bar::after { content: ""; position: absolute; inset: 0; border-radius: inherit;
  background: linear-gradient(180deg, rgba(255,255,255,.42) 0%, rgba(255,255,255,.08) 46%, rgba(0,0,0,0) 54%, rgba(0,0,0,.08) 100%); }
.cut { position: absolute; top: calc(var(--top) - 10px); height: calc(var(--bh) + 20px); width: 0;
  border-left: 2px solid var(--text); }
.cut span { position: absolute; top: calc(100% + 30px); left: 0; transform: translateX(var(--cx, -50%));
  white-space: nowrap; font-size: 14px; color: var(--text); font-weight: 700; }
.ticks { position: relative; height: 30px; margin-top: 2px; }
.tick { position: absolute; top: 0; width: 0; display: flex; flex-direction: column; align-items: center; }
.tick i { display: block; width: 1px; height: 7px; background: var(--muted); }
.tick b { white-space: nowrap; font-weight: 400; font-size: 14px; color: var(--muted); margin-top: 3px; font-variant-numeric: tabular-nums; }
.unit { position: absolute; left: 0; top: calc(var(--top) + var(--bh) + 40px); font-size: 14px; color: var(--muted); }
.tick.first b { transform: translateX(50%); }
.tick.last b { transform: translateX(-50%); }
.swatch { position: absolute; top: 0; width: 44px; margin-left: -22px; display: flex; flex-direction: column;
  align-items: center; will-change: transform; }
.chip { width: 44px; height: 44px; border-radius: 10px; border: 3px solid #fff;
  box-shadow: 0 6px 18px rgba(27,35,64,.28), 0 0 0 1px rgba(27,35,64,.18); }
.stem { width: 2px; height: calc(var(--top) - 50px); background: var(--text); opacity: .6; }
.swatch span { position: absolute; bottom: calc(100% + 4px); white-space: nowrap; font-size: 14px; font-weight: 700; }
.hidden { opacity: 0; }
</style></head><body>
<div class="wrap" role="img" aria-label="__ARIA__">
  __PHOTO__
  <div class="scale" id="scale">
    <div class="bar"></div>
    __CUT__
    __SWATCH__
    <div class="ticks">__TICKS__</div>
    <div class="unit">Hb, g/dL</div>
  </div>
</div>
<script>
(() => {
  const animate = __ANIMATE__;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const sw = document.getElementById("swatch"), cut = document.getElementById("cut");
  if (!sw || !animate || reduce) { if (sw) sw.classList.remove("hidden"); if (cut) cut.classList.remove("hidden"); return; }
  const ring = document.getElementById("ring");
  const end = sw.getBoundingClientRect();
  let dx, dy;
  if (ring) {
    const r = ring.getBoundingClientRect();
    dx = (r.left + r.width / 2) - (end.left + end.width / 2);
    dy = (r.top + r.height / 2) - (end.top + 22);
  } else { dx = -end.left + 12; dy = 6; }
  const travel = sw.animate([
    { transform: `translate(${dx}px, ${dy}px) scale(.35)`, opacity: 0 },
    { transform: `translate(${dx}px, ${dy - 18}px) scale(1.15)`, opacity: 1, offset: .28 },
    { transform: "translate(0, -6px) scale(1.05)", offset: .86 },
    { transform: "none", opacity: 1 }
  ], { duration: 1300, delay: 250, easing: "cubic-bezier(.3,.7,.2,1)", fill: "both" });
  sw.classList.remove("hidden");
  travel.finished.then(() => {
    cut.classList.remove("hidden");
    cut.animate([{ transform: "translateY(-14px)", opacity: 0 }, { transform: "none", opacity: 1 }],
                { duration: 320, easing: "cubic-bezier(.2,.8,.2,1)" });
  });
})();
</script></body></html>"""


def hb_strip(hb: float | None = None, swatch_rgb: tuple[int, int, int] | None = None, threshold: float = 11.0,
             photo_url: str | None = None, photo_point: tuple[float, float] = (0.5, 0.5),
             animate: bool = True, show_cutoff: bool = True, photo_width: int = 120, bar_height: int = 30) -> None:
    """The digital Hb colour scale. With hb and swatch_rgb, the tissue swatch lifts out of the photo (if given)
    and settles at its position; then the cut-off marker drops. prefers-reduced-motion shows the final state."""
    tk = tokens()
    has_swatch = hb is not None and swatch_rgb is not None
    top = 96 if has_swatch else 14
    photo = ""
    if photo_url:
        px, py = photo_point
        photo = (f'<div class="photo"><img src="{html.escape(photo_url)}" alt="">'
                 f'<div class="ring" id="ring" style="left:{px * 100:.1f}%;top:{py * 100:.1f}%"></div></div>')
    cut = ""
    if show_cutoff:
        cls = "cut hidden" if has_swatch and animate else "cut"
        cut = (f'<div class="{cls}" id="cut" style="left:{_hb_frac(threshold) * 100:.2f}%">'
               f'<span>{html.escape(t("cutoff"))} {threshold:g} g/dL</span></div>')
    swatch = ""
    if has_swatch:
        r, g, b = (int(c) for c in swatch_rgb)
        swatch = (f'<div class="swatch{" hidden" if animate else ""}" id="swatch" style="left:{_hb_frac(hb) * 100:.2f}%">'
                  f'<span>{html.escape(t("this_photo"))}</span>'
                  f'<div class="chip" style="background:rgb({r},{g},{b})"></div><div class="stem"></div></div>')
    ticks = "".join(
        f'<div class="tick{" first" if v == HB_MIN else " last" if v == HB_MAX else ""}" '
        f'style="left:{_hb_frac(v) * 100:.2f}%"><i></i><b>{v:g}</b></div>'
        for v in range(int(HB_MIN), int(HB_MAX) + 1))
    doc = (_STRIP_HTML.replace("__TICKS__", ticks).replace("__FONTS__", FONTS_URL).replace("__TEXT__", tk["text"])
           .replace("__MUTED__", tk["muted"]).replace("__BG__", tk["bg"]).replace("__STOPS__", ", ".join(STRIP_STOPS))
           .replace("__ARIA__", html.escape(t("strip_aria"))).replace("__PHOTO__", photo).replace("__CUT__", cut)
           .replace("__SWATCH__", swatch).replace("__ANIMATE__", "true" if animate else "false"))
    doc = doc.replace("<style>", f"<style>:root{{--top:{top}px;--bh:{bar_height}px;--pw:{photo_width}px}}", 1)
    label_room = 60
    height = max(top + bar_height + label_room + 6, photo_width + 12 if photo_url else 0)
    components.html(doc, height=height)


def result_panel(refer: bool, prob: float, band: tuple[float, float], reasons: list[str],
                 severity: str | None = None) -> None:
    state = "refer" if refer else "normal"
    word = t("likely_anaemic") if refer else t("likely_normal")
    items = "".join(f"<li>{html.escape(r)}</li>" for r in reasons[:3])
    sev = f'<p class="nh-result-prob">{html.escape(severity)}</p>' if severity else ""
    st.html(f'<section class="nh-result {state}" aria-live="polite">'
            f'<p class="nh-result-word">{html.escape(t(state))}</p>'
            f'<p class="nh-result-prob">{html.escape(t("prob_line", word=word, p=round(prob * 100)))}</p>'
            f'<p class="nh-result-band">{html.escape(t("band_line", lo=round(band[0] * 100), hi=round(band[1] * 100)))}</p>'
            f'{sev}<h4>{html.escape(t("why"))}</h4><ul>{items}</ul>'
            f'<p class="nh-result-caveat">{html.escape(t("severity_caveat"))}</p></section>')


_ICON_OK = '<span class="nh-icon nh-icon-sm nh-icon-ok" aria-hidden="true"></span>'
_ICON_RETAKE = '<span class="nh-icon nh-icon-sm nh-icon-retake" aria-hidden="true"></span>'


def quality_chips(checks: dict[str, bool]) -> bool:
    """checks maps 'light' / 'glare' / 'sharp' to pass (True) or retake (False). Returns True if all pass."""
    chips, fixes = [], []
    for name, ok in checks.items():
        status = t("q_ok") if ok else t("q_retake")
        chips.append(f'<span class="nh-chip{"" if ok else " retake"}">{_ICON_OK if ok else _ICON_RETAKE}'
                     f'{html.escape(t("q_" + name))}: {html.escape(status)}</span>')
        if not ok:
            fixes.append(f"<li>{html.escape(t('fix_' + name))}</li>")
    fix_html = f'<ul class="nh-fixes">{"".join(fixes)}</ul>' if fixes else ""
    st.html(f'<div class="nh-chips" role="status">{"".join(chips)}</div>{fix_html}')
    return not fixes


def toast(key: str, icon: str = ":material/check_circle:") -> None:
    st.toast(t(key), icon=icon)


def empty_state(key: str = "no_photo") -> None:
    st.html(f'<div class="nh-empty">{html.escape(t(key))}</div>')


def _template(tk: dict[str, str]) -> go.layout.Template:
    axis = dict(gridcolor=tk["grid"], linecolor=tk["line"], zerolinecolor=tk["line"], tickcolor=tk["line"],
                tickfont=dict(color=tk["muted"], size=14), title=dict(font=dict(color=tk["muted"], size=14)),
                showline=True, ticks="outside")
    return go.layout.Template(layout=dict(
        font=dict(family=BODY_FONT, color=tk["text"], size=14),
        title=dict(font=dict(family=DISPLAY_FONT, size=20, color=tk["text"]), x=0, xanchor="left"),
        colorway=[tk["refer"] if tk is DARK else HAEM, tk["normal"] if tk is DARK else CLEAR, tk["muted"]],
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=axis, yaxis=axis,
        legend=dict(font=dict(color=tk["text"], size=14), bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(font=dict(family=BODY_FONT, size=14), bgcolor=tk["surface"], bordercolor=tk["line"]),
        margin=dict(l=56, r=16, t=48, b=48),
        colorscale=dict(sequential=[[i / 4, c] for i, c in enumerate(STRIP_STOPS)]),
    ))


pio.templates["netra"] = _template(LIGHT)
pio.templates["netra_dark"] = _template(DARK)


def class_color(anaemic: bool) -> str:
    tk = tokens()
    return (tk["refer"] if anaemic else tk["normal"]) if is_dark() else (HAEM if anaemic else CLEAR)


def chart(fig: go.Figure, takeaway: str) -> None:
    st.html(f'<p class="nh-section-lede" style="margin-bottom:0.25rem">{html.escape(takeaway)}</p>')
    fig.update_layout(template="netra_dark" if is_dark() else "netra")
    st.plotly_chart(fig, config={"displayModeBar": False})
