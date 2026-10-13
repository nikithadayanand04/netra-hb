import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import ui  # noqa: E402

FLOW_KEYS = ["refer", "normal", "start", "try_sample", "no_photo", "fix_light", "fix_glare", "fix_sharp",
             "slip_button", "slip_toast", "next_step", "footer", "age_6_59m", "age_15_man"]


@pytest.mark.parametrize("key", FLOW_KEYS)
def test_flow_strings_have_all_languages(key: str) -> None:
    assert set(ui.STRINGS[key]) == set(ui.LANGS)
    assert all(ui.STRINGS[key][code].strip() for code in ui.LANGS)


def test_t_formats_and_falls_back() -> None:
    assert ui.t("prob_line", word="Likely anaemic", p=78) == "Likely anaemic, 78% chance"
    assert ui.t("no_such_key") == "no_such_key"


def test_who_cutoffs_match_brief() -> None:
    assert ui.AGE_BANDS == {"age_6_59m": 11.0, "age_5_11": 11.5, "age_12_14": 12.0,
                            "age_15_woman": 12.0, "age_15_man": 13.0}


def test_hb_frac_clamps() -> None:
    assert ui._hb_frac(3.0) == 0.0 and ui._hb_frac(20.0) == 1.0 and ui._hb_frac(10.5) == pytest.approx(0.5)


def test_plotly_templates_registered() -> None:
    import plotly.io as pio
    assert {"netra", "netra_dark"} <= set(pio.templates)
