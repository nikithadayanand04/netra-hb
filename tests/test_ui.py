import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
import art  # noqa: E402
import ui  # noqa: E402
from strings import STRINGS  # noqa: E402


@pytest.mark.parametrize("key", sorted(STRINGS))
def test_every_string_in_all_three_languages(key: str) -> None:
    entry = STRINGS[key]
    assert set(entry) == set(ui.LANGS), key
    assert all(entry[code].strip() for code in ui.LANGS), key
    # the same {placeholders} in every language, so formatting never fails in Kannada or Hindi
    fields = {code: set(re.findall(r"{(\w+)}", entry[code])) for code in ui.LANGS}
    assert fields["kn"] == fields["en"] == fields["hi"], key


def test_every_t_key_used_in_the_app_exists() -> None:
    code = "\n".join(p.read_text() for p in (ROOT / "app").rglob("*.py"))
    used = set(re.findall(r"""\bt\(\s*["']([a-z0-9_]+)["']""", code))
    prefixes = {u for u in used if u.endswith("_")}   # t("sev_" + level) style: some key must start with it
    assert all(any(k.startswith(pre) for k in STRINGS) for pre in prefixes), prefixes
    assert used - prefixes - set(STRINGS) == set(), used - prefixes - set(STRINGS)


def test_t_formats_and_falls_back(monkeypatch) -> None:
    monkeypatch.setattr(ui, "lang", lambda: "hi")
    assert ui.t("prob_line", word="X", p=78) == "X, 78% संभावना"
    assert ui.t("no_such_key") == "no_such_key"


def test_who_cutoffs_match_brief() -> None:
    assert ui.AGE_BANDS == {"age_6_59m": 11.0, "age_5_11": 11.5, "age_12_14": 12.0, "age_15_woman": 12.0,
                            "age_15_man": 13.0}
    assert all(k in STRINGS for k in ui.AGE_BANDS) and ui.TRAINED_BAND in ui.AGE_BANDS


def test_five_pages_in_nav_order_and_all_exist() -> None:
    assert [STRINGS[k]["en"] for _, k, _, _ in ui.PAGES] == ["Home", "Screen", "Results", "Insights", "About"]
    assert all((ROOT / "app" / script).exists() for script, *_ in ui.PAGES)
    assert all(icon in art.ICONS for *_, icon in ui.PAGES)


def test_hb_frac_clamps() -> None:
    assert ui._hb_frac(3.0) == 0.0 and ui._hb_frac(20.0) == 1.0 and ui._hb_frac(10.5) == pytest.approx(0.5)


def test_plotly_templates_registered() -> None:
    import plotly.io as pio
    assert {"netra", "netra_dark"} <= set(pio.templates)


def test_dark_tokens_lighten_the_class_colours() -> None:
    assert ui.DARK["refer"] == "#D17189" and ui.DARK["normal"] == "#4C958A"
    assert ".nh-dark {" in (ROOT / "app" / "style.css").read_text()


def test_fonts_are_local_including_kannada_and_devanagari() -> None:
    fonts = ROOT / "app" / "static" / "fonts"
    for f in ("AtkinsonHyperlegible-Regular.ttf", "BricolageGrotesque-VF.ttf", "NotoSansKannada-VF.ttf",
              "NotoSansDevanagari-VF.ttf"):
        assert (fonts / f).exists(), f
    code = "\n".join(p.read_text() for p in (ROOT / "app").rglob("*.py")) + (ROOT / "app" / "style.css").read_text()
    assert "googleapis" not in code and "gstatic" not in code


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_illustrations_render_without_text(mode: str) -> None:
    svgs = [art.hero(mode)] + [art.step(s, mode) for s in ("photo", "check", "result")] + \
           [art.guide(s, mode) for s in ("eye", "palm", "nail")] + \
           [art.header(s, mode) for s in ("data", "sites", "clusters", "search", "about")] + \
           [art.pipeline_node(s, mode) for s in ("photo", "mask", "features", "model", "threshold", "result")]
    for svg in svgs:
        assert svg.startswith("<svg") and "<text" not in svg   # an SVG image cannot use the page fonts


def test_removed_features_stay_removed() -> None:
    app = ROOT / "app"
    code = "\n".join(p.read_text() for p in app.rglob("*.py"))
    for gone in ("fpdf", "referral_slip", "scr_register", "export_register"):
        assert gone not in code, gone
    assert not (app / "slip.py").exists()
    reqs = (ROOT / "requirements.txt").read_text()
    assert "fpdf2" not in reqs and "uharfbuzz" not in reqs
