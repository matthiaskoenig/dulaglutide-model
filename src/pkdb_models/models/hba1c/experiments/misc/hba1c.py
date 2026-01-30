
from typing import Dict

from sbmlsim.plot import Axis, Figure, Plot
from sbmlsim.simulation import Timecourse, TimecourseSim

from pkdb_models.models.hba1c.experiments.hba1c_experiment import (
    Hba1cSimulationExperiment,
)
from pkdb_models.models.hba1c.helpers import run_experiments


class Hba1cExperiment(Hba1cSimulationExperiment):
    """Tests po application."""

    fpgs = [5, 6, 7, 8, 9]  # [mM]
    hba1cs = [5, 6, 7, 8, 9]  # [percent]
    concentrations = [0E-6, 5E-6, 10E-6, 20E-6, 40E-6]  # glp1 [mM]
    value_units = {
        "fpg": "mM",
        "hba1c": "percent",
        "concentration": "mM",
    }
    colors = {
        "fpg": ["blue", "tab:blue", "black", "tab:red", "red"],
        "hba1c": ["blue", "tab:blue", "black", "tab:red", "red"],
        "concentration": ["black", "tab:blue", "tab:orange", "tab:green", "tab:red"],
    }

    def simulations(self) -> Dict[str, TimecourseSim]:
        Q_ = self.Q_
        tcsims = {}

        changes = {
            "k_fpg": Q_(1E-5/5, "l*l/min/mmole"),
            # diabetes
            "fpg0": Q_(8, "mM"),
            "[fpg]": Q_(8, "mM"),
            "hba1c0": Q_(8, "percent"),
            "hba1c": Q_(8, "percent"),
            # glp1 ra drug
            "glp1": Q_(5, "mM"),
        }

        for fpg in self.fpgs:
            tcsims[f"fpg_{fpg}"] = TimecourseSim(
                Timecourse(
                    start=0,
                    end=50 * 7 * 24*60,  # 30 days,
                    steps = 1000,
                    changes={
                        **changes,
                        "fpg0": Q_(fpg, "mM"),
                        "[fpg]": Q_(fpg, "mM"),
                    }
                )
            )
        for hba1c in self.hba1cs:
            tcsims[f"hba1c_{hba1c}"] = TimecourseSim(
                Timecourse(
                    start=0,
                    end=50 * 7 * 24*60,  # 30 days,
                    steps = 1000,
                    changes={
                        **changes,
                        "hba1c0": Q_(hba1c, "percent"),
                        "hba1c": Q_(hba1c, "percent"),
                    }
                )
            )
        for concentration in self.concentrations:
            tcsims[f"concentration_{concentration}"] = TimecourseSim(
                Timecourse(
                    start=0,
                    end=50 * 7 * 24*60,  # 30 days,
                    steps = 1000,
                    changes={
                        **changes,
                        "glp1": Q_(concentration, "mM"),
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

        for key in ["concentration", "fpg", "hba1c"]:

            fig = Figure(
                experiment=self,
                sid=f"Fig_{key}",
                num_rows=2,
                num_cols=2,
                name=f"{key.title()}",
            )
            plots = fig.create_plots(xaxis=Axis("time", unit="month"), legend=True)
            sids = [
                # plasma
                ("fpg0", 0),
                ("[fpg]", 1),
                ("hba1c0", 2),
                ("hba1c", 3),
            ]

            for sid, ksid in sids:
                if sid:
                    plots[ksid].set_yaxis(label=self.labels[sid], unit=self.units[sid], min=0)

            if key == "fpg":
                values = self.fpgs
            elif key == "hba1c":
                values = self.hba1cs
            elif key == "concentration":
                values = self.concentrations

            colors = self.colors[key]
            for kcolor, value in enumerate(values):
                for (sid, ksid) in sids:
                    plots[ksid].add_data(
                        task=f"task_{key}_{value}",
                        xid="time",
                        yid=sid,
                        label=f"{value} {self.value_units[key]}",
                        color=colors[kcolor],
                    )

            figures[fig.sid] = fig

        return figures


if __name__ == "__main__":
    run_experiments(Hba1cExperiment, output_dir=Hba1cExperiment.__name__)
