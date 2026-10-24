"""Sensitivity analysis of the dulaglutide model.

The outputs of the single dose (`single`) are the pharmacokinetic parameters of
dulaglutide after a single subcutaneous dose of 1.5 mg in a healthy subject
(the non-compartmental analysis of `pkpdutils`), the outputs of the weekly
doses (`multi`, 26 weekly doses of 1.5 mg in type 2 diabetes, HbA1c 8 %) the
extremes of the pharmacodynamics: the minima of the changes of the fasting
plasma glucose, the HbA1c and the body weight. The parameters are the
parameters of the model with bounds of +-15 % around their value. The analyses are run as a script, the local analysis of the single dose
by default; the names of the arguments select the analyses and the simulations:

    python -m pkdb_models.models.dulaglutide.sensitivity.sensitivity_analysis
    python -m pkdb_models.models.dulaglutide.sensitivity.sensitivity_analysis local sampling multi

The analyses run on `pkpdsim.sensitivity.SensitivityRunner`, a runner per
simulation (`run_subfolders`), which writes the table of the parameters into
`results/sensitivity` of the model and the tables and figures of sbmlsim 0.8.5
of an analysis into `results/sensitivity/<simulation>/<analysis>`. An analysis
does not vary a parameter which one of its groups sets
(`pkpdsim.sensitivity.free_parameters`): `sampling`, over the three groups of
the body weight, leaves out `BW0`. The model has no renal or hepatic mechanism
of the elimination of dulaglutide, so there are no groups of an impaired renal
or hepatic function. The environment variable
`PKPDSIM_SENSITIVITY_N` replaces the numbers of samples of the global analyses
for a quick run, see `pkpdsim.sensitivity.sample_size`.
"""

from collections.abc import Mapping, Sequence

import numpy as np
from pkpdsim.sensitivity import (
    FastAnalysis,
    LocalAnalysis,
    ParameterType,
    SamplingAnalysis,
    SensitivityGroup,
    SensitivityOutput,
    SensitivityParameter,
    SensitivityRunner,
    SobolAnalysis,
    parameters_from_sbml,
    run_subfolders,
    set_bounds,
    set_relative_bounds,
)
from sbmlsim import Q
from sbmlsim.simulation import PK, Change, Formula, Observable, Simulation

from pkdb_models.models.dulaglutide import MODEL, MODEL_PATH
from pkdb_models.models.dulaglutide.fitting.parameters import (
    parameters_all as fit_parameters,
)

#: subcutaneous dose of the analysis [mg]
DOSE_DULAGLUTIDE = 1.5
#: the number of weekly doses of `multi`
N_DOSES = 26
#: the baselines of `multi`: type 2 diabetes, HbA1c 8 % and the FPG of
#: `fpg_from_hba1c` (1.11 * 8 + 0.2605 mM)
T2DM_CHANGES: dict[str, float] = {"hba1c0": 0.08, "fpg0": 9.1405}
#: fraction of the bounds of a parameter relative to its value
BOUNDS_FRACTION = 0.15

#: outputs of the non-compartmental analysis of pkpdutils -> unit of the output
PK_OUTPUTS: dict[str, dict[str, str]] = {
    "[Cvep_dul]": {
        "auc_inf_obs": "mM*min",
        "cmax": "mM",
        "tmax": "min",
        "thalf": "min",
        "vz_f": "l",
        "cl_f": "ml/min",
    },
}
#: names of the substances and of the pharmacokinetic parameters in the outputs
PK_SUBSTANCE_NAMES: dict[str, str] = {"[Cvep_dul]": "DUL"}
PK_PARAMETER_NAMES: dict[str, str] = {
    "auc_inf_obs": "AUC∞",
    "cmax": "Cmax",
    "tmax": "tmax",
    "thalf": "Half-life",
    "vz_f": "Vz/F",
    "cl_f": "CL/F",
}
#: the outputs whose unit has the amount of the dose: the dose is a mass
#: (`SCDOSE_dul` in mg), so they are divided by the molecular weight (its value
#: at the start, a value per simulation like the parameter of the analysis)
PK_PER_DOSE_MASS: frozenset[str] = frozenset({"vz_f", "cl_f"})

