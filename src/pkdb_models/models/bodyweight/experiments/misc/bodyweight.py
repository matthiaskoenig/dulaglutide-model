
from typing import Dict

from sbmlsim.plot import Axis, Figure, Plot
from sbmlsim.simulation import Timecourse, TimecourseSim

from pkdb_models.models.bodyweight.experiments.bodyweight_experiment import (
    BodyweightSimulationExperiment,
)
from pkdb_models.models.bodyweight.helpers import run_experiments


class BodyweightExperiment(BodyweightSimulationExperiment):
    """Tests po application."""

    bodyweights = [50, 75, 100, 125, 150]  # [kg]
    doses = [0, 2.5, 5, 10, 20]
    colors = {
        "bodyweight": ["blue", "tab:blue", "black", "tab:red", "red"],
        "dose": ["black", "tab:blue", "tab:orange", "tab:green", "tab:red"],
    }

    def simulations(self) -> Dict[str, TimecourseSim]:
        Q_ = self.Q_
        tcsims = {}

        changes = {
            "Emax_FAT": Q_(1 / 70, "1/day"),
            "EC50_FAT": Q_(5.0, "mM"),
        }

        for bodyweight in self.bodyweights:
            tcsims[f"bodyweight_{bodyweight}"] = TimecourseSim(
                Timecourse(
                    start=0,
                    end=50 * 7 * 24*60,  # 30 days,
                    steps = 1000,
                    changes={
                        "BW0": Q_(bodyweight, "kg"),
                        "D": Q_(5, "mM"),
                        **changes,
                    }
                )
            )
        for dose in self.doses:
            tcsims[f"dose_{dose}"] = TimecourseSim(
                Timecourse(
                    start=0,
                    end=50 * 7 * 24*60,  # 30 days,
                    steps = 1000,
                    changes={
                        "BW0": Q_(100, "kg"),
                        "D": Q_(dose, "mM"),
                        **changes,
                    }
                )
            )


        return tcsims

    def figures(self) -> Dict[str, Figure]:
        return {
            **self.figure_pd(),
        }

    def figure_pd(self) -> Dict[str, Figure]:
        figures = {}

        for key in ["dose", "bodyweight"]:

            fig = Figure(
                experiment=self,
                sid=f"Fig_{key}",
                num_rows=4,
                num_cols=2,
                name=f"{key.title()}",
            )
            plots = fig.create_plots(xaxis=Axis("time", unit="week"), legend=True)
            sids = [
                # plasma
                ("BW0", 0),
                ("LBW0", 1),
                ("FAT0", 2),

                ("BW", 4),
                ("FAT", 5),


                ("BMI", 6),
                ("BSA", 7),
            ]

            for sid, ksid in sids:
                if sid:
                    plots[ksid].set_yaxis(label=self.labels[sid], unit=self.units[sid], min=0)

            if key == "bodyweight":
                values = self.bodyweights
                unit = "kg"
            elif key == "dose":
                values = self.doses
                unit = "mM"

            colors = self.colors[key]
            for kcolor, value in enumerate(values):
                for (sid, ksid) in sids:
                    plots[ksid].add_data(
                        task=f"task_{key}_{value}",
                        xid="time",
                        yid=sid,
                        label=f"{value} {unit}",
                        color=colors[kcolor],
                    )

            figures[fig.sid] = fig

        return figures


if __name__ == "__main__":
    run_experiments(BodyweightExperiment, output_dir=BodyweightExperiment.__name__)
