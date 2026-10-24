"""Dulaglutide parameter fitting.

The fit problems of the dulaglutide model: which fit mapping collections enter
a fit and which parameters are adjusted, see `FIT_DEFINITIONS`. The commands
`run_fit`, `run_report` and `run_identifiability` of pkpdsim run them with the
package of the model:

    run_fit pkdb_models.models.dulaglutide --subset=PK --runs=3 --cores=3 --seed=1234 --method=DE
    run_fit pkdb_models.models.dulaglutide --subset=PD --runs=3 --cores=3 --seed=1234 --method=DE

The pharmacokinetics are fitted first, the pharmacodynamics (the fasting
plasma glucose, the HbA1c and the body weight) on the adopted values of the
pharmacokinetics (`MODEL.fits`).

The results, figures and the HTML report are written into the fit folder of the
model (`MODEL.fit_dir`), unless `--output_dir` is given. The identifiability of
parameters which were fitted earlier is analysed without fitting again with the
`run_identifiability` command, a report of stored parameters is created with
the `run_report` command:

    run_identifiability pkdb_models.models.dulaglutide --subset=PK results/fit/PK_<fit id>/parameters.json
    run_report pkdb_models.models.dulaglutide --subset=PK results/fit/PK_<fit id>/parameters.json
"""

from pkpdsim.fit import default_fit_settings
from sbmlsim.fit.cli import FitDefinition

from pkdb_models.models.dulaglutide import DATA_PATHS, DULAGLUTIDE_PATH
from pkdb_models.models.dulaglutide.fitting.mapping_collections import (
    f_collections_pd,
    f_collections_pk,
)
from pkdb_models.models.dulaglutide.fitting.parameters import (
    parameters_pd,
    parameters_pk,
)
from pkdb_models.models.dulaglutide.tolerances import absolute_tolerance

#: settings of the fits, stored with the result and read back by the report;
#: the dulaglutide states get tolerances of their own scale, see `tolerances`
FIT_SETTINGS = default_fit_settings(
    absolute_tolerance=absolute_tolerance(1e-6, dulaglutide=1e-14)
)

#: the fit problems of the dulaglutide model, the keys are the `--subset` argument
FIT_DEFINITIONS: dict[str, FitDefinition] = {
    # the pharmacokinetics of dulaglutide (IV and SC)
    "PK": FitDefinition(
        mapping_collections=f_collections_pk,
        parameters=parameters_pk,
        base_path=DULAGLUTIDE_PATH,
        data_path=DATA_PATHS,
        settings=FIT_SETTINGS,
    ),
    # the pharmacodynamics: fasting plasma glucose, HbA1c and body weight
    "PD": FitDefinition(
        mapping_collections=f_collections_pd,
        parameters=parameters_pd,
        base_path=DULAGLUTIDE_PATH,
        data_path=DATA_PATHS,
        settings=FIT_SETTINGS,
    ),
}
