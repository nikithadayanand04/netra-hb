import hashlib
import html

import numpy as np
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

import screen_core as core
import ui
from netra import screening

ui.setup_page("Screen", "pages/1_Screen.py")
ss = st.session_state
ss.setdefault("scr_age", ui.TRAINED_BAND)
ss.setdefault("scr_site", None)
ss.setdefault("scr_img", None)
ss.setdefault("scr_result", None)
ss.setdefault("scr_sample_next", 0)
ss.setdefault("scr_animated", set())

SITE_NAMES = {"eye": "Eyelid", "palm": "Palm", "nail": "Nail"}
HOW_TO = {
    "eye": "Gently pull down the lower eyelid with one finger. Photograph the red inner rim.",
    "palm": "Open the hand flat, palm up. Fill the frame with the centre of the palm.",
    "nail": "Rest the fingers flat. Photograph the nail beds from above, no nail polish.",
}
TESTED_ON = {"eye": "Tested on 220 children with lab Hb.", "palm": "Tested on 522 children, folder labels.",
             "nail": "Tested on 530 children, folder labels."}


def cutoff() -> float:
    return ui.AGE_BANDS[ss.scr_age]


def scroll_to(anchor: str) -> None:
    st.iframe(f"<script>const e = window.parent.document.getElementById('{anchor}');"
              "if (e) e.scrollIntoView({behavior: 'instant', block: 'start'});</script>", height=1)


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
    res |= {"sample": img["sample"], "id": f"{ss.scr_site}-{img['sig']}",
            "photo": core.png_url(core.overlay(core.on_black(rgb, alpha), tissue, dim=img["how"] is None))}
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
    why = ["This photo looks unlike the training photos, so the result is less reliable."] \
        if res["familiarity"]["unfamiliar"] else []
    if ss.scr_age != ui.TRAINED_BAND:
        why.append("The models were trained on young children (eye 6–59 months, palm and nail under 5 years), "
                   "so this result is less reliable for this age band.")
    return why


# ---------------------------------------------------------------- page
ui.page_title("Screen a patient", "Choose the age band and the site, add a photo, pass the photo check, read the "
                                  "result. Or pick a sample patient.")
if core.bundles() is None:
    ui.missing("models/screen_eye.joblib", "build_screen_models")
    ui.footer()
    st.stop()

if ss.pop("sample_mode", False) and core.samples():   # "Try a sample patient" on Home
    load_sample(ss.scr_sample_next)


def step_head(n: int, title: str, lede: str | None = None, anchor: str | None = None) -> None:
    a = f' id="{anchor}"' if anchor else ""
    lede_html = f'<p class="nh-section-lede">{html.escape(lede)}</p>' if lede else ""
    st.html(f'<h2 class="nh-section-title nh-step-title"{a}><span class="nh-step-n">{n}</span>{html.escape(title)}</h2>'
            f'{lede_html}')


# ---------------------------------------------------------------- 1. patient and site
step_head(1, "Patient and site")
left, right = st.columns([1.3, 1], gap="large")
with left:
    st.segmented_control("Age band", list(ui.AGE_BANDS), key="scr_age", required=True)
    if ss.scr_age != ui.TRAINED_BAND:
        ui.note("The models learned from children aged 6 to 59 months. For this age band the cut-off moves on the "
                "colour scale, which has not been validated.")
with right:
    c = cutoff()
    st.html(f'<div class="nh-cutoff"><p class="nh-cutoff-label">WHO anaemia cut-off</p>'
            f'<p class="nh-cutoff-num">{c:g}<small> g/dL</small></p>'
            f'<p class="nh-cutoff-text">Below {c:g} g/dL counts as anaemia for this age band.</p></div>')

ui.spacer(small=True)
cols = st.columns(3, gap="large")
for col, site in zip(cols, core.SITES):
    with col, st.container(key=f"nh_site_{site}{'_on' if ss.scr_site == site else ''}"):
        st.html(f'{core.illustration(site)}<h3 class="nh-site-name">{SITE_NAMES[site]}</h3>'
                f'<p class="nh-site-how">{html.escape(HOW_TO[site])}</p>'
                f'<p class="nh-site-data">{TESTED_ON[site]}</p>')
        st.button("Selected" if ss.scr_site == site else f"Use {SITE_NAMES[site].lower()}", key=f"scr_site_{site}",
                  width="stretch", type="primary" if ss.scr_site == site else "secondary",
                  on_click=choose_site, args=(site,))


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
        ui.note("This file could not be read as a photo. Try a JPG or PNG.", warn=True)
        return
    set_image(*got, sig)


