from pathlib import Path

BODYWEIGHT_PATH = Path(__file__).parent

MODEL_BASE_PATH = BODYWEIGHT_PATH / "models" / "results" / "models"
MODEL_PATH = MODEL_BASE_PATH / "bodyweight.xml"

RESULTS_PATH = BODYWEIGHT_PATH / "results"
RESULTS_PATH_FIT = RESULTS_PATH / "fit"

DATA_PATH_BASE = BODYWEIGHT_PATH.parents[3] / "pkdb_data" / "studies"
DATA_PATH_BODYWEIGHT = DATA_PATH_BASE
DATA_PATHS = [
     DATA_PATH_BODYWEIGHT,
]
