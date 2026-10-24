"""Simulation experiment of the study Barrington2011."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    AdministrationSite,
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


class Barrington2011(DulaglutideSimulationExperiment):
    """Simulation experiment of Barrington2011.

    Escalating single subcutaneous doses (abdomen) of 0.1 to 12 mg in healthy
    subjects (19 of 20 men), about 15 min after a standard meal (400 kcal),
    plasma concentrations over 14 days (Fig1, means without errors, n = 6 per
    dose, 4 at 3 mg). The doses 0.1 mg (concentrations at 2 times the limit of
    quantification) and 12 mg (supratherapeutic, every subject vomited) are
    validation data of the doses.
    """

    # the body weight is not reported (BMI 21-30 kg/m2): the reference subject
    # of the model, 75 kg at 170 cm (BMI 26)
    bodyweight: ClassVar[float] = 75.0  # [kg]

    interventions: ClassVar[list[str]] = [
        "DUL01",
        "DUL03",
        "DUL1",
        "DUL3",
        "DUL6",
        "DUL12",
    ]
    doses: ClassVar[dict[str, float]] = {
        "DUL01": 0.1,  # mg
        "DUL03": 0.3,  # mg
        "DUL1": 1,  # mg
        "DUL3": 3,  # mg
        "DUL6": 6,  # mg
        "DUL12": 12,  # mg
    }
    colors: ClassVar[dict[str, str]] = {
        "DUL01": "tab:blue",
        "DUL03": "tab:cyan",
        "DUL1": "tab:olive",
        "DUL3": "tab:orange",
        "DUL6": "tab:red",
        "DUL12": "tab:brown",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
            df = self.load_dataframe(fig_id)
            # the pre-dose concentrations are below the limit of quantification
            # (5 ng/ml), stored as 0: the model starts at 0, the points carry no
            # information and have no place on the logarithmic axis
            df = df[~((df["time"] == 0) & (df["mean"] == 0))]
            for label, df_label in df.groupby("label"):
                label = str(label)
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
                    # physiological changes (healthy)
                    **self.baseline_changes(self.bodyweight),
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
                    yid_sd=None,
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
                    administration_site=AdministrationSite.ABDOMEN,
                    health=Health.HEALTHY,
                    # about 15 min after a standard meal
                    fasting=Fasting.FED,
                    coadministration=Coadministration.NONE,
                ),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        # the doses span 2 decades: linear and logarithmic concentrations
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_cols=2,
            name=f"{self.__class__.__name__} (healthy)",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul, scale="linear")
        plots[1].set_yaxis(self.label_dul, unit=self.unit_dul, scale="log")

        for plot in plots:
            for intervention in self.interventions:
                # simulation
                plot.add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid="[Cvep_dul]",
                    label=f"{self.doses[intervention]} mg",
                    color=self.colors[intervention],
                )

                # data
                plot.add_data(
                    dataset=f"dulaglutide_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label=f"{self.doses[intervention]} mg",
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Barrington2011, output_dir=Barrington2011.__name__)
