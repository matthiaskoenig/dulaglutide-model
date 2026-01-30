"""Sensitivity analysis.

requires the `sbmlsim2` branch of https://github.com/matthiaskoenig/sbmlsim.git
install with
```
cd sbmlsim
git checkout sbmlsim2
(pkdb_models) uv pip install -e ../sbmlsim
```

"""
from __future__ import annotations

import numpy as np
import pandas as pd
import roadrunner
from pint import UnitRegistry
from sbmlutils.console import console

from pkdb_analysis.pk.pharmacokinetics import TimecoursePK

from sbmlsim.sensitivity.analysis import (
    SensitivitySimulation,
    SensitivityOutput,
    AnalysisGroup,
)
from sbmlsim.sensitivity.parameters import (
    SensitivityParameter,
    ParameterType,
)

from pkdb_models.models.dulaglutide import MODEL_PATH
from pkdb_models.models.dulaglutide.fitting.parameters import parameters_all as fit_parameters

dose_dulaglutide = 1.5  # [mg]

# Subgroups to perform sensitivity analysis on
sensitivity_groups: list[AnalysisGroup] = [
    AnalysisGroup(
        uid="control",
        name="Control",
        changes={},
        color="dimgrey",
    ),
    AnalysisGroup(
        uid="mildRI",
        name="Mild renal impairment",
        changes={"KI__f_renal_function": 0.69},
        color="#66c2a4",
    ),
    AnalysisGroup(
        uid="modRI",
        name="Moderate renal impairment",
        changes={"KI__f_renal_function": 0.32},
        color="#2ca25f",
    ),
    AnalysisGroup(
        uid="sevRI",
        name="Severe renal impairment",
        changes={"KI__f_renal_function": 0.19},
        color="#006d2c",
    ),
    AnalysisGroup(
        uid="CPT A",
        name="Mild cirrhosis (CPT A)",
        changes={"f_cirrhosis": 0.399},
        color="#74a9cf",
    ),
    AnalysisGroup(
        uid="CPT B",
        name="Moderate cirrhosis (CPT B)",
        changes={"f_cirrhosis": 0.698},
        color="#2b8cbe",
    ),
    AnalysisGroup(
        uid="CPT C",
        name="Severe cirrhosis (CPT C)",
        changes={"f_cirrhosis": 0.813},
        color="#045a8d",
    )
]


class DulaglutideSensitivitySimulation(SensitivitySimulation):
    """Simulation for sensitivity calculation."""
    tend = 4 * 7 * 24 * 60  # [min] (slow half-life)
    steps = 3000

    def simulate(self, r: roadrunner.RoadRunner, changes: dict[str, float]) -> dict[str, float]:

        # apply changes and simulate
        all_changes = {
            **self.changes_simulation,  # model
            **changes  # sensitivity
        }
        self.apply_changes(r, all_changes, reset_all=True)
        # ensure tolerances
        r.integrator.setValue("absolute_tolerance", self.init_tolerances)
        s = r.simulate(start=0, end=self.tend, steps=self.steps)


        # pharmacokinetic parameters
        y: dict[str, float] = {}

        # pharmacokinetics
        ureg = UnitRegistry()
        Q_ = ureg.Quantity

        time = Q_(s["time"], "min")
        tcpk = TimecoursePK(
            time=time,
            concentration=Q_(s["[Cve_dul]"], "mM"),
            substance="dulaglutide",
            ureg=ureg,
            dose=Q_(dose_dulaglutide, "mg")/Q_(3314.6, "g/mole")
        )
        pk_dict = tcpk.pk.to_dict()

        for pk_key in [
            "aucinf",
            "cmax",
            "thalf",
            "vd",
            "cl",
            "kel",
        ]:
            y[f"[Cve_dul]_{pk_key}"] = pk_dict[pk_key]

        for sid in [
            "[Cve_dm]",
        ]:
            tcpk = TimecoursePK(
                time=time,
                concentration=Q_(s[sid], "mM"),
                substance="dulaglutide",
                ureg=ureg,
                dose=None,
            )
            pk_dict = tcpk.pk.to_dict()
            for pk_key in [
                "aucinf",
                "cmax",
                "thalf",
                "kel",
            ]:
                y[f"{sid}_{pk_key}"] = pk_dict[pk_key]

        # pharmacodynamics (maximum reduction of FPG, bodyweight, hba1c
        for sid in ["BW", "hba1c", "fpg"]:
            y[f"{sid}_ratio_min"] = np.min(s[f"{sid}_ratio"])

        return y


sensitivity_simulation = DulaglutideSensitivitySimulation(
    model_path=MODEL_PATH,
    selections=[
        "time",
        "[Cve_dul]",
        "[Cve_dm]",
        "BW_ratio",
        "hba1c_ratio",
        "fpg_ratio",
    ],
    changes_simulation = {
        # ! make sure all the changes from base-experiment are injected here !
        "SCDOSE_dul": dose_dulaglutide,  # [mg]
        "f_cirrhosis": 0,  # [-]
        "KI__f_renal_function": 1.0,  # [-]
    },
    outputs=[
        # FIXME: auto-calculate units
        SensitivityOutput(uid='[Cve_dul]_aucinf', name='DUL AUC∞', unit="mM*min"),
        SensitivityOutput(uid='[Cve_dul]_cmax', name='DUL Cmax', unit="mM"),
        SensitivityOutput(uid='[Cve_dul]_thalf', name='DUL Half-life', unit="min"),
        SensitivityOutput(uid='[Cve_dul]_vd', name='DUL Vd', unit="l"),
        SensitivityOutput(uid='[Cve_dul]_cl', name='DUL CL', unit="mole/min/mM"),
        SensitivityOutput(uid='[Cve_dul]_kel', name='DUL kel', unit="1/min"),

        SensitivityOutput(uid='[Cve_dm]_aucinf', name='DM AUC∞', unit="mM*min"),
        SensitivityOutput(uid='[Cve_dm]_cmax', name='DM Cmax', unit="mM"),
        SensitivityOutput(uid='[Cve_dm]_thalf', name='DM Half-life', unit="min"),
        SensitivityOutput(uid='[Cve_dm]_kel', name='DM kel', unit="1/min"),

        SensitivityOutput(uid='BW_ratio_min', name='min BW ratio', unit="-"),
        SensitivityOutput(uid='hba1c_ratio_min', name='min HbA1c ratio', unit="-"),
        SensitivityOutput(uid='fpg_ratio_min', name='min FPG ratio', unit="-"),
    ]
)


