"""Metabolites intestine model."""
import numpy as np
import pandas as pd
from sbmlutils.converters import odefac

from sbmlutils.cytoscape import visualize_sbml
from sbmlutils.factory import *
from sbmlutils.metadata import *
from pkdb_models.models.dulaglutide.models import annotations
from pkdb_models.models.dulaglutide.models import templates


class U(templates.U):
    """UnitDefinitions"""

    per_hr = UnitDefinition("per_hr", "1/hr")
    mg_per_min = UnitDefinition("mg_per_min", "mg/min")


_m = Model(
    "dulaglutide_intestine",
    name="Model for dulaglutide absorption",
    notes="""
    # Model for dulaglutide absorption and fecal excretion
    """
    + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=annotations.model + [
        # tissue
        (BQB.OCCURS_IN, "fma/FMA:45615"),  # gut
        (BQB.OCCURS_IN, "bto/BTO:0000545"),  # gut
        (BQB.OCCURS_IN, "NCIT:C12736"),  # intestine
        (BQB.OCCURS_IN, "fma/FMA:7199"),  # intestine
        (BQB.OCCURS_IN, "bto/BTO:0000648"),  # intestine

        (BQB.HAS_PROPERTY, "NCIT:C79369"),  # Pharmacokinetics: Absorption
        (BQB.HAS_PROPERTY, "NCIT:C79372"),  # Pharmacokinetics: Excretion
    ]
)

_m.compartments = [
    Compartment(
        "Vext",
        1.0,
        name="plasma",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        port=True,
        annotations=annotations.compartments["plasma"],
    ),
    Compartment(
        "Vgu",
        1.2825,  # 0.0171 [l/kg] * 75 kg
        name="intestine",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        port=True,
        annotations=annotations.compartments["gu"],
    ),
    Compartment(
        "Vlumen",
        1.2825 * 0.9,  # 0.0171 [l/kg] * 75 kg * 0.9,
        name="intestinal lumen (inner part of intestine)",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        constant=False,
        port=True,
        annotations=annotations.compartments["gu_lumen"],
    ),
    Compartment(
        "Vfeces",
        metaId="meta_Vfeces",
        value=1,
        unit=U.liter,
        constant=True,
        name="feces",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        port=True,
        annotations=annotations.compartments["feces"],
    ),
    Compartment(
        "Ventero",
        1.2825 * 0.1,  # 0.0171 [l/kg] * 75 kg * 0.9,  # FIXME: synchronize with body
        name="intestinal lining (enterocytes)",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        constant=False,
    ),
    Compartment(
        "Vapical",
        np.nan,
        name="apical membrane (intestinal membrane enterocytes)",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.m2,
        annotations=annotations.compartments["apical"],
        spatialDimensions=2,
    ),
    Compartment(
        "Vbaso",
        np.nan,
        name="basolateral membrane (intestinal membrane enterocytes)",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.m2,
        annotations=annotations.compartments["basolateral"],
        spatialDimensions=2,
    ),
    Compartment(
        "Vstomach",
        metaId="meta_Vstomach",
        value=1,
        unit=U.liter,
        constant=True,
        name="stomach",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        port=True,
        annotations=annotations.compartments["stomach"],
    ),
]

n_chain = 5

_m.parameters = [
    Parameter(
        "Vchain",
        0.1,
        unit=U.liter,
        name="volume of chain compartment",
        sboTerm=SBO.KINETIC_CONSTANT,
    ),

]

for k in range(n_chain):
    # compartments for chain
    _m.compartments.append(
        Compartment(
            f"Vint_{k}",
            "Vchain",
            name="intestinal lumen (inner part of intestine)",
            sboTerm=SBO.PHYSICAL_COMPARTMENT,
            unit=U.liter,
            annotations=annotations.compartments["gu_lumen"],
            constant=False
        ),
    )


_m.species = [
    Species(
        "dm_lumen",
        initialConcentration=0.0,
        name="dulaglutide metabolite (intestinal volume)",
        compartment="Vlumen",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["dm"],
        port=True,
    ),
    Species(
        "dm_feces",
        initialConcentration=0.0,
        name="dulaglutide (feces)",
        compartment="Vfeces",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=True,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["dm"],
        port=True,
    ),

]

for k in range(n_chain):
    # species for chain
    _m.species.append(
        Species(
            f"dm_int_{k}",
            initialConcentration=0.0,
            name=f"dulaglutide (intestine) {k}",
            compartment=f"Vint_{k}",
            substanceUnit=U.mmole,
            hasOnlySubstanceUnits=False,
            sboTerm=SBO.SIMPLE_CHEMICAL,
            annotations=annotations.species["dm"],
        ),
    )


