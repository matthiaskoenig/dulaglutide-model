from pathlib import Path

HBA1C_PATH = Path(__file__).parent

MODEL_BASE_PATH = HBA1C_PATH / "models" / "results" / "models"
MODEL_PATH = MODEL_BASE_PATH / "hba1c_model.xml"

RESULTS_PATH = HBA1C_PATH / "results"
RESULTS_PATH_FIT = RESULTS_PATH / "fit"

DATA_PATH_BASE = HBA1C_PATH.parents[3] / "pkdb_data" / "studies"
DATA_PATH_HBA1C = DATA_PATH_BASE
DATA_PATHS = [
     DATA_PATH_HBA1C,
]