def _sensitivity_parameters() -> list[SensitivityParameter]:
    """Definition of parameters and bounds for sensitivity analysis."""
    console.rule("Parameters", style="white")
    parameters: list[SensitivityParameter] = SensitivityParameter.parameters_from_sbml(
        sbml_path=MODEL_PATH,
        exclude_ids={
            # conversion factors
            "conversion_min_per_day",
            "conversion_cm_per_m",
            "cf_units_per_mmole",

            # molecular weights
            "Mr_dul",
            "Mr_dm",

            # unchangable values
            "FQlu",
            "FVhv",
            "FVpo",
            "f_lumen",

            # dosing parameters
            "Ri_dul",
            "ti_dul",
        },
        exclude_na=True,
        exclude_zero=True,
    )
    bounds_fraction = 0.15  # fraction of bounds relative to value

    # bounds from fitted parameters
    fit_bounds = [
        # (fp.pid, fp.lower_bound, fp.upper_bound, ParameterType.FIT) for fp in fit_parameters
        (fp.pid, np.nan, np.nan, ParameterType.FIT) for fp in fit_parameters
    ]
    SensitivityParameter.parameters_set_bounds(parameters, bounds=fit_bounds)

    # bounds from scaled parameters
    uids_scaling = [
        # FIXME
        # "GU__f_absorption",
        # "KI__f_renal_function",
        # "KI__f_ugt1a9",
        # "LI__f_ugt1a9",
        # "LI__f_ugt2b4",
        # "LI__f_cyp3a4",
    ]
    scaling_bounds = [
        (uid, 1 - bounds_fraction, 1 + bounds_fraction, ParameterType.SCALING) for uid in uids_scaling
    ]
    SensitivityParameter.parameters_set_bounds(parameters, bounds=scaling_bounds)

    # references for values
    reference_data={
        "HCT": r"\cite{Mondal2025, Fiseha2023}",
        #"BW0": r"\cite{Ogden2004, Jones2013, Thompson2009, Brown1997}",
        "FQgu": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FQh": r"\cite{Jones2013, Wynne1989, Thompson2009, Brown1997}",
        "FQki": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVar": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVgu": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVki": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVli": r"\cite{Jones2013, Wynne1989, Thompson2009, Brown1997}",
        "FVlu": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVve": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "COBW": r"\cite{Cattermole2017, Patel2021, Collis2001}",
        "KI__f_renal_function": r"\cite{Stevens2024}",
    }
    p_dict = {p.uid: p for p in parameters}
    for pid, reference in reference_data.items():
        p = p_dict[pid]
        p.reference = reference
        if p.type == ParameterType.NA:
            p.type = ParameterType.DATA

    # setting missing bounds;
    for p in parameters:
        if np.isnan(p.lower_bound) and np.isnan(p.upper_bound):
            p.lower_bound = p.value * (1 - bounds_fraction)
            p.upper_bound = p.value * (1 + bounds_fraction)

    # print parameters
    pd.options.display.float_format = "{:.5g}".format
    df_parameters = SensitivityParameter.parameters_to_df(parameters)
    console.print(df_parameters)

    return parameters

sensitivity_parameters = _sensitivity_parameters()


if __name__ == "__main__":
    import multiprocessing
    from sbmlsim.sensitivity import (
        SobolSensitivityAnalysis,
        LocalSensitivityAnalysis,
        SamplingSensitivityAnalysis,
        FASTSensitivityAnalysis,
    )
    from pkdb_models.models.dulaglutide import RESULTS_PATH
    sensitivity_path = RESULTS_PATH / "sensitivity"
    settings = {
        "cache_results": False,
        "n_cores": int(round(0.9 * multiprocessing.cpu_count())),
        "seed": 1234
    }

    sa_local = LocalSensitivityAnalysis(
        sensitivity_simulation=sensitivity_simulation,
        parameters=sensitivity_parameters,
        groups=sensitivity_groups,
        results_path=sensitivity_path / "local",
        difference=0.01,
        **settings,
    )
    sa_sampling = SamplingSensitivityAnalysis(
        sensitivity_simulation=sensitivity_simulation,
        parameters=sensitivity_parameters,
        groups=sensitivity_groups,
        results_path=sensitivity_path / "sampling",
        N=1000,
        **settings,
    )
    sa_fast = FASTSensitivityAnalysis(
        sensitivity_simulation=sensitivity_simulation,
        parameters=sensitivity_parameters,
        groups=sensitivity_groups,
        results_path=sensitivity_path / "fast",
        N=1000,
        **settings,
    )
    sa_sobol = SobolSensitivityAnalysis(
        sensitivity_simulation=sensitivity_simulation,
        parameters=sensitivity_parameters,
        groups=[sensitivity_groups[0]],
        results_path=sensitivity_path / "sobol",
        N=4096,
        **settings,
    )
    for sa in [
        sa_local,
        sa_sampling,
        # sa_fast,
        # sa_sobol,
    ]:
        sa.execute()
        sa.plot()