#: outputs of the pharmacodynamics, the minima of the changes from baseline
#: -> name, formula, unit
PD_OUTPUTS: dict[str, tuple[str, str, str]] = {
    "fpg_change_min": ("min FPG change", "min(fpg_change)", "mM"),
    "hba1c_change_min": ("min HbA1c change", "min(hba1c_change)", "dimensionless"),
    "BW_change_min": ("min BW change", "min(BW_change)", "kg"),
}


def _pk_id(selection: str) -> str:
    """Get the id of the non-compartmental analysis of a concentration."""
    return f"pk_{selection.strip('[]')}"


def _pk_formula(selection: str, key: str) -> str:
    """Get the formula of a pharmacokinetic output of a concentration."""
    if key in PK_PER_DOSE_MASS:
        return f"{_pk_id(selection)}.{key} / at(Mr_dul, 0)"
    return f"{_pk_id(selection)}.{key}"


#: the outputs of the weekly doses
OUTPUTS_MULTI: list[SensitivityOutput] = [
    SensitivityOutput(uid, name) for uid, (name, _, _) in PD_OUTPUTS.items()
]
#: the outputs of the single dose: the id of a pharmacokinetic output names the
#: concentration with its brackets (`[Cvep_dul]_cmax`), as the tables of
#: sbmlsim 0.8.5, its observable has the id without them (`Cvep_dul_cmax`)
OUTPUTS_SINGLE: list[SensitivityOutput] = [
    SensitivityOutput(
        f"{sid}_{key}",
        f"{PK_SUBSTANCE_NAMES[sid]} {PK_PARAMETER_NAMES[key]}",
        f"{sid.strip('[]')}_{key}",
    )
    for sid, outputs in PK_OUTPUTS.items()
    for key in outputs
]

#: the observables of the weekly doses, the outputs with their units
OBSERVABLES_MULTI: list[Observable] = [
    Formula(uid, formula, unit=unit) for uid, (_, formula, unit) in PD_OUTPUTS.items()
]
#: the observables of the single dose: the subcutaneous dose is extravascular
#: (`oral` of pkpdutils)
OBSERVABLES_SINGLE: list[Observable] = [
    *(
        PK(
            _pk_id(sid),
            sid,
            dose="SCDOSE_dul",
            route="oral",
            parameters=list(outputs),
        )
        for sid, outputs in PK_OUTPUTS.items()
    ),
    *(
        Formula(f"{sid.strip('[]')}_{key}", _pk_formula(sid, key), unit=unit)
        for sid, outputs in PK_OUTPUTS.items()
        for key, unit in outputs.items()
    ),
]


def sensitivity_simulation(
    changes: Mapping[str, float], end: float, steps: int, n_doses: int = 1
) -> Simulation:
    """Get the simulation of a group: subcutaneous doses of dulaglutide.

    Args:
        changes: the changes of the group.
        end: the end of the simulation [min].
        steps: the number of steps of the simulation.
        n_doses: the number of weekly doses.
    """
    week = 7 * 24 * 60  # [min]
    return Simulation(
        end=end,
        time_unit="min",
        preinit_changes={"SCDOSE_dul": Q(DOSE_DULAGLUTIDE, "mg"), **changes},
        changes=[
            Change(
                [k * week for k in range(1, n_doses)],
                {"SCDOSE_dul": Q(DOSE_DULAGLUTIDE, "mg")},
            )
        ]
        if n_doses > 1
        else [],
    )


#: the groups the analyses are run for: the control (75 kg) and a low and a
#: high body weight, the covariate of the clearance -> name, changes, color
GROUPS: dict[str, tuple[str, dict[str, float], str]] = {
    "control": ("Control (75 kg)", {}, "dimgrey"),
    "lowBW": ("Body weight 55 kg", {"BW0": 55.0}, "#74a9cf"),
    "highBW": ("Body weight 110 kg", {"BW0": 110.0}, "#045a8d"),
}


