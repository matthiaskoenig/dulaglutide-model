"""Run all simulation experiments."""
import shutil

from sbmlutils.console import console

from pkdb_models.models.bodyweight.helpers import run_experiments
from pkdb_models.models.bodyweight.experiments.misc import *

from sbmlutils import log
from sbmlsim.plot import Figure

Figure.legend_fontsize = 10
Figure.fig_dpi = 300


logger = log.get_logger(__name__)


if __name__ == "__main__":
    """Run experiments."""
    from pkdb_models.models.hba1c import RESULTS_PATH
    experiments = {

        "misc": [
            Hba1cExperiment
        ],
    }
    experiments["all"] = experiments["misc"]
    selected = "all"

    output_dir = RESULTS_PATH / selected
    run_experiments(
        experiment_classes=experiments[selected],
        output_dir=output_dir,
    )

    # collect figures
    figures_dir = RESULTS_PATH / selected / "_figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    for f in output_dir.glob("**/*.png"):
        try:
            shutil.copy2(f, figures_dir / f.name)
        except shutil.SameFileError as err:
            console.print(str(err), style="warning")

