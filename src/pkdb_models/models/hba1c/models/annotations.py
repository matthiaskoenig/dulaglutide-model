from sbmlutils.metadata import *

model = [
    # taxonomy
    (BQB.HAS_TAXON, "taxonomy/9606"),  # human
    (BQB.HAS_TAXON, "snomedct/337915000"),  # human

    # modelling approach
    (BQB.HAS_PROPERTY, "mamo/MAMO_0000046"),  # ordinary differential equation model

    # biological process explained by model (GO/NCIT)
    # (BQB.HAS_PROPERTY, "NCIT:C81328"),  # body weight
]

species = {
    "fpg": [
        (BQB.IS_VERSION_OF, "SNOMEDCT:167096006")
    ],
    "hb": [
        (BQB.IS, "CHEBI:35143")  # hemoglobin
    ],
    "hba1c": [
        (BQB.IS_VERSION_OF, "CHEBI:35143"),  # hemoglobin
        (BQB.IS_VERSION_OF, "NCIT:C64849"),
        (BQB.IS_VERSION_OF, "EFO:0004541"),
    ]
}

compartments = {
    "plasma": [
        (BQB.IS, "ncit/C13356"),
        (BQB.IS, "bto/BTO:0000131"),
    ],
}
