"""Annotations of the dulaglutide models: the model, its compartments and species."""

from pkpdsim.annotations import compartments as shared_compartments
from sbmlutils.metadata import BQB

model = [
    # taxonomy
    (BQB.HAS_TAXON, "taxonomy/9606"),  # human
    (BQB.HAS_TAXON, "snomedct/337915000"),  # human
    # modelling approach
    (BQB.HAS_PROPERTY, "mamo/MAMO_0000046"),  # ordinary differential equation model
    # biological process explained by model (GO/NCIT)
    (BQB.HAS_PROPERTY, "NCIT:C169923"),  # dulaglutide
    (BQB.HAS_PROPERTY, "NCIT:C98085"),  # GLP1 mimetics
    (BQB.HAS_PROPERTY, "NCIT:C15299"),  # pharmacokinetics
    # model relevance to a particular area
    (BQB.HAS_PROPERTY, "NCIT:C2985"),  # Diabetes Mellitus
    (BQB.HAS_PROPERTY, "NCIT:C99532"),  # Diabetes Therapy
    # model reference
    (BQB.IS_DESCRIBED_BY, "doi/10.5281/zenodo.18432433"),  # dulaglutide-model
    # model
    # (BQM.IS, "biomodels.db/MODEL2510140001"),
]

species = {
    "dul": [  # dulaglutide, an Fc fusion protein: no PubChem compound or ChEBI entry
        (BQB.IS, "NCIT:C169923"),
        (BQB.IS, "drugbank/DB09045"),
    ],
}


# the adipose tissue and the shared compartments
compartments = {
    "ad": [
        (BQB.IS, "fma/FMA:20110"),
        (BQB.IS, "bto/BTO:0001487"),
        (BQB.IS, "NCIT:C12472"),
    ],
    **shared_compartments,
}
