"""Dulaglutide body model: the whole-body PBPK model of dulaglutide.

Dulaglutide is a dimeric GLP-1 analogue fused to an IgG4 Fc fragment (59.7 kDa).
It is given subcutaneously: the dose enters a depot, from which the fraction
`Fsc_dul` is absorbed into the venous plasma and the rest is degraded at the
injection site. In the body it stays in the plasma and distributes into the
interstitial space of the tissues (`ftissue_dul`, `Kp_dul`); it is eliminated
by protein catabolism (`DULCAT`), which scales with the body weight. The intact
protein is not excreted (no glomerular filtration of the Fc fusion protein, no
biliary excretion), its catabolism products are amino acids, so the model has
no metabolites and no organ submodels: the organs are their plasma and tissue
volumes in the circulation.

The factory merges the model with the body weight and HbA1c models, which take
the dulaglutide plasma concentration `glp1`.
"""

from typing import TypedDict

from sbmlutils.factory import (
    AssignmentRule,
    Compartment,
    Model,
    Parameter,
    RateRule,
    Reaction,
    Species,
    UnitDefinition,
    create_model,
)
from sbmlutils.metadata import BQB, SBO

from pkdb_models.models.dulaglutide.models import annotations, templates
from pkdb_models.models.dulaglutide.models.fits import FITS


class U(templates.U):
    """UnitsDefinitions."""

    kg = UnitDefinition("kg")
    l_per_kg = UnitDefinition("l_per_kg", "l/kg")
    mg_per_min = UnitDefinition("mg_per_min", "mg/min")
    ml_per_l = UnitDefinition("ml_per_l", "ml/l")
    ml_per_s = UnitDefinition("ml_per_s", "ml/s")
    ml_per_s_kg = UnitDefinition("ml_per_s_kg", "ml/s/kg")
    s_per_min = UnitDefinition("s_per_min", "s/min")


_m = Model(
    "dulaglutide_body",
    name="Dulaglutide body model",
    notes="""
    # Dulaglutide body model

    Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of
    dulaglutide in human.

    Dulaglutide (59.7 kDa, a dimeric GLP-1 analogue fused to an IgG4 Fc
    fragment) is given subcutaneously: the dose enters a depot, from which the
    fraction `Fsc_dul` (the absolute bioavailability, 44 % after 1.5 mg) is
    absorbed into the venous plasma and the rest is degraded at the injection
    site (`sc_deg_dul`). An intravenous dose or infusion enters the venous
    plasma. Dulaglutide distributes from the plasma into the interstitial space
    of the tissues (`ftissue_dul`, `Kp_dul`) and is eliminated by protein
    catabolism (`DULCAT`, a plasma clearance which scales with the body
    weight). The intact protein is not excreted in the urine or the bile (FDA
    clinical pharmacology review BLA 125469). The amounts degraded at the
    injection site (`Asc_deg_dul`) and catabolized (`Acat_dul`) close the mass
    balance.

    The fasting plasma glucose, the HbA1c and the body weight respond to the
    dulaglutide plasma concentration `glp1`.
    """
    + templates.terms_of_use,
    units=U,
    model_units=templates.model_units,
    creators=templates.creators,
    annotations=[
        *annotations.model,
        # tissue
        (BQB.OCCURS_IN, "BTO:0001489"),  # whole body
        (BQB.OCCURS_IN, "FMA:256135"),  # body
        (BQB.HAS_PROPERTY, "NCIT:C79369"),  # Pharmacokinetics: Absorption
        (BQB.HAS_PROPERTY, "NCIT:C79371"),  # Pharmacokinetics: Metabolism
        (BQB.HAS_PROPERTY, "NCIT:C79370"),  # Pharmacokinetics: Distribution
    ],
)


class SubstanceBody(TypedDict):
    """Definition of a substance transported in the whole-body model."""

    name: str
    unit: UnitDefinition
    Mr: float  # molecular weight [g/mole]


SUBSTANCES_BODY: dict[str, SubstanceBody] = {
    "dul": {
        "name": "dulaglutide",
        "unit": U.mmole,
        # dimeric GLP-1 analogue-IgG4 Fc fusion protein, 59.7 kDa
        # (Barrington2011a, FDA clinical pharmacology review BLA 125469)
        "Mr": 59670.0,  # [g/mole]
    },
}

