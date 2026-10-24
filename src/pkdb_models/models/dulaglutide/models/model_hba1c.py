"""HbA1c model of dulaglutide: the fasting plasma glucose and the glycation of hemoglobin.

The GLP-1 agonist lowers the excess of the fasting plasma glucose (FPG) over
the normal FPG, the FPG glycates hemoglobin to HbA1c. The GLP-1 models
(dulaglutide, liraglutide, lixisenatide) share this model, each has its own
copy with the values of its drug. The factory merges it with the body weight
model and the body model, which assigns the GLP-1 agonist concentration `glp1`
(dulaglutide in venous plasma).

The baselines `hba1c0` and `fpg0` of a subject are the only values an
experiment sets: the HbA1c, the hemoglobin and the FPG start at them, and the
glycation rate `k_hb_gly` is set so that the HbA1c is at steady state at the
baseline FPG (no drift without the drug).
"""

from dataclasses import dataclass

import numpy as np
from pkpdsim.templates import terms_of_use
from sbmlutils.factory import (
    AssignmentRule,
    Compartment,
    Creator,
    InitialAssignment,
    Model,
    Parameter,
    Reaction,
    Species,
    UnitDefinition,
)
from sbmlutils.metadata import BQB, SBO

from pkdb_models.models.dulaglutide.models import templates
from pkdb_models.models.dulaglutide.models.fits import FITS


class U(templates.U):
    """Units of the HbA1c model."""

    cm = UnitDefinition("cm")
    hr = UnitDefinition("hr")
    kg = UnitDefinition("kg")
    cm_per_m = UnitDefinition("cm_per_m", "cm/m")
    m2_per_kg = UnitDefinition("m2_per_kg", "meter^2/kg")
    kg_per_m2 = UnitDefinition("kg_per_m2", "kg/meter^2")
    kg_per_cm = UnitDefinition("kg_per_cm", "kg/cm")
    kg_per_min = UnitDefinition("kg_per_min", "kg/min")
    l_per_mmole = UnitDefinition("l_per_mmole", "l/mmole")
    l_per_min_mmole = UnitDefinition("l_per_min_mmole", "l/(min*mmole)")
    l2_per_min_mmole = UnitDefinition("l2_per_min_mmole", "(l*l)/(min*mmole)")
    mM_per_mg = UnitDefinition("mM_per_mg", "(mmole/l)/mg")


creators = [
    Creator(
        familyName="Kim",
        givenName="Minjun",
        email="kim.minjun@u.nus.edu",
        organization="National University of Singapore",
    ),
    Creator(
        familyName="Tan",
        givenName="Isabella",
        email="bella.tan@mail.utoronto.ca",
        organization="University of Toronto",
    ),
    Creator(
        familyName="Yau",
        givenName="Olivia",
        email="oliviaayau@gmail.com",
        organization="University of Toronto",
    ),
    Creator(
        familyName="König",
        givenName="Matthias",
        email="koenigmx@hu-berlin.de",
        organization="Humboldt-Universität zu Berlin, Faculty of Life Sciences, Department of Biology, Institute of Theoretical Biology, Systems Medicine of the Liver; University of Stuttgart, Institute of Structural Mechanics and Dynamics in Aerospace Engineering",
        site="https://livermetabolism.com",
    ),
]

annotations_model = [
    # taxonomy
    (BQB.HAS_TAXON, "taxonomy/9606"),  # human
    (BQB.HAS_TAXON, "snomedct/337915000"),  # human
    # modelling approach
    (BQB.HAS_PROPERTY, "mamo/MAMO_0000046"),  # ordinary differential equation model
]

annotations_species = {
    "fpg": [(BQB.IS_VERSION_OF, "SNOMEDCT:167096006")],
    "hb": [(BQB.IS, "CHEBI:35143")],  # hemoglobin
    "hba1c": [
        (BQB.IS_VERSION_OF, "CHEBI:35143"),  # hemoglobin
        (BQB.IS_VERSION_OF, "NCIT:C64849"),
        (BQB.IS_VERSION_OF, "EFO:0004541"),
    ],
}

annotations_plasma = [
    (BQB.IS, "ncit/C13356"),
    (BQB.IS, "bto/BTO:0000131"),
]

