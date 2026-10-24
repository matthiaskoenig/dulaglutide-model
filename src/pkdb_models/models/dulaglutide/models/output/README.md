[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18432433.svg)](https://doi.org/10.5281/zenodo.18432433)
[![GitHub Action](https://github.com/matthiaskoenig/dulaglutide-model/actions/workflows/python.yml/badge.svg)](https://github.com/matthiaskoenig/dulaglutide-model/actions/workflows/python.yml)
[![GitHub Action](https://github.com/matthiaskoenig/dulaglutide-model/actions/workflows/docker.yml/badge.svg)](https://github.com/matthiaskoenig/dulaglutide-model/actions/workflows/docker.yml)


# dulaglutide model
This repository provides the dulaglutide physiologically based pharmacokinetics/pharmacodynamics (PBPK/PD) model.

The model is distributed in [SBML](http://sbml.org) format available from [`dulaglutide_body.xml`](./models/dulaglutide_body.xml) with 
corresponding [SBML4humans model report](https://sbml4humans.de/report?url=https%3A%2F%2Fraw.githubusercontent.com%2Fmatthiaskoenig%2Fdulaglutide-model%2Fmain%2Fmodels%2Fdulaglutide_body.xml) and [model equations](./models/dulaglutide_body.md).

The COMBINE archive is available from [`dulaglutide_model.omex`](./dulaglutide_model.omex).

![PK/PD model overview](./figures/dulaglutide_model.png)

### Model
The whole-body model of dulaglutide (59.7 kDa, a GLP-1 analogue-IgG4 Fc fusion protein): the subcutaneous
depot with its bioavailability (the rest is degraded at the injection site), the distribution into the
interstitial space of the tissues and the protein catabolism, which scales with the body weight. The
pharmacodynamics are the fasting plasma glucose, the HbA1c (glycation of hemoglobin, at steady state at the
baselines of a subject) and the body weight (subcutaneous fat). The model has no submodels: the body model,
the HbA1c model and the body weight model are merged into one SBML model.
The fitted parameters carry their uncertainty from the fits to the data of 26 clinical studies as
`distrib:uncertainty` of the SBML.

## How to cite
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18432433.svg)](https://doi.org/10.5281/zenodo.18432433)

> Kim, M. & König, M. (2026).
> *Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of dulaglutide.*   
> Zenodo. [https://doi.org/10.5281/zenodo.18432433](https://doi.org/10.5281/zenodo.18432433)

## License

* Source Code: [MIT](https://opensource.org/license/MIT)
* Documentation: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
* Models: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.

## Run simulations
### python
Clone the repository 
```bash
git clone https://github.com/matthiaskoenig/dulaglutide-model.git
cd dulaglutide-model
```

#### uv
Run the complete analysis with uv (https://docs.astral.sh/uv/getting-started/installation/):
```bash
uv run run_simulation pkdb_models.models.dulaglutide -a all -r results
```

#### pip
If you use pip install the package via
```bash
pip install -e .
```
Run the complete analysis in the environment via:
```bash
run_simulation pkdb_models.models.dulaglutide -a all -r results
```

### docker
Simulations can also be run within a docker container:

```bash
docker run -v "${PWD}/results:/results" -it matthiaskoenig/dulaglutide:latest /bin/bash
```

Run the complete analysis:
```bash
uv run run_simulation pkdb_models.models.dulaglutide -a all -r /results
```
The results are written into the mounted `/results` folder on the host.

In case of permission issues with the mounted folder, adjust ownership and access rights with:
```bash
sudo chown $(id -u):$(id -g) -R "${PWD}/results"
sudo chmod 775 "${PWD}/results"
```

## Funding
Matthias König was supported by the Federal Ministry of Research, Technology and Space (BMFTR, Germany) within ATLAS by grant number 031L0304B and by the German Research Foundation (DFG) within the Research Unit Program FOR 5151 QuaLiPerF (Quantifying Liver Perfusion-Function Relationship in Complex Resection - A Systems Medicine Approach) by grant number 436883643 and by grant number 465194077 (Priority Programme SPP 2311, Subproject SimLivA). This work was supported by the BMBF-funded de.NBI Cloud within the German Network for Bioinformatics Infrastructure (de.NBI) (031A537B, 031A533A, 031A538A, 031A533B, 031A535A, 031A537C, 031A534A, 031A532B).

© 2025-2026 Matthias König, [Systems Medicine of the Liver](https://livermetabolism.com)
