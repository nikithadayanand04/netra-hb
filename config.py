from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---- Paths (edit these) ----
DATA_DIR = ROOT / "data" / "cp_anemic"          # folder containing the CP-AnemiC images (searched recursively)
METADATA_FILE = None                            # e.g. ROOT / "data" / "cp_anemic" / "Anemia_Data.xlsx"; None = auto-detect
OUT_DIR = ROOT / "outputs"
FEATURES_CSV = OUT_DIR / "features_cp_anemic.csv"

# ---- Metadata columns (None = auto-detect by name) ----
ID_COL = None     # column whose value matches the image file name (stem)
HB_COL = None     # haemoglobin in g/dL
AGE_COL = None
SEX_COL = None
AGE_IN_MONTHS = True   # CP-AnemiC ages are in months

DATASET_NAME = "cp_anemic"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# ---- Pixel masking ----
BLACK_THRESH = 25      # pixels with max(R,G,B) below this are background
GLARE_V = 0.92         # specular glare: high brightness ...
GLARE_S = 0.12         # ... and low saturation
MIN_PIXELS = 500       # images with fewer valid pixels are dropped

# ---- Modelling ----
SEED = 42
N_FOLDS = 5
SENS_FLOOR = 0.80      # screening target
N_BOOT = 1000
