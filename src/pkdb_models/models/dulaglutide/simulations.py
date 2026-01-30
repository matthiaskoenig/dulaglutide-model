"""Run all simulation experiments."""
import shutil
from pathlib import Path

from sbmlutils.console import console

from pkdb_models.models.dulaglutide.helpers import run_experiments
from pkdb_models.models.dulaglutide.experiments.studies import *
from pkdb_models.models.dulaglutide.experiments.misc import *
from pkdb_models.models.dulaglutide.experiments.scans import *
import pkdb_models.models.dulaglutide as dulaglutide

from sbmlutils import log
from sbmlsim.plot import Figure

Figure.legend_fontsize = 10
Figure.legend_position: str = "inside"
Figure.fig_dpi = 300


logger = log.get_logger(__name__)

EXPERIMENTS = {
    "studies": [
        Barrington2011,
        Barrington2011a,
        Blonde2015,
        Chen2018,
        Dungan2014,
        Dungan2016,
        FDAGBCM,
        FDAGBCN,
        FDAGBDO,
        FDAGBDR,
        Gao2024,
        Gerstein2019,
        Giorgino2015,
        Liu2025,
        Nauck2014,
        Pratley2018,
        Xu2022,
        Zhang2023
    ],
    "hepatic_impairment": [
    ],
    "renal_impairment": [
    ],
    "misc": [
        DoseDependencyExperiment,
    ],
    "scan": [
        DulaglutideParameterScan
    ]
}
EXPERIMENTS["all"] = EXPERIMENTS["studies"] + EXPERIMENTS["misc"] + EXPERIMENTS["scan"]


def run_simulation_experiments(
        selected: str = None,
        experiment_classes: list = None,
        output_dir: Path = None
) -> None:
    """Run simulation experiments."""

    # Figure.fig_dpi = 600
    # Figure.legend_fontsize = 10

    # Determine which experiments to run
    if experiment_classes is not None:
        experiments_to_run = experiment_classes
        if output_dir is None:
            output_dir = dulaglutide.RESULTS_PATH_SIMULATION / "custom_selection"
    elif selected:
        # Using the 'selected' parameter
        if selected not in EXPERIMENTS:
            console.rule(style="red bold")
            console.print(
                f"[red]Error: Unknown group '{selected}'. Valid groups: {', '.join(EXPERIMENTS.keys())}[/red]"
            )
            console.rule(style="red bold")
            return
        experiments_to_run = EXPERIMENTS[selected]
        if output_dir is None:
            output_dir = dulaglutide.RESULTS_PATH_SIMULATION / selected
    else:
        console.print("\n[red bold]Error: No experiments specified![/red bold]")
        console.print("[yellow]Use selected='all' or selected='studies' or provide experiment_classes=[...][/yellow]\n")
        return

    # Run the experiments
    run_experiments(experiment_classes=experiments_to_run, output_dir=output_dir)

    # Collect figures into one folder
    figures_dir = output_dir / "_figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    for f in output_dir.glob("**/*.png"):
        if f.parent == figures_dir:
            continue
        try:
            shutil.copy2(f, figures_dir / f.name)
        except Exception as err:
            print(f"file {f.name} in {f.parent} fails, skipping. Error: {err}")
    console.print(f"Figures copied to: file://{figures_dir}", style="info")


if __name__ == "__main__":
    """
    # Run experiments

    # selected = "all"
    # selected = "misc"
    # selected = "studies"
    # selected = "pharmacodynamics"
    # selected = "dose_dependency"
    # selected = "food"
    # selected = "hepatic_impairment"
    # selected = "renal_impairment"
    # selected = "scan"
    """

    run_simulation_experiments(selected="all")
