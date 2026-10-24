[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18432433.svg)](https://doi.org/10.5281/zenodo.18432433)
[![Release](https://img.shields.io/github/v/release/matthiaskoenig/dulaglutide-model)](https://github.com/matthiaskoenig/dulaglutide-model/releases)
[![Documentation](https://github.com/matthiaskoenig/dulaglutide-model/actions/workflows/docs.yml/badge.svg)](https://matthiaskoenig.github.io/dulaglutide-model/)
[![CI](https://github.com/matthiaskoenig/dulaglutide-model/actions/workflows/ci.yml/badge.svg)](https://github.com/matthiaskoenig/dulaglutide-model/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/docker/v/matthiaskoenig/dulaglutide?sort=semver&label=docker)](https://hub.docker.com/r/matthiaskoenig/dulaglutide)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org)
[![Code license: MIT](https://img.shields.io/badge/code%20license-MIT-blue)](https://opensource.org/license/MIT)
[![Model license: CC BY-SA 4.0](https://img.shields.io/badge/model%20license-CC%20BY--SA%204.0-lightgrey)](https://creativecommons.org/licenses/by-sa/4.0/)

# Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of dulaglutide

This repository provides the dulaglutide physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model: the subcutaneous absorption of dulaglutide with its bioavailability, its distribution into the interstitial space, its protein catabolism and its effects on the fasting plasma glucose, the HbA1c and the body weight in type 2 diabetes.

Documentation: <https://matthiaskoenig.github.io/dulaglutide-model/>

## Quick start

```bash
git clone https://github.com/matthiaskoenig/dulaglutide-model.git && cd dulaglutide-model
uv sync
uv run run_simulation pkdb_models.models.dulaglutide --action all -r results
```

## How to cite

> Kim, M. & König, M. (2026). *Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of dulaglutide*. Zenodo. https://doi.org/10.5281/zenodo.18432433

## License

* Source Code: [MIT](https://opensource.org/license/MIT)
* Documentation: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
* Models: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

&copy; 2025-2026 Minjun Kim and Matthias König
