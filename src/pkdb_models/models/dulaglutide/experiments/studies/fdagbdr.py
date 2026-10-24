"""Simulation experiment of the study FDAGBDR."""

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
from sbmlsim.simulation import Change, Simulation

from pkdb_models.models.dulaglutide import MODEL
from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)


class FDAGBDR(DulaglutideSimulationExperiment):
    """Simulation experiment of FDA_GBDR (FDA review of BLA 125469, Fig. 15, 32).

    Absolute and relative bioavailability in healthy subjects: 0.1 mg
    dulaglutide as an IV infusion over 30 min (n=22, Tab. 10), 1.5 mg SC (n=16),
    0.75 mg SC (n=8) and 0.75 mg IM (n=7). The bioavailability of 1.5 mg SC is
    44.3 %, the IV clearance 0.0426 l/h and Vz 5.32 l. The model has no IM
    route, the IM dose is simulated as SC (relative bioavailability IM/SC
    0.958, Tab. 31). Body weight and sex are not reported.
    """

    groups: ClassVar[list[str]] = ["DUL01IV", "DUL15SC", "DUL075SC", "DUL075IM"]
    doses: ClassVar[dict[str, float]] = {
        "DUL01IV": 0.1,  # mg
        "DUL15SC": 1.5,  # mg
        "DUL075SC": 0.75,  # mg
        "DUL075IM": 0.75,  # mg
    }
    routes: ClassVar[dict[str, Route]] = {
        "DUL01IV": Route.IV,
        "DUL15SC": Route.SC,
        "DUL075SC": Route.SC,
        "DUL075IM": Route.IM,
    }
    colors: ClassVar[dict[str, str]] = {
        "DUL01IV": "blue",
        "DUL15SC": "green",
        "DUL075SC": "green",
        "DUL075IM": "red",
    }
    # sampling until 120 h (IV), 336 h (SC) and 168 h (IM)
    ends: ClassVar[dict[str, float]] = {  # [hr]
        "DUL01IV": 6 * 24,
        "DUL15SC": 15 * 24,
        "DUL075SC": 15 * 24,
        "DUL075IM": 8 * 24,
    }
    infusion_duration: ClassVar[float] = 30  # [min]
    # not reported, 70 kg assumed for all groups
    bodyweight: ClassVar[float] = 70  # [kg]

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig15", "Fig32"]:
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
            dose = self.doses[group]
            changes: list[Change] = []
            if self.routes[group] == Route.IV:
                # infusion over 30 min
                dosing = {"Ri_dul": Q(dose / self.infusion_duration, "mg/min")}
                changes = [
                    Change(self.infusion_duration / 60, {"Ri_dul": Q(0, "mg/min")})
                ]
            else:
                # SC and IM (simulated as SC, relative bioavailability IM/SC
                # 0.958, the same tmax, Tab. 31)
                dosing = {"SCDOSE_dul": Q(dose, "mg")}

            simulations[f"dul_{group}"] = Simulation(
                time_unit="hr",
                end=self.ends[group],
                preinit_changes={
                    **self.default_changes(),
                    # healthy subjects
                    **self.baseline_changes(self.bodyweight),
                    **dosing,
                },
                changes=changes,
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
                    route=self.routes[group],
                    application_form=ApplicationForm.SOLUTION,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    fasting=Fasting.NR,
                    coadministration=Coadministration.NONE,
                ),
            )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig15 = Figure(
            experiment=self,
            sid="Fig15",
            name=self.__class__.__name__,
        )
        fig32 = Figure(
            experiment=self,
            sid="Fig32",
            name=self.__class__.__name__,
        )
        for fig, groups in [
            (fig15, ["DUL15SC", "DUL01IV"]),
            (fig32, ["DUL075SC", "DUL075IM"]),
        ]:
            plots = fig.create_plots(
                xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
            )
            plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

            for group in groups:
                # simulation
                plots[0].add_data(
                    task=f"task_dul_{group}",
                    xid="time",
                    yid="[Cvep_dul]",
                    label=group,
                    color=self.colors[group],
                )
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

        return self.figures_by_sid(fig15, fig32)


if __name__ == "__main__":
    MODEL.run_experiments(FDAGBDR, output_dir=FDAGBDR.__name__)
