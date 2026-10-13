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
# No dataset sizes, model names or intervals here: those live on Results, Insights and About
st.html(f'<p class="nh-section-lede">{html.escape(ui.t("home_results_lede"))}</p>')
st.page_link("pages/2_Results.py", label=ui.t("home_results_link"))

ui.footer()
