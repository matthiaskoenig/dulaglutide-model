"""Subsets of data for dulaglutide."""
from typing import Dict, List
from sbmlsim.fit.helpers import f_fitexp, filter_empty
from sbmlutils.console import console
from sbmlutils.log import get_logger

from sbmlsim.fit import FitExperiment, FitMapping

from pkdb_models.models.dulaglutide import DULAGLUTIDE_PATH, DATA_PATHS
from pkdb_models.models.dulaglutide.experiments.metadata import (
    Tissue, Route, Dosing, ApplicationForm, Health,
    Fasting, DulaglutideMappingMetaData, Coadministration
)
from pkdb_models.models.dulaglutide.experiments.studies import *

logger = get_logger(__name__)


# --- Filters ---
def filter_baseline(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """Healthy control model."""

    metadata: DulaglutideMappingMetaData = fit_mapping.metadata

    # filter coadminstration
    # if metadata.coadministration != Coadministration.NONE:
    #     return False

    # filter health (no renal, cardiac impairment, ...)
    if metadata.health not in {Health.HEALTHY, Health.T2DM, Health.HYPERTENSION}:
        return False

    # remove outliers
    if metadata.outlier is True:
        return False

    return True


# --- Fit experiments ---
f_fitexp_kwargs = dict(
    experiment_classes  = [
        Barrington2011,
        Barrington2011a,
        Blonde2015,
        Chen2018,
        Dungan2014,
        Dungan2016,
        Gao2024,
        Gerstein2019,
        Giorgino2015,
        Liu2025,
        Nauck2014,
        Pratley2018,
        Xu2022,
        Zhang2023
    ],
    base_path=DULAGLUTIDE_PATH,
    data_path=DATA_PATHS,
)
# --- Experiment classes ---
def filter_pharmacokinetics(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """Only d3g data."""
    yid = "__".join(fit_mapping.observable.y.sid.split("__")[1:])
    if yid not in {
        "Cve_dul",
        "Cve_dm",
        "Cve_dul_dm",
        "Aurine_dm",
        "Afeces_dm",
    }:
        return False
    return True

def filter_pharmacodynamics(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """Only pharmacodynamics data."""
    yid = "__".join(fit_mapping.observable.y.sid.split("__")[1:])
    if yid not in {
        "BW",
        "BW_change",
        "hba1c",
        "hba1c_change",
        "fpg",
        "fpg_change",
    }:
        return False
    return True

def f_fitexp_all():
    """All data."""
    return f_fitexp(metadata_filters=filter_empty, **f_fitexp_kwargs)

def f_fitexp_control() -> Dict[str, List[FitExperiment]]:
    """Control data."""
    return f_fitexp(metadata_filters=[filter_baseline], **f_fitexp_kwargs)

def f_fitexp_pharmacokinetics() -> Dict[str, List[FitExperiment]]:
    """Pharmacokinetics data."""
    return f_fitexp(metadata_filters = [filter_baseline, filter_pharmacokinetics], **f_fitexp_kwargs)

def f_fitexp_pharmacodynamics() -> Dict[str, List[FitExperiment]]:
    """Pharmacodynamics data."""
    return f_fitexp(metadata_filters = [filter_baseline, filter_pharmacodynamics], **f_fitexp_kwargs)


if __name__ == "__main__":
    """Test construction of FitExperiments."""

    for f in [
        f_fitexp_all,
        f_fitexp_pharmacodynamics,

    ]:
        console.rule(style="white")
        console.print(f"{f.__name__}")
        fitexp = f()
