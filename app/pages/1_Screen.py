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

SITE_ICON = {"eye": "eye", "palm": "palm", "nail": "nail"}
TIPS = {"eye": (("light", "tip_daylight"), ("noflash", "tip_noflash"), ("makeup", "tip_nomakeup")),
        "palm": (("light", "tip_daylight"), ("noflash", "tip_noflash"), ("hand", "tip_flat")),
        "nail": (("light", "tip_daylight"), ("noflash", "tip_noflash"), ("nopolish", "tip_nopolish"))}
REASON_ICON = {"redness": "drop", "lightness": "halfsun", "blood_index": "blood", "red_share": "pie", "tone": "palette"}


def cutoff() -> float:
    return ui.AGE_BANDS[ss.scr_age]


def scroll_to(anchor: str) -> None:
    st.iframe(f"<script>const e = window.parent.document.getElementById('{anchor}');"
              "if (e) e.scrollIntoView({behavior: 'instant', block: 'start'});</script>", height=1, tab_index=-1)


def choose_site(site: str) -> None:
    if ss.scr_site != site:
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
                  "point": None, "box": None, "last_click": None}
    ss.scr_result = None


def run_analysis() -> None:
    img = ss.scr_img
    photo = screening.analyse_photo(img["rgb"], img["tissue"], ss.scr_site)
    # A sample photo is in the training set, where the model has seen it; show its out-of-fold score instead
    res = core.analyse(ss.scr_site, photo, p_override=img["sample"]["oof_p"] if img["sample"] else None)
    rgb, tissue, alpha = core.display_size(img["rgb"], img["tissue"], img["alpha"])
    # transparent where there is no photo (auto / cropped samples), so it sits right in both modes
    res |= {"sample": img["sample"], "id": f"{ss.scr_site}-{img['sig']}",
            "photo": core.png_url(core.overlay(rgb, tissue, dim=img["how"] is None), alpha)}
    ss.scr_result = res
    ss.scr_scroll = "nh-result"


def load_sample(i: int) -> None:
    sample = core.samples()[i]
    ss.scr_age = sample["age_band"]
    choose_site(sample["site"])
    rgb, alpha = core.load_sample(sample)
    set_image(rgb, alpha, f"sample-{sample['id']}", {**sample, "n": i + 1})
    run_analysis()
    ss.scr_sample_next = (i + 1) % len(core.samples())


def low_confidence(res: dict) -> list[str]:
    why = ["unfamiliar"] if res["familiarity"]["unfamiliar"] else []
    return why + (["age_outside"] if ss.scr_age != ui.TRAINED_BAND else [])


def step_head(n: int, title: str, lede: str | None = None, anchor: str | None = None, todo: bool = False) -> None:
    a = f' id="{anchor}"' if anchor else ""
    lede_html = f'<p class="nh-section-lede">{html.escape(lede)}</p>' if lede else ""
    st.html(f'<h2 class="nh-section-title nh-step-title{" nh-step-todo" if todo else ""}"{a}>'
            f'<span class="nh-step-n">{n}</span>{html.escape(title)}</h2>{lede_html}')


# ---------------------------------------------------------------- page
ui.page_title(t("screen_title"), t("screen_lede"))
if core.bundles() is None:
    ui.missing("models/screen_eye.joblib", "build_screen_models")
    ui.footer()
    st.stop()

if ss.pop("sample_mode", False) and core.samples():   # "Try a sample patient" on Home
    load_sample(ss.scr_sample_next)

m = ui.mode()

# ---------------------------------------------------------------- 1. patient and site
step_head(1, t("step_patient"))
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
for col, site in zip(cols, core.SITES):
    with col, st.container(key=f"nh_site_{site}{'_on' if ss.scr_site == site else ''}"):
        tips = "".join(f"<li>{ui.icon(i, 'nh-icon-sm')}{html.escape(t(k))}</li>" for i, k in TIPS[site])
        st.html(f'{art.img(art.guide(site, m), cls="nh-guide-img")}'
                f'<h3 class="nh-site-name">{ui.icon(SITE_ICON[site])}{html.escape(t("site_" + site))}</h3>'
                f'<p class="nh-site-how">{html.escape(t("how_" + site))}</p><ul class="nh-tips">{tips}</ul>'
                f'<p class="nh-site-data">{html.escape(t("tested_" + site))}</p>')
        on = ss.scr_site == site
        st.button(t("selected") if on else t("use_site", site=t("site_" + site)), key=f"scr_site_{site}",
                  width="stretch", type="primary" if on else "secondary", on_click=choose_site, args=(site,))


# ---------------------------------------------------------------- 2. photo
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


