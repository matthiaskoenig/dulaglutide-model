
from typing import Dict

from sbmlsim.plot import Axis, Figure, Plot
from sbmlsim.simulation import Timecourse, TimecourseSim

from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)
from pkdb_models.models.dulaglutide.helpers import run_experiments


class DoseDependencyExperiment(DulaglutideSimulationExperiment):
    """Tests po application."""

    routes = {
        "dul": ["IV", "SC"],
    }
    doses = [0, 0.25, 0.5, 0.75, 1.5]  # [mg]
    colors = ["black", "tab:orange", "tab:blue", "tab:red", "tab:green"]

    def simulations(self) -> Dict[str, TimecourseSim]:
        Q_ = self.Q_
        tcsims = {}

        for substance, routes in self.routes.items():
            for route in routes:
                for dose in self.doses:

                    tc0 = Timecourse(
                        start=0,
                        end=7 * 24 * 60,  # [min]  every week
                        steps=1000,
                        changes={
                            **self.default_changes(),
                            f"{route}DOSE_{substance}": Q_(dose, "mg"),
                        },
                    )
                    tc1 = Timecourse(
                        start=0,
                        end=7 * 24 * 60,  # [min]  every week
                        steps=1000,
                        changes={
                            f"{route}DOSE_{substance}": Q_(dose, "mg"),
                        },
                    )
                    tc2 = Timecourse(
                        start=0,
                        end=8 * 7 * 24 * 60,  # [min]  8 weeks
                        steps=1000,
                        changes={
                            f"{route}DOSE_{substance}": Q_(dose, "mg"),
                        },
                    )

                    tcsims[f"dul_{substance}_{route}_{dose}"] = TimecourseSim(
                        [tc0] + [tc1 for _ in range(3)] + [tc2],
                        time_offset=0
                    )


        return tcsims

    def figures(self) -> Dict[str, Figure]:
        return {
            **self.figure_pk(),
        }

    def figure_pk(self) -> Dict[str, Figure]:
        figures = {}
        for substance, routes in self.routes.items():
            for route in routes:

                fig = Figure(
                    experiment=self,
                    sid=f"Fig_dose_dependency_pk_{substance}_{route}",
                    num_rows=5,
                    num_cols=2,
                    name=f"Dose Dependency {substance}_{route}",
                )
                plots = fig.create_plots(xaxis=Axis("time", unit="week"), legend=True)
                sids = [
                    # plasma
                    "[Cve_dul]",
                    "[Cve_dm]",

                    # urine,
                    "Aurine_dm",

                    # feces
                    "Afeces_dm",

                    "BW",
                    "BW_change",
                    "hba1c",
                    "hba1c_change",
                    "[fpg]",
                    "fpg_change",
                ]
                for ksid, sid in enumerate(sids):
                    if sid:
                        plots[ksid].set_yaxis(label=self.labels[sid], unit=self.units[sid])

                for ksid, sid in enumerate(sids):
                    if sid:
                        for kval, dose in enumerate(self.doses):
                            plots[ksid].add_data(
                                task=f"task_dul_{substance}_{route}_{dose}",
                                xid="time",
                                yid=sid,
                                label=f"{dose} mg",
                                color=self.colors[kval],
                            )

                figures[fig.sid] = fig

        return figures


if __name__ == "__main__":
    run_experiments(DoseDependencyExperiment, output_dir=DoseDependencyExperiment.__name__)