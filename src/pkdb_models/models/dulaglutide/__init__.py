"""Dulaglutide: PBPK/PD model of the subcutaneous GLP-1 receptor agonist dulaglutide.

The paths of the model and its model object `MODEL`, which the commands
`run_simulation`, `run_fit`, `run_report` and `run_identifiability` of pkpdsim
run by its package `pkdb_models.models.dulaglutide`.
"""

from pathlib import Path

from pkpdsim.model import FigureSettings, PKPDModel, SimulatorSettings
from pkpdsim.release.settings import Author, ReleaseSettings

from pkdb_models.models.dulaglutide.tolerances import ABSOLUTE_TOLERANCE

DULAGLUTIDE_PATH = Path(__file__).parent

MODEL_BASE_PATH = DULAGLUTIDE_PATH / "models" / "output" / "models"
# the body model has no submodels, it is the model the simulations run
MODEL_PATH = MODEL_BASE_PATH / "dulaglutide_body.xml"

DATA_PATH_BASE = DULAGLUTIDE_PATH / "data"
DATA_PATH_DULAGLUTIDE = DATA_PATH_BASE / "dulaglutide"
DATA_PATHS = [
    DATA_PATH_DULAGLUTIDE,
]

MODEL = PKPDModel(
    name="dulaglutide",
    package=__name__,
    title="Dulaglutide PBPK/PD model",
    path=DULAGLUTIDE_PATH,
    model_path=MODEL_PATH,
    data_paths=tuple(DATA_PATHS),
    archive_path=MODEL_BASE_PATH.parent / "dulaglutide_model.omex",
    factory=".models.factory:create_dulaglutide_models",
    experiments=".simulations:EXPERIMENTS",
    fit_definitions=".fitting.fitting:FIT_DEFINITIONS",
    # the adopted fits, the factory takes the fitted values from their records
    fits=("PK_20261018_102441__faa2d", "PD_20261019_103700__c0378"),
    fit_identifiability=True,
    simulator=SimulatorSettings(
        absolute_tolerance=ABSOLUTE_TOLERANCE, relative_tolerance=1e-10
    ),
    # static images
    figures=FigureSettings(
        formats=("svg",),
        savefig_dpi=300,
        legend_fontsize=10,
        legend_position="inside",
    ),
    # the release of the model repository
    release=ReleaseSettings(
        title=(
            "Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model"
            " of dulaglutide"
        ),
        repository="matthiaskoenig/dulaglutide-model",
        doi="10.5281/zenodo.18432433",
        authors=(
            Author(
                "Kim, Minjun",
                "0009-0006-1453-0143",
                "National University of Singapore, Department of Statistics and Data Science",
            ),
            Author(
                "König, Matthias",
                "0000-0003-1725-179X",
                (
                    "Humboldt-Universität zu Berlin, Faculty of Life Sciences, Department of Biology, Institute of Theoretical Biology, Systems Medicine of the Liver; University of Stuttgart, Institute of Structural Mechanics and Dynamics in Aerospace Engineering; University of Southern Denmark, Clinical Pharmacology, Pharmacy and Environmental Medicine, Department of Public Health; University Hospital Schleswig-Holstein, Campus Lübeck, First Department of Medicine, Lübeck, Germany"
                ),
            ),
        ),
        keywords=(
            "model",
            "dulaglutide",
            "GLP-1 receptor agonist",
            "type 2 diabetes",
            "pharmacokinetics",
            "pharmacodynamics",
            "HbA1c",
            "PBPK/PD",
            "physiologically based pharmacokinetic/pharmacodynamic model",
            "SBML",
        ),
        docker_image="matthiaskoenig/dulaglutide",
        funding=(
            "Matthias König was supported by the Federal Ministry of Research, Technology and Space (BMFTR, Germany) within ATLAS by grant number 031L0304B and by the German Research Foundation (DFG) within the Research Unit Program FOR 5151 QuaLiPerF (Quantifying Liver Perfusion-Function Relationship in Complex Resection - A Systems Medicine Approach) by grant number 436883643 and by grant number 465194077 (Priority Programme SPP 2311, Subproject SimLivA). This work was supported by the BMBF-funded de.NBI Cloud within the German Network for Bioinformatics Infrastructure (de.NBI) (031A537B, 031A533A, 031A538A, 031A533B, 031A535A, 031A537C, 031A534A, 031A532B)."
        ),
        description=(
            "This repository provides the dulaglutide physiologically based"
            " pharmacokinetic/pharmacodynamic (PBPK/PD) model: the subcutaneous"
            " absorption of dulaglutide with its bioavailability, its"
            " distribution into the interstitial space, its protein catabolism"
            " and its effects on the fasting plasma glucose, the HbA1c and the"
            " body weight in type 2 diabetes."
        ),
        first_year=2025,
    ),
)
"""The dulaglutide model: its commands, see `pkpdsim.model`."""
