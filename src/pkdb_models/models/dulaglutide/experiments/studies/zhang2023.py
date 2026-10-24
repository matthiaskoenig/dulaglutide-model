"""Simulation experiment of the study Zhang2023.

A randomized, open-label, single-dose, parallel PK similarity study of the
biosimilar LY05008 against dulaglutide (Trulicity) 0.75 mg SC in healthy Han
Chinese men, a pilot study (12 + 12 subjects, `DULP`, PK set of 11) and the
formal study (41 + 41 subjects, `DULF`); only the dulaglutide arms are
simulated. Plasma concentrations are arithmetic means with SD (Fig 2, ECLIA,
LLOQ 4 ng/ml, values below the LLOQ after the first quantifiable value are
missing).
"""

from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
    DataType,
    Dosing,
    Fasting,
    Health,
    PKPDData,
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


class Zhang2023(DulaglutideSimulationExperiment):
    """Simulation experiment of Zhang2023."""

    interventions: ClassVar[list[str]] = ["DULP", "DULF"]
    bodyweights: ClassVar[dict[str, float]] = {
        "DULP": 63.43,  # kg
        "DULF": 65.98,  # kg
    }
    heights: ClassVar[dict[str, float]] = {
        "DULP": 170.54,  # cm
        "DULF": 171.89,  # cm
    }
    doses: ClassVar[dict[str, float]] = {
        "DULP": 0.75,  # mg
        "DULF": 0.75,  # mg
    }
    colors: ClassVar[dict[str, str]] = {
        # pilot study
        "DULP": "tab:blue",
        # formal study
        "DULF": "black",
    }
    #: the mean of the pilot study at 360 h (7.9 +- 6.1 ng/ml) lies above the
    #: one at 288 h (6.2 ng/ml): the mean of the values above the LLOQ only,
    #: biased upwards
    below_lloq: ClassVar[dict[str, list[float]]] = {
        "dulaglutide_DULP": [360.0],  # [hr]
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if label in self.below_lloq:
                    df_label = df_label[~df_label["time"].isin(self.below_lloq[label])]
                dset = DataSet.from_df(df_label, self.ureg)
                # unit conversion
                if label.startswith("dulaglutide_"):
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
                    # healthy subjects
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
                    tissue=Tissue.PLASMA,
                    route=Route.SC,
                    application_form=ApplicationForm.SOLUTION,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    fasting=Fasting.NR,
                    coadministration=Coadministration.NONE,
                    data=PKPDData.PK,
                    data_type=DataType.MEAN,
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
    MODEL.run_experiments(Zhang2023, output_dir=Zhang2023.__name__)