_m = Model(
    sid="hba1c_model",
    name="Model for hba1c and FPG changes.",
    notes="""
    Model for hba1c changes.

    **version 3**
    - HbA1c at steady state at the baselines (`k_hb_gly` initial assignment),
      glycation with the glucose offset of the ADAG relation (`G_off_fpg`)
    - the GLP-1 agonist and the trial lower the excess FPG over `fpg_norm`
      by fractions (`Emax_glp1_fpg`, `f_trial_fpg`)

    **version 2**
    - moved to species and reactions

    **version 1**
    initial model
    """
    + terms_of_use,
    creators=creators,
    units=U,
    model_units=templates.model_units,
    annotations=annotations_model,
)


@dataclass
class PDParameter:
    """Pharmacodynamic quantity with its baseline and its changes to the baseline."""

    sid: str
    name: str
    init: float
    unit: UnitDefinition
    substance_unit: UnitDefinition


pd_parameters = [
    PDParameter(
        sid="hba1c",
        name="HbA1c",
        init=0.05,
        unit=U.dimensionless,
        substance_unit=U.dimensionless,
    ),
    PDParameter(
        sid="fpg",
        name="fasting plasma glucose (FPG)",
        init=5.0,
        unit=U.mM,
        substance_unit=U.mmole,
    ),
]
pd_parameters_dict = {p.sid: p for p in pd_parameters}

