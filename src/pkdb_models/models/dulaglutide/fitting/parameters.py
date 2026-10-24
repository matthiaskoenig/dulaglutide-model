"""The parameters of the dulaglutide fits with their bounds."""

from sbmlsim.fit import FitParameter

#: the pharmacokinetics of dulaglutide: the catabolic clearance, the
#: interstitial distribution and the subcutaneous absorption with its
#: bioavailability. The intravenous and subcutaneous crossover of FDAGBDR
#: separates the clearance, the volumes and the bioavailability.
parameters_pk: list[FitParameter] = [
    # CL = DULCAT_k * BP = 0.0426 l/hr (FDAGBDR IV), 1.45e-3 l/min of blood
    FitParameter(
        pid="DULCAT_k",
        start_value=1.55e-3,
        lower_bound=2e-4,
        upper_bound=1e-2,
        unit="l/min",
    ),
    # Vss 5.3 l (FDAGBDR IV), 2.5 l more than the plasma volume in about
    # 65 l of tissue
    FitParameter(
        pid="Kp_dul",
        start_value=0.1,
        lower_bound=0.005,
        upper_bound=0.5,
        unit="dimensionless",
    ),
    # the distribution phase of the IV data (35 ng/ml at 1 hr, 15 ng/ml at
    # 24 hr)
    FitParameter(
        pid="ftissue_dul",
        start_value=0.02,
        lower_bound=1e-3,
        upper_bound=1.0,
        unit="l/min",
    ),
    # tmax 48 hr, the half-life after SC (107 hr) longer than after IV (87 hr)
    FitParameter(
        pid="Ksc_dul",
        start_value=4e-4,
        lower_bound=2e-5,
        upper_bound=1e-2,
        unit="1/min",
    ),
    # F 0.44 after 1.5 mg (FDAGBDR), 0.65 and 0.47 after 0.75 and 1.5 mg
    # (label)
    FitParameter(
        pid="Fsc_dul",
        start_value=0.47,
        lower_bound=0.2,
        upper_bound=1.0,
        unit="dimensionless",
    ),
]

#: the fasting plasma glucose: the effect of dulaglutide and of the trial on
#: the excess FPG over the normal FPG and the rate of the response
parameters_fpg: list[FitParameter] = [
    FitParameter(
        pid="Emax_glp1_fpg",
        start_value=0.7,
        lower_bound=0.05,
        upper_bound=1.0,
        unit="dimensionless",
    ),
    # the plasma concentration at steady state is about 1 nM after 1.5 mg
    FitParameter(
        pid="EC50_glp1_fpg",
        start_value=5e-7,
        lower_bound=1e-8,
        upper_bound=1e-4,
        unit="mM",
    ),
    # the response within days (half-life about 2 days)
    FitParameter(
        pid="k_fpg",
        start_value=3.7e-4,
        lower_bound=1e-5,
        upper_bound=1e-2,
        unit="l/min",
    ),
    # the placebo arms: -0.5 mM of an excess of about 4 mM
    FitParameter(
        pid="f_trial_fpg",
        start_value=0.1,
        lower_bound=1e-3,
        upper_bound=0.5,
        unit="dimensionless",
    ),
]

#: the HbA1c: the turnover of the hemoglobin, time constants of 3-15 weeks
parameters_hba1c: list[FitParameter] = [
    FitParameter(
        pid="k_hb_deg",
        start_value=2e-5,
        lower_bound=5e-6,
        upper_bound=5e-5,
        unit="mmole/min",
    ),
]

#: the body weight: the fraction of the subcutaneous fat which dulaglutide
#: removes, its EC50 and the rate of the change (plateau at 26-52 weeks)
parameters_bodyweight: list[FitParameter] = [
    FitParameter(
        pid="Emax_SAT_glp1",
        start_value=0.3,
        lower_bound=0.01,
        upper_bound=0.8,
        unit="dimensionless",
    ),
    FitParameter(
        pid="EC50_SAT_glp1",
        start_value=1e-6,
        lower_bound=1e-8,
        upper_bound=1e-4,
        unit="mM",
    ),
    FitParameter(
        pid="k_SAT_glp1",
        start_value=1e-5,
        lower_bound=5e-7,
        upper_bound=1e-4,
        unit="1/min",
    ),
]

#: the parameters of the pharmacodynamic fit, on the adopted pharmacokinetics
parameters_pd: list[FitParameter] = [
    *parameters_fpg,
    *parameters_hba1c,
    *parameters_bodyweight,
]

#: all fitted parameters
parameters_all: list[FitParameter] = [*parameters_pk, *parameters_pd]
