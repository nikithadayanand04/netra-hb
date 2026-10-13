import html

import streamlit as st

import ui

ui.setup_page("Screen")

st.html(f'<h1 class="nh-section-title" style="font-size:var(--fs-40)">{html.escape(ui.t("screen_title"))}</h1>')
ui.spacer(small=True)
ui.empty_state()
ui.footer()
