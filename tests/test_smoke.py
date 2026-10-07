import importlib

import pytest

PACKAGES = [
    "numpy", "pandas", "sklearn", "imblearn", "cv2", "skimage", "scipy", "matplotlib",
    "seaborn", "plotly", "streamlit", "streamlit_image_coordinates", "openpyxl", "xlrd",
    "joblib", "jupyter", "config", "netra", "netra.scratch",
]


@pytest.mark.parametrize("name", PACKAGES)
def test_import(name: str) -> None:
    importlib.import_module(name)


def test_config_paths() -> None:
    import config
    assert config.ROOT.name == "netra-hb"
    assert config.DATA_DIR.exists()
