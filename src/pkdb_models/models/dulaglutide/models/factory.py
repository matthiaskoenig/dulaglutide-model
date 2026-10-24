"""Dulaglutide model factory."""

from pathlib import Path
from typing import Any

from pkpdsim.licenses import License, write_license
from pymetadata.omex import EntryFormat, ManifestEntry, Omex
from sbmlode import OdeSystem
from sbmlutils.factory import create_model

from pkdb_models.models.dulaglutide import MODEL_BASE_PATH
from pkdb_models.models.dulaglutide.models.model_body import model_body
from pkdb_models.models.dulaglutide.models.model_bodyweight import model_bodyweight
from pkdb_models.models.dulaglutide.models.model_hba1c import model_hba1c


def create_dulaglutide_models(model_output_dir: Path) -> dict[str, dict[str, Any]]:
    """Create the whole-body model of dulaglutide.

    The whole-body model is the body model merged with the body weight and
    HbA1c models with the parameters of dulaglutide. It has no submodels (no
    `comp`), so it is the model the simulations run and the master of the
    COMBINE archive, which is written next to the directory of the models,
    with the README, the licenses and the figure of the model.

    Args:
        model_output_dir: directory of the models, the COMBINE archive and the
            license texts are written into its parent.

    Returns:
        The files of the model with their entries in the COMBINE archive.
    """
    model_output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {
        "README": {
            "path": MODEL_BASE_PATH.parent / "README.md",
            "entry": ManifestEntry(
                location="./README.md",
                format=EntryFormat.MARKDOWN,
                master=False,
            ),
        },
        "cc-by": {
            "path": write_license(model_output_dir.parent, License.CC_BY_SA_4_0),
            "entry": ManifestEntry(
                location="./cc-by-sa-4.0.txt",
                format=EntryFormat.TXT,
                master=False,
            ),
        },
        "mit": {
            "path": write_license(
                model_output_dir.parent,
                License.MIT,
                copyright="2025-2026 Matthias König",
            ),
            "entry": ManifestEntry(
                location="./mit.txt",
                format=EntryFormat.TXT,
                master=False,
            ),
        },
        "model_figure": {
            "path": MODEL_BASE_PATH.parent / "figures" / "dulaglutide_model.png",
            "entry": ManifestEntry(
                location="./figures/dulaglutide_model.png",
                format=EntryFormat.PNG,
                master=False,
            ),
        },
    }
    models = [model_bodyweight, model_hba1c, model_body]
    sid = model_body.sid
    factory_results = create_model(
        model=models,
        filepath=model_output_dir / f"{sid}.xml",
        sbml_level=3,
        sbml_version=2,
    )
    sbml_path = factory_results.sbml_path
    results[sid] = {
        "path": sbml_path,
        "entry": ManifestEntry(
            location=f"./models/{sbml_path.name}",
            format=EntryFormat.SBML_L3V2,
            master=True,
        ),
    }

    # create differential equations
    md_path = model_output_dir / f"{sid}.md"
    ode_system = OdeSystem.from_sbml(sbml_path)
    ode_system.write(md_path)
    results[f"{sid}_md"] = {
        "path": md_path,
        "entry": ManifestEntry(
            location=f"./models/{md_path.name}",
            format=EntryFormat.MARKDOWN,
            master=False,
        ),
    }

    # create omex
    omex = Omex()
    for info in results.values():
        omex.add_entry(entry_path=info["path"], entry=info["entry"])
    omex.to_omex(omex_path=model_output_dir.parent / "dulaglutide_model.omex")

    return results


if __name__ == "__main__":
    # create the models
    create_dulaglutide_models(MODEL_BASE_PATH)
