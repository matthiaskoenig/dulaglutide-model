from sbmlutils.metadata import *
model = [
    # taxonomy
    (BQB.HAS_TAXON, "taxonomy/9606"),  # human
    (BQB.HAS_TAXON, "snomedct/337915000"),  # human

    # modelling approach
    (BQB.HAS_PROPERTY, "mamo/MAMO_0000046"),  # ordinary differential equation model

    # biological process explained by model (GO/NCIT)
    (BQB.HAS_PROPERTY, "NCIT:C81328"),  # body weight
]

species = {
}

compartments = {
}
