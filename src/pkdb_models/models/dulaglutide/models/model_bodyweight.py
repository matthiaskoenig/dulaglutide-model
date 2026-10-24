"""Body weight model of dulaglutide: lean body weight and fat, and the fat loss.

The body weight is the lean body weight and the fat, the fat the visceral and
the subcutaneous fat. The GLP-1 agonist reduces the subcutaneous fat. The GLP-1
models (dulaglutide, liraglutide, lixisenatide) share this model, each has its
own copy with the values of its drug. The factory merges it with the HbA1c
model and the body model, which defines the GLP-1 agonist concentration `glp1`
(dulaglutide in venous plasma) with an assignment rule, so this model does not
define it.
"""

from dataclasses import dataclass

import numpy as np
from pkpdsim.templates import terms_of_use
from sbmlutils.factory import (
    AssignmentRule,
    Creator,
    Model,
    Parameter,
    RateRule,
    UnitDefinition,
)
from sbmlutils.metadata import BQB, SBO

from pkdb_models.models.dulaglutide.models import templates
from pkdb_models.models.dulaglutide.models.fits import FITS


class U(templates.U):
    """Units of the body weight model."""

    cm = UnitDefinition("cm")
    hr = UnitDefinition("hr")
    kg = UnitDefinition("kg")
    l_per_kg = UnitDefinition("l_per_kg", "l/kg")
    cm_per_m = UnitDefinition("cm_per_m", "cm/m")
    m2_per_kg = UnitDefinition("m2_per_kg", "meter^2/kg")
    kg_per_m2 = UnitDefinition("kg_per_m2", "kg/meter^2")
    kg_per_cm = UnitDefinition("kg_per_cm", "kg/cm")
    kg_per_min = UnitDefinition("kg_per_min", "kg/min")


creators = [
    Creator(
        familyName="Kim",
        givenName="Minjun",
        email="kim.minjun@u.nus.edu",
        organization="National University of Singapore, Department of Statistics and Data Science",
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
    # biological process explained by model (GO/NCIT)
    (BQB.HAS_PROPERTY, "NCIT:C81328"),  # body weight
]

version = 1

_m = Model(
    sid="bodyweight",
    name="Model for bodyweight changes.",
    notes=f"""
    Model for bodyweight composition and changes.

    Handles bodyweight as a combination of LBW (lean body weight)
    and additional fat tissue. The fat tissue is distinguished in core
    fat (which is very difficult to loose and has physiological function) and
    additional fat depots which can be lost easily.

    There are sex differences in the bodyweight composition, mainly in
    LBW due to differences in mainly muscle mass and fat tissue (women have
    higher baseline body fat).

    At the same BMI, women on average have about 8–10 percentage points higher body fat
    than men throughout adulthood.
    [PMID:22651247]
    Subcutaneous white adipose tissue (**SAT**) depots, just
    under the skin, store ~80-90% of total body fat, mainly
    in the abdominal (around the waist), subscapular (on the
    upper back), gluteal and femoral (thigh) areas.

    Essential body fat (minimum needed for normal physiology) is higher
    in women (roughly 10–13%) than in men (roughly 2–5%)
    Intraabdominal depots include visceral adipose tissues (**VAT**,
    omental and mesenteric), which are associated with di-
    gestive organs. VATs drain their blood into the portal vein
    and account for 6-20% of total body fat, with higher values
    in males than females [9-12].

    Men tend to have more lean mass (muscle and bone),
    while women have proportionally more fat mass.

    For the same body mass index (BMI), women typically
    present with ~10% higher body fat compared to men
    [19,20]. Aging increases adiposity in both sexes, but again,
    women are characterized by higher percent body fat
    throughout the entire life span [21].



    **version** {version}
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


pd_parameters = [
    PDParameter(sid="BW", name="bodyweight", init=75.0, unit=U.kg),
]

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

    # dynamic parameter
    _m.parameters.append(
        Parameter(
            p.sid,
            p.init,
            p.unit,
            constant=False,
            name=p.name,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
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


_m.parameters.extend(
    [
        Parameter(
            "FAT",
            0,
            U.kg,
            constant=False,
            name="additional fat to LBM [kg]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "FVad",
            np.nan,
            U.l_per_kg,
            constant=False,
            name="adipose tissue volume",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "DSAT",
            0,
            U.kg,
            constant=False,
            name="change in additional fat to LBM [kg]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
        Mainly SAT.
        """,
        ),
        Parameter(
            "HEIGHT",
            170,
            U.cm,
            name="height [cm]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "SEX",
            0,
            U.dimensionless,
            constant=True,
            name="sex",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
        Flag to switch sex in model:
        0: male,
        1: female,
        """,
        ),
        Parameter(
            "conversion_cm_per_m",
            100,
            U.cm_per_m,
            constant=True,
            name="Conversion factor cm to m",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        # pharmacodynamic parameters of the fat loss: the GLP-1 agonist lowers
        # the set point of the subcutaneous fat by the fraction E(glp1), the
        # fat relaxes to it with the rate k_SAT_glp1
        Parameter(
            "Emax_SAT_glp1",
            **FITS.parameter("Emax_SAT_glp1", unit=U.dimensionless),
            name="maximal effect of the GLP-1 agonist on the subcutaneous fat (fraction)",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
        The fraction of the subcutaneous fat which is lost at a saturating
        concentration; the trials lose 1-3 kg of 10-20 kg of subcutaneous fat
        after 0.75 and 1.5 mg weekly.
        """,
        ),
        Parameter(
            "gamma_SAT_glp1",
            1.0,
            U.dimensionless,
            name="gamma for GLP-1 agonist on fat loss",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "EC50_SAT_glp1",
            **FITS.parameter("EC50_SAT_glp1", unit=U.mM),
            name="EC50 for GLP-1 agonist on fat loss",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
        The dulaglutide plasma concentration at steady state is about 1 nM
        (60 ng/ml) after weekly doses of 1.5 mg.
        """,
        ),
        Parameter(
            "k_SAT_glp1",
            **FITS.parameter("k_SAT_glp1", unit=U.per_min),
            name="rate of the change of the subcutaneous fat",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
        A time constant of about 10 weeks, the body weight of the trials
        plateaus at 26-52 weeks.
        """,
        ),
    ]
)


# The body composition is initialized at time 0, afterwards it changes
# dynamically:
#   BW0 = LBW0 + VAT0 + SAT0
#   d LBW/dt = 0  (simplification: muscle could be lost or gained)
#   d VAT/dt = 0  (essential visceral fat, which does not change normally,
#                  except at extremely low body weights)
#   d SAT/dt      (weight loss or weight gain)
_m.rules.extend(
    [
        # initial variables
        AssignmentRule(
            "LBW0",
            "piecewise(0.407 dimensionless * BW0 + 0.267 kg_per_cm * HEIGHT - 19.2 kg, SEX==0,"
            "0.252 dimensionless * BW0 + 0.473 kg_per_cm * HEIGHT - 48.3 kg, SEX==1)",
            U.kg,
            notes="""
        1. Boer Formula (uses weight and height)

        For males:
        LBW0 = 0.407×W + 0.267×H − 19.2

        For females:
        LBM0 = 0.252×W + 0.473×H − 48.3

        Where W is weight in kilograms and H is height in centimeters
        """,
        ),
        AssignmentRule(
            "VAT0",
            "piecewise(min(BW0-LBW0, 0.2 dimensionless * LBW0), SEX==0, "
            "min(BW0-LBW0, 0.1 dimensionless * LBW0), SEX==1)",
            U.kg,  # < FAT0 = BW0 - LBW0
            notes="""
        Essential body fat (minimum needed for normal physiology) is higher
        in women (roughly 10–13%) than in men (roughly 2–5%)

        Intraabdominal depots include visceral adipose tissues (**VAT**,
        omental and mesenteric), which are associated with di-
        gestive organs. VATs drain their blood into the portal vein
        and account for 6-20% of total body fat, with higher values
        in males than females [9-12].

        For males:
        VAT0 = 0.2 * LBW0

        For females:
        VAT0 = 0.1 * LBW0
        """,
        ),
        AssignmentRule(
            "FAT0",
            "BW0 - LBW0",
            U.kg,
            notes="""
        BW0 = LBW0 + VAT0 + SAT0 = LBWO + FAT0
        """,
        ),
        AssignmentRule(
            "SAT0",
            "FAT0 - VAT0",
            U.kg,
        ),
        # time dependent variables
        AssignmentRule(
            "LBW", "LBW0", U.kg, notes="""Lean body weight assumed constant."""
        ),
        AssignmentRule(
            "VAT",
            "VAT0",
            U.kg,
            notes="""VAT assumed constant.
        Essential fat, not touched in weight loss/gain.
        """,
        ),
        AssignmentRule(
            "BW",
            "LBW + FAT",
            U.kg,
        ),
        AssignmentRule("FAT", "VAT + SAT", U.kg, notes="""Total fat."""),
        AssignmentRule("SAT", "SAT0 + DSAT", U.kg, notes="""Total fat."""),
        # body surface area (Haycock1978)
        AssignmentRule(
            "BSA",
            "0.024265 m2 * power(BW/1 kg, 0.5378) * power(HEIGHT/1 cm, 0.3964)",
            U.m2,
        ),
        # BMI
        AssignmentRule(
            "BMI",
            "BW/(HEIGHT/conversion_cm_per_m * HEIGHT/conversion_cm_per_m)",
            U.kg_per_m2,
        ),
        # fractional tissue volume adipose tissue
        AssignmentRule(
            "FVad",
            "FAT/BW * 1 l_per_kg",
            U.l_per_kg,
        ),
        AssignmentRule("BFF", "FAT/BW", U.dimensionless, name="body fat fraction"),
    ]
)

# The subcutaneous fat relaxes to its set point, the baseline lowered by the
# effect of the GLP-1 agonist: d DSAT/dt = k_SAT * (-SAT0 * E(glp1) - DSAT), so
# the fat loss ends at SAT0 * E(glp1) and is restored after the end of the
# treatment. The fat loss does not depend on the fasting plasma glucose.
_m.rate_rules.extend(
    [
        RateRule(
            "DSAT",
            "k_SAT_glp1 * (-SAT0 * Emax_SAT_glp1 * power(glp1, gamma_SAT_glp1)/"
            "(power(glp1, gamma_SAT_glp1) + power(EC50_SAT_glp1, gamma_SAT_glp1)) - DSAT)",
            U.kg_per_min,
        ),
    ]
)


model_bodyweight: Model = _m
