"""Simulation experiment of the study FDAGBCN."""

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


class FDAGBCN(DulaglutideSimulationExperiment):
    """Simulation experiment of FDA_GBCN (FDA review of BLA 125469, Fig. 34).

    A single dose of 1.5 mg dulaglutide SC into the abdomen, the upper arm and
    the thigh of 45 healthy subjects in a crossover (29 M / 16 F, 84.5 kg, BMI
    28.7). The model has no parameter of the injection site: the three sites
    are the same simulation (relative bioavailability arm/abdomen 96.6 %,
    thigh/abdomen 99.0 %, Cmax of the thigh 11 % lower, Tab. 11).
    """

    groups: ClassVar[list[str]] = ["abdomen", "arm", "thigh"]
    colors: ClassVar[dict[str, str]] = {
        "abdomen": "tab:blue",
        "arm": "tab:red",
        "thigh": "tab:orange",
    }
    bodyweight: ClassVar[float] = 84.53  # [kg]
    bmi: ClassVar[float] = 28.7  # [kg/m^2]
    injection_sites: ClassVar[dict[str, AdministrationSite]] = {
        "abdomen": AdministrationSite.ABDOMEN,
        "arm": AdministrationSite.UPPER_ARM,
        "thigh": AdministrationSite.THIGH,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig34"]:
            df = self.load_dataframe(fig_id)
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
        for group in self.groups:
            simulations[f"dul_{group}"] = Simulation(
                time_unit="hr",
                end=16 * 24,
                preinit_changes={
                    **self.default_changes(),
                    # healthy subjects, height from body weight and BMI
                    **self.baseline_changes(self.bodyweight),
                    "HEIGHT": Q(100 * (self.bodyweight / self.bmi) ** 0.5, "cm"),
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
                    health=Health.HEALTHY,
                    fasting=Fasting.NR,
                    coadministration=Coadministration.NONE,
                    administration_site=self.injection_sites[group],
                ),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig34",
            name=self.__class__.__name__,
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        # simulation: the sites are the same simulation
        plots[0].add_data(
            task="task_dul_abdomen",
            xid="time",
            yid="[Cvep_dul]",
            label="all sites",
            color="black",
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
    MODEL.run_experiments(FDAGBCN, output_dir=FDAGBCN.__name__)
