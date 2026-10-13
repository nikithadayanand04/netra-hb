import hashlib
import html

import numpy as np
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

import art
import screen_core as core
import ui
from netra import screening

ui.setup_page("nav_screen", "pages/1_Screen.py")
ss = st.session_state
t = ui.t
ss.setdefault("scr_age", ui.TRAINED_BAND)
if ss.scr_age not in ui.AGE_BANDS:          # sessions from before the age bands were keyed
    ss.scr_age = ui.TRAINED_BAND
ss.setdefault("scr_site", None)
ss.setdefault("scr_img", None)
ss.setdefault("scr_result", None)
ss.setdefault("scr_sample_next", 0)
ss.setdefault("scr_animated", set())
ss.setdefault("scr_scanned", set())

SITE_ORDER = ("eye", "nail", "palm")      # recommended order: the eyelid is the most skin-tone robust
SITE_ICON = {"eye": "eye", "palm": "palm", "nail": "nail"}
TIPS = {"eye": (("light", "tip_daylight"), ("noflash", "tip_noflash"), ("makeup", "tip_nomakeup")),
        "palm": (("light", "tip_daylight"), ("noflash", "tip_noflash"), ("hand", "tip_flat")),
        "nail": (("light", "tip_daylight"), ("noflash", "tip_noflash"), ("nopolish", "tip_nopolish"))}
REASON_ICON = {"redness": "drop", "lightness": "halfsun", "blood_index": "blood", "red_share": "pie", "tone": "palette"}
m = ui.mode()


def cutoff() -> float:
    return ui.AGE_BANDS[ss.scr_age]


def scroll_to(anchor: str) -> None:
    st.iframe(f"<script>const e = window.parent.document.getElementById('{anchor}');"
              "if (e) e.scrollIntoView({behavior: 'instant', block: 'start'});</script>", height=1, tab_index=-1)


def choose_site(site: str) -> None:
    if ss.scr_site != site or (ss.scr_img or {}).get("sample"):   # a site click always leaves sample mode
        ss.scr_img, ss.scr_result = None, None
        ss.pop("scr_seen", None)
    ss.scr_site = site


def set_image(rgb: np.ndarray, alpha: np.ndarray | None, sig: str, sample: dict | None = None) -> None:
    if sample is not None and sample["whole_image_is_tissue"]:
        tissue, how = np.ones(rgb.shape[:2], bool), "whole"
    else:
        tissue = screening.auto_tissue(rgb, alpha)
        how = "auto" if tissue is not None else None
    ss.scr_img = {"rgb": rgb, "alpha": alpha, "sig": sig, "sample": sample, "tissue": tissue, "how": how,
                  "box": None, "last_click": None}
    ss.scr_result = None


def run_analysis() -> None:
    img = ss.scr_img
    photo = screening.analyse_photo(img["rgb"], img["tissue"], ss.scr_site)
    # A sample photo is in the training set, where the model has seen it; show its out-of-fold score instead
    res = core.analyse(ss.scr_site, photo, p_override=img["sample"]["oof_p"] if img["sample"] else None)
    res |= {"sample": img["sample"], "id": f"{ss.scr_site}-{img['sig']}-{img['box']}"}
    ss.scr_result = res
    ss.scr_scroll = "nh-result"


def load_sample(i: int) -> None:
    sample = core.samples()[i]
    ss.scr_age = sample["age_band"]
    ss.scr_site = sample["site"]
    ss.pop("scr_seen", None)
    rgb, alpha = core.load_sample(sample)
    set_image(rgb, alpha, f"sample-{sample['id']}", {**sample, "n": i + 1})
    run_analysis()
    ss.scr_sample_next = (i + 1) % len(core.samples())


def low_confidence(res: dict) -> bool:
    return bool(res["familiarity"]["unfamiliar"]) or ss.scr_age != ui.TRAINED_BAND


# ---------------------------------------------------------------- page
ui.page_title(t("screen_title"), t("screen_lede_samples"))
if core.bundles() is None:
    ui.missing("models/screen_eye.joblib", "build_screen_models")
    ui.footer()
    st.stop()

if ss.pop("sample_mode", False) and core.samples():   # "Try a sample patient" on Home
    load_sample(ss.scr_sample_next)


# ---------------------------------------------------------------- 1. sample patients (the main path)
ui.section(t("gallery_title"), t("gallery_lede"))
with st.container(horizontal=True, wrap=True, gap="small", key="nh_samples"):
    for i, s in enumerate(core.samples()):
        with st.container(width=160, gap="small", key=f"nh_sample_{i}"):
            rgb, alpha = core.load_sample(s)
            st.html(f'<div class="nh-sample-card"><img class="nh-sample-img" alt="" src="{core.sample_thumb(rgb, alpha)}">'
                    f'<span class="nh-sample-badge">{ui.icon(SITE_ICON[s["site"]])}</span>'
                    f'<p class="nh-sample-meta"><b>{html.escape(t("sample_n", n=i + 1))}</b>'
                    f'<span>{html.escape(t("site_" + s["site"]))}</span></p>'
                    f'<p class="nh-sample-meta"><span>{html.escape(t(s["age_band"]))}</span></p></div>')
            st.button(t("load_sample"), key=f"scr_sample_{i}", width="stretch", on_click=load_sample, args=(i,))


