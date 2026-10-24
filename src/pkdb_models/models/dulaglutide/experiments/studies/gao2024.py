"""Simulation experiment of the study Gao2024."""

from typing import ClassVar, override

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


class Gao2024(DulaglutideSimulationExperiment):
    """Simulation experiment of Gao2024.

    A single dose of 0.75 mg SC into the abdomen in healthy Chinese men after an
    overnight fast of at least 10 h: dulaglutide (Trulicity, n=33) or the
    biosimilar candidate HEC14028 (n=35), serum by ELISA (LLOQ 2 ng/ml), mean
    and SE (Fig. 2). HEC14028 is another product, simulated as dulaglutide.
    """

    interventions: ClassVar[list[str]] = ["HEC14028", "DUL075"]
    doses: ClassVar[dict[str, float]] = {
        "DUL075": 0.75,  # [mg]
        "HEC14028": 0.75,  # [mg]
    }
    colors: ClassVar[dict[str, str]] = {
        "DUL075": "black",
        "HEC14028": "tab:blue",
    }
    bodyweights: ClassVar[dict[str, float]] = {  # [kg]
        "DUL075": 68.47,
        "HEC14028": 69.21,
    }
    heights: ClassVar[dict[str, float]] = {  # [cm]
        "DUL075": 171.82,
        "HEC14028": 172.57,
    }
    # lower limit of quantification of the ELISA
    lloq: ClassVar[float] = 2.0  # [ng/ml]

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2"]:
            df = self.load_dataframe(fig_id)
            # the means below the LLOQ (336 and 384 h) are biased by the
            # samples below the LLOQ, the pre-dose concentration is 0
            df = df[(df["time"] == 0) | (df["mean"] >= self.lloq)]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                # unit conversion
                dset.unit_conversion("mean", 1 / self.Mr.dul)

                dsets[label] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        for intervention in self.interventions:
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=18 * 24,
                preinit_changes={
                    **self.default_changes(),
                    # healthy men
                    **self.baseline_changes(self.bodyweights[intervention]),
                    "HEIGHT": Q(self.heights[intervention], "cm"),
                    # dose
                    "SCDOSE_dul": Q(self.doses[intervention], "mg"),
                },
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for intervention in self.interventions:
            mappings[f"fm_dul_{intervention}"] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=f"dulaglutide_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid="[Cvep_dul]",
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.SERUM,
                    route=Route.SC,
                    application_form=ApplicationForm.SOLUTION,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    fasting=Fasting.FASTED,
                    coadministration=Coadministration.NONE,
                ),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            name=f"{self.__class__.__name__} (Healthy)",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for intervention in self.interventions:
            # simulation
            plots[0].add_data(
                task=f"task_dul_{intervention}",
                xid="time",
                yid="[Cvep_dul]",
                label=intervention,
                color=self.colors[intervention],
            )
            # data
            plots[0].add_data(
                dataset=f"dulaglutide_{intervention}",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=intervention,
                color=self.colors[intervention],
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Gao2024, output_dir=Gao2024.__name__)
