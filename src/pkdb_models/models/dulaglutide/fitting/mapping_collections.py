"""Parameter fit problems for dulaglutide.

The data of a fit is selected from the fit mappings of the studies in three
steps, see `sbmlsim.fit.helpers`: the filters on the metadata of the mappings
select the training data of the fit and exclude the rest, the outliers are
named once for all mappings and are the training data which is not usable, and
the validation data is the part of the training data a fit is evaluated on but
not fitted to. The metadata of a mapping describes its curve, what a fit does
with the curve is decided here.

The training data of the pharmacokinetics (`f_collections_pk`) are the
dulaglutide plasma concentrations after single doses and exactly encoded
repeated doses (IV, SC) of healthy subjects; the pharmacokinetics in type 2
diabetes are population validation (`POPULATION_VALIDATION`). The training
data of the pharmacodynamics (`f_collections_pd`) are the absolute series of
the fasting plasma glucose, the HbA1c and the body weight of the trials in
type 2 diabetes (the changes from baseline are the same measurements, they are
not fitted). Both take the arms on an oral background therapy
(`BACKGROUND_THERAPY`), none with another coadministered drug. The validation
data has four parts, each a different question: the doses
(`DOSE_VALIDATION`), the populations (`POPULATION_VALIDATION`, the groups with
an impaired renal function and populations which the model predicts without
parameters of their own), the interactions (`INTERACTION_VALIDATION`) and the
limitations (`LIMITATION_VALIDATION`, data of a population, a route, a product
or a process the model does not describe). The summaries of data which is
fitted one by one are excluded (`AGGREGATE_MAPPINGS`).
"""

from pkpdsim.fit import mapping_metadata, observable_filter
from pkpdsim.metadata import Coadministration, Health
from sbmlsim.console import console
from sbmlsim.experiment import SimulationExperiment
from sbmlsim.fit import FitMapping, FitMappingCollection, MappingKind
from sbmlsim.fit.helpers import FitMappings, MappingFilter

from pkdb_models.models.dulaglutide import DATA_PATHS, DULAGLUTIDE_PATH
from pkdb_models.models.dulaglutide.experiments.studies import (
    FDAGBCM,
    FDAGBCN,
    FDAGBDO,
    FDAGBDR,
    Barrington2011,
    Barrington2011a,
    Blonde2015,
    Chen2018,
    Dungan2014,
    Dungan2016,
    Gao2024,
    Gerstein2019,
    Giorgino2015,
    Grunberger2012,
    Liu2025,
    Morioka2024,
    Nauck2014,
    Pratley2018,
    Terauchi2014,
    Umpierrez2011,
    Umpierrez2014,
    Wang2019,
    Weinstock2015,
    Wysham2014,
    Xu2022,
    Zhang2023,
)

#: the keys of fit mappings by study: the keys of the mappings are SIds of their
#: experiment, which two studies can share, so a named mapping is named with
#: its study
type NamedMappings = dict[str, set[str]]

EXPERIMENT_CLASSES: list[type[SimulationExperiment]] = [
    Barrington2011,
    Barrington2011a,
    Blonde2015,
    Chen2018,
    Dungan2014,
    Dungan2016,
    FDAGBCM,
    FDAGBCN,
    FDAGBDO,
    FDAGBDR,
    Gao2024,
    Gerstein2019,
    Giorgino2015,
    Grunberger2012,
    Liu2025,
    Morioka2024,
    Nauck2014,
    Pratley2018,
    Terauchi2014,
    Umpierrez2011,
    Umpierrez2014,
    Wang2019,
    Weinstock2015,
    Wysham2014,
    Xu2022,
    Zhang2023,
]

#: the health of the training data: dulaglutide is given to people with type
#: 2 diabetes, the trials of the pharmacodynamics; the pharmacokinetics in
#: type 2 diabetes are named population validation
TRAINING_HEALTH: frozenset[Health] = frozenset({Health.HEALTHY, Health.T2DM})

