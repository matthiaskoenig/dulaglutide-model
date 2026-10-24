"""Simulation experiment of the study FDAGBDO."""

from typing import ClassVar, override

import pandas as pd
from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
    Dosing,
    Fasting,
    Health,
    PKPDMappingMetaData,
    Route,
    Tissue,
)
from sbmlsim import Q
from sbmlsim.data import DataSet
from sbmlsim.fit import FitData, FitMapping
from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Simulation

from pkdb_models.models.dulaglutide import MODEL
from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)


class FDAGBDO(DulaglutideSimulationExperiment):
    """Simulation experiment of FDA_GBDO (FDA review of BLA 125469, Fig. 45).

    A single dose of 1.5 mg dulaglutide SC in subjects with a normal hepatic
    function (control, n=11) and a mild (n=6), moderate (n=6) or severe (n=3)
    hepatic impairment (Child-Pugh A, B, C). The exposure of the impaired
    groups is 21-33 % lower than that of the control (CL/F +26 to +49 %,
    Tab. 49) without a trend over the classes and without a known mechanism.
    The model has no hepatic elimination of dulaglutide (protein catabolism):
    every group is simulated as the control, the impaired groups validate this
    limitation. Body weight and sex are not reported.
    """

    groups: ClassVar[list[str]] = ["control", "mildH", "modH", "sevH"]
    colors: ClassVar[dict[str, str]] = {
        "control": "black",
        "mildH": "#5bc0de",
        "modH": "#2ca0c2",
        "sevH": "#1f77b4",
    }
    # not reported, 80 kg assumed for all groups
    bodyweight: ClassVar[float] = 80  # [kg]

    @override
    def datasets(self) -> dict[str, DataSet]:
        """Get the mean, SD and number of the subjects per group and time.

        Fig. 45 shows a point per subject and time without the identity of the
        subjects, the statistics of the groups are calculated from them.
        """
        dsets = {}
        df = self.load_dataframe("Fig45")
        for group, df_group in df.groupby("group"):
            stats = (
                df_group.groupby("time")["mean"]
                .agg(["mean", "std", "count"])
                .reset_index()
            )
            df_stats = pd.DataFrame(
                {
                    "time": stats["time"],
                    "time_unit": df_group["time_unit"].iloc[0],
                    "mean": stats["mean"],
                    "sd": stats["std"],
                    "count": stats["count"],
                    "unit": df_group["unit"].iloc[0],
                }
            )
            dset = DataSet.from_df(df_stats, self.ureg)
            dset.unit_conversion("mean", 1 / self.Mr.dul)
            dsets[f"dulaglutide_{group}"] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        for group in self.groups:
            simulations[f"dul_{group}"] = Simulation(
                time_unit="hr",
                end=18 * 24,
                preinit_changes={
                    **self.default_changes(),
                    # subjects without diabetes
                    **self.baseline_changes(self.bodyweight),
                    # dose
                    "SCDOSE_dul": Q(1.5, "mg"),
                },
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in self.groups:
            mappings[f"fm_dul_{group}"] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=f"dulaglutide_{group}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task=f"task_dul_{group}",
                    xid="time",
                    yid="[Cvep_dul]",
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.PLASMA,
                    route=Route.SC,
                    application_form=ApplicationForm.SOLUTION,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY
                    if group == "control"
                    else Health.HEPATIC_IMPAIRMENT,
                    fasting=Fasting.NR,
                    coadministration=Coadministration.NONE,
                ),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig45",
            name=self.__class__.__name__,
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        # simulation: the groups are the same simulation
        plots[0].add_data(
            task="task_dul_control",
            xid="time",
            yid="[Cvep_dul]",
            label="all groups",
            color=self.colors["control"],
        )
        for group in self.groups:
            # data
            plots[0].add_data(
                dataset=f"dulaglutide_{group}",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=group,
                color=self.colors[group],
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(FDAGBDO, output_dir=FDAGBDO.__name__)