COMPARTMENTS_BODY = {
    "ki": "kidney",
    "li": "liver",
    "lu": "lung",
    "ad": "adipose",
    "gu": "gut",
    "re": "rest",
    "ar": "arterial blood",
    "ve": "venous blood",
    "po": "portal vein",
    "hv": "hepatic vein",
}
#: the vessels, whole blood
VESSELS = ("ar", "ve", "po", "hv")
#: the organs with a plasma and a tissue (interstitial) volume
ORGANS = tuple(cid for cid in COMPARTMENTS_BODY if cid not in VESSELS)

# -------------------------------------------------------------------------------------------------
# Compartments
# -------------------------------------------------------------------------------------------------
_m.compartments = [
    *(
        Compartment(
            f"V{cid}",
            metaId=f"meta_V{cid}",
            value=1,
            unit=U.liter,
            constant=False,
            name=cname,
            sboTerm=SBO.PHYSICAL_COMPARTMENT,
            annotations=annotations.compartments[cid],
        )
        for cid, cname in COMPARTMENTS_BODY.items()
    ),
    Compartment(
        "Vdeg",
        metaId="meta_Vdeg",
        value=1,
        unit=U.liter,
        constant=True,
        name="catabolism products",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        notes="""
        The amounts of dulaglutide degraded at the injection site and
        catabolized in the body (to amino acids), for the mass balance.
        """,
    ),
]
for cid in ORGANS:
    _m.compartments.extend(
        [
            Compartment(
                f"V{cid}_tissue",
                value=1,
                unit=U.liter,
                constant=False,
                name=f"{cid} tissue",
                metaId=f"meta_V{cid}_tissue",
                annotations=[
                    *annotations.compartments["parenchyma"],
                    *[
                        (BQB.IS_PART_OF, aid[1])
                        for aid in annotations.compartments[cid]
                    ],
                ],
                sboTerm=SBO.PHYSICAL_COMPARTMENT,
            ),
            Compartment(
                f"V{cid}_plasma",
                value=1,
                unit=U.liter,
                constant=False,
                name=f"{cid} plasma",
                metaId=f"meta_V{cid}_plasma",
                annotations=[
                    *annotations.compartments["plasma"],
                    *[
                        (BQB.IS_PART_OF, aid[1])
                        for aid in annotations.compartments[cid]
                    ],
                ],
                sboTerm=SBO.PHYSICAL_COMPARTMENT,
            ),
        ]
    )

# -------------------------------------------------------------------------------------------------
# Species
# -------------------------------------------------------------------------------------------------
_m.species = []
for sid, sdict in SUBSTANCES_BODY.items():
    for cid, cname in COMPARTMENTS_BODY.items():
        if cid in VESSELS:
            sid_ex, cid_ex = f"C{cid}_{sid}", f"V{cid}"
        else:
            sid_ex, cid_ex = f"C{cid}_plasma_{sid}", f"V{cid}_plasma"
        _m.species.append(
            Species(
                sid_ex,
                metaId=f"meta_{sid_ex}",
                initialConcentration=0.0,
                compartment=cid_ex,
                substanceUnit=sdict["unit"],
                name=f"{sdict['name']} ({cname} plasma)",
                hasOnlySubstanceUnits=False,
                sboTerm=SBO.SIMPLE_CHEMICAL,
                annotations=annotations.species[sid],
            )
        )
    # interstitial space of the tissues
    for cid in ORGANS:
        _m.species.append(
            Species(
                f"C{cid}_{sid}",
                metaId=f"meta_C{cid}_{sid}",
                initialConcentration=0.0,
                compartment=f"V{cid}_tissue",
                substanceUnit=sdict["unit"],
                name=f"{sdict['name']} ({COMPARTMENTS_BODY[cid]})",
                hasOnlySubstanceUnits=False,
                sboTerm=SBO.SIMPLE_CHEMICAL,
                annotations=annotations.species[sid],
            )
        )

