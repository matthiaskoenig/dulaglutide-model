"""
Reusable functionality for multiple simulation experiments.
"""

from typing import Dict

from pkdb_models.models.bodyweight import MODEL_BASE_PATH
from sbmlsim.experiment import SimulationExperiment
from sbmlsim.model import AbstractModel
from sbmlsim.task import Task



class BodyweightSimulationExperiment(SimulationExperiment):
    """Base class for all SimulationExperiments."""

    font = {"weight": "bold", "size": 22}
    scan_font = {"weight": "bold", "size": 15}
    tick_font_size = 15
    legend_font_size = 9
    suptitle_font_size = 25

    # labels
    label_time = "time"
    label_bw = "bodyweight"
    label_fat = "FAT"
    label_lbw = "LBW"
    label_bmi = "BMI"
    label_bsa = "BSA"

    labels: Dict[str, str] = {
        "time": "time",
        "BW": label_bw,
        "BW0": "initial " + label_bw,
        "FAT": label_fat,
        "FAT0": "initial " + label_fat,
        "LBW0": label_lbw,
        "BMI": label_bmi,
        "BSA": label_bsa,

    }
    # units
    unit_time = "day"
    unit_bw = "kg"
    unit_fat = "kg"
    unit_lbw = "kg"
    unit_bmi = "kg/m^2"
    unit_bsa = "m^2"

    units: Dict[str, str] = {
        "time": unit_time,
        "BW": unit_bw,
        "BW0": unit_bw,
        "FAT": unit_fat,
        "FAT0": unit_fat,
        "LBW0": unit_lbw,
        "BMI": unit_bmi,
        "BSA": unit_bsa,
    }

    def models(self) -> Dict[str, AbstractModel]:
        Q_ = self.Q_
        return {
            "model": AbstractModel(
                source=MODEL_BASE_PATH / "bodyweight.xml",
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
        return BodyweightSimulationExperiment._default_changes(Q_=self.Q_)

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

                # dosing
                'HEIGHT',
                'BW0',
                'FAT0',
                'BW',
                'LBW0',
                'FAT',
                'BMI',
                'BSA',
                'SEX',
            ]
        )
        return {}