def sample_gallery() -> None:
    ui.note(t("samples_lede"))
    with st.container(horizontal=True, wrap=True, gap="small", key="nh_samples"):
        for i, s in enumerate(core.samples()):
            with st.container(width=158, gap="small", key=f"nh_sample_{i}"):
                rgb, alpha = core.load_sample(s)
                st.html(f'<div class="nh-sample-card"><img class="nh-sample-img" alt="" src="{core.sample_thumb(rgb, alpha)}">'
                        f'<span class="nh-sample-badge">{ui.icon(SITE_ICON[s["site"]])}</span>'
                        f'<p class="nh-sample-meta"><b>{html.escape(t("sample_n", n=i + 1))}</b>'
                        f'<span>{html.escape(t("site_" + s["site"]))}</span></p>'
                        f'<p class="nh-sample-meta"><span>{html.escape(t(s["age_band"]))}</span></p></div>')
                st.button(t("load_sample"), key=f"scr_sample_{i}", width="stretch", on_click=load_sample, args=(i,),
                          help=f'{t("sample_n", n=i + 1)}: {t("site_" + s["site"])}')


def select_tissue(img: dict, click: dict) -> None:
    """A tap grows a region of similar colour; a drag of more than a few pixels selects that box."""
    h, w = img["rgb"].shape[:2]
    sx, sy = w / click["width"], h / click["height"]
    if "x1" in click:
        x1, y1, x2, y2 = (int(click[k] * (sx if k[0] == "x" else sy)) for k in ("x1", "y1", "x2", "y2"))
    else:
        x1 = x2 = int(click["x"] * sx)
        y1 = y2 = int(click["y"] * sy)
    if abs(x2 - x1) > 6 and abs(y2 - y1) > 6:
        region = screening.box_region(img["rgb"].shape, x1, y1, x2, y2)
        img["box"], img["point"] = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)), None
    else:
        x, y = int(np.clip(x1, 0, w - 1)), int(np.clip(y1, 0, h - 1))
        region = screening.grow_region(img["rgb"], x, y)
        img["point"], img["box"] = (x, y), None
    img["tissue"] = region if region.sum() >= 200 else None
    ss.scr_result = None


def photo_panel(img: dict) -> None:
    noun = core.noun(ss.scr_site)
    if img["how"] in ("auto", "whole"):
        ui.note(t("tissue_" + img["how"]))
    else:
        shown = core.overlay(core.on_black(img["rgb"], img["alpha"]), img["tissue"], img["point"], box=img["box"])
        click = streamlit_image_coordinates(shown, key=f"scr_click_{img['sig']}", width="stretch",
                                            cursor="crosshair", image_format="JPEG", jpeg_quality=88,
                                            click_and_drag=True)
        if click and click.get("unix_time") != img["last_click"]:   # a resize re-sends the old click
            img["last_click"] = click.get("unix_time")
            select_tissue(img, click)
            st.rerun()
        if img["tissue"] is None and (img["point"] or img["box"]):
            ui.note(t("tissue_small", site=noun), warn=True)
        elif img["tissue"] is None:
            ui.note(t("tissue_drag", site=noun))
        else:
            ui.note(t("tissue_selected"))

    photo = screening.analyse_photo(img["rgb"], img["tissue"], ss.scr_site) if img["tissue"] is not None else None
    if photo is None:
        st.html(f'<h3 class="nh-sub">{html.escape(t("quality_title"))}</h3>')
        ui.note(t("quality_wait"))
        return
    # Analysis view: measured tissue in colour, removed pixels grey; the scan line sweeps once per selection
    key = f"{img['sig']}-{img['point']}-{img['box']}"
    removed = 1 - photo.mask.sum() / max(photo.tissue.sum(), 1)
    st.html(f'<h3 class="nh-sub">{html.escape(t("preview_title"))}</h3>')
    ui.scan_view(core.measured_preview(photo), height=300, animate=key not in ss.scr_scanned)
    ss.scr_scanned.add(key)
    ui.note(t("preview_text", pct=round(removed * 100)))
    st.html(f'<h3 class="nh-sub">{html.escape(t("quality_title"))}</h3>')
    ok = ui.quality_chips({k: v["ok"] for k, v in photo.checks.items()})
    if ok:
        ui.note(t("quality_pass"))
    st.button(t("analyse"), type="primary", disabled=not ok, key="scr_analyse", on_click=run_analysis)


ui.spacer()
if ss.scr_site is None:
    step_head(2, t("step_photo_todo"), todo=True)
    ui.note(t("choose_first"))
    sample_gallery()
else:
    step_head(2, t("step_photo", site=core.noun(ss.scr_site)), t("how_" + ss.scr_site))
    left, right = st.columns([1, 1.15], gap="large")
    with left:
        cam_tab, up_tab, sample_tab = st.tabs([t("tab_camera"), t("tab_upload"), t("tab_sample")])
        cam_key, up_key = f"scr_cam_{ss.scr_site}", f"scr_up_{ss.scr_site}"
        with cam_tab:
            take_input(cam_key, st.camera_input(t("camera_label"), key=cam_key))
        with up_tab:
            take_input(up_key, st.file_uploader(t("upload_label"), type=["jpg", "jpeg", "png"], key=up_key))
        with sample_tab:
            sample_gallery()
    with right:
        if ss.scr_img is None:
            ui.empty_state("no_photo")
        else:
            photo_panel(ss.scr_img)


