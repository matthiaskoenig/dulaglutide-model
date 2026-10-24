# Dulaglutide

Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of the GLP-1 receptor agonist dulaglutide, a dimeric GLP-1 analogue-IgG4 Fc fusion protein (59.7 kDa), given once weekly by subcutaneous injection. The subcutaneous dose is absorbed from a depot with a bioavailability of about 0.48, the rest is degraded at the injection site. Dulaglutide distributes into the interstitial space of the tissues (Vss about 5 l) and is catabolized like an immunoglobulin with a clearance that scales with the body weight (0.044 l/hr at 70 kg, a half-life of about 90 hr); it is not filtered or excreted, so the model has no renal or hepatic mechanism of its elimination. The pharmacodynamics in type 2 diabetes are the fasting plasma glucose (dulaglutide and the participation in a trial lower its excess over 5 mM), the HbA1c (glycation of hemoglobin, at steady state at the baselines of a subject) and the body weight (the subcutaneous fat relaxes to a set point lowered by dulaglutide). Healthy subjects have no glucose response.

The model repository of the release is [dulaglutide-model](https://github.com/matthiaskoenig/dulaglutide-model) ([10.5281/zenodo.18432433](https://doi.org/10.5281/zenodo.18432433)).

## Structure

- `__init__.py`: the paths of the model and its model object `MODEL` with its release metadata and its adopted fits, which the commands below run (pkpdsim).
- `models/`: the whole-body model (`model_body.py`) with the pharmacodynamics of the HbA1c and the fasting plasma glucose (`model_hba1c.py`) and of the body weight (`model_bodyweight.py`), merged into one SBML model without submodels. `models/factory.py` creates the SBML model which is simulated, the ODEs and the COMBINE archive in `models/output/`; the fitted values come from the adopted fits (`models/fits.py`, `models/output/fits/`).
- `experiments/`: the simulation experiments of the 26 clinical studies (`studies/`), the dose dependency of 26 weekly doses (`misc/`) and the parameter scans of the dose and the body weight (`scans/`). The fit mappings are described with the vocabulary of `pkpdsim.metadata`; the base sets the baselines of the subjects (`baseline_changes`: body weight, HbA1c, FPG).
- `fitting/`: the fit problems of the pharmacokinetics (`PK`) and of the pharmacodynamics on the adopted pharmacokinetics (`PD`), their parameters and the selection of the training data and of the validation data by question (doses, populations, limitations), the outliers and the aggregates.
- `sensitivity/`: the sensitivity analysis of the pharmacokinetics after a single dose and of the pharmacodynamics after 26 weekly doses.
- `dulaglutide_pk.py`: the pharmacokinetic parameters of the scans, the non-compartmental analysis of `pkpdutils`, over the draws of the fitted parameters.
- `tolerances.py`: the absolute tolerances of the integrator per state.
- `simulations.py`: the simulation experiments and their groups, `MODEL` runs them.
- `data/`: the data of the studies, a subset of the PK-DB studies (`data/collect_data.py`) with corrections against the publications.
- `baseline_viz/`: the baselines (HbA1c, FPG, body weight) of the curated studies and their changes under dulaglutide, with the regressions between them (`fpg_from_hba1c` of the experiments is such a regression).
- `TODO.md`: the open issues of the model.

## Commands

```bash
# models, simulations
run_simulation pkdb_models.models.dulaglutide --action factory
run_simulation pkdb_models.models.dulaglutide --action list_experiments
run_simulation pkdb_models.models.dulaglutide --action simulate --experiments all
run_simulation pkdb_models.models.dulaglutide --action simulate --experiments all --uncertainty

# fits, adoption of a fit, reports of stored parameters, identifiability
run_fit pkdb_models.models.dulaglutide --subset=PK --runs=3 --cores=3 --method=DE
run_fit pkdb_models.models.dulaglutide --subset=PD --runs=3 --cores=3 --method=DE
run_fit pkdb_models.models.dulaglutide --adopt PK_<fit id>
run_report pkdb_models.models.dulaglutide --subset=PK results/fit/PK_<fit id>/parameters.json
run_identifiability pkdb_models.models.dulaglutide --subset=PK results/fit/PK_<fit id>/parameters.json

# sensitivity analysis (local by default)
python -m pkdb_models.models.dulaglutide.sensitivity.sensitivity_analysis
```

The results are written into `results/` of the model.

## Adopted fits and uncertainty

The values of the fitted parameters come from the adopted fits of the model,
not from numbers in the code: `PK_20261018_102441__faa2d` (the
pharmacokinetics: catabolism, interstitial distribution, subcutaneous
absorption and bioavailability) and `PD_20261019_103700__c0378` (the effects
on the fasting plasma glucose, the HbA1c turnover, the trial effect and the
body weight). `run_fit pkdb_models.models.dulaglutide --adopt <fit id>` copies
the record of a finished fit (its parameters, problem, profile likelihood and
Fisher information) into `models/output/fits/<fit id>/`, which is tracked; the
ids of the adopted fits are listed in `fits` of the model object
(`__init__.py`). The factory takes the fitted values and their uncertainty from
the records (`models/fits.py`) and writes the uncertainty into the SBML
(`distrib:uncertainty`). `run_simulation ... --uncertainty` runs the
experiments over draws of these distributions and draws the simulations as the
median with a band of quantiles into `results/simulation_uncertainty`. A refit
is: fit, adopt, replace the id in `fits`, rebuild the model. The PD fit rests
on the adopted PK, a refit of the PK needs a refit of the PD.