_m.parameters = [
    Parameter(
        sid="cf_units_per_mmole",
        value=1.0,
        unit=U.per_mmole,
        name="conversion factor for dimensionless species",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
]

_m.compartments.append(
    Compartment(
        "Vext",
        value=1.5,
        unit=U.liter,
        name="plasma",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations_plasma,
        port=True,
    )
)

# dynamic species: HbA1c is a fraction of the hemoglobin (an amount), FPG a
# concentration
for p in pd_parameters:
    if p.unit == U.dimensionless:
        _m.species.append(
            Species(
                p.sid,
                initialAmount=p.init,
                substanceUnit=p.substance_unit,
                hasOnlySubstanceUnits=True,
                name=p.name,
                sboTerm=SBO.SIMPLE_CHEMICAL,
                conversionFactor="cf_units_per_mmole",
                compartment="Vext",
                annotations=annotations_species[p.sid],
            )
        )
    else:
        _m.species.append(
            Species(
                p.sid,
                initialAmount=p.init,
                substanceUnit=p.substance_unit,
                hasOnlySubstanceUnits=False,
                name=p.name,
                sboTerm=SBO.SIMPLE_CHEMICAL,
                compartment="Vext",
                annotations=annotations_species[p.sid],
            )
        )


# relative changes
for p in pd_parameters:
    # reference parameter (set initially), initial parameter
    _m.parameters.append(
        Parameter(
            f"{p.sid}0",
            p.init,
            p.unit,
            constant=True,
            name=p.name,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
    )
    _m.assignments.append(
        InitialAssignment(p.sid, f"{p.sid}0", unit=p.unit),
    )

    # absolute change
    _m.parameters.append(
        Parameter(
            f"{p.sid}_change",
            name=f"{p.name} change",
            value=np.nan,
            unit=p.unit,
            constant=False,
            notes=f"Absolute change to baseline {p.name}",
        )
    )
    _m.rules.append(AssignmentRule(f"{p.sid}_change", f"{p.sid}-{p.sid}0", unit=p.unit))

    # ratio to baseline
    _m.parameters.append(
        Parameter(
            f"{p.sid}_ratio",
            name=f"{p.name} ratio",
            value=np.nan,
            unit=U.dimensionless,
            constant=False,
            notes=f"Ratio relative to baseline {p.name}",
        )
    )
    _m.rules.append(
        AssignmentRule(f"{p.sid}_ratio", f"{p.sid}/{p.sid}0", unit=U.dimensionless)
    )

    # relative change to baseline
    _m.parameters.append(
        Parameter(
            f"{p.sid}_relchange",
            name=f"{p.name} relative change",
            value=np.nan,
            unit=U.dimensionless,
            constant=False,
            notes=f"Change relative to baseline {p.name}",
        )
    )
    _m.rules.append(
        AssignmentRule(
            f"{p.sid}_relchange", f"({p.sid}-{p.sid}0)/{p.sid}0", unit=U.dimensionless
        )
    )


# total amount is 1.0
p_hba1c = pd_parameters_dict["hba1c"]
_m.species.extend(
    [
        Species(
            "hb",
            initialAmount=1.0 - p_hba1c.init,
            substanceUnit=p_hba1c.substance_unit,
            hasOnlySubstanceUnits=True,
            name="Hb total",
            sboTerm=SBO.SIMPLE_CHEMICAL,
            conversionFactor="cf_units_per_mmole",
            compartment="Vext",
            annotations=annotations_species["hb"],
        ),
        Species(
            "hb_total",
            initialAmount=1.0,
            substanceUnit=p_hba1c.substance_unit,
            hasOnlySubstanceUnits=True,
            name="Hb total",
            sboTerm=SBO.SIMPLE_CHEMICAL,
            conversionFactor="cf_units_per_mmole",
            compartment="Vext",
            annotations=annotations_species["hb"],
        ),
    ]
)

_m.parameters.append(
    Parameter(
        "hb0",
        1 - p_hba1c.init,
        p_hba1c.unit,
        constant=False,
        name="Hb (baseline)",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="The non-glycated hemoglobin at the baseline, `1 - hba1c0`.",
    )
)
_m.rules.append(
    AssignmentRule("hb0", "1 dimensionless - hba1c0", unit=U.dimensionless),
)
_m.assignments.append(
    InitialAssignment("hb", "1 dimensionless - hba1c0", unit=U.dimensionless),
)
_m.rules.append(
    AssignmentRule("hb_total", "hb + hba1c", unit=U.dimensionless),
)

# --- FPG turnover ---
# The FPG relaxes with `k_fpg` to its target `fpg_baseline`: the baseline FPG
# `fpg0` with its excess over the normal FPG `fpg_norm` lowered by the trial
# effect `f_trial_fpg` (diet, exercise and adherence in a clinical trial, every
# arm, placebo included) and by the GLP-1 agonist (`Emax_glp1_fpg`,
# `EC50_glp1_fpg`). Both are fractions of the excess FPG, so the response
# depends on the baseline FPG (the main covariate of the FPG response, FDA
# clinical pharmacology review BLA 125469), a subject at the normal FPG (5 mM)
# has no response and no hypoglycemia.
_m.parameters.extend(
    [
        Parameter(
            "glp1",
            0,
            U.mM,
            constant=True,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="GLP-1 agonist plasma concentration [mM]",
        ),
        Parameter(
            "fpg_baseline",
            5.0,
            U.mM,
            constant=False,
            name="target fasting plasma glucose",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "fpg_norm",
            5.0,
            U.mM,
            constant=True,
            name="normal fasting plasma glucose",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="The FPG which neither the GLP-1 agonist nor the trial lowers.",
        ),
        Parameter(
            "k_fpg",
            **FITS.parameter("k_fpg", unit=U.l_per_min),
            constant=True,
            name="rate normalization FPG with GLP-1 agonist",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            With the volume 1.5 l the FPG relaxes to its target with a
            half-life of about 2 days.
            """,
        ),
        Parameter(
            "Emax_glp1_fpg",
            **FITS.parameter("Emax_glp1_fpg", unit=U.dimensionless),
            constant=True,
            name="maximal effect of the GLP-1 agonist on the excess FPG (fraction)",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "EC50_glp1_fpg",
            **FITS.parameter("EC50_glp1_fpg", unit=U.mM),
            constant=True,
            name="EC50 of the GLP-1 agonist on the excess FPG",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            The dulaglutide plasma concentration at steady state is about
            1 nM (60 ng/ml) after weekly doses of 1.5 mg.
            """,
        ),
        Parameter(
            "f_trial_fpg",
            **FITS.parameter("f_trial_fpg", unit=U.dimensionless),
            constant=True,
            name="trial effect on the excess FPG (fraction)",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            The effect of a clinical trial (diet and exercise advice,
            adherence) on the excess FPG, in every arm: the FPG of the placebo
            arms falls by about 0.5 mM from 9 mM.
            """,
        ),
    ]
)
_m.rules.extend(
    [
        AssignmentRule(
            "fpg_baseline",
            "fpg0 - max(fpg0 - fpg_norm, 0 mM) * "
            "(1 dimensionless - (1 dimensionless - f_trial_fpg) * "
            "(1 dimensionless - Emax_glp1_fpg * glp1 / (EC50_glp1_fpg + glp1)))",
            unit=U.mM,
        ),
    ]
)


_m.reactions.extend(
    [
        Reaction(
            "FPGC",
            name="fpg change",
            equation="fpg -> ",
            sboTerm=SBO.BIOCHEMICAL_REACTION,
            compartment="Vext",
            formula=(
                "k_fpg * (fpg - fpg_baseline)",  # l/min * mmole/l
                U.mmole_per_min,
            ),
        ),
    ]
)


# --- HB turnover ---
# Hemoglobin is synthesized and degraded with the turnover of the erythrocytes
# (`k_hb_deg`), the total hemoglobin stays 1. Hemoglobin is glycated with the
# FPG plus the glucose offset `G_off_fpg`, the intercept of the ADAG relation
# of the mean glucose and the HbA1c (AG [mM] = 1.59 * HbA1c [%] - 2.59,
# Nathan2008); the glycation rate `k_hb_gly` is set so that the HbA1c is at
# steady state at the baselines `hba1c0` and `fpg0`.
_m.parameters.extend(
    [
        Parameter(
            "k_hb_deg",
            **FITS.parameter("k_hb_deg", unit=U.mmole_per_min),
            constant=True,
            name="hb degradation rate",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            The turnover rate of the hemoglobin fractions, which are amounts
            of the extent 1 mmole (conversion factor `cf_units_per_mmole`), so
            the unit is mmole/min for a rate in 1/min. The HbA1c relaxes with
            the rate `k_hb_deg / (1 - hba1c0)`, a time constant of about
            4.5 weeks; the HbA1c of the trials plateaus at
            12-16 weeks (Nauck2014, Morioka2024, Pratley2018).
            """,
        ),
        Parameter(
            "k_hb_syn",
            np.nan,
            U.mmole_per_min,
            constant=False,
            name="hb synthesis rate",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
    set based on turnover of erythrocytes
    """,
        ),
        Parameter(
            "G_off_fpg",
            2.59,
            U.mM,
            constant=True,
            name="glucose offset of the glycation",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="Intercept of the ADAG relation (Nathan2008).",
        ),
        Parameter(
            "k_hb_gly",
            np.nan,
            U.l_per_min,
            constant=True,
            name="hb glycation rate",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            Set so that the HbA1c is at steady state at the baselines:
            `k_hb_gly * (fpg0 + G_off_fpg) * (1 - hba1c0) = k_hb_deg * hba1c0`.
            """,
        ),
    ]
)
_m.assignments.append(
    InitialAssignment(
        "k_hb_gly",
        "k_hb_deg * hba1c0 / ((1 dimensionless - hba1c0) * (fpg0 + G_off_fpg))",
        unit=U.l_per_min,
    )
)
_m.rules.append(
    AssignmentRule(
        "k_hb_syn",
        "k_hb_deg",
        unit=U.mmole_per_min,
        notes="""Synthesis rate set to turnover rate for steady state.""",
    )
)

_m.reactions.extend(
    [
        Reaction(
            "HBSYN",
            name="HB synthesis",
            equation=" -> hb",
            sboTerm=SBO.BIOCHEMICAL_REACTION,
            compartment="Vext",
            formula=(
                "k_hb_syn",
                U.mmole_per_min,
            ),
        ),
        Reaction(
            "HBDEG",
            name="HB degradation",
            equation="hb -> ",
            sboTerm=SBO.BIOCHEMICAL_REACTION,
            compartment="Vext",
            formula=(
                "k_hb_deg * hb",
                U.mmole_per_min,
            ),
        ),
        Reaction(
            "HBA1CDEG",
            name="HBA1C degradation",
            equation="hba1c -> ",
            sboTerm=SBO.BIOCHEMICAL_REACTION,
            compartment="Vext",
            formula=(
                "k_hb_deg * hba1c",
                U.mmole_per_min,
            ),
        ),
        Reaction(
            "HBGLYC",
            name="HB glycation",
            equation="hb -> hba1c [fpg]",
            sboTerm=SBO.BIOCHEMICAL_REACTION,
            compartment="Vext",
            formula=(
                "k_hb_gly * (fpg + G_off_fpg) * hb",
                U.mmole_per_min,
            ),
        ),
    ]
)

model_hba1c: Model = _m