# ---------------------------------------------------------------- result (directly under the gallery)
@st.cache_data(show_spinner=False, max_entries=64)
def reasons_for(site: str, feats_key: tuple, refer: bool) -> list[dict]:
    return screening.reasons(core.bundles()[site], dict(feats_key), refer)


def plain_reasons(res: dict, refer: bool) -> list[tuple[str, str]]:
    """2 or 3 reasons: the ones that point the way of the result first; a care note when none do."""
    rs = reasons_for(res["site"], res["feats_key"], refer)
    agree = [r for r in rs if r["agrees"]]
    if not agree:
        return [("alert", t("reasons_none_refer" if refer else "reasons_none_normal"))] + \
               [(REASON_ICON[r["group"]], core.reason_text(res["site"], r)) for r in rs[:2]]
    shown = agree[:3] if len(agree) >= 2 else agree + [r for r in rs if not r["agrees"]][:1]
    return [(REASON_ICON[r["group"]], core.reason_text(res["site"], r)) for r in shown]


res = ss.scr_result
if res is not None:
    ui.spacer(small=True)
    c = cutoff()
    refer = res["position"] < c
    state = "refer" if refer else "normal"
    animate = res["id"] not in ss.scr_animated
    ss.scr_animated.add(res["id"])
    st.html('<span id="nh-result"></span>')
    with st.container(key=f"nh_result_{state}"):
        head, gauge_col = st.columns([2.4, 1], vertical_alignment="center")
        with head:
            tag = (f'<span class="nh-conf" role="status">{ui.icon("alert", "nh-icon-sm")}{html.escape(t("low_conf"))}</span>'
                   if low_confidence(res) else "")
            st.html(f'<div class="nh-result-head" aria-live="polite">{tag}'
                    f'<p class="nh-result-word">{html.escape(t(state))}</p></div>')
        with gauge_col:
            ui.gauge(res["p"], refer, animate=animate)
        ui.hb_strip(hb=float(np.clip(res["position"], ui.HB_MIN, ui.HB_MAX)), swatch_rgb=res["swatch"], threshold=c,
                    photo_url=res["thumb"], photo_point=res["thumb_point"], animate=animate, photo_width=88,
                    bar_height=26)
        items = "".join(f'<li>{ui.icon(i)}<span>{html.escape(text)}</span></li>' for i, text in plain_reasons(res, refer))
        st.html(f'<div class="nh-result-body"><h4>{html.escape(t("why"))}</h4><ul class="nh-reasons">{items}</ul>'
                f'<p class="nh-result-caveat">{html.escape(t("result_footer"))}</p></div>')


# ---------------------------------------------------------------- 2. your own photo (secondary)
def take_input(src: str, f) -> None:
    if f is None:
        return
    data = f.getvalue()
    sig = f"{src}-{hashlib.sha1(data).hexdigest()[:12]}"
    seen = ss.setdefault("scr_seen", {})
    if seen.get(src) == sig:   # only a new capture or upload replaces the photo, not every rerun
        return
    seen[src] = sig
    got = core.decode(data)
    if got is None:
        ui.note(t("bad_image"), warn=True)
        return
    set_image(*got, sig)


def guided_crop(img: dict, click: dict) -> None:
    """A tight box (a tap gives a small default box); only the oval inscribed in it is measured."""
    h, w = img["rgb"].shape[:2]
    sx, sy = w / click["width"], h / click["height"]
    if "x1" in click and abs(click["x2"] - click["x1"]) > 6 and abs(click["y2"] - click["y1"]) > 6:
        x1, y1, x2, y2 = (int(click[k] * (sx if k[0] == "x" else sy)) for k in ("x1", "y1", "x2", "y2"))
    else:
        cx, cy = int(click.get("x", click.get("x1", 0)) * sx), int(click.get("y", click.get("y1", 0)) * sy)
        r = int(0.12 * min(h, w))
        x1, y1, x2, y2 = cx - r, cy - r // 2, cx + r, cy + r // 2
    x1, x2 = sorted((int(np.clip(x1, 0, w - 1)), int(np.clip(x2, 0, w - 1))))
    y1, y2 = sorted((int(np.clip(y1, 0, h - 1)), int(np.clip(y2, 0, h - 1))))
    region = screening.oval_region(img["rgb"].shape, x1, y1, x2, y2)
    img["box"] = (x1, y1, x2, y2)
    img["tissue"] = region if region.sum() >= 200 else None
    ss.scr_result = None