_m.species.extend(
    [
        Species(
            "Cvep_dul",
            metaId="meta_Cvep_dul",
            initialConcentration=0,
            compartment="Vve",
            substanceUnit=U.mmole,
            name="dulaglutide (venous plasma)",
            hasOnlySubstanceUnits=False,
            sboTerm=SBO.SIMPLE_CHEMICAL,
            annotations=annotations.species["dul"],
        ),
        Species(
            "Acat_dul",
            metaId="meta_Acat_dul",
            initialAmount=0,
            compartment="Vdeg",
            substanceUnit=U.mmole,
            name="dulaglutide catabolized (amount)",
            hasOnlySubstanceUnits=True,
            sboTerm=SBO.SIMPLE_CHEMICAL,
        ),
        Species(
            "Asc_deg_dul",
            metaId="meta_Asc_deg_dul",
            initialAmount=0,
            compartment="Vdeg",
            substanceUnit=U.mmole,
            name="dulaglutide degraded at the injection site (amount)",
            hasOnlySubstanceUnits=True,
            sboTerm=SBO.SIMPLE_CHEMICAL,
        ),
    ]
)

# -------------------------------------------------------------------------------------------------
# Parameters
# -------------------------------------------------------------------------------------------------
_m.parameters = [
    # body weight BW and height HEIGHT are defined in the body weight submodel
    Parameter(
        "BW_ref",
        75,
        U.kg,
        constant=True,
        name="reference body weight [kg]",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes=(
            "Body weight at which the exchange flow of the tissue distribution "
            "(`ftissue_dul`) and the catabolic clearance (`DULCAT_k`) are "
            "given; they scale with the body weight as the volumes and the "
            "blood flows do."
        ),
    ),
    Parameter(
        "COBW",
        1.548,
        U.ml_per_s_kg,
        constant=True,
        name="cardiac output per bodyweight [ml/s/kg]",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "f_cardiac_function",
        1.0,
        U.dimensionless,
        constant=True,
        name="heart function",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
        1.0: normal function;
        <1.0: reduced function as reduced cardiac output;
        """,
    ),
    Parameter(
        "CO",
        108.33,
        U.ml_per_s,
        constant=False,
        name="cardiac output [ml/s]",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "QC",
        6.5,
        U.l_per_min,
        constant=False,
        name="cardiac output [l/min]",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "Fblood",
        0.02,
        U.dimensionless,
        constant=True,
        name="blood fraction of organ volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "HCT",
        0.51,
        U.dimensionless,
        constant=True,
        metaId="meta_HCT",
        name="hematocrit",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    # fractional tissue volumes
    Parameter(
        "FVgu",
        0.0171,
        U.l_per_kg,
        constant=True,
        name="gut fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FVki",
        0.0044,
        U.l_per_kg,
        constant=True,
        name="kidney fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FVli",
        0.0210,
        U.l_per_kg,
        constant=True,
        name="liver fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FVlu",
        0.0076,
        U.l_per_kg,
        constant=True,
        name="lung fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    # the adipose fractional tissue volume FVad is calculated dynamically by
    # the body weight submodel
    Parameter(
        "FVre",
        0,
        U.l_per_kg,
        constant=False,
        name="rest of body fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FVve",
        0.0514,
        U.l_per_kg,
        constant=True,
        name="venous fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FVar",
        0.0257,
        U.l_per_kg,
        constant=True,
        name="arterial fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FVpo",
        0.001,
        U.l_per_kg,
        constant=True,
        name="portal fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FVhv",
        0.001,
        U.l_per_kg,
        constant=True,
        name="hepatic venous fractional tissue volume",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    # fractional tissue blood flows
    Parameter(
        "FQgu",
        0.18,
        U.dimensionless,
        constant=True,
        name="gut fractional tissue blood flow",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
        Assumed FQgu is the sum of FQgu + FQsp + FQpa for correct portal blood flow.
        with FQgu=0.146, FQsp=0.017, FQpa=0.017
        """,
    ),
    Parameter(
        "FQki",
        0.190,
        U.dimensionless,
        constant=True,
        name="kidney fractional tissue blood flow",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FQh",
        0.215,
        U.dimensionless,
        constant=True,
        name="hepatic (venous side) fractional tissue blood flow",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FQad",
        0.05,
        U.dimensionless,
        constant=True,
        name="adipose tissue fractional tissue blood flow",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FQlu",
        1,
        U.dimensionless,
        constant=True,
        name="lung fractional tissue blood flow",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    Parameter(
        "FQre",
        0,
        U.dimensionless,
        constant=False,
        name="rest of body fractional tissue blood flow",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
    # dulaglutide
    Parameter(
        "Mr_dul",
        SUBSTANCES_BODY["dul"]["Mr"],
        U.g_per_mole,
        constant=True,
        name="Molecular weight dul [g/mole]",
        sboTerm=SBO.MOLECULAR_MASS,
    ),
    Parameter(
        "BP_dul",
        0.49,
        U.dimensionless,
        constant=False,
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        name="blood-to-plasma ratio dul",
        notes="""
        Dulaglutide does not enter the red blood cells, its blood-to-plasma
        ratio is the plasma fraction of the blood, `1 - HCT`.
        """,
    ),
    Parameter(
        "ftissue_dul",
        **FITS.parameter("ftissue_dul", unit=U.l_per_min),
        constant=True,
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        name="tissue distribution dul",
        notes="""
        Exchange flow between the plasma and the interstitial space of a
        tissue at the reference body weight `BW_ref`, it scales with the body
        weight. The intravenous data (FDAGBDR) fall from 35 ng/ml at 1 hr to
        15 ng/ml at 24 hr before the terminal phase.
        """,
    ),
    Parameter(
        "Kp_dul",
        **FITS.parameter("Kp_dul", unit=U.dimensionless),
        constant=True,
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        name="tissue/plasma partition coefficient dul",
        notes="""
        The interstitial distribution of a 60 kDa protein: the volume of
        distribution at steady state is 5.3 l after an intravenous dose
        (FDAGBDR), 2.5 l more than the plasma volume.
        """,
    ),
]

# -------------------------------------------------------------------------------------------------
# AssignmentRules
# -------------------------------------------------------------------------------------------------
_m.rules = [
    AssignmentRule("BP_dul", "1 dimensionless - HCT", U.dimensionless),
    # rest body volume
    AssignmentRule(
        "FVre",
        "1.0 l_per_kg - (FVgu + FVki + FVli + FVlu + FVad + FVve + FVar)",
        U.l_per_kg,
    ),
    # rest body perfusion
    AssignmentRule("FQre", "1.0 dimensionless - (FQki + FQad + FQh)", U.dimensionless),
    # cardiac output (depending on heart function and bodyweight)
    AssignmentRule("CO", "f_cardiac_function*BW*COBW", U.ml_per_s),
    AssignmentRule("QC", "CO/1000 ml_per_l * 60 s_per_min", U.l_per_min),
    # volumes
    AssignmentRule("Vgu", "BW*FVgu", U.liter),
    AssignmentRule("Vki", "BW*FVki", U.liter),
    AssignmentRule("Vli", "BW*FVli", U.liter),
    AssignmentRule("Vlu", "BW*FVlu", U.liter),
    # the adipose tissue of the body weight submodel
    AssignmentRule("Vad", "BW*FVad", U.liter),
    AssignmentRule("Vre", "BW*FVre", U.liter),
    # venous and arterial blood volume (corrected for tissue blood volumes)
    AssignmentRule(
        "Vve",
        "BW*FVve - FVve/(FVar+FVve) * BW * Fblood * (1 l_per_kg - FVve - FVar)",
        U.liter,
    ),
    AssignmentRule(
        "Var",
        "BW*FVar - FVar/(FVar+FVve) * BW * Fblood * (1 l_per_kg - FVve - FVar)",
        U.liter,
    ),
    AssignmentRule(
        "Vpo",
        "(1 dimensionless - HCT) * (BW*FVpo - FVpo/(FVar+FVve+FVpo+FVhv) "
        "* BW * Fblood * (1 l_per_kg - (FVar+FVve+FVpo+FVhv)))",
        U.liter,
    ),
    AssignmentRule(
        "Vhv",
        "(1 dimensionless - HCT) * (BW*FVhv - FVhv/(FVar+FVve+FVpo+FVhv) "
        "* BW * Fblood * (1 l_per_kg - (FVar+FVve+FVpo+FVhv)))",
        U.liter,
    ),
    # blood flows
    AssignmentRule("Qgu", "QC*FQgu", U.l_per_min, name="gut blood flow"),
    AssignmentRule("Qki", "QC*FQki", U.l_per_min, name="kidney blood flow"),
    AssignmentRule(
        "Qh", "QC*FQh", U.l_per_min, name="hepatic (venous side) blood flow"
    ),
    AssignmentRule("Qha", "Qh - Qgu", U.l_per_min, name="hepatic artery blood flow"),
    AssignmentRule("Qlu", "QC*FQlu", U.l_per_min, name="lung blood flow"),
    AssignmentRule("Qad", "QC*FQad", U.l_per_min, name="adipose tissue blood flow"),
    AssignmentRule("Qre", "QC*FQre", U.l_per_min, name="rest of body blood flow"),
    AssignmentRule("Qpo", "Qgu", U.l_per_min, name="portal blood flow"),
]

# the plasma and tissue volumes of the organs
for cid in ORGANS:
    cname = COMPARTMENTS_BODY[cid]
    _m.rules.extend(
        [
            AssignmentRule(
                f"V{cid}_plasma",
                value=f"V{cid} * Fblood * (1 dimensionless - HCT)",
                unit=U.liter,
                name=f"plasma volume of {cname}",
            ),
            AssignmentRule(
                f"V{cid}_tissue",
                value=f"V{cid}*(1 dimensionless - Fblood)",
                unit=U.liter,
                name=f"tissue volume of {cname}",
            ),
        ]
    )

# --------------------------------------------------------------------------------------------------
# Reactions
# --------------------------------------------------------------------------------------------------
_m.reactions = []

for sid, sdict in SUBSTANCES_BODY.items():
    sname = sdict["name"]

    # tissue distribution into the interstitial space
    for cid in ORGANS:
        _m.reactions.append(
            Reaction(
                sid=f"transport_{cid}_{sid}",
                name=f"transport {sname}",
                formula=(
                    f"ftissue_{sid} * BW/BW_ref * (C{cid}_plasma_{sid}*Kp_{sid} - C{cid}_{sid})",
                    U.mmole_per_min,
                ),
                equation=f"C{cid}_plasma_{sid} <-> C{cid}_{sid}",
                compartment=f"V{cid}_tissue",
                sboTerm=SBO.TRANSPORT_REACTION,
            ),
        )

    # ve -> lung -> ar
    _m.reactions.extend(
        [
            Reaction(
                sid=f"Flow_ve_lu_{sid}",
                name=f"inflow lung {sname}",
                formula=(f"Qlu*Cve_{sid}", U.mmole_per_min),
                equation=f"Cve_{sid} -> Clu_plasma_{sid}",
                sboTerm=SBO.TRANSPORT_REACTION,
            ),
            Reaction(
                sid=f"Flow_lu_ar_{sid}",
                name=f"outflow lung {sname}",
                formula=(f"Qlu*Clu_plasma_{sid}", U.mmole_per_min),
                equation=f"Clu_plasma_{sid} -> Car_{sid}",
                sboTerm=SBO.TRANSPORT_REACTION,
            ),
        ]
    )
    # ar -> organ -> ve, ar -> gut -> po
    for cid, target in [("ki", "ve"), ("ad", "ve"), ("re", "ve"), ("gu", "po")]:
        cname = COMPARTMENTS_BODY[cid]
        _m.reactions.extend(
            [
                Reaction(
                    sid=f"Flow_ar_{cid}_{sid}",
                    name=f"inflow {cname} {sname}",
                    formula=(f"Q{cid}*Car_{sid}", U.mmole_per_min),
                    equation=f"Car_{sid} -> C{cid}_plasma_{sid}",
                    sboTerm=SBO.TRANSPORT_REACTION,
                ),
                Reaction(
                    sid=f"Flow_{cid}_{target}_{sid}",
                    name=f"outflow {cname} {sname}",
                    formula=(f"Q{cid}*C{cid}_plasma_{sid}", U.mmole_per_min),
                    equation=f"C{cid}_plasma_{sid} -> C{target}_{sid}",
                    sboTerm=SBO.TRANSPORT_REACTION,
                ),
            ]
        )
    # ar -> li, po -> li, li -> hv -> ve
    _m.reactions.extend(
        [
            Reaction(
                sid=f"Flow_arli_li_{sid}",
                name=f"arterial inflow liver {sname}",
                formula=(f"Qha*Car_{sid}", U.mmole_per_min),
                equation=f"Car_{sid} -> Cli_plasma_{sid}",
                sboTerm=SBO.TRANSPORT_REACTION,
            ),
            Reaction(
                sid=f"Flow_po_li_{sid}",
                name=f"portal inflow liver {sname}",
                formula=(f"Qpo*Cpo_{sid}", U.mmole_per_min),
                equation=f"Cpo_{sid} -> Cli_plasma_{sid}",
                sboTerm=SBO.TRANSPORT_REACTION,
            ),
            Reaction(
                sid=f"Flow_li_hv_{sid}",
                name=f"outflow liver {sname}",
                formula=(f"(Qpo+Qha)*Cli_plasma_{sid}", U.mmole_per_min),
                equation=f"Cli_plasma_{sid} -> Chv_{sid}",
                sboTerm=SBO.TRANSPORT_REACTION,
            ),
            Reaction(
                sid=f"Flow_hv_ve_{sid}",
                name=f"outflow hepatic vein {sname}",
                formula=(f"Qh*Chv_{sid}", U.mmole_per_min),
                equation=f"Chv_{sid} -> Cve_{sid}",
                sboTerm=SBO.TRANSPORT_REACTION,
            ),
        ]
    )

# --------------------------------------------------------------------------------------------------
# Catabolism
# --------------------------------------------------------------------------------------------------
_m.reactions.append(
    Reaction(
        sid="DULCAT",
        name="dulaglutide catabolism",
        equation="Cve_dul -> Acat_dul",
        pars=[
            Parameter(
                "DULCAT_k",
                **FITS.parameter("DULCAT_k", unit=U.l_per_min),
                constant=True,
                sboTerm=SBO.KINETIC_CONSTANT,
                name="dulaglutide catabolic clearance (blood)",
                notes="""
                Clearance of the venous blood at the reference body weight
                `BW_ref`, it scales with the body weight. The plasma clearance
                is `DULCAT_k * BP_dul`, 0.0426 l/hr after an intravenous dose
                of 0.1 mg (FDAGBDR, Table 10).
                """,
            ),
        ],
        formula=("DULCAT_k * BW/BW_ref * Cve_dul", U.mmole_per_min),
        sboTerm=SBO.DEGRADATION,
        compartment="Vve",
        notes="""
        Protein catabolism of dulaglutide (general proteolytic pathways, FDA
        clinical pharmacology review BLA 125469), from the venous blood.
        """,
    )
)

_m.rules.append(
    AssignmentRule(
        "Cvep_dul",
        "Cve_dul/BP_dul",
        unit=U.mM,
        name="dulaglutide (venous plasma)",
    )
)
# the amount of dulaglutide in the body, for the mass balance
_m.parameters.append(
    Parameter(
        "Abody_dul",
        0,
        U.mmole,
        constant=False,
        name="dulaglutide in the body (amount)",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    )
)
_m.rules.append(
    AssignmentRule(
        "Abody_dul",
        " + ".join(
            [
                *(f"C{cid}_dul*V{cid}" for cid in VESSELS),
                *(f"C{cid}_plasma_dul*V{cid}_plasma" for cid in ORGANS),
                *(f"C{cid}_dul*V{cid}_tissue" for cid in ORGANS),
            ]
        ),
        unit=U.mmole,
    )
)

# --------------------------------------------------------------------------------------------------
# Dosing and application
# --------------------------------------------------------------------------------------------------
# intravenous: a bolus `IVDOSE_dul` or an infusion with the rate `Ri_dul`
_m.parameters.extend(
    [
        Parameter(
            "IVDOSE_dul",
            0,
            U.mg,
            constant=False,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="IV bolus dose dul [mg]",
        ),
        Parameter(
            "ti_dul",
            10,
            U.second,
            constant=True,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="injection time dul [s]",
        ),
        Parameter(
            "Ki_dul",
            0.02,
            U.per_min,
            constant=False,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="Ki [1/min] injection dul",
        ),
        Parameter(
            "Ri_dul",
            0,
            U.mg_per_min,
            constant=True,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="Ri [mg/min] rate of infusion dul",
        ),
    ]
)
_m.rules.append(
    AssignmentRule(
        "Ki_dul",
        "0.693 dimensionless/ti_dul * 60 s_per_min",
        U.per_min,
        name="injection rate IV",
        notes="""
        log(2) ~ 0.693 used for conversion of half-life injection time to
        injection rate.
        """,
    )
)
_m.reactions.append(
    Reaction(
        sid="iv_dul",
        name="iv dulaglutide",
        formula=("Ki_dul*IVDOSE_dul/Mr_dul", U.mmole_per_min),
        equation="-> Cve_dul",
        sboTerm=SBO.TRANSPORT_REACTION,
        annotations=[(BQB.IS, "NCIT:C38276")],  # intravenous route
        compartment="Vve",
    )
)
_m.rate_rules = [
    RateRule("IVDOSE_dul", "-iv_dul*Mr_dul + Ri_dul", U.mg_per_min),
]

# subcutaneous: the dose is moved into the depot with the fast rate
# Ksc_injection, so that a repeated dose (a change of SCDOSE) adds to the rest
# of the earlier doses in the depot
_m.parameters.extend(
    [
        Parameter(
            "SCDOSE_dul",
            0,
            U.mg,
            constant=False,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="subcutaneous dose dul [mg]",
        ),
        Parameter(
            "SCDEPOT_dul",
            0,
            U.mg,
            constant=False,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="subcutaneous depot dul [mg]",
        ),
        Parameter(
            "Ksc_injection_dul",
            100.0,
            U.per_min,
            constant=True,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="subcutaneous injection rate dul",
        ),
        Parameter(
            "Ksc_dul",
            **FITS.parameter("Ksc_dul", unit=U.per_min),
            constant=True,
            sboTerm=SBO.KINETIC_CONSTANT,
            name="subcutaneous absorption rate dul",
            notes="""
            Rate of the loss from the subcutaneous depot (absorption and
            degradation at the injection site); tmax 48 hr after 0.75 and
            1.5 mg (FDAGBDR).
            """,
        ),
        Parameter(
            "Fsc_dul",
            **FITS.parameter("Fsc_dul", unit=U.dimensionless),
            constant=True,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="subcutaneous bioavailability dul",
            notes="""
            The fraction of the depot which is absorbed, the absolute
            bioavailability: 44 % after 1.5 mg in the crossover with an
            intravenous dose (FDAGBDR, Table 10), 65 % and 47 % after 0.75 and
            1.5 mg (label, population PK). The rest is degraded at the
            injection site and in the lymph.
            """,
        ),
    ]
)
_m.reactions.extend(
    [
        Reaction(
            sid="sc_dul",
            name="subcutaneous absorption dulaglutide",
            formula=("Fsc_dul * Ksc_dul * SCDEPOT_dul/Mr_dul", U.mmole_per_min),
            equation="-> Cve_dul",
            sboTerm=SBO.TRANSPORT_REACTION,
            annotations=[(BQB.IS, "NCIT:C38299")],  # subcutaneous route
            compartment="Vve",
        ),
        Reaction(
            sid="sc_deg_dul",
            name="subcutaneous degradation dulaglutide",
            formula=(
                "(1 dimensionless - Fsc_dul) * Ksc_dul * SCDEPOT_dul/Mr_dul",
                U.mmole_per_min,
            ),
            equation="-> Asc_deg_dul",
            sboTerm=SBO.DEGRADATION,
            compartment="Vdeg",
        ),
    ]
)
_m.rate_rules.extend(
    [
        RateRule("SCDOSE_dul", "-Ksc_injection_dul*SCDOSE_dul", U.mg_per_min),
        RateRule(
            "SCDEPOT_dul",
            "Ksc_injection_dul*SCDOSE_dul - (sc_dul + sc_deg_dul)*Mr_dul",
            U.mg_per_min,
        ),
    ]
)

# GLP-1 agonist concentration of the body weight and HbA1c models
_m.rules.append(AssignmentRule("glp1", "Cvep_dul", unit=U.mM))

model_body: Model = _m


if __name__ == "__main__":
    from pkdb_models.models.dulaglutide import MODEL_BASE_PATH
    from pkdb_models.models.dulaglutide.models.model_bodyweight import model_bodyweight
    from pkdb_models.models.dulaglutide.models.model_hba1c import model_hba1c

    result = create_model(
        filepath=MODEL_BASE_PATH / f"{model_body.sid}.xml",
        model=[model_bodyweight, model_hba1c, model_body],
        sbml_level=3,
        sbml_version=2,
    )
