import hashlib
import html
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

import screen_core as core
import slip
import ui
from netra import screening

ui.setup_page("Screen", "pages/1_Screen.py")
ss = st.session_state
STEPS = ("patient", "site", "photo", "result")

# Widget values must survive steps where their widget is not drawn
for k in ("scr_name", "scr_age"):
    if k in ss:
        ss[k] = ss[k]
ss.setdefault("scr_step", "patient")
ss.setdefault("scr_age", "age_6_59m")
ss.setdefault("scr_name", "")
ss.setdefault("scr_site", None)
ss.setdefault("scr_img", None)
ss.setdefault("scr_results", [])
ss.setdefault("scr_register", {})
ss.setdefault("scr_visit", 1)
ss.setdefault("scr_sample_next", 0)
ss.setdefault("scr_animated", set())

if ss.pop("scr_toast", False):
    ui.toast("slip_toast")


def cutoff() -> float:
    return ui.AGE_BANDS[ss.scr_age]


def low_confidence(res: dict) -> list[str]:
    why = ["unfamiliar"] if res.get("familiarity", {}).get("unfamiliar") else []
    return why + (["age_outside"] if ss.scr_age != "age_6_59m" else [])


def go(step: str) -> None:
    ss.scr_step = step


def new_visit() -> None:
    ss.scr_visit += 1
    ss.scr_results, ss.scr_img, ss.scr_site = [], None, None
    ss.scr_name = ""


def choose_site(site: str, fresh: bool = False) -> None:
    if fresh or ss.scr_site != site:
        ss.scr_img = None
        ss.pop("scr_seen", None)
    ss.scr_site = site
    go("photo")


def next_patient() -> None:
    new_visit()
    ss.scr_age = "age_6_59m"
    go("patient")


def set_image(rgb: np.ndarray, alpha: np.ndarray | None, sig: str, sample: dict | None = None) -> None:
    if sample is not None and sample["whole_image_is_tissue"]:
        tissue, how = np.ones(rgb.shape[:2], bool), "whole"
    else:
        tissue = screening.auto_tissue(rgb, alpha)
        how = "auto" if tissue is not None else None
    ss.scr_img = {"rgb": rgb, "alpha": alpha, "sig": sig, "sample": sample, "tissue": tissue, "how": how,
                  "point": None, "last_click": None}


def run_analysis() -> None:
    img = ss.scr_img
    photo = screening.analyse_photo(img["rgb"], img["tissue"], ss.scr_site)
    # A sample photo is in the training set, where the model has seen it; show the out-of-fold score instead
    res = core.analyse(ss.scr_site, photo, p_override=img["sample"]["oof_p"] if img["sample"] else None)
    res["sample"] = img["sample"]
    rgb, tissue, alpha = core.display_size(img["rgb"], img["tissue"], img["alpha"])
    res["photo"] = core.png_url(core.overlay(core.on_black(rgb, alpha), tissue, dim=img["how"] is None))
    res["id"] = f"{ss.scr_visit}-{ss.scr_site}-{img['sig']}"
    ss.scr_results = [r for r in ss.scr_results if r["site"] != ss.scr_site] + [res]
    log_visit()
    go("result")


def log_visit() -> None:
    # Safety first: any site that refers makes the visit a referral; the experimental average never cancels one
    c = cutoff()
    worst = min(ss.scr_results, key=lambda r: r["position"])
    ss.scr_register[ss.scr_visit] = {
        "time": datetime.now(), "name": ss.scr_name.strip(), "age_key": ss.scr_age,
        "sites": [r["site"] for r in ss.scr_results], "refer": bool(worst["position"] < c),
        "low_conf": any(low_confidence(r) for r in ss.scr_results),
        "p": worst["p"], "combined": len(ss.scr_results) > 1}


def load_sample(i: int) -> None:
    sample = core.samples()[i]
    new_visit()
    ss.scr_age, ss.scr_site = sample["age_band"], sample["site"]
    rgb, alpha = core.load_sample(sample)
    set_image(rgb, alpha, f"sample-{sample['id']}", {**sample, "n": i + 1})
    run_analysis()
    ss.scr_sample_next = (i + 1) % len(core.samples())


