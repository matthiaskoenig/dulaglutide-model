"""Kidney model for dulaglutide."""

import numpy as np
from sbmlutils.converters import odefac
from sbmlutils.factory import *
from sbmlutils.metadata import *

from pkdb_models.models.dulaglutide.models import annotations
from pkdb_models.models.dulaglutide.models import templates


class U(templates.U):
    """UnitDefinitions"""

    pass


mid = "dulaglutide_kidney"
version = 1

_m = Model(
    sid=mid,
    name="Model for renal dulaglutide excretion.",
    notes=f"""
    Model for renal dulaglutide excretion.

    **version** {version}        
    """ + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=annotations.model + [
        # tissue
        (BQB.OCCURS_IN, "fma/FMA:7203"),  # kidney
        (BQB.OCCURS_IN, "bto/BTO:0000671"),
        (BQB.OCCURS_IN, "NCIT:C12415"),

        (BQB.HAS_PROPERTY, "NCIT:C79372"),  # Pharmacokinetics: Excretion
    ]
)

_m.compartments = [
    Compartment(
        "Vext",
        value=1.5,
        unit=U.liter,
        name="plasma",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["plasma"],
        port=True
    ),
    Compartment(
        "Vki",
        value=0.3,  # 0.4 % of bodyweight
        unit=U.liter,
        name="kidney",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["ki"],
        port=True
    ),
    Compartment(
        "Vmem",
        value=np.nan,
        unit=U.m2,
        name="plasma membrane",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["plasma membrane"],
        spatialDimensions=2,
    ),
    Compartment(
        "Vurine",
        1.0,
        name="urine",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        port=True,
        annotations=annotations.compartments["urine"],
    ),

]

_m.species = [
    Species(
        "dm_ext",
        name="dulaglutide metabolites (plasma)",
        initialConcentration=0.0,
        compartment="Vext",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,  # this is a concentration
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["dm"],
        port=True
    ),
    Species(
        "dm_urine",
        name="dulaglutide metabolites (urine)",
        initialConcentration=0.0,
        compartment="Vurine",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=True,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["dm"],
        port=True
    ),
]

_m.parameters.append(
    Parameter(
        "f_renal_function",
        name="parameter for renal function",
        value=1.0,
        unit=U.dimensionless,
        sboTerm=SBO.KINETIC_CONSTANT,
        notes="""scaling factor for renal function. 1.0: normal renal function; 
        <1.0: reduced renal function; >1.0: increased renal function.
        """
    )
)

_m.reactions = [
    Reaction(
        sid="DMEX",
        name="dulaglutide metabolite excretion (DMEX)",
        equation="dm_ext <-> dm_urine",
        compartment="Vki",
        sboTerm=SBO.TRANSPORT_REACTION,
        pars=[
            Parameter(
                "DMEX_k",
                0.1,
                U.per_min,
                name="rate urinary excretion of dulaglutide",
                sboTerm=SBO.KINETIC_CONSTANT,
            ),
        ],
        formula=(
            "f_renal_function * DMEX_k * Vki * dm_ext"
        )
    ),
]

model_kidney = _m


if __name__ == "__main__":
    from pkdb_models.models.dulaglutide import MODEL_BASE_PATH

    # SBML model
    results: FactoryResult = create_model(
        model=model_kidney,
        filepath=MODEL_BASE_PATH / f"{model_kidney.sid}.xml",
        sbml_level=3, sbml_version=2,
    )

    # create differential equations
    md_path = MODEL_BASE_PATH / f"{model_kidney.sid}.md"
    ode_factory = odefac.SBML2ODE.from_file(sbml_file=results.sbml_path)
    ode_factory.to_markdown(md_file=md_path)

    # visualization
    from sbmlutils import cytoscape as cyviz
    cyviz.visualize_sbml(results.sbml_path, delete_session=True)
    # cyviz.export_image(
    #     MODEL_BASE_PATH / f"{model_kidney.sid}.png",
    #     fit_content=True,
    # )