def sensitivity_parameters() -> list[SensitivityParameter]:
    """Get the parameters of the analyses with their bounds and references."""
    parameters = parameters_from_sbml(
        MODEL_PATH,
        exclude_ids={
            # the reference body weight of the tissue exchange
            "BW_ref",
            # conversion factors
            "conversion_cm_per_m",
            "cf_units_per_mmole",
            # molecular weights
            "Mr_dul",
            # unchangeable values
            "FQlu",
            "FVhv",
            "FVpo",
            # dosing parameters
            "Ri_dul",
            "ti_dul",
            "Ksc_injection_dul",
            # the compartment of the catabolism products, no effect
            "Vdeg",
        },
        exclude_na=True,
        exclude_zero=True,
    )

    # the fitted parameters, their bounds are set relative to the value below
    set_bounds(
        parameters,
        [(fp.pid, np.nan, np.nan, ParameterType.FIT) for fp in fit_parameters],
    )

    # the references of the values from the literature
    references = {
        "HCT": r"\cite{Mondal2025, Fiseha2023}",
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
    }
    by_uid = {p.uid: p for p in parameters}
    for uid, reference in references.items():
        p = by_uid[uid]
        p.reference = reference
        if p.type == ParameterType.NA:
            p.type = ParameterType.DATA

    # every parameter without bounds varies around its value
    set_relative_bounds(parameters, BOUNDS_FRACTION)
    return parameters


def _runner(
    groups: list[SensitivityGroup],
    outputs: list[SensitivityOutput],
    observables: list[Observable],
) -> SensitivityRunner:
    """Get the runner of a simulation, with the analyses and sizes of sbmlsim 0.8.5."""
    return SensitivityRunner(
        model=MODEL,
        parameters=sensitivity_parameters,
        outputs=outputs,
        observables=observables,
        analyses={
            "local": LocalAnalysis(groups=groups[:1], delta=0.01),
            "sampling": SamplingAnalysis(groups=groups, n=1000),
            "fast": FastAnalysis(groups=groups[:1], n=1000),
            "sobol": SobolAnalysis(groups=groups[:1], n=4096),
        },
        default=("local",),
    )


#: the runners of the simulations by name, the subfolders of their results
SIMULATIONS: dict[str, SensitivityRunner] = {
    # the single dose: six weeks (half-life about 4 days)
    "single": _runner(
        [
            SensitivityGroup(
                uid, name, sensitivity_simulation(changes, 6 * 7 * 24 * 60, 3000), color
            )
            for uid, (name, changes, color) in GROUPS.items()
        ],
        OUTPUTS_SINGLE,
        OBSERVABLES_SINGLE,
    ),
    # the weekly doses in type 2 diabetes, half a year
    "multi": _runner(
        [
            SensitivityGroup(
                uid,
                name,
                sensitivity_simulation(
                    {**T2DM_CHANGES, **changes},
                    N_DOSES * 7 * 24 * 60,
                    2000,
                    n_doses=N_DOSES,
                ),
                color,
            )
            for uid, (name, changes, color) in GROUPS.items()
        ],
        OUTPUTS_MULTI,
        OBSERVABLES_MULTI,
    ),
}


def main(argv: Sequence[str] | None = None) -> None:
    """Run the analyses of the simulations named on the command line.

    Args:
        argv: the arguments, those of the process if `None`: the names of the
            analyses (`local` without one) and of the simulations (`single`
            without one), in any order, and `--workers N`, the processes of
            the pool.
    """
    runner = SIMULATIONS["single"]
    words = runner.parse_command_line(argv, choices=list(SIMULATIONS))
    run_subfolders(
        SIMULATIONS,
        words.analyses,
        subfolders=words.choices or ("single",),
        simulator=runner.simulator_settings(words.workers),
    )


if __name__ == "__main__":
    main()
