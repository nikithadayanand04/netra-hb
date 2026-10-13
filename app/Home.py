import html

import streamlit as st

import ui

ui.setup_page("Home", "Home.py")

STEP_ICONS = {1: "eye", 2: "checks", 3: "slip"}

hero_text, hero_actions = st.columns([1.35, 1], gap="large", vertical_alignment="bottom")
with hero_text:
    st.html(f'<h1 class="nh-hero-title">{html.escape(ui.t("hero_title"))}</h1>'
            f'<p class="nh-lede">{html.escape(ui.t("hero_lede"))}</p>')
with hero_actions:
    if st.button(ui.t("start"), type="primary", width="stretch", key="home_start"):
        st.session_state["sample_mode"] = False
        st.switch_page("pages/1_Screen.py")
    if st.button(ui.t("try_sample"), type="secondary", width="stretch", key="home_sample"):
        st.session_state["sample_mode"] = True
        st.switch_page("pages/1_Screen.py")
    st.html(f'<p class="nh-actions-note">{html.escape(ui.t("actions_note"))}</p>')

ui.spacer(small=True)
ui.hb_strip(bar_height=40)
st.html(f'<p class="nh-actions-note">{html.escape(ui.t("strip_caption"))}</p>')

ui.spacer()
ui.section(ui.t("how_title"))
steps = "".join(
    f'<li class="nh-step"><div class="nh-step-head"><span class="nh-step-num">{i}</span>'
    f'<span class="nh-step-name">{html.escape(ui.t(f"step{i}_name"))}</span></div>'
    f'<p>{html.escape(ui.t(f"step{i}_text"))}</p><span class="nh-icon nh-icon-lg nh-icon-{STEP_ICONS[i]}" aria-hidden="true"></span></li>'
    for i in (1, 2, 3)
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
    ui.missing("final.json", "tune_models")
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