#: the coadministrations of the training data: the oral background therapy of
#: the trials (metformin, a sulfonylurea, a thiazolidinedione), to which
#: dulaglutide is added. The background therapy lowers the baseline of the
#: glucose and the HbA1c, which the arms set, and does not change the
#: pharmacokinetics of an Fc fusion protein, which is catabolized like an
#: immunoglobulin (no CYP or transporter). Titrated insulin is no background
#: therapy (Blonde2015, `LIMITATION_VALIDATION`)
BACKGROUND_THERAPY: frozenset[Coadministration] = frozenset(
    {
        Coadministration.NONE,
        Coadministration.METFORMIN,
        Coadministration.GLIMEPIRIDE,
        Coadministration.ANTIHYPERGLYCEMIC_MEDICATION,
    }
)

#: the observable of the pharmacokinetics: dulaglutide in venous plasma
PK_OBSERVABLES: set[str] = {"Cvep_dul"}

#: the observables of the pharmacodynamics, the absolute series (the changes
#: from baseline are the same measurements and only drawn)
PD_OBSERVABLES: set[str] = {"fpg", "hba1c", "BW"}

#: mappings which are not fitted, the data is not usable; sbmlsim names an
#: outlier by its key alone, which must be the key of one mapping of all
#: studies
OUTLIER_MAPPINGS: NamedMappings = {
    # 0.05 mg: the concentrations are below the limit of quantification, the
    # arm has 3 patients and its FPG (-36 mg/dl) and HbA1c (-0.66 %) fall more
    # than at 0.3 and 1 mg
    "Barrington2011a": {
        "fm_dul_fpg_DUL005",
        "fm_dul_hba1c_DUL005",
        "fm_dul_bodyweight_DUL005",
    },
}

#: the validation of the doses: doses outside the range of the training
DOSE_VALIDATION: NamedMappings = {
    # 0.1 mg at twice the limit of quantification; 12 mg, supratherapeutic,
    # all subjects vomited
    "Barrington2011": {"fm_dul_DUL01", "fm_dul_DUL12"},
    # the titrations 0.5 -> 1.0 mg and 1.0 -> 2.0 mg (above the approved doses)
    "Umpierrez2011": {
        f"fm_dul_{arm}__{observable}"
        for arm in ["DUL0510", "DUL1020"]
        for observable in ["fpg", "hba1c", "bodyweight"]
    },
}

#: the validation of the populations: populations which the model predicts
#: without parameters of their own. `filter_health` lets the validation data
#: through for this reason
POPULATION_VALIDATION: NamedMappings = {
    # the groups with an impaired renal function, which the model simulates as
    # the control (no renal elimination of the Fc fusion protein; the AUC of
    # the groups lies within +7 to +29 % of the control without a trend with
    # the creatinine clearance)
    "FDAGBCM": {"fm_dul_mildR", "fm_dul_modR", "fm_dul_sevR", "fm_dul_ESR"},
    # the pharmacokinetics in type 2 diabetes on an oral background therapy:
    # CL/F 1.3-1.6-fold of the healthy subjects (Barrington2011a 0.157 vs
    # 0.107 l/hr), more than the body weight explains; the model has no
    # covariate of the diabetes, and as training data they shorten the
    # half-life to 70 hr (literature 90-113 hr) and raise the IV clearance by
    # 30 % (a fit with them as training data)
    "Barrington2011a": {
        f"fm_dul_dulaglutide_{arm}" for arm in ["DUL03", "DUL1", "DUL3", "DUL5", "DUL8"]
    },
    "Liu2025": {"fm_dul_DUL15__dulaglutide"},
    "Xu2022": {"fm_dul_DUL05M", "fm_dul_DUL075M", "fm_dul_DUL15M"},
    # healthy Chinese men, serum ELISA, a half-life of 63 hr (100-107 hr in
    # the studies of the FDA review)
    "Gao2024": {"fm_dul_DUL075"},
    # added to metformin and glimepiride with dose reductions of glimepiride
    # and rescue therapy, 78 weeks with a loss of the effect
    "Giorgino2015": {
        f"fm_dul_{arm}__{observable}"
        for arm in ["DUL075", "DUL15"]
        for observable in ["fpg", "hba1c", "bodyweight"]
    },
}

#: the validation of the interactions: no study of the model has an
#: interacting drug
INTERACTION_VALIDATION: NamedMappings = {}