# ---------------------------------------------------------------- page head
if core.bundles() is None:
    st.html(f'<h1 class="nh-page-title">{html.escape(ui.t("screen_title"))}</h1>')
    ui.missing("../models/screen_eye.joblib", "build_screen_models")
    ui.footer()
    st.stop()

if ss.pop("sample_mode", False) and core.samples():
    load_sample(ss.scr_sample_next)


def stepper(current: str) -> None:
    idx = STEPS.index(current)
    items = []
    for i, s in enumerate(STEPS):
        state = "done" if i < idx else "current" if i == idx else "todo"
        cur = ' aria-current="step"' if i == idx else ""
        items.append(f'<li class="nh-stepper-item {state}"{cur}><span class="nh-stepper-num">{i + 1}</span>'
                     f'<span class="nh-stepper-name">{html.escape(ui.t("step_" + s))}</span></li>')
    st.html(f'<nav aria-label="{html.escape(ui.t("steps_aria"))}"><ol class="nh-stepper">{"".join(items)}</ol></nav>')


head_l, head_r = st.columns([1.4, 1], vertical_alignment="bottom")
with head_l:
    st.html(f'<h1 class="nh-page-title">{html.escape(ui.t("screen_title"))}</h1>'
            f'<p class="nh-section-lede">{html.escape(ui.t("screen_lede"))}</p>')
with head_r:
    stepper(ss.scr_step)


def sample_tiles() -> None:
    items = core.samples()
    if not items:
        return
    ui.spacer()
    ui.section(ui.t("samples_title"), ui.t("samples_lede"))
    with st.container(horizontal=True, wrap=True, gap="small", key="nh_samples"):
        for i, s in enumerate(items):
            with st.container(width=148, gap="small", key=f"nh_sample_{i}"):
                rgb, alpha = core.load_sample(s)
                st.html(f'<img class="nh-sample-img" alt="" src="{core.sample_thumb(rgb, alpha)}">')
                st.button(f'{ui.t("sample_n", n=i + 1)}, {ui.t("site_" + s["site"]).lower()}',
                          key=f"scr_sample_{i}", width="stretch", on_click=load_sample, args=(i,))


# ---------------------------------------------------------------- 1. patient
def step_patient() -> None:
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.text_input(ui.t("name_label"), key="scr_name", help=ui.t("name_help"), max_chars=60)
        st.segmented_control(ui.t("age_band"), list(ui.AGE_BANDS), format_func=ui.t, key="scr_age",
                             required=True)
        ui.spacer(small=True)
        st.button(ui.t("next"), type="primary", key="scr_next_patient", on_click=go, args=("site",))
    with right:
        c = cutoff()
        note = "" if ss.scr_age == "age_6_59m" else f'<p class="nh-note">{html.escape(ui.t("cutoff_note"))}</p>'
        st.html(f'<div class="nh-cutoff"><p class="nh-cutoff-label">{html.escape(ui.t("cutoff_title"))}</p>'
                f'<p class="nh-cutoff-num">{c:g}<small> g/dL</small></p>'
                f'<p class="nh-cutoff-text">{html.escape(ui.t("cutoff_text", c=f"{c:g}"))}</p>{note}</div>')
        ui.hb_strip(threshold=c, bar_height=22)
    sample_tiles()


# ---------------------------------------------------------------- 2. site
def step_site() -> None:
    ui.section(ui.t("site_title"), ui.t("site_lede"))
    cols = st.columns(3, gap="large")
    for col, site in zip(cols, core.SITES):
        with col, st.container(key=f"nh_site_{site}{'_on' if ss.scr_site == site else ''}"):
            st.html(f'{core.illustration(site)}<h3 class="nh-site-name">{html.escape(ui.t("site_" + site))}</h3>'
                    f'<p class="nh-site-how">{html.escape(ui.t("how_" + site))}</p>'
                    f'<p class="nh-site-data">{html.escape(ui.t("site_data_" + site))}</p>')
            st.button(ui.t("choose_site", site=ui.t("site_" + site)), key=f"scr_site_{site}", width="stretch",
                      type="primary" if ss.scr_site == site else "secondary", on_click=choose_site, args=(site,))
    ui.spacer(small=True)
    st.button(ui.t("back"), key="scr_back_site", on_click=go, args=("patient",))


# ---------------------------------------------------------------- 3. photo
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
        st.html(f'<p class="nh-error">{html.escape(ui.t("bad_image"))}</p>')
        return
    set_image(*got, sig)


def step_photo() -> None:
    site = ss.scr_site
    noun = ui.t("noun_" + site)
    ui.section(ui.t("photo_title", site=noun), ui.t("how_" + site))
    left, right = st.columns([1, 1.15], gap="large")
    with left:
        cam_tab, up_tab = st.tabs([ui.t("camera"), ui.t("upload")])
        cam_key, up_key = f"scr_cam_{ss.scr_visit}_{site}", f"scr_up_{ss.scr_visit}_{site}"
        with cam_tab:
            take_input(cam_key, st.camera_input(ui.t("camera_label"), key=cam_key))
        with up_tab:
            take_input(up_key, st.file_uploader(ui.t("upload_label"), type=["jpg", "jpeg", "png"], key=up_key))
        st.html(core.illustration(site).replace('class="nh-illo"', 'class="nh-illo nh-illo-sm"'))
    with right:
        img = ss.scr_img
        if img is None:
            ui.empty_state()
        else:
            photo_panel(img, noun)
    ui.spacer(small=True)
    st.button(ui.t("back"), key="scr_back_photo", on_click=go, args=("site",))
    sample_tiles()


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


def photo_panel(img: dict, noun: str) -> None:
    rgb = core.on_black(img["rgb"], img["alpha"])
    if img["how"] in ("auto", "whole"):
        big, tissue, alpha = core.display_size(img["rgb"], img["tissue"], img["alpha"])
        shown = core.overlay(core.on_black(big, alpha), tissue, dim=False)
        st.html(f'<img class="nh-photo" alt="" src="{core.png_url(shown)}">')
        st.html(f'<p class="nh-note">{html.escape(ui.t("tissue_" + img["how"]))}</p>')
    else:
        shown = core.overlay(rgb, img["tissue"], img["point"], box=img.get("box"))
        click = streamlit_image_coordinates(shown, key=f"scr_click_{img['sig']}", width="stretch",
                                            cursor="crosshair", image_format="JPEG", jpeg_quality=88,
                                            click_and_drag=True)
        if click and click.get("unix_time") != img["last_click"]:   # a resize re-sends the old click
            img["last_click"] = click.get("unix_time")
            select_tissue(img, click)
            st.rerun()
        if img["tissue"] is None and (img["point"] is not None or img.get("box")):
            st.html(f'<p class="nh-note nh-note-warn">{html.escape(ui.t("tissue_small", site=noun))}</p>')
        else:
            msg = ui.t("tissue_selected") if img["tissue"] is not None else ui.t("tissue_drag", site=noun)
            st.html(f'<p class="nh-note">{html.escape(msg)}</p>')

    st.html(f'<h3 class="nh-sub">{html.escape(ui.t("quality_title"))}</h3>')
    photo = screening.analyse_photo(img["rgb"], img["tissue"], ss.scr_site) if img["tissue"] is not None else None
    if photo is None:
        st.html(f'<p class="nh-note">{html.escape(ui.t("quality_wait"))}</p>')
        return
    ok = ui.quality_chips({k: v["ok"] for k, v in photo.checks.items()})
    if ok:
        st.html(f'<p class="nh-note">{html.escape(ui.t("quality_pass"))}</p>')
    removed = 1 - photo.mask.sum() / max(photo.tissue.sum(), 1)
    st.html(f'<h3 class="nh-sub">{html.escape(ui.t("preview_title"))}</h3>'
            f'<img class="nh-preview" alt="" src="{core.measured_preview(photo)}">'
            f'<p class="nh-note">{html.escape(ui.t("preview_text", pct=round(removed * 100)))}</p>')
    if st.button(ui.t("analyse"), type="primary", disabled=not ok, key="scr_analyse"):
        run_analysis()
        st.rerun()


# ---------------------------------------------------------------- 4. result
@st.cache_data(show_spinner=False, max_entries=64)
def reasons_for(site: str, feats_key: tuple, refer: bool) -> list[dict]:
    return screening.reasons(core.bundles()[site], dict(feats_key), refer)


