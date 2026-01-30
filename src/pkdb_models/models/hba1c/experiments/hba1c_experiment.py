"""
Reusable functionality for multiple simulation experiments.
"""

from typing import Dict

from pkdb_models.models.hba1c import MODEL_BASE_PATH
from sbmlsim.experiment import SimulationExperiment
from sbmlsim.model import AbstractModel
from sbmlsim.task import Task



class Hba1cSimulationExperiment(SimulationExperiment):
    """Base class for all SimulationExperiments."""

    font = {"weight": "bold", "size": 22}
    scan_font = {"weight": "bold", "size": 15}
    tick_font_size = 15
    legend_font_size = 9
    suptitle_font_size = 25

    # labels
    label_time = "time"
    label_hba1c = "HbA1c"
    label_fpg = "FPG"

    labels: Dict[str, str] = {
        "time": "time",
        "hba1c": label_hba1c,
        "hba1c0": "initial " + label_hba1c,
        "[fpg]": label_fpg,
        "fpg0": "initial " + label_fpg,

    }
    # units
    unit_time = "day"
    unit_hba1c = "percent"
    unit_fpg = "mM"

    units: Dict[str, str] = {
        "time": unit_time,
        "hba1c": unit_hba1c,
        "hba1c0": unit_hba1c,
        "[fpg]": unit_fpg,
        "fpg0": unit_fpg,
    }

    def models(self) -> Dict[str, AbstractModel]:
        Q_ = self.Q_
        return {
            "model": AbstractModel(
                source=MODEL_BASE_PATH / "hba1c_model.xml",
                language_type=AbstractModel.LanguageType.SBML,
                changes={},
            )
        }

    @staticmethod
    def _default_changes(Q_):
        """Default changes to simulations."""

        changes = {
        }

        return changes

    def default_changes(self: SimulationExperiment) -> Dict:
        """Default changes to simulations."""
        return Hba1cSimulationExperiment._default_changes(Q_=self.Q_)

    def tasks(self) -> Dict[str, Task]:
        if self.simulations():
            return {
                f"task_{key}": Task(model="model", simulation=key)
                for key in self.simulations()
            }
        return {}

    def data(self) -> Dict:
        self.add_selections_data(
            selections=[
                "time",
                'hba1c0',
                'hba1c',
                'fpg0',
                '[fpg]',
            ]
        )
        return {}