#: the validation of the limitations of the model: valid data of a population,
#: a route, a product or a process the model does not describe, which would
#: distort the fitted parameters of the processes it does describe
LIMITATION_VALIDATION: NamedMappings = {
    # hepatic impairment: 21-33 % lower exposure without a trend over the
    # Child-Pugh classes and without a known mechanism, the model has no
    # hepatic elimination of dulaglutide
    "FDAGBDO": {"fm_dul_mildH", "fm_dul_modH", "fm_dul_sevH"},
    # the intramuscular injection, simulated as the subcutaneous one (relative
    # F 0.96, the same tmax)
    "FDAGBDR": {"fm_dul_DUL075IM"},
    # titrated insulin lispro in every arm, the model has no insulin; 293-295
    # patients per arm would dominate a fit
    "Blonde2015": {
        f"fm_dul_{observable}_{arm}"
        for arm in ["DUL075", "DUL15"]
        for observable in ["hba1c", "bodyweight"]
    },
    # 5 years, intention to treat with discontinuation and add-on therapy
    "Gerstein2019": {
        f"fm_dul_{arm}__{observable}"
        for arm in ["PLAC", "DUL15"]
        for observable in ["hba1c", "bodyweight"]
    },
    # pioglitazone titrated in the lead-in: placebo HbA1c -0.65 % at an
    # unchanged FPG and a weight gain of 1.4 kg, the model has no background
    # drug
    "Wysham2014": {
        "fm_dul_PLAC__hba1c",
        "fm_dul_PLAC__bodyweight",
        "fm_dul_DUL075__bodyweight",
        "fm_dul_DUL15__bodyweight",
    },
    # 4-6 weeks: the HbA1c falls by 1 % in 4 weeks (placebo -0.3 %), faster
    # than the turnover of the red cells
    "Xu2022": {
        f"fm_dul_{arm}__hba1c" for arm in ["DULPLAM", "DUL05M", "DUL075M", "DUL15M"]
    },
    # the biosimilar candidates HEC14028 and LY05008, other products
    "Gao2024": {"fm_dul_HEC14028"},
    "Liu2025": {
        f"fm_dul_LY05008__{observable}"
        for observable in ["dulaglutide", "fpg", "hba1c", "bodyweight"]
    },
}

#: the summaries of data which the fits use one by one, excluded from every
#: fit: a mean of subjects would count the subjects twice
AGGREGATE_MAPPINGS: NamedMappings = {
    # weeks 0-52 of AWARD-5 are the measurements of Nauck2014, Weinstock2015
    # contributes the second year (the `_ext` mappings)
    "Weinstock2015": {
        f"fm_dul_{arm}__{observable}"
        for arm in ["DUL075", "DUL15"]
        for observable in ["fpg", "hba1c", "bodyweight"]
    },
}

#: the validation questions by name
QUESTIONS: dict[str, NamedMappings] = {
    "doses": DOSE_VALIDATION,
    "populations": POPULATION_VALIDATION,
    "interactions": INTERACTION_VALIDATION,
    "limitations": LIMITATION_VALIDATION,
}

#: the validation data
VALIDATION_MAPPINGS: NamedMappings = {
    study: set().union(*(mappings.get(study, set()) for mappings in QUESTIONS.values()))
    for mappings in QUESTIONS.values()
    for study in mappings
}


def study(fit_mapping: FitMapping) -> str:
    """Get the study of a fit mapping, the id of its experiment."""
    return fit_mapping.reference.experiment.sid


def named(
    mappings: NamedMappings, fit_mapping_key: str, fit_mapping: FitMapping
) -> bool:
    """Check whether a fit mapping is one of the named mappings of its study."""
    return fit_mapping_key in mappings.get(study(fit_mapping), set())


def check_named(mappings: NamedMappings, fit_mappings: FitMappings) -> None:
    """Check that the named mappings are fit mappings of their studies.

    Raises:
        ValueError: for a study which is no experiment, or a key which is no fit
            mapping of its study.
    """
    for sid, keys in mappings.items():
        experiment = fit_mappings.experiments.get(sid)
        if experiment is None:
            raise ValueError(f"'{sid}' is no experiment of the fits.")
        if unknown := sorted(keys - set(experiment._fit_mappings)):
            raise ValueError(f"'{unknown}' are no fit mappings of '{sid}'.")