def sample_tiles() -> None:
    ui.note("Real photos from the training sets, to show the flow. Each shows its out-of-fold score, from a model "
            "that did not see that child. Not a test of accuracy.")
    with st.container(horizontal=True, wrap=True, gap="small", key="nh_samples"):
        for i, s in enumerate(core.samples()):
            with st.container(width=150, gap="small", key=f"nh_sample_{i}"):
                rgb, alpha = core.load_sample(s)
                st.html(f'<img class="nh-sample-img" alt="" src="{core.sample_thumb(rgb, alpha)}">')
                st.button(f"Sample {i + 1}, {SITE_NAMES[s['site']].lower()}", key=f"scr_sample_{i}",
                          width="stretch", on_click=load_sample, args=(i,))


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
    noun = core.NOUNS[ss.scr_site]
    rgb = core.on_black(img["rgb"], img["alpha"])
    if img["how"] in ("auto", "whole"):
        big, tissue, alpha = core.display_size(img["rgb"], img["tissue"], img["alpha"])
        shown = core.overlay(core.on_black(big, alpha), tissue, dim=False)
        st.html(f'<img class="nh-photo" alt="" src="{core.png_url(shown)}">')
        ui.note("Tissue found automatically from the clear background." if img["how"] == "auto"
                else "This photo is already cropped to the tissue.")
    else:
        shown = core.overlay(rgb, img["tissue"], img["point"], box=img["box"])
        click = streamlit_image_coordinates(shown, key=f"scr_click_{img['sig']}", width="stretch",
                                            cursor="crosshair", image_format="JPEG", jpeg_quality=88,
                                            click_and_drag=True)
        if click and click.get("unix_time") != img["last_click"]:   # a resize re-sends the old click
            img["last_click"] = click.get("unix_time")
            select_tissue(img, click)
            st.rerun()
        if img["tissue"] is None and (img["point"] or img["box"]):
            ui.note(f"That area is too small. Tap the middle of the {noun}, or drag a bigger box.", warn=True)
        elif img["tissue"] is None:
            ui.note(f"Tap the {noun}, or drag a box over it. For the eye, box only the pink inner eyelid.")
        else:
            ui.note("Selected. Tap or drag again to change.")

    st.html('<h3 class="nh-sub">Photo check</h3>')
    photo = screening.analyse_photo(img["rgb"], img["tissue"], ss.scr_site) if img["tissue"] is not None else None
    if photo is None:
        ui.note("Select the tissue to run the checks.")
        return
    ok = ui.quality_chips({k: v["ok"] for k, v in photo.checks.items()})
    if ok:
        ui.note("All checks passed.")
    removed = 1 - photo.mask.sum() / max(photo.tissue.sum(), 1)
    st.html(f'<h3 class="nh-sub">Pixels measured</h3>'
            f'<img class="nh-preview" alt="" src="{core.measured_preview(photo)}">')
    ui.note(f"Only the coloured pixels are measured. Grey: removed as makeup, lashes or glare "
            f"({round(removed * 100)}% of the selection).")
    st.button("See result", type="primary", disabled=not ok, key="scr_analyse", on_click=run_analysis)


if ss.scr_site is None:
    ui.spacer()
    st.html('<h2 class="nh-section-title nh-step-title nh-step-todo"><span class="nh-step-n">2</span>Photo</h2>')
    ui.note("Choose a site above, or pick a sample patient.")
    sample_tiles()
