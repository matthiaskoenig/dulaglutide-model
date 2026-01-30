"""FitParameters for dulaglutide fitting."""

from sbmlsim.fit import FitParameter


parameters_pharmacokinetics = [
    # subcutaneous absorption rate
    FitParameter(
        pid="Ksc_dul",
        lower_bound=1E-6,
        start_value=0.001,
        upper_bound=0.1,
        unit="1/min",
    ),

    # plasma cleavage
    FitParameter(
        pid="DUL2DM_k",
        lower_bound=1E-6,
        start_value=0.001,
        upper_bound=0.1,
        unit="l/min",
    ),
    # tm renal clearance
    FitParameter(
        pid="KI__DMEX_k",
        lower_bound=1E-6,
        start_value=0.001,
        upper_bound=0.1,
        unit="1/min",
    ),

    # # tm enterohepatic circulation and feces excretion
    # FitParameter(
    #     pid="LI__LMEX_k",
    #     lower_bound=1E-6,
    #     start_value=0.001,
    #     upper_bound=0.1,
    #     unit="1/min",
    # ),
    # # intestinal transport
    # FitParameter(
    #     pid="GU__LMEXC_k",
    #     lower_bound=1E-6,
    #     start_value=0.001,
    #     upper_bound=0.1,
    #     unit="1/min",
    # ),
]

parameters_pharmacodynamics = [
    # bodyweight
    FitParameter(
        pid = "EC50_FAT",
        lower_bound = 1E-6,
        start_value = 1.0,
        upper_bound = 1E3,
        unit = "mmol/l"
    ),
    FitParameter(
        pid = "Emax_FAT",
        lower_bound = 1E-6,
        start_value = 1.0,
        upper_bound = 1E3,
        unit = "1/min",
    ),
    #fpg
    FitParameter(
        pid="k_fpg",
        lower_bound=1E-6,
        start_value=0.2E-5,
        upper_bound=1E2,
        unit="l/min/mmole",
    )
]

parameters_all = parameters_pharmacokinetics + parameters_pharmacodynamics