def filter_aggregates(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """No summaries of data which is fitted one by one, see `AGGREGATE_MAPPINGS`."""
    return not named(AGGREGATE_MAPPINGS, fit_mapping_key, fit_mapping)


def filter_health(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """No impaired renal or hepatic function, besides the validation data."""
    if named(VALIDATION_MAPPINGS, fit_mapping_key, fit_mapping):
        return True
    return mapping_metadata(fit_mapping).health in TRAINING_HEALTH


def filter_coadministration(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """No coadministered drug but the oral background therapy, besides the validation data."""
    if named(VALIDATION_MAPPINGS, fit_mapping_key, fit_mapping):
        return True
    return mapping_metadata(fit_mapping).coadministration in BACKGROUND_THERAPY


def mapping_collections(
    filters: list[MappingFilter],
    validation: NamedMappings = VALIDATION_MAPPINGS,
) -> dict[str, list[FitMappingCollection]]:
    """Select the data of a fit from the fit mappings of the studies.

    The filters select the training data, the mappings which fail them are
    excluded, and so are the summaries of data which is fitted one by one
    (`AGGREGATE_MAPPINGS`), the groups with an impairment (`filter_health`)
    and the arms with a coadministered drug which is no oral background
    therapy (`filter_coadministration`). The outliers are `OUTLIER_MAPPINGS`, the validation
    data is `VALIDATION_MAPPINGS`. Neither kind enters the cost; both are
    simulated and evaluated with the training data, so a report says how the
    fitted parameters describe data they were not fitted on.

    Args:
        filters: filters of the training data.
        validation: the keys of the validation data by study.

    Returns:
        The fit mapping collections of all kinds by experiment id.

    Raises:
        ValueError: if an outlier is a mapping of no study or of several.
    """
    fit_mappings = FitMappings(
        experiment_classes=EXPERIMENT_CLASSES,
        base_path=DULAGLUTIDE_PATH,
        data_path=DATA_PATHS,
    )
    for mappings in [OUTLIER_MAPPINGS, AGGREGATE_MAPPINGS, validation]:
        check_named(mappings, fit_mappings)
    # sbmlsim selects the outliers by their keys alone, which must name one
    # mapping of all studies
    outliers = {key for keys in OUTLIER_MAPPINGS.values() for key in keys}
    for key in outliers:
        studies = [
            sid
            for sid, experiment in fit_mappings.experiments.items()
            if key in experiment._fit_mappings
        ]
        if len(studies) != 1:
            raise ValueError(f"The outlier '{key}' is a mapping of {studies}.")
    selection = fit_mappings.select(
        filters=[
            *filters,
            filter_aggregates,
            filter_health,
            filter_coadministration,
        ],
        outliers=outliers,
        validation=lambda key, fit_mapping: named(validation, key, fit_mapping),
        print_info=False,
    )
    # the counts per experiment and kind, not the single mappings
    selection.print(detail=False)
    # the validation mappings by the question they answer
    selected = {
        (sid, key)
        for sid, kinds in selection.kinds.items()
        for key, kind in kinds.items()
        if kind is MappingKind.VALIDATION
    }

    def pairs(mappings: NamedMappings) -> set[tuple[str, str]]:
        return {(sid, key) for sid, keys in mappings.items() for key in keys}

    console.print(
        "validation: "
        + ", ".join(
            f"{len(selected & pairs(mappings))} {question}"
            for question, mappings in QUESTIONS.items()
        )
    )
    return selection.collections


def f_collections_pk() -> dict[str, list[FitMappingCollection]]:
    """Pharmacokinetic data: dulaglutide in plasma."""
    return mapping_collections([observable_filter(PK_OBSERVABLES)])


def f_collections_pd() -> dict[str, list[FitMappingCollection]]:
    """Pharmacodynamic data: fasting plasma glucose, HbA1c and body weight."""
    return mapping_collections([observable_filter(PD_OBSERVABLES)])


if __name__ == "__main__":
    for f in [f_collections_pk, f_collections_pd]:
        console.rule(title=f.__name__, align="left", style="white")
        f()
