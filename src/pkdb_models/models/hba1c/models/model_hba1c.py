"""Model for HBA1C changes."""
from dataclasses import dataclass

import numpy as np
from sbmlutils.converters import odefac
from sbmlutils.factory import *
from sbmlutils.metadata import *

from pkdb_models.models.hba1c.models import annotations
from pkdb_models.models.hba1c.models import templates


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
    l_per_mmole = UnitDefinition("l_per_mmole", "l/mmole")
    l_per_min_mmole = UnitDefinition("l_per_min_mmole", "l/(min*mmole)")
    l2_per_min_mmole = UnitDefinition("l2_per_min_mmole", "(l*l)/(min*mmole)")


mid = "hba1c_model"

_m = Model(
    sid=mid,
    name="Model for hba1c and FPG changes.",
    notes=f"""
    Model for hba1c changes.

    **version 2**
    - moved to species and reactions

    **version 1**
    initial model        
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
    )
]
pd_parameters_dict = {p.sid:p for p in pd_parameters}

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
        annotations=annotations.compartments["plasma"],
        port=True
    )
)

# dynamic species
for p in pd_parameters:
    if p.unit == U.dimensionless:
        s = Species(
            p.sid,
            initialAmount=p.init,
            substanceUnit=p.substance_unit,
            hasOnlySubstanceUnits=True,
            name=p.name,
            sboTerm=SBO.SIMPLE_CHEMICAL,
            conversionFactor="cf_units_per_mmole",
            compartment="Vext",
            annotations=annotations.species[p.sid],
        )
    elif p.unit == U.mM:
        s = Species(
            p.sid,
            initialAmount=p.init,
            substanceUnit=p.substance_unit,
            hasOnlySubstanceUnits=False,
            name=p.name,
            sboTerm=SBO.SIMPLE_CHEMICAL,
            compartment="Vext",
            annotations = annotations.species[p.sid],
        )

    _m.species.append(s)


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


# total amount is 1.0
p_hba1c = pd_parameters_dict["hba1c"]
_m.species.extend([
    Species(
        "hb",
        initialAmount=1.0 - p_hba1c.init,
        substanceUnit=p_hba1c.substance_unit,
        hasOnlySubstanceUnits=True,
        name="Hb total",
        sboTerm=SBO.SIMPLE_CHEMICAL,
        conversionFactor="cf_units_per_mmole",
        compartment="Vext",
        annotations=annotations.species["hb"],
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
        annotations=annotations.species["hb"],
    ),
])
_m.assignments.append(
    InitialAssignment("hb", f"1.0 dimensionless - hba1c0", unit=U.dimensionless),
)
_m.rules.append(
    AssignmentRule("hb_total", f"hb + hba1c0", unit=U.dimensionless),
)



# --- GLP1 drug effect ---
_m.parameters.extend([
    Parameter(
        "glp1",
        0.0,
        U.mM,
        constant=False,
        name="GLP-1 agonist concentration in plasma",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "E_glp1",
        0.0,
        U.dimensionless,
        constant=False,
        name="Effect of glp1",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "EC50_glp1",
        25E-6,  # [mM] 25 nM
        U.mM,
        name="half-maximal effective concentration",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "Emax_glp1",
        1.0,  # maximum efficacy
        U.dimensionless,
        name="maximum drug efficacy",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""Maximum effect between 0 an 1"""
    ),
    Parameter(
        "gamma_glp1",
        1.0,  # [dimensionless] - Hill coefficient
        U.dimensionless,
        constant=True, #keep as 1 for now, adjustable if needed, but avoid it..?
        name="Hill coefficient",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
])
_m.rules.extend([
    AssignmentRule(
        "E_glp1",
        "Emax_glp1 * power(glp1, gamma_glp1) / (power(EC50_glp1, gamma_glp1) + power(glp1, gamma_glp1))",
        unit=U.dimensionless,
        name="Hill equation for drug effect",
        notes="""
        Effect of GLP-1 inhibitor.
        Modelled via hill equation.
        """
    ),
])

# --- FPG turnover ---
_m.parameters.extend([
    Parameter(
        "fpg_healthy",
        5.0,
        U.mM,
        constant=True,
        name="healthy fasting plasma glucose",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "k_fpg",
        1.0,
        U.l2_per_min_mmole,
        constant=True,
        name="rate normalization FPG with GLP-1 agonist",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
])

_m.reactions.extend([
    Reaction(
        "FPGC",
        name="fpg change",
        equation="fpg -> ",
        sboTerm=SBO.BIOCHEMICAL_REACTION,
        compartment="Vext",
        formula=(
            # FIXME: improve equation
            "k_fpg * glp1 * (fpg - fpg_healthy)",  # mmole/l * mmole/l   (l*l)/(min*mmole)
            U.mmole_per_min,
        ),
    ),
])



# HB turnover
k_turnover = np.log(2) / (3 * 30 * 24 * 60)   # [1/min]
_m.parameters.extend([
    Parameter(
        "k_hb_syn",
        k_turnover,
        U.mmole_per_min,
        constant=False,
        name="hb synthesis rate",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
        set based on turnover of erythrocytes
        """
    ),
    Parameter(
        "k_hb_turn",
        k_turnover,
        U.mmole_per_min,
        constant=False,
        name="hb turnover rate",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
    halflife turnover of erythrocytes of tau = 4 month
    k = ln(2) / (4 * 30 * 24 * 60) [1/min]
    """
    ),
    Parameter(
        "k_hb_gly",
        (k_turnover * 0.05) / 5,
        U.l_per_min,
        constant=False,
        name="hb glycation rate",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
    set so that the HbA1c is 5% at steady state for 5 mM FPG
    """
    ),
])
_m.reactions.extend([
    Reaction(
        "HBSYN",
        name="HB synthesis",
        equation=" -> hb",
        sboTerm=SBO.BIOCHEMICAL_REACTION,
        compartment="Vext",
        formula=(
            "k_hb_syn",
            U.mmole_per_min,  # check units
        ),
    ),
    Reaction(
        "HBDEG",
        name="HB degradation",
        equation="hb -> ",
        sboTerm=SBO.BIOCHEMICAL_REACTION,
        compartment="Vext",
        formula=(
            "k_hb_turn * hb",
            U.mmole_per_min,  # check units
        ),
    ),
    Reaction(
        "HBA1CDEG",
        name="HBA1C degradation",
        equation="hba1c -> ",
        sboTerm=SBO.BIOCHEMICAL_REACTION,
        compartment="Vext",
        formula=(
            "k_hb_turn * hba1c",
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
            "k_hb_gly * fpg * hb",
            U.mmole_per_min,
        ),
    ),

])

model_hba1c = _m


if __name__ == "__main__":
    from pkdb_models.models.hba1c import MODEL_BASE_PATH

    # SBML model
    results: FactoryResult = create_model(
        model=model_hba1c,
        filepath=MODEL_BASE_PATH / f"{model_hba1c.sid}.xml",
        sbml_level=3, sbml_version=2,
    )

    # create differential equations
    md_path = MODEL_BASE_PATH / f"{model_hba1c.sid}.md"
    ode_factory = odefac.SBML2ODE.from_file(sbml_file=results.sbml_path)
    ode_factory.to_markdown(md_file=md_path)

    # visualization
    from sbmlutils import cytoscape as cyviz
    cyviz.visualize_sbml(results.sbml_path, delete_session=True)