else:
    ui.spacer()
    step_head(2, f"Photo of the {core.NOUNS[ss.scr_site]}", HOW_TO[ss.scr_site])
    left, right = st.columns([1, 1.15], gap="large")
    with left:
        cam_tab, up_tab, sample_tab = st.tabs(["Camera", "Upload", "Sample patient"])
        cam_key, up_key = f"scr_cam_{ss.scr_site}", f"scr_up_{ss.scr_site}"
        with cam_tab:
            take_input(cam_key, st.camera_input("Take a photo", key=cam_key))
        with up_tab:
            take_input(up_key, st.file_uploader("Choose a photo (JPG or PNG)", type=["jpg", "jpeg", "png"],
                                                key=up_key))
        with sample_tab:
            sample_tiles()
    with right:
        if ss.scr_img is None:
            ui.empty_state("No photo yet. Take one, upload one or pick a sample patient.")
        else:
            photo_panel(ss.scr_img)


# ---------------------------------------------------------------- 3. result
@st.cache_data(show_spinner=False, max_entries=64)
def reasons_for(site: str, feats_key: tuple, refer: bool) -> list[dict]:
    return screening.reasons(core.bundles()[site], dict(feats_key), refer)


def severity_text(res: dict, refer: bool) -> str:
    if res["site"] != "eye":
        return "Not available for palm or nail: those photo sets have no Hb values."
    if not refer:
        return "None expected."
    sev = screening.severity(res["position"], cutoff())
    return f"{sev.capitalize()}: colour suggests about {res['position']:.1f} g/dL, give or take {res['hb_mae']:.1f}."


res = ss.scr_result
if res is not None:
    ui.spacer()
    step_head(3, "Result", anchor="nh-result")
    c = cutoff()
    refer = res["position"] < c
    state = "refer" if refer else "normal"
    left, right = st.columns([1, 1.45], gap="large")
    with left:
        st.html(f'<img class="nh-photo" alt="" src="{res["photo"]}">')
        ui.quality_chips({k: v["ok"] for k, v in res["checks"].items()})
        if res["sample"]:
            s = res["sample"]
            truth = f"Lab Hb {s['hb']:.1f} g/dL." if s["hb"] is not None else \
                f"Folder label: {'anaemic' if s['label'] else 'not anaemic'}."
            ui.note(f"Sample patient {s['n']}: {core.NOUNS[s['site']]} photo from the training data. {truth}")
    with right, st.container(key=f"nh_result_{state}"):
        lo, hi = res["band"]
        word = "Likely anaemic" if refer else "Likely not anaemic"
        st.html(f'<div class="nh-result-head" aria-live="polite">'
                f'<p class="nh-result-word">{ui.REFER if refer else ui.NORMAL}</p>'
                f'<p class="nh-result-prob">{word}, {round(res["p"] * 100)}% chance</p>'
                f'<p class="nh-result-band">Among children who scored like this, {round(lo * 100)}–{round(hi * 100)}% '
                f'were anaemic.</p></div>')
        why_low = low_confidence(res)
        if why_low:
            items = "".join(f"<li>{html.escape(x)}</li>" for x in why_low)
            st.html(f'<p class="nh-conf" role="status">Low confidence</p><ul class="nh-conf-why">{items}</ul>')
        animate = res["id"] not in ss.scr_animated
        ss.scr_animated.add(res["id"])
        ui.hb_strip(hb=float(np.clip(res["position"], ui.HB_MIN, ui.HB_MAX)), swatch_rgb=res["swatch"], threshold=c,
                    photo_url=res["thumb"], photo_point=res["thumb_point"], animate=animate, photo_width=88,
                    bar_height=26)
        if res["site"] != "eye":
            ui.note("Palm and nail have no Hb values: the strip position is a colour position only.")
        items = "".join(f"<li>{html.escape(core.reason_text(res['site'], r))}</li>"
                        for r in reasons_for(res["site"], res["feats_key"], refer))
        st.html(f'<div class="nh-result-body"><h4>Why</h4><ul>{items}</ul><h4>Rough severity</h4>'
                f'<p class="nh-result-sev">{html.escape(severity_text(res, refer))}</p>'
                '<p class="nh-result-caveat">Severity is a rough guide from colour only. Only a blood test gives the '
                'Hb level.</p></div>')
    ui.spacer(small=True)
    ui.note("Next step: visit the PHC for a finger-prick Hb test within 7 days." if refer
            else "No referral needed today. Screen again at the next visit.")
    ui.spacer(small=True)
    ui.known_limits()

if anchor := ss.pop("scr_scroll", None):
    scroll_to(anchor)
ui.footer()