def severity_html(res: dict, refer: bool) -> str:
    if res["site"] != "eye":
        body = ui.t("sev_none_ghana")
    elif not refer:
        body = ui.t("sev_none")
    else:
        sev = screening.severity(res["position"], cutoff())
        body = ui.t("sev_line", sev=ui.t("sev_" + sev), hb=f"{res['position']:.1f}", mae=f"{res['hb_mae']:.1f}")
    return (f'<h4>{html.escape(ui.t("sev_title"))}</h4><p class="nh-result-sev">{html.escape(body)}</p>'
            f'<p class="nh-result-caveat">{html.escape(ui.t("severity_caveat"))}</p>')


def step_result() -> None:
    if not ss.scr_results:
        go("patient")
        st.rerun()
    res = ss.scr_results[-1]
    c = cutoff()
    refer = res["position"] < c
    why_low = low_confidence(res)
    state = "refer" if refer else "normal"
    left, right = st.columns([1, 1.45], gap="large")
    with left:
        st.html(f'<img class="nh-photo" alt="" src="{res["photo"]}">')
        ui.quality_chips({k: v["ok"] for k, v in res["checks"].items()})
        if res["sample"]:
            s = res["sample"]
            truth = (ui.t("sample_truth_hb", hb=f"{s['hb']:.1f}") if s["hb"] is not None else
                     ui.t("sample_truth_folder", label=ui.t("anaemic_word" if s["label"] else "not_anaemic_word")))
            st.html(f'<p class="nh-note">{html.escape(ui.t("sample_banner", n=s["n"], site=ui.t("noun_" + s["site"])))}'
                    f' {html.escape(truth)}</p>')
    with right, st.container(key=f"nh_result_{state}"):
        word = ui.t("likely_anaemic") if refer else ui.t("likely_normal")
        lo, hi = res["band"]
        st.html(f'<div class="nh-result-head" aria-live="polite"><p class="nh-result-word">{html.escape(ui.t(state))}</p>'
                f'<p class="nh-result-prob">{html.escape(ui.t("prob_line", word=word, p=round(res["p"] * 100)))}</p>'
                f'<p class="nh-result-band">{html.escape(ui.t("band_explain", lo=round(lo * 100), hi=round(hi * 100)))}'
                f'</p></div>')
        if why_low:
            items = "".join(f"<li>{html.escape(ui.t(k))}</li>" for k in why_low)
            st.html(f'<p class="nh-conf" role="status">{html.escape(ui.t("low_conf"))}</p><ul class="nh-conf-why">{items}</ul>')
        animate = res["id"] not in ss.scr_animated
        ss.scr_animated.add(res["id"])
        ui.hb_strip(hb=float(np.clip(res["position"], ui.HB_MIN, ui.HB_MAX)), swatch_rgb=res["swatch"], threshold=c,
                    photo_url=res["thumb"], photo_point=res["thumb_point"], animate=animate, photo_width=88,
                    bar_height=26)
        if res["site"] != "eye":
            st.html(f'<p class="nh-note">{html.escape(ui.t("strip_ghana_note"))}</p>')
        rs = reasons_for(res["site"], res["feats_key"], refer)
        items = "".join(f"<li>{html.escape(core.reason_text(res['site'], r))}</li>" for r in rs)
        st.html(f'<div class="nh-result-body"><h4>{html.escape(ui.t("why"))}</h4><ul>{items}</ul>'
                f'{severity_html(res, refer)}</div>')

    combined = core.combine(ss.scr_results, c)
    # Safety first: any site that refers makes the visit a referral; the experimental average never cancels one
    final_refer = any(r["position"] < c for r in ss.scr_results)

    ui.spacer(small=True)
    with st.container(horizontal=True, wrap=True, gap="small", key="nh_result_actions"):
        if final_refer:
            visit = {"name": ss.scr_name.strip(), "age_key": ss.scr_age, "cutoff": c, "time": datetime.now(),
                     "results": [{**r, "refer": r["position"] < c} for r in ss.scr_results],
                     "refer": final_refer, "low_conf": [k for r in ss.scr_results for k in low_confidence(r)],
                     "combined": None if combined is None else {**combined, "refer": combined["position"] < c}}
            st.download_button(ui.t("slip_button"), data=slip.referral_slip(visit), mime="application/pdf",
                               file_name=f"netra-hb-referral-{datetime.now():%Y%m%d-%H%M}.pdf", type="primary",
                               key="scr_slip", on_click=lambda: ss.update(scr_toast=True),
                               icon=":material/download:")
        done = {r["site"] for r in ss.scr_results}
        for site in core.SITES:
            if site not in done:
                st.button(ui.t("add_site", site=ui.t("noun_" + site)), key=f"scr_add_{site}",
                          on_click=choose_site, args=(site, True))
        st.button(ui.t("retake"), key="scr_retake", on_click=choose_site, args=(res["site"], True))
        st.button(ui.t("new_patient"), key="scr_new", on_click=next_patient)
    if not final_refer:
        st.html(f'<p class="nh-note">{html.escape(ui.t("no_referral"))}</p>')
    ui.spacer(small=True)
    ui.known_limits()

    if combined:
        ui.spacer()
        ui.section(ui.t("combined"), ui.t("combined_lede"))
        cstate = "refer" if combined["position"] < c else "normal"
        lines = "".join(
            f'<li>{html.escape(ui.t("site_result", site=ui.t("site_" + r["site"]), p=round(r["p"] * 100), word=ui.t("anaemic_word" if r["position"] < c else "not_anaemic_word")))}</li>'
            for r in ss.scr_results)
        with st.container(key=f"nh_result_{cstate}_combined"):
            st.html(f'<p class="nh-result-word nh-result-word-sm">{html.escape(ui.t(cstate))}</p>'
                    f'<p class="nh-result-prob">{html.escape(ui.t("combined"))}: {round(combined["p"] * 100)}%</p>'
                    f'<ul class="nh-site-list">{lines}</ul>')
            ui.hb_strip(hb=float(np.clip(combined["position"], ui.HB_MIN, ui.HB_MAX)), swatch_rgb=combined["swatch"],
                        threshold=c, animate=False, bar_height=20, swatch_label=ui.t("combined_short").capitalize())


