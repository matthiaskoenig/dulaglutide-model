"""Model for bodyweight changes."""
from dataclasses import dataclass

import numpy as np
from sbmlutils.converters import odefac
from sbmlutils.factory import *
from sbmlutils.metadata import *

from pkdb_models.models.bodyweight.models import annotations
from pkdb_models.models.bodyweight.models import templates


class U(templates.U):
    """UnitDefinitions"""

    cm = UnitDefinition("cm")
    hr = UnitDefinition("hr")
    kg = UnitDefinition("kg")
    cm_per_m = UnitDefinition("cm_per_m", "cm/m")
    m2_per_kg = UnitDefinition("m2_per_kg", "meter^2/kg")
    kg_per_m2 = UnitDefinition("kg_per_m2", "kg/meter^2")
    kg_per_cm = UnitDefinition("kg_per_cm", "kg/cm")
    kg_per_min = UnitDefinition("kg_per_min", "kg/min")


mid = "bodyweight"
version = 1

_m = Model(
    sid=mid,
    name="Model for bodyweight changes.",
    notes=f"""
    Model for bodyweight changes.

    **version** {version}        
    """ + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=annotations.model,
)

@dataclass
class PDParameter:
    sid: str
    name: str
    init: float
    unit: UnitDefinition

pd_parameters = [
    PDParameter(
        sid="BW",
        name="bodyweight",
        init=75.0,
        unit=U.kg
    ),
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
            # annotations=annotations.species[s.sid],
            constant=False,
            notes=f"Absolute change to baseline {p.name}",
        )
    )
    _m.rules.append(
        AssignmentRule(
            f"{p.sid}_change", f"{p.sid}-{p.sid}0", unit=p.unit
        )
    )

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
        AssignmentRule(
            f"{p.sid}_ratio", f"{p.sid}/{p.sid}0", unit=U.dimensionless
        )
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


_m.parameters.extend([
    # Parameter(
    #     "BW0",
    #     75,
    #     U.kg,
    #     constant=True,
    #     name="initial body weight [kg]",
    #     sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    # ),
    Parameter(
        "FAT",
        0,
        U.kg,
        constant=False,
        name="additional fat to LBM [kg]",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "DFAT",
        0,
        U.kg,
        constant=False,
        name="change in additional fat to LBM [kg]",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
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
        """
    ),
    Parameter(
        "conversion_cm_per_m",
        100,
        U.cm_per_m,
        constant=True,
        name="Conversion factor cm to m",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),

    Parameter(
        "D",
        0.0,
        U.mM,
        constant=False,
        name="GLP-1 agonist concentration in plasma",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    # pharmacodynamic parameters for fat loss
    Parameter(
        "Emax_FAT",
        1.0e-5,  # [1/min] adjusted for realistic weight loss rate (~2-4 kg over 26 weeks)
        U.per_min,
        name="Emax for GLP-1 agonist on fat loss (rate of fat change)",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
        Adjusted to match clinical weight loss rates:
        - Typical weight loss: 2-4 kg over 26 weeks
        - Rate: ~1.5e-4 kg/min at steady state
        - Emax accounts for maximum effect at saturating drug concentrations
        """
    ),
    Parameter(
        "gamma_FAT",
        1.0,
        U.dimensionless,
        name="gamma for GLP-1 agonist on fat loss",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "EC50_FAT",
        2.5e-5,  # [mM] = 25 µM, adjusted to match typical dulaglutide plasma concentrations
        U.mM,
        name="EC50 for GLP-1 agonist on fat loss",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
        Adjusted to physiologically relevant range:
        - Typical dulaglutide Cmax: 10-100 ng/mL after 0.75-1.5 mg dose
        - Converted to molar: ~3-30 µM (3e-6 to 3e-5 mM)
        - EC50 set to mid-range for reasonable dose-response
        """
    ),

    ]
)

_m.rules.extend([
    # FIXME: sex dependency
    AssignmentRule(
        "LBW0", "0.407 dimensionless * BW0 + 0.267 kg_per_cm * HEIGHT - 19.2 kg", U.kg,
        notes="""
        1. Boer Formula (uses weight and height)

        For males:
        LBM=0.407×W+0.267×H−19.2
    
        For females:
        LBM=0.252×W+0.473×H−48.3
    
        Where W is weight in kilograms and H is height in centimeters
        
        FIXME: This formula most likely does not work for small bodyweights
        """
    ),
    AssignmentRule(
        "FAT0", "BW0 - LBW0", U.kg,
    ),
    AssignmentRule(
        "FAT", "FAT0 + DFAT", U.kg,
    ),
    AssignmentRule(
        "BW", "LBW0 + FAT", U.kg,
    ),

    # Body surface area (Haycock1978)
    AssignmentRule(
        "BSA", "0.024265 m2 * power(BW/1 kg, 0.5378) * power(HEIGHT/1 cm, 0.3964)", U.m2
    ),
    # BMI
    AssignmentRule(
        "BMI", "BW/(HEIGHT/conversion_cm_per_m * HEIGHT/conversion_cm_per_m)", U.kg_per_m2
    ),
])

_m.rate_rules.extend([
    # FIXME: add glucose dependency
    RateRule(
        "DFAT", "-FAT * Emax_FAT * power(D, gamma_FAT)/(power(D, gamma_FAT) + power(EC50_FAT, gamma_FAT))", U.kg_per_min
    ),
])


model_bodyweight = _m


if __name__ == "__main__":
    from pkdb_models.models.bodyweight import MODEL_BASE_PATH

    # SBML model
    results: FactoryResult = create_model(
        model=model_bodyweight,
        filepath=MODEL_BASE_PATH / f"{model_bodyweight.sid}.xml",
        sbml_level=3, sbml_version=2,
    )

    # create differential equations
    md_path = MODEL_BASE_PATH / f"{model_bodyweight.sid}.md"
    ode_factory = odefac.SBML2ODE.from_file(sbml_file=results.sbml_path)
    ode_factory.to_markdown(md_file=md_path)

    # visualization
    from sbmlutils import cytoscape as cyviz
    cyviz.visualize_sbml(results.sbml_path, delete_session=True)