_m.reactions = [
    Reaction(
        sid="dmEXC",
        name=f"excretion dulaglutide metabolite (feces)",
        compartment="Vlumen",
        equation=f"dm_lumen -> dm_int_0",
        sboTerm=SBO.TRANSPORT_REACTION,
        pars=[
            Parameter(
                "DMEXC_k",
                0.0003920629361513939,
                unit=U.per_min,
                name="rate of dulaglutide metabolite fecal excretion",
                sboTerm=SBO.KINETIC_CONSTANT,
            ),
        ],
        formula=(
            f"DMEXC_k * Vgu  * dm_lumen",
            U.mmole_per_min),
    ),
]

for k in range(n_chain):
    # reactions for chain
    source = f"dm_int_{k}"
    target = f"dm_int_{k+1}" if k < n_chain - 1 else f"dm_feces"
    _m.reactions.append(
        Reaction(
            sid=f"dmEXC_{k}",
            name=f"excretion dulaglutide metabolite {k}",
            compartment="Vlumen",
            equation=f"{source} -> {target}",
            sboTerm=SBO.TRANSPORT_REACTION,
            formula=(
                f"DMEXC_k * Vint_{k} * {source}",
                U.mmole_per_min,
            ),
        ),
    )



model_intestine = _m
def layout(dx=200, dy=200) -> pd.DataFrame:
    """Layout definition."""

    delta_x = 0.5 * dx
    delta_y = 0.4 * dy

    positions = [

        ["dm_lumen", 0 * delta_x, 3 * delta_y],
        [f"dmEXC", 0 * delta_x, 4 * delta_y],
        ["dm_int_0", 0 * delta_x, 5 * delta_y],
        ["dmEXC_0", 0 * delta_x, 6 * delta_y],
        ["dm_int_1", 1 * delta_x, 6 * delta_y],
        ["dmEXC_1", 2 * delta_x, 6 * delta_y],
        ["dm_int_2", 3 * delta_x, 6 * delta_y],
        ["dmEXC_2", 3 * delta_x, 7 * delta_y],
        ["dm_int_3", 3 * delta_x, 8 * delta_y],
        ["dmEXC_3", 2 * delta_x, 8 * delta_y],
        ["dm_int_4", 1 * delta_x, 8 * delta_y],
        ["dmEXC_4", 0 * delta_x, 8 * delta_y],
        ["dm_feces", 0 * delta_x, 9 * delta_y],
    ]

    df = pd.DataFrame(positions, columns=["id", "x", "y"])
    df.set_index("id", inplace=True)
    return df

def annotations(dx=200, dy=200) -> list:

    delta_x = 0.5 * dx
    delta_y = 0.4 * dy

    kwargs = {
        "type": cyviz.AnnotationShapeType.ROUND_RECTANGLE,
        "opacity": 20,
        "border_color": "#000000",
        "border_thickness": 2,
    }
    annotations = [
        # intestine lumen (PG and OATP are at the apical side (it is near to the enterocytes)
        cyviz.AnnotationShape(
            x_pos=int(-1* delta_x), y_pos=int(2.5 * delta_y), width= int(2 * delta_x), height=int(2 * delta_y),
            fill_color="#FFFFFF", **kwargs
        ),
        # chain
        cyviz.AnnotationShape(
            x_pos=int(-1 * delta_x), y_pos=int(4.5 * delta_y), width=int(5* delta_x), height=int(4 * delta_y),
            fill_color="#0000FF", **kwargs
        ),
        #feces
        cyviz.AnnotationShape(
            x_pos=int(-1 * delta_x), y_pos=int(8.5 * delta_y), width=int(2 * delta_x), height=int(1 * delta_y),
            fill_color="#000000", **kwargs
        ),

    ]
    return annotations


if __name__ == "__main__":
    from pkdb_models.models.dulaglutide import MODEL_BASE_PATH

    # SBML model
    results: FactoryResult = create_model(
        model=model_intestine,
        filepath=MODEL_BASE_PATH / f"{model_intestine.sid}.xml",
        sbml_level=3, sbml_version=2,
    )

    # create differential equations
    md_path = MODEL_BASE_PATH / f"{model_intestine.sid}.md"
    ode_factory = odefac.SBML2ODE.from_file(sbml_file=results.sbml_path)
    ode_factory.to_markdown(md_file=md_path)

    # visutmzation
    from sbmlutils import cytoscape as cyviz
    cyviz.visualize_sbml(results.sbml_path, delete_session=True)
    cyviz.apply_layout(layout=layout())
    cyviz.add_annotations(annotations=annotations())
    cyviz.export_image(
        MODEL_BASE_PATH / f"{model_intestine.sid}.png",
        fit_content=True,
    )
