"""Pharmacokinetic parameters of the dulaglutide scans.

The parameters are the non-compartmental analysis of `pkpdutils`, named like
the variables of its `NCAResult` (e.g. `auc_inf_obs`, `cmax`, `tmax`, `thalf`,
`lambda_z`, `cl_f`, `vz_f`), with the unit of every parameter in
`<name>_unit`. Dulaglutide is analysed in venous plasma with its subcutaneous
dose, an extravascular dose (`Route.ORAL` of pkpdutils, which has no
subcutaneous route; the analysis of an extravascular dose is the same), so the
clearance and the volume are the apparent ones. The concentrations below
`LLOQ_FRACTION` of the maximum are below the limit of quantification, so that
the noise of the integrator is not the terminal phase.

A scan has one dimension, the scanned parameter; a run over the draws of the
fitted parameters (`run_simulation pkdb_models.models.dulaglutide
--uncertainty`) adds the dimension of the draws. The parameters are
calculated for every point of every dimension, a row per point with its
position along each dimension (the columns `point` and, with draws, `draw`),
see `summarize`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from pkpdsim.pk import nca_frame, scan_nca
from pkpdsim.scan import scan_dimensions, start_values
from pkpdutils import Route
from sbmlsim import Q
from sbmlsim.result import ScanResult

if TYPE_CHECKING:
    from pkdb_models.models.dulaglutide.experiments.base_experiment import (
        DulaglutideSimulationExperiment,
    )

#: subcutaneous dose of the scans
DOSE = "SCDOSE_dul"
#: the concentration of dulaglutide in venous plasma
CONCENTRATION = "[Cvep_dul]"
#: the name of the analyte, the column `substance` of the parameters
SUBSTANCE = "dulaglutide"
#: the limit of quantification relative to the maximal concentration
LLOQ_FRACTION = 1e-4


def _point_dimension(res: ScanResult, across: str | None) -> str:
    """Get the dimension of the scan besides the draws `across`.

    Raises:
        ValueError: if the scan has not one dimension besides the draws.
    """
    dims = scan_dimensions(res, across)
    if len(dims) != 1:
        raise ValueError(
            f"A scan of one dimension is required, not of {dims} (draws: {across})."
        )
    return dims[0]


def calculate_dulaglutide_pk(
    experiment: DulaglutideSimulationExperiment,
    res: ScanResult,
    across: str | None = None,
) -> pd.DataFrame:
    """Calculate the pharmacokinetic parameters of every simulation of a scan.

    The non-compartmental analysis of all simulations at once
    (`pkpdsim.pk.scan_nca`), with the dose in the substance unit of the
    concentration, which `cl_f` and `vz_f` require.

    Args:
        experiment: experiment of the scan, for the molecular weight.
        res: result of the scan, a scan of a subcutaneous dose.
        across: the dimension of the draws of the fitted parameters, `None`
            for a scan without draws.

    Returns:
        One row per simulation of the scan, with its position (`point`, and
        `draw` with draws), the parameters and their units (`<name>_unit`).
    """
    point = _point_dimension(res, across)
    dose_mass = Q(start_values(res, DOSE).values, res.units[DOSE])
    result = scan_nca(
        res,
        CONCENTRATION,
        dose=(dose_mass / experiment.Mr.dul).to("mmole"),
        route=Route.ORAL,
        substance=SUBSTANCE,
        lloq_fraction=LLOQ_FRACTION,
    )
    df = nca_frame(result).drop(columns="nca_flags")
    df.insert(len(res.dims), "substance", SUBSTANCE)
    names = {point: "point", **({across: "draw"} if across is not None else {})}
    return df.rename(columns=names)


def summarize(
    df: pd.DataFrame, key: str, quantiles: tuple[float, float]
) -> pd.DataFrame:
    """Get the median and the quantiles of a parameter over the draws of every point.

    Args:
        df: the parameters with the columns `point` and `draw`.
        key: the parameter.
        quantiles: the lower and the upper quantile.

    Returns:
        One row per point (the index), the columns `lower`, `median`, `upper`.
    """
    low, high = quantiles
    grouped = df.groupby("point")[key]
    return pd.DataFrame(
        {
            "lower": grouped.quantile(low),
            "median": grouped.median(),
            "upper": grouped.quantile(high),
        }
    ).astype(np.float64)
