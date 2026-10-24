"""Simulation experiment of the dose dependency of subcutaneous dulaglutide."""

from typing import ClassVar, override

from sbmlsim import Q
from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Simulation

from pkdb_models.models.dulaglutide import MODEL
from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)


class DoseDependencyExperiment(DulaglutideSimulationExperiment):
    """26 weekly subcutaneous doses of dulaglutide in T2DM, followed for 39 weeks."""

    routes: ClassVar[dict[str, list[str]]] = {
        "dul": ["SC"],
    }
    #: the names of the substances and the routes in the titles of the figures
    names: ClassVar[dict[str, str]] = {"dul": "dulaglutide", "SC": "s.c."}
    bodyweight: ClassVar[int] = 90  # [kg]
    hba1c: ClassVar[float] = 8.0  # [percent], T2DM
    fpg: ClassVar[float] = 9.14  # [mM], `fpg_from_hba1c`
    doses: ClassVar[list[float]] = [0, 0.25, 0.5, 0.75, 1.5]  # [mg]
    n_doses: ClassVar[int] = 26
    colors: ClassVar[list[str]] = [
        "black",
        "tab:orange",
        "tab:blue",
        "tab:red",
        "tab:green",
    ]

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        week = 7 * 24  # [hr]

        for substance, routes in self.routes.items():
            for route in routes:
                for dose in self.doses:
                    simulations[self.to_sid(f"dul_{substance}_{route}_{dose}")] = (
                        Simulation(
                            time_unit="hr",
                            # weekly doses, followed for 13 weeks after the
                            # last dose
                            end=(self.n_doses + 13) * week,
                            preinit_changes={
                                **self.default_changes(),
                                **self.baseline_changes(
                                    self.bodyweight, self.hba1c, Q(self.fpg, "mM")
                                ),
                                # week 0
                                f"{route}DOSE_{substance}": Q(dose, "mg"),
                            },
                            changes=[
                                # weekly doses
                                self.add_doses(
                                    [k * week for k in range(1, self.n_doses)],
                                    {f"{route}DOSE_{substance}": Q(dose, "mg")},
                                ),
                            ],
                        )
                    )

        return simulations

    @override
    def figures(self) -> dict[str, Figure]:
        return self.figures_by_sid(
            # pharmacokinetics and pharmacodynamics
            *self._figures_doses(
                kind="pk",
                sids=[
                    # plasma
                    "[Cvep_dul]",
                    # subcutaneous depot
                    "SCDEPOT_dul",
                    # mass balance
                    "Acat_dul",
                    "Asc_deg_dul",
                    "BW",
                    "BW_change",
                    "hba1c",
                    "hba1c_change",
                    "[fpg]",
                    "fpg_change",
                ],
                num_rows=5,
                num_cols=2,
            ),
            # body composition
            *self._figures_doses(
                kind="bodyweight",
                sids=[
                    # plasma
                    "[Cvep_dul]",
                    "LBW0",
                    "BW",
                    "FAT",
                ],
                num_rows=2,
                num_cols=2,
            ),
        )

    def _figures_doses(
        self, kind: str, sids: list[str], num_rows: int, num_cols: int
    ) -> list[Figure]:
        """Figures of the timecourses of all doses, one figure per route.

        Args:
            kind: kind of the figure in its id.
            sids: ids of the variables, one panel each.
            num_rows: number of rows of the panels.
            num_cols: number of columns of the panels.
        """
        figures: list[Figure] = []
        for substance, routes in self.routes.items():
            for route in routes:
                fig = Figure(
                    experiment=self,
                    sid=self.to_sid(f"Fig_dose_dependency_{kind}_{substance}_{route}"),
                    num_rows=num_rows,
                    num_cols=num_cols,
                    name=(
                        f"Dose dependency of {self.names[substance]}"
                        f" ({self.names[route]})"
                    ),
                    settings={"legend_scope": "row"},
                )
                plots = fig.create_plots(xaxis=Axis("time", unit="week"), legend=True)
                for ksid, sid in enumerate(sids):
                    plots[ksid].set_yaxis(label=self.labels[sid], unit=self.units[sid])
                    for kval, dose in enumerate(self.doses):
                        plots[ksid].add_data(
                            task=self.to_sid(f"task_dul_{substance}_{route}_{dose}"),
                            xid="time",
                            yid=sid,
                            label=f"{dose} mg",
                            color=self.colors[kval],
                        )

                figures.append(fig)

        return figures


if __name__ == "__main__":
    MODEL.run_experiments(
        DoseDependencyExperiment, output_dir=DoseDependencyExperiment.__name__
    )