# ---------------------------------------------------------------- 3. result
@st.cache_data(show_spinner=False, max_entries=64)
def reasons_for(site: str, feats_key: tuple, refer: bool) -> list[dict]:
    return screening.reasons(core.bundles()[site], dict(feats_key), refer)


def severity_text(res: dict, refer: bool) -> str:
    if res["site"] != "eye":
        return t("sev_none_ghana")
    if not refer:
        return t("sev_none")
    sev = screening.severity(res["position"], cutoff())
    return t("sev_line", sev=t("sev_" + sev), hb=f"{res['position']:.1f}", mae=f"{res['hb_mae']:.1f}")


res = ss.scr_result
if res is not None:
    ui.spacer()
    step_head(3, t("step_result"), anchor="nh-result")
    c = cutoff()
    refer = res["position"] < c
    state = "refer" if refer else "normal"
    animate = res["id"] not in ss.scr_animated
    ss.scr_animated.add(res["id"])
    left, right = st.columns([1, 1.45], gap="large")
    with left:
        st.html(f'<img class="nh-photo" alt="" src="{res["photo"]}">')
        ui.quality_chips({k: v["ok"] for k, v in res["checks"].items()})
        if res["sample"]:
            s = res["sample"]
            truth = (t("truth_hb", hb=f"{s['hb']:.1f}") if s["hb"] is not None else
                     t("truth_folder", label=t("word_anaemic" if s["label"] else "word_not_anaemic")))
            ui.note(f'{t("sample_banner", n=s["n"], site=core.noun(s["site"]))} {truth}')
        swatches = [("this", res["swatch"], "swatch_this"), ("", res["typical"]["healthy"], "swatch_healthy"),
                    ("", res["typical"]["anaemic"], "swatch_anaemic")]
        chips = "".join(f'<div class="nh-swatch {cls}">{art.img(art.swatch_chip(rgb, m))}<span>{html.escape(t(k))}</span></div>'
                        for cls, rgb, k in swatches)
        st.html(f'<h3 class="nh-sub">{html.escape(t("swatch_title"))}</h3><div class="nh-swatches">{chips}</div>')
    with right, st.container(key=f"nh_result_{state}"):
        lo, hi = res["band"]
        word = t("likely_anaemic") if refer else t("likely_normal")
        head, gauge_col = st.columns([2.3, 1], vertical_alignment="center")
        with head:
            st.html(f'<div class="nh-result-head" aria-live="polite"><p class="nh-result-word">{html.escape(t(state))}</p>'
                    f'<p class="nh-result-prob">{html.escape(t("prob_line", word=word, p=round(res["p"] * 100)))}</p>'
                    f'<p class="nh-result-band">{html.escape(t("band_explain", lo=round(lo * 100), hi=round(hi * 100)))}</p></div>')
        with gauge_col:
            ui.gauge(res["p"], refer, animate=animate)
        why_low = low_confidence(res)
        if why_low:
            items = "".join(f"<li>{html.escape(t(k))}</li>" for k in why_low)
            st.html(f'<p class="nh-conf" role="status">{ui.icon("alert", "nh-icon-sm")}{html.escape(t("low_conf"))}</p>'
                    f'<ul class="nh-conf-why">{items}</ul>')
        ui.hb_strip(hb=float(np.clip(res["position"], ui.HB_MIN, ui.HB_MAX)), swatch_rgb=res["swatch"], threshold=c,
                    photo_url=res["thumb"], photo_point=res["thumb_point"], animate=animate, photo_width=88,
                    bar_height=26)
        if res["site"] != "eye":
            ui.note(t("strip_ghana_note"))
        rs = reasons_for(res["site"], res["feats_key"], refer)
        items = "".join(f'<li>{ui.icon(REASON_ICON[r["group"]])}<span>{html.escape(core.reason_text(res["site"], r))}</span></li>'
                        for r in rs)
        if not any(r["agrees"] for r in rs):
            items += f'<li class="care">{ui.icon("alert")}<span>{html.escape(t("reasons_none_refer" if refer else "reasons_none_normal"))}</span></li>'
        st.html(f'<div class="nh-result-body"><h4>{html.escape(t("why"))}</h4><ul class="nh-reasons">{items}</ul>'
                f'<h4>{html.escape(t("sev_title"))}</h4><p class="nh-result-sev">{html.escape(severity_text(res, refer))}</p>'
                f'<p class="nh-result-caveat">{html.escape(t("severity_caveat"))}</p></div>')
    ui.spacer(small=True)
    ui.note(t("next_refer") if refer else t("next_normal"))
    ui.spacer(small=True)
    ui.known_limits()

if anchor := ss.pop("scr_scroll", None):
    scroll_to(anchor)
ui.footer()
