"""Liver model for dulaglutide."""

import numpy as np
import pandas as pd
from sbmlutils.converters import odefac
from sbmlutils.factory import *
from sbmlutils.metadata import *

from pkdb_models.models.dulaglutide.models import annotations
from pkdb_models.models.dulaglutide.models import templates


class U(templates.U):
    """UnitDefinitions"""

    pass


mid = "dulaglutide_liver"
version = 1

_m = Model(
    sid=mid,
    name="Model for hepatic dulaglutide enterohepatic circulation.",
    notes=f"""
    # Model for dulaglutide enterohepatic circulation.  
    """ + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=annotations.model + [
        # tissue
        (BQB.OCCURS_IN, "fma/FMA:7197"),
        (BQB.OCCURS_IN, "bto/BTO:0000759"),
        (BQB.OCCURS_IN, "NCIT:C12392"),

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
        "Vli",
        value=1.5,
        unit=U.liter,
        name="liver",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["li"],
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
        "Vapical",
        np.nan,
        name="apical membrane",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.m2,
        annotations=annotations.compartments["apical"],
        spatialDimensions=2,
    ),
    Compartment(
        "Vbi",
        1.0,
        name="bile",
        unit=U.liter,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["bi"],
        port=True,
    ),
    Compartment(
        "Vlumen",
        1.2825 * 0.9,  # 0.0171 [l/kg] * 75 kg * 0.9, # FIXME: calculate from whole-body
        name="intestinal lumen (inner part of intestine)",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        constant=False,
        port=True,
        annotations=annotations.compartments["gu_lumen"],
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
        "dm",
        name="dulaglutide metabolites (liver)",
        initialConcentration=0.0,
        compartment="Vli",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,  # this is a concentration
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["dm"],
    ),
    Species(
        "dm_bi",
        initialConcentration=0.0,
        name="dulaglutide metabolites (bile)",
        compartment="Vbi",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=True,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["dm"],
        notes="""
        Bile dulaglutide in amount.
        """,
    ),
    Species(
        "dm_lumen",
        initialConcentration=0.0,
        name="dulaglutide metabolites (lumen)",
        compartment="Vlumen",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["dm"],
        port=True,
    ),
]

# _m.parameters.append(
#     Parameter(
#         "vDMIM", "DMIM", unit=U.mmole_per_min,
#         notes="Global parameter for flux assignments."
#     )
# )

_m.reactions = [
    Reaction(
        sid="DMIM",
        name="dulaglutide import (DMIM)",
        equation="dm_ext -> dm",
        compartment="Vmem",
        sboTerm=SBO.TRANSPORT_REACTION,
        pars=[
            Parameter(
                "DMEX_k",
                0.003949307625018046,
                unit=U.per_min,
                name="rate for DM transport",
                sboTerm=SBO.KINETIC_CONSTANT,
            )
        ],
        formula=(
            "DMEX_k * Vli * dm_ext", U.mmole_per_min
        ),
    ),
    Reaction(
        "DMEX",
        name="dulaglutide bile export",
        equation="dm -> dm_bi",
        sboTerm=SBO.TRANSPORT_REACTION,
        compartment="Vapical",
        formula=(
            "DMIM",
            U.mmole_per_min,
        ),
    ),
    Reaction(
        "DMEHC",
        name="dulaglutide enterohepatic circulation",
        equation="dm_bi -> dm_lumen",
        sboTerm=SBO.TRANSPORT_REACTION,
        compartment="Vlumen",
        formula=("DMIM", U.mmole_per_min),
    ),
]

def liver_layout(dx=200, dy=200) -> pd.DataFrame:
    """Layout definition."""

    delta_x = 0.5 * dx
    delta_y = 0.4 * dy

    positions = [
        ["dm_ext", 0, 0],
        ["DMIM", 0, 1 * delta_y],
        ["dm", 0, 2 * delta_y],
        ["DMEX", delta_x, 2 * delta_y],
        ["dm_bi", 2*delta_x, 2 * delta_y],
        ["DMEHC", 2*delta_x, 1 * delta_y],
        ["dm_lumen", 2 * delta_x, 0 * delta_y],
    ]

    df = pd.DataFrame(positions, columns=["id", "x", "y"])
    df.set_index("id", inplace=True)
    return df

def liver_annotations(dx=200, dy=200) -> list:

    delta_x = 0.5 * dx
    delta_y = 0.4 * dy

    kwargs = {
        "type": cyviz.AnnotationShapeType.ROUND_RECTANGLE,
        "opacity": 20,
        "border_color": "#000000",
        "border_thickness": 2,
    }
    annotations = [
        # liver
        cyviz.AnnotationShape(
            x_pos=-delta_x, y_pos=delta_y, width=2 * delta_x, height=1.75* delta_y,
            fill_color="#FFFFFF", **kwargs
        ),
        #plasma
        cyviz.AnnotationShape(
            x_pos=-delta_x, y_pos=- 0.75 * delta_y, width=2 * delta_x, height=1.75 * delta_y,
            fill_color="#FF0000", **kwargs
        ),
        #intestine
        cyviz.AnnotationShape(
            x_pos=delta_x, y_pos=- 0.75 * delta_y, width=2 * delta_x, height=1.75 * delta_y,
            fill_color="#FFFFFF", **kwargs
        ),
        #bile duct
        cyviz.AnnotationShape(
            x_pos=delta_x, y_pos= 1 * delta_y, width=2 * delta_x, height=1.75 * delta_y,
            fill_color="#000000", **kwargs
        ),
    ]
    return annotations


model_liver = _m


if __name__ == "__main__":
    from pkdb_models.models.dulaglutide import MODEL_BASE_PATH
    results: FactoryResult = create_model(
        model=model_liver,
        filepath=MODEL_BASE_PATH / f"{model_liver.sid}.xml",
        sbml_level=3, sbml_version=2,
    )

    # create differential equations
    md_path = MODEL_BASE_PATH / f"{model_liver.sid}.md"
    ode_factory = odefac.SBML2ODE.from_file(sbml_file=results.sbml_path)
    ode_factory.to_markdown(md_file=md_path)


    # visualization
    from sbmlutils import cytoscape as cyviz
    cyviz.visualize_sbml(results.sbml_path, delete_session=True)
    cyviz.apply_layout(layout=liver_layout())
    cyviz.add_annotations(annotations=liver_annotations())
    # cyviz.export_image(
    #     MODEL_BASE_PATH / f"{model_liver.sid}.png",
    #     fit_content=True,
    # )