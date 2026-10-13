import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
import ui  # noqa: E402


def test_who_cutoffs_match_brief() -> None:
    assert ui.AGE_BANDS == {"6–59 months": 11.0, "5–11 years": 11.5, "12–14 years": 12.0,
                            "15+ woman": 12.0, "15+ man": 13.0}
    assert ui.TRAINED_BAND in ui.AGE_BANDS


def test_five_pages_in_nav_order_and_all_exist() -> None:
    assert [label for _, label, _ in ui.PAGES] == ["Home", "Screen", "Results", "Insights", "About"]
    assert all((ROOT / "app" / script).exists() for script, _, _ in ui.PAGES)
    assert sorted(p.name for p in (ROOT / "app" / "pages").glob("*.py")) == \
        sorted(Path(s).name for s, _, _ in ui.PAGES if s.startswith("pages/"))


def test_hb_frac_clamps() -> None:
    assert ui._hb_frac(3.0) == 0.0 and ui._hb_frac(20.0) == 1.0 and ui._hb_frac(10.5) == pytest.approx(0.5)


def test_plotly_template_registered() -> None:
    import plotly.io as pio
    assert "netra" in pio.templates


def test_every_quality_check_has_a_label_and_one_fix() -> None:
    assert set(ui.CHECK_LABELS) == set(ui.CHECK_FIXES) == {"light", "glare", "sharp", "makeup"}


def test_removed_features_stay_removed() -> None:
    app = ROOT / "app"
    code = "\n".join(p.read_text() for p in app.rglob("*.py"))
    for gone in ("fpdf", "referral_slip", "scr_register", "export_register", "segmented_control(\"Language",
                 "st.toggle(", "ಕ", "हि"):
        assert gone not in code, gone
    assert not (app / "fonts").exists() and not (app / "slip.py").exists()
    reqs = (ROOT / "requirements.txt").read_text()
    assert "fpdf2" not in reqs and "uharfbuzz" not in reqs
