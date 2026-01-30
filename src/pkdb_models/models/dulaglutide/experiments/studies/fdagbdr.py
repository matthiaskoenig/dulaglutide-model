from typing import Dict

from sbmlsim.data import DataSet, load_pkdb_dataframe
from sbmlsim.fit import FitMapping, FitData
from sbmlutils.console import console

from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)
from pkdb_models.models.dulaglutide.experiments.metadata import (
    Tissue, Route, Dosing, ApplicationForm, Health,
    Fasting, DulaglutideMappingMetaData, Coadministration
)

from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Timecourse, TimecourseSim

from pkdb_models.models.dulaglutide.helpers import run_experiments


class FDAGBDR(DulaglutideSimulationExperiment):
    """Simulation experiment of FDA_GBDR."""

    groups = ["DUL01IV", "DUL15SC", "DUL075SC", "DUL075IM"]
    doses = {
        "DUL01IV":  0.1,  #mg
        "DUL15SC":  1.5,  #mg
        "DUL075SC": 0.75, #mg
        "DUL075IM": 0.75, #mg
    }
    colors = {
        "DUL01IV":  "blue",
        "DUL15SC":  "green",
        "DUL075SC": "green",
        "DUL075IM": "red",
    }
    bodyweights = {  # [kg]
        "DUL01IV": 70,
        "DUL15SC": 70,
        "DUL075SC": 70,
        "DUL075IM": 70,
        #FIXME: assume 70kg for all groups (no data provided)
    }
    

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig15", "Fig32"]:
            # full_sid = f"{self.sid}_{fig_id}"
            # console.print(f"[debug] Using sid={self.sid}, full_sid={full_sid}")
            df = load_pkdb_dataframe(f"{self.sid}_{fig_id}", data_path=self.data_path)
            for label, df_label in df.groupby("label"):
                dset = DataSet.from_df(df_label, self.ureg)
                # unit conversion
                dset.unit_conversion("mean", 1 / self.Mr.dul)

                dsets[label] = dset

        # console.print(dsets)
        # console.print(dsets.keys())
        return dsets

    def simulations(self) -> Dict[str, TimecourseSim]:
        Q_ = self.Q_
        tcsims = {}
        for group in self.groups:
            if group.endswith("IV"):
                tcsims[f"dul_{group}"] = TimecourseSim(
                    [Timecourse(
                        start=0,
                        end=6 * 24 * 60,  # [min]
                        steps=1000,
                        changes={
                            **self.default_changes(),

                            # physiological changes
                            "BW0": Q_(self.bodyweights[group], "kg"),
                            "hba1c0": Q_(self.hba1c_healthy, "percent"),
                            "hba1c": Q_(self.hba1c_healthy, "percent"),
                            "fpg0": Q_(self.fpg_healthy, "mM"),
                            "[fpg]": Q_(self.fpg_healthy, "mM"),

                            # dose
                            "IVDOSE_dul": Q_(self.doses[group], "mg"),
                        },
                    )]
                )
            elif group.endswith("IM"):
                tcsims[f"dul_{group}"] = TimecourseSim(
                    [Timecourse(
                        start=0,
                        end=8 * 24 * 60,  # [min]
                        steps=1000,
                        changes={
                            **self.default_changes(),

                            # physiological changes
                            "BW0": Q_(self.bodyweights[group], "kg"),
                            "hba1c0": Q_(self.hba1c_healthy, "percent"),
                            "hba1c": Q_(self.hba1c_healthy, "percent"),
                            "fpg0": Q_(self.fpg_healthy, "mM"),
                            "[fpg]": Q_(self.fpg_healthy, "mM"),

                            # dose: FIXME
                            "SCDOSE_dul": Q_(self.doses[group], "mg"),
                        },
                    )]
                )
            else:
                tcsims[f"dul_{group}"] = TimecourseSim(
                    [Timecourse(
                        start=0,
                        end=15 * 24 * 60,  # [min]
                        steps=1000,
                        changes={
                            **self.default_changes(),

                            # physiological changes
                            "BW0": Q_(self.bodyweights[group], "kg"),
                            "hba1c0": Q_(self.hba1c_healthy, "percent"),
                            "hba1c": Q_(self.hba1c_healthy, "percent"),
                            "fpg0": Q_(self.fpg_healthy, "mM"),
                            "[fpg]": Q_(self.fpg_healthy, "mM"),

                            # dose
                            "SCDOSE_dul": Q_(self.doses[group], "mg"),
                        },
                    )]
                )

        # console.print(tcsims.keys())
        return tcsims

    def fit_mappings(self) -> Dict[str, FitMapping]:

        mappings = {}
        for group in self.groups:
            if group in {"DUL15SC", "DUL075SC"}:
                mappings[f"fm_dul_{group}"] = FitMapping(
                    self,
                    reference = FitData(
                        self,
                        dataset=f"dulaglutide_{group}",
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable = FitData(
                        self, task = f"task_dul_{group}", xid="time", yid=f"[Cve_dul]",
                    ),
                    metadata = DulaglutideMappingMetaData(
                        tissue = Tissue.PLASMA,
                        route = Route.SC,
                        application_form = ApplicationForm.SOLUTION,
                        dosing = Dosing.SINGLE,
                        health = Health.HEALTHY,
                        fasting = Fasting.NR,
                        coadministration = Coadministration.NONE
                    )
                )
            elif group == "DUL01IV":
                mappings[f"fm_dul_{group}"] = FitMapping(
                    self,
                    reference = FitData(
                        self,
                        dataset=f"dulaglutide_{group}",
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable = FitData(
                        self, task = f"task_dul_{group}", xid="time", yid=f"[Cve_dul]",
                    ),
                    metadata = DulaglutideMappingMetaData(
                        tissue = Tissue.PLASMA,
                        route = Route.IV,
                        application_form = ApplicationForm.SOLUTION,
                        dosing = Dosing.SINGLE,
                        health = Health.HEALTHY,
                        fasting = Fasting.NR,
                        coadministration = Coadministration.NONE
                    )
                )
            else:
                mappings[f"fm_dul_{group}"] = FitMapping(
                    self,
                    reference = FitData(
                        self,
                        dataset=f"dulaglutide_{group}",
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable = FitData(
                        self, task = f"task_dul_{group}", xid="time", yid=f"[Cve_dul]",
                    ),
                    metadata = DulaglutideMappingMetaData(
                        tissue = Tissue.PLASMA,
                        route = Route.IM,
                        application_form = ApplicationForm.SOLUTION,
                        dosing = Dosing.SINGLE,
                        health = Health.HEALTHY,
                        fasting = Fasting.NR,
                        coadministration = Coadministration.NONE
                    )
                )
        
        return mappings

    def figures(self) -> Dict[str, Figure]:
        #fig15
        fig15 = Figure(
            experiment=self,
            sid="Fig15",
            name=f"{self.__class__.__name__}",
        )
        plots = fig15.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for group in {"DUL15SC", "DUL01IV"}:
            # simulation
            plots[0].add_data(
                task=f"task_dul_{group}",
                xid="time",
                yid=f"[Cve_dul]",
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

        fig32 = Figure(
            experiment=self,
            sid="Fig32",
            name=f"{self.__class__.__name__}",
        )
        plots = fig32.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for group in {"DUL075SC", "DUL075IM"}:
            # simulation
            plots[0].add_data(
                task=f"task_dul_{group}",
                xid="time",
                yid=f"[Cve_dul]",
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

        return {
            fig15.sid: fig15,
            fig32.sid: fig32,
        }


if __name__ == "__main__":
    run_experiments(FDAGBDR, output_dir=FDAGBDR.__name__)
