import html

import streamlit as st

import art
import ui

ui.setup_page("nav_home", "Home.py")
m = ui.mode()

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

# The page's one animation: the strip in the illustration glows once on load (still under reduced motion)
st.html(f'<div class="nh-hero-art">{art.img(art.hero(m), html.escape(ui.t("hero_art_alt")))}</div>'
        f'<p class="nh-actions-note">{html.escape(ui.t("strip_caption"))}</p>')

ui.spacer()
ui.section(ui.t("how_title"))
steps = "".join(
    f'<li class="nh-step-card">{art.img(art.step(name, m))}<div class="nh-step-head"><span class="nh-step-num">{i}</span>'
    f'<span class="nh-step-name">{html.escape(ui.t(f"step{i}_name"))}</span></div>'
    f'<p>{html.escape(ui.t(f"step{i}_text"))}</p></li>'
    for i, name in enumerate(("photo", "check", "result"), 1))
st.html(f'<ol class="nh-steps-art">{steps}</ol>')

ui.spacer()
ui.section(ui.t("brief_title"), ui.t("brief_lede"))


def pct(v: dict) -> tuple[int, int, int]:
    return round(v["value"] * 100), round(v["ci_low"] * 100), round(min(v["ci_high"], 1.0) * 100)


final = ui.read_result("final.json")
if final is None:
    ui.missing("results/final.json", "tune_models")
else:
    fm = final["headline"]["fold_mean"]
    sens, spec, auc = pct(fm["sensitivity"]), pct(fm["specificity"]), fm["roc_auc"]
    of = html.escape(ui.t("of_100"))
    auc_lo, auc_hi = f"{auc['ci_low']:.2f}", f"{auc['ci_high']:.2f}"
    st.html(
        '<div class="nh-stats">'
        f'<div class="nh-stat nh-stat-refer"><div class="nh-stat-num">{sens[0]}<small> {of}</small></div>'
        f'<p class="nh-stat-label">{html.escape(ui.t("stat_sens"))}</p>'
        f'<p class="nh-stat-ci">{html.escape(ui.t("stat_ci", lo=sens[1], hi=sens[2]))}</p></div>'
        f'<div class="nh-stat nh-stat-normal"><div class="nh-stat-num">{spec[0]}<small> {of}</small></div>'
        f'<p class="nh-stat-label">{html.escape(ui.t("stat_spec", n=100 - spec[0]))}</p>'
        f'<p class="nh-stat-ci">{html.escape(ui.t("stat_ci", lo=spec[1], hi=spec[2]))}</p></div>'
        f'<div class="nh-stat"><div class="nh-stat-num">{auc["value"]:.2f}</div>'
        f'<p class="nh-stat-label">{html.escape(ui.t("stat_auc"))}</p>'
        f'<p class="nh-stat-ci">{html.escape(ui.t("stat_ci", lo=auc_lo, hi=auc_hi))}</p></div>'
        '</div>')

sites = ui.read_result("sites.json")
notes = [f"<p>{ui.t('note_who')}</p>"]
if sites is not None:
    by_site = {row["site"]: row for row in sites["table"]}
    palm, nail = (f'{float(by_site[k]["roc_auc"].split()[0]):.2f}' for k in ("palm", "nail"))
    notes.append(f"<p>{ui.t('note_sites', palm=palm, nail=nail)}</p>")
notes.append(f"<p>{ui.t('note_meaning')}</p>")
st.html(f'<div class="nh-notes">{"".join(notes)}</div>')

ui.footer()