# ---------------------------------------------------------------- register
def register() -> None:
    ui.spacer()
    ui.section(ui.t("register"), ui.t("register_lede"))
    rows = list(ss.scr_register.values())
    if not rows:
        ui.empty_state("register_empty")
        return
    df = pd.DataFrame({
        ui.t("col_time"): [r["time"].strftime("%H:%M") for r in rows],
        ui.t("col_name"): [r["name"] or "" for r in rows],
        ui.t("col_age"): [ui.t(r["age_key"]) for r in rows],
        ui.t("col_site"): [" + ".join(ui.t("site_" + s) for s in r["sites"])
                           + (f' ({ui.t("combined_short")})' if r["combined"] else "") for r in rows],
        ui.t("col_result"): [ui.t("refer" if r["refer"] else "normal") for r in rows],
        ui.t("col_chance"): [f"{round(r['p'] * 100)}%" for r in rows],
        ui.t("col_conf"): [ui.t("low_conf" if r.get("low_conf") else "conf_ok") for r in rows],
    })
    if not any(r["name"] for r in rows):
        df = df.drop(columns=ui.t("col_name"))
    n_ref = sum(r["refer"] for r in rows)
    st.html(f'<p class="nh-register-totals">{html.escape(ui.t("register_totals", n=len(rows), r=n_ref, k=len(rows) - n_ref))}</p>')
    st.dataframe(df, hide_index=True, width="stretch")
    st.download_button(ui.t("export_register"), data=df.to_csv(index=False).encode("utf-8-sig"), mime="text/csv",
                       file_name=f"netra-hb-register-{datetime.now():%Y%m%d}.csv", key="scr_export",
                       icon=":material/table:")


if ss.get("scr_shown_step") != ss.scr_step:   # a new step starts at the top, where its content is
    ss.scr_shown_step = ss.scr_step
    st.iframe("<script>const m = window.parent.document.querySelector('[data-testid=\"stMain\"]');"
              "if (m) m.scrollTo({top: 0}); window.parent.scrollTo({top: 0});</script>", height=1)
{"patient": step_patient, "site": step_site, "photo": step_photo, "result": step_result}[ss.scr_step]()
register()
ui.footer()
