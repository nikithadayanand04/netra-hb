"""Every page runs headless without an exception (needs outputs/ from the pipeline scripts)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
sys.path.insert(0, str(APP))
MODELS = ROOT / "outputs" / "models" / "screen_eye.joblib"


def _run(page: str | None = None, **state):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(APP / "Home.py"), default_timeout=120)
    at.run()
    for k, v in state.items():
        at.session_state[k] = v
    if page:
        at.switch_page(page).run()
    return at


@pytest.mark.parametrize("page", [None, "pages/2_Results.py", "pages/3_Insights.py", "pages/4_About.py"])
def test_page_runs(page) -> None:
    at = _run(page)
    assert not at.exception, at.exception


@pytest.mark.skipif(not MODELS.exists(), reason="run python -m scripts.build_screen_models")
def test_screen_sample_patients_give_mixed_results() -> None:
    at = _run("pages/1_Screen.py", sample_mode=True)
    assert not at.exception, at.exception
    seen = set()
    for i in range(6):
        at.button(key=f"scr_sample_{i}").click().run()
        assert not at.exception, at.exception
        res = at.session_state["scr_result"]
        seen.add((res["site"], res["position"] < 11.0))
    assert len({s for s, _ in seen}) == 3 and {r for _, r in seen} == {True, False}


@pytest.mark.skipif(not MODELS.exists(), reason="run python -m scripts.build_screen_models")
def test_results_threshold_slider_runs() -> None:
    at = _run("pages/2_Results.py")
    at.selectbox(key="res_model").set_value("knn").run()
    at.slider(key="res_thr_knn").set_value(0.9).run()
    assert not at.exception, at.exception
