import html

import streamlit as st

import ui

ui.setup_page("Home", "Home.py")

STEPS = [
    ("eye", "Photograph", "Gently pull down the lower eyelid, or show the palm or a nail, in daylight without flash."),
    ("checks", "Quality check", "Light, glare, sharpness and makeup are checked at once. If one fails, you get one "
                                "plain fix and retake."),
    ("slip", "Result", "Refer for Hb test or Normal, with the chance, its uncertainty band and three plain reasons."),
]

hero_text, hero_actions = st.columns([1.35, 1], gap="large", vertical_alignment="bottom")
with hero_text:
    st.html('<h1 class="nh-hero-title">Needle-free anaemia screening</h1>'
            '<p class="nh-lede">From one phone photo of the inner eyelid, palm or nail bed, Netra-Hb suggests whether '
            'to refer a child for a blood Hb test.</p>')
with hero_actions:
    if st.button("Start a screening", type="primary", width="stretch", key="home_start"):
        st.session_state["sample_mode"] = False
        st.switch_page("pages/1_Screen.py")
    if st.button("Try a sample patient", type="secondary", width="stretch", key="home_sample"):
        st.session_state["sample_mode"] = True
        st.switch_page("pages/1_Screen.py")
    st.html('<p class="nh-actions-note">Classical machine learning on colour features. No needle, no test strips.</p>')

ui.spacer(small=True)
ui.hb_strip(bar_height=40)
st.html('<p class="nh-actions-note">The haemoglobin colour scale. Paler tissue sits to the left, richer red to the '
        'right.</p>')

ui.spacer()
ui.section("How it works")
steps = "".join(
    f'<li class="nh-step"><div class="nh-step-head"><span class="nh-step-num">{i}</span>'
    f'<span class="nh-step-name">{html.escape(name)}</span></div>'
    f'<p>{html.escape(text)}</p><span class="nh-icon nh-icon-lg nh-icon-{icon}" aria-hidden="true"></span></li>'
    for i, (icon, name, text) in enumerate(STEPS, 1)
)
st.html(f'<ol class="nh-steps">{steps}</ol>')

ui.spacer()
ui.section("Results in brief",
           "Eye model on 220 children, tested with repeated patient-grouped cross-validation. "
           "Numbers are the mean over 25 held-out folds, with 95% intervals.")


def pct(m: dict) -> tuple[int, int, int]:
    return round(m["value"] * 100), round(m["ci_low"] * 100), round(min(m["ci_high"], 1.0) * 100)


final = ui.read_result("final.json")
if final is None:
    ui.missing("results/final.json", "tune_models")
else:
    fm = final["headline"]["fold_mean"]
    sens, spec, auc = pct(fm["sensitivity"]), pct(fm["specificity"]), fm["roc_auc"]
    st.html(
        '<div class="nh-stats">'
        f'<div class="nh-stat nh-stat-refer"><div class="nh-stat-num">{sens[0]}<small> of 100</small></div>'
        '<p class="nh-stat-label">anaemic children are sent for a blood test (sensitivity)</p>'
        f'<p class="nh-stat-ci">95% interval {sens[1]} to {sens[2]}</p></div>'
        f'<div class="nh-stat nh-stat-normal"><div class="nh-stat-num">{spec[0]}<small> of 100</small></div>'
        f'<p class="nh-stat-label">healthy children are correctly cleared; the other {100 - spec[0]} get a test '
        'they did not need (specificity)</p>'
        f'<p class="nh-stat-ci">95% interval {spec[1]} to {spec[2]}</p></div>'
        f'<div class="nh-stat"><div class="nh-stat-num">{auc["value"]:.2f}</div>'
        '<p class="nh-stat-label">ROC-AUC: how often an anaemic child scores above a healthy one (0.5 is chance)</p>'
        f'<p class="nh-stat-ci">95% interval {auc["ci_low"]:.2f} to {auc["ci_high"]:.2f}</p></div>'
        '</div>'
    )

sites = ui.read_result("sites.json")
notes = [
    "<p><strong>Who it was tested on.</strong> Children aged 6 to 59 months in Ghana (CP-AnemiC), "
    "with lab Hb and the WHO cut-off of 11 g/dL; 42% were anaemic. Not yet tested on Indian patients or adults.</p>"
]
if sites is not None:
    by_site = {row["site"]: row for row in sites["table"]}
    palm, nail = (f'{float(by_site[k]["roc_auc"].split()[0]):.2f}' for k in ("palm", "nail"))
    notes.append(
        f"<p><strong>Palm and nail.</strong> ROC-AUC {palm} for palm and {nail} for nail, on separate Ghana sets "
        "with folder labels (taken from file names, about 3% label noise). Different children, so this is not a "
        "fair head-to-head with the eye.</p>")
else:
    notes.append('<p class="nh-missing">Palm and nail results need <code>python -m scripts.compare_sites</code>.</p>')
notes.append("<p><strong>What this means.</strong> It catches most anaemic children but sends many healthy "
             "ones for a test too. That trade-off is deliberate for screening, and a blood test always decides.</p>")
st.html(f'<div class="nh-notes">{"".join(notes)}</div>')

ui.footer()
