from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---- Paths (edit these) ----
DATA_DIR = ROOT / "data" / "cp_anemic" / "All Categories"   # all 251 images; Anaemic/ and Non-Anaemic/ are duplicates, ignore them
METADATA_FILE = ROOT / "data" / "cp_anemic" / "Cp-Anaemic Dataset.xlsx"
METADATA_SHEET = "Cp-Anaemic Dataset"         # main sheet; never use its Folder_Label column as the label
OUT_DIR = ROOT / "outputs"
FEATURES_CSV = OUT_DIR / "features_cp_anemic.csv"

# ---- Metadata columns (None = auto-detect by name) ----
ID_COL = "Image_ID"   # equals the image file stem; one image per child, so this is also the patient_id
HB_COL = "Hb_g_dl"   # haemoglobin in g/dL
AGE_COL = None       # CP-AnemiC sheet has no age column
SEX_COL = None       # ... and no sex column
AGE_IN_MONTHS = True
DEFAULT_AGE_MONTHS = 30   # used when AGE_COL is None: all children are 6–59 mo -> WHO cut-off Hb < 11

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

# ---- Cleaning flags (report only unless noted) ----
GLARE_MAX_FRAC = 0.05   # flag if glare pixels exceed this fraction of tissue
BLUR_VAR_MIN = 3.0      # flag if Laplacian variance on eroded tissue is below this (~5th pct of CP-AnemiC)
PIXEL_EQ_MAX = 0.30     # flag upscaling/pixelation if > this fraction of adjacent tissue pixels are identical
DUP_HAMMING = 6         # pHash Hamming distance for duplicate candidates ...
DUP_MAE = 6.0           # ... confirmed if mean abs RGB diff on 64x64 tissue composites is below this
DUP_HB_TOL = 1.0        # duplicate groups whose Hb spans more than this (or whose labels differ) are dropped entirely

# ---- Model inputs ----
# Raw colour features only. glare_frac, tissue_px, quality flags and gw_* stay in the CSV for EDA/ablations.
_MED = ["R", "G", "B", "chrom_r", "chrom_g", "chrom_b", "lab_L", "lab_a", "lab_b",
        "a_over_L", "hsv_h", "hsv_s", "erythema_index"]          # hsv_v dropped: hsv_v_med == R_med / 255
_PCT = ["chrom_r", "lab_a", "a_over_L", "erythema_index", "hsv_s"]
CANDIDATE_FEATURES = [f"{c}_med" for c in _MED] + [f"{c}_p{q}" for c in _PCT for q in (10, 90)]

# Label-free redundancy pruning (scripts.prune_features): for every candidate pair with |Spearman rho| > REDUNDANCY_RHO,
# drop the one later in INTERPRETABILITY. Uses no labels, so it cannot leak label information into feature choice.
REDUNDANCY_RHO = 0.95
INTERPRETABILITY = ["lab_a", "erythema_index", "chrom_r", "lab_L", "lab_b", "a_over_L",
                    "R", "G", "B", "hsv_s", "hsv_h", "chrom_g", "chrom_b"]
COLLINEAR_DROP = ["chrom_b_med"]   # chrom_r + chrom_g + chrom_b = 1: pairwise pruning cannot catch this
MODEL_FEATURES = [
    "R_med", "B_med", "chrom_r_med", "chrom_g_med", "lab_L_med", "lab_a_med", "lab_b_med",
    "hsv_h_med", "erythema_index_med", "chrom_r_p10", "lab_a_p10", "lab_a_p90", "erythema_index_p10",
    "erythema_index_p90",
]
EXCLUDED_FEATURES = ["glare_frac", "tissue_px"]