def photo_panel(img: dict) -> None:
    site = ss.scr_site
    if img["how"] is None:     # camera or upload with a real background: the guided crop
        shown = core.overlay(core.on_black(img["rgb"], img["alpha"]), img["tissue"], None, box=img["box"])
        click = streamlit_image_coordinates(shown, key=f"scr_click_{img['sig']}", width="stretch",
                                            cursor="crosshair", image_format="JPEG", jpeg_quality=88,
                                            click_and_drag=True)
        if click and click.get("unix_time") != img["last_click"]:   # a resize re-sends the old click
            img["last_click"] = click.get("unix_time")
            guided_crop(img, click)
            st.rerun()
        ui.note(t("crop_done") if img["tissue"] is not None else t("crop_" + site))
    if img["tissue"] is None:
        return
    photo = screening.analyse_photo(img["rgb"], img["tissue"], site)
    if photo is None:
        ui.note(t("retake_" + site), warn=True)
        return
    key = f"{img['sig']}-{img['box']}"
    st.html(f'<h3 class="nh-sub">{html.escape(t("measured_title"))}</h3>')
    ui.scan_view(core.measured_preview(photo), height=260, animate=key not in ss.scr_scanned)
    ss.scr_scanned.add(key)
    # makeup filter, light, glare and sharpness run silently: one friendly line if any fails
    ok = all(v["ok"] for v in photo.checks.values())
    ui.note(t("photo_ok") if ok else t("retake_" + site), warn=not ok)
    st.button(t("analyse"), type="primary", disabled=not ok, key="scr_analyse", on_click=run_analysis)


ui.spacer()
ui.section(t("own_title"), t("own_lede"))
left, right = st.columns([1.3, 1], gap="large")
with left:
    st.segmented_control(t("age_band"), list(ui.AGE_BANDS), format_func=t, key="scr_age", required=True)
    if ss.scr_age != ui.TRAINED_BAND:
        ui.note(t("cutoff_note"))
with right:
    c = cutoff()
    st.html(f'<div class="nh-cutoff"><p class="nh-cutoff-label">{html.escape(t("cutoff_title"))}</p>'
            f'<p class="nh-cutoff-num">{c:g}<small> g/dL</small></p>'
            f'<p class="nh-cutoff-text">{html.escape(t("cutoff_text", c=f"{c:g}"))}</p></div>')

ui.spacer(small=True)
cols = st.columns(3, gap="large")
for rank, (col, site) in enumerate(zip(cols, SITE_ORDER), 1):
    on = ss.scr_site == site and not (ss.scr_img or {}).get("sample")
    with col, st.container(key=f"nh_site_{site}{'_on' if on else ''}"):
        tips = "".join(f"<li>{ui.icon(i, 'nh-icon-sm')}{html.escape(t(k))}</li>" for i, k in TIPS[site])
        badge = f'<span class="nh-rec">{html.escape(t("recommended"))}</span>' if rank == 1 else ""
        st.html(f'{art.img(art.guide(site, m), cls="nh-guide-img")}'
                f'<h3 class="nh-site-name"><span class="nh-rank">{rank}</span>{ui.icon(SITE_ICON[site])}'
                f'{html.escape(t("site_" + site))}{badge}</h3>'
                f'<p class="nh-site-rank">{html.escape(t("rank_" + site))}</p>'
                f'<p class="nh-site-how">{html.escape(t("how_" + site))}</p><ul class="nh-tips">{tips}</ul>')
        st.button(t("selected") if on else t("use_site", site=t("site_" + site)), key=f"scr_site_{site}",
                  width="stretch", type="primary" if on else "secondary", on_click=choose_site, args=(site,))

if ss.scr_site is not None and not (ss.scr_img or {}).get("sample"):
    ui.spacer(small=True)
    left, right = st.columns([1, 1.15], gap="large")
    with left:
        cam_tab, up_tab = st.tabs([t("tab_camera"), t("tab_upload")])
        cam_key, up_key = f"scr_cam_{ss.scr_site}", f"scr_up_{ss.scr_site}"
        with cam_tab:
            take_input(cam_key, st.camera_input(t("camera_label"), key=cam_key))
        with up_tab:
            take_input(up_key, st.file_uploader(t("upload_label"), type=["jpg", "jpeg", "png"], key=up_key))
    with right:
        if ss.scr_img is None or ss.scr_img.get("sample"):
            ui.empty_state("no_photo")
        else:
            photo_panel(ss.scr_img)

if anchor := ss.pop("scr_scroll", None):
    scroll_to(anchor)
ui.footer()
