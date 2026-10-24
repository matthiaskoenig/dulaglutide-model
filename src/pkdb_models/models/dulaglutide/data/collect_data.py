"""Collect the data of the dulaglutide studies from the PK-DB study folders.

The studies are copied from a `pkdb_data` checkout (`PKDB_DATA`, else
`../pkdb_data`, see `pkpdsim.data.studies_dir`) into the data folder of the
model, see `pkpdsim.data.collect_tsv_files`.
"""

from pathlib import Path

from pkpdsim.data import collect_tsv_files
from pkpdsim.data import studies_dir as pkdb_studies_dir

from pkdb_models.models.dulaglutide import DATA_PATH_DULAGLUTIDE


def collect_data(studies_dir: Path | None = None) -> None:
    """Copy the data of the dulaglutide studies into the data folder of the model.

    Args:
        studies_dir: the `studies` folder of pkdb_data, by default the one of
            the checkout `pkpdsim.data.studies_dir` finds.
    """
    if studies_dir is None:
        studies_dir = pkdb_studies_dir()
    collect_tsv_files(
        source_dir=studies_dir / "dulaglutide", target_dir=DATA_PATH_DULAGLUTIDE
    )


if __name__ == "__main__":
    collect_data()
