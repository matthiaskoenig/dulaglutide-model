from pathlib import Path

DULAGLUTIDE_PATH = Path(__file__).parent

MODEL_BASE_PATH = DULAGLUTIDE_PATH / "models" / "results" / "models"
MODEL_PATH = MODEL_BASE_PATH / "dulaglutide_body_flat.xml"

RESULTS_PATH = DULAGLUTIDE_PATH / "results"
RESULTS_PATH_SIMULATION = RESULTS_PATH / "simulation"
RESULTS_PATH_FIT = RESULTS_PATH / "fit"

DATA_PATH_BASE = DULAGLUTIDE_PATH / "data"
# DATA_PATH_BASE = DULAGLUTIDE_PATH.parents[3] / "pkdb_data" / "studies"
DATA_PATH_DULAGLUTIDE = DATA_PATH_BASE / "dulaglutide"
DATA_PATHS = [
     DATA_PATH_DULAGLUTIDE,
]
