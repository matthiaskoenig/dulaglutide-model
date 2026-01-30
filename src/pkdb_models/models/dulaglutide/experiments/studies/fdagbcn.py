from typing import Dict

from sbmlsim.data import DataSet, load_pkdb_dataframe
from sbmlsim.fit import FitMapping, FitData
from sbmlutils.console import console

from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)
from pkdb_models.models.dulaglutide.experiments.metadata import (
    Tissue, Route, Dosing, ApplicationForm, Health,
    Fasting, DulaglutideMappingMetaData, Coadministration, InjectionSite
)

from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Timecourse, TimecourseSim

from pkdb_models.models.dulaglutide.helpers import run_experiments


class FDAGBCN(DulaglutideSimulationExperiment):
    """Simulation experiment of FDA_GBCN."""

    groups = ["abdomen", "arm", "thigh"]
    colors = {
        "abdomen": "tab:blue",
        "arm":     "tab:red",
        "thigh":   "tab:orange",
    }
    bodyweights = {  # [kg]
        "abdomen": 84.53,
        "arm":     84.53,
        "thigh":   84.53,
    }

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig34"]:
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
            tcsims[f"dul_{group}"] = TimecourseSim(
                [Timecourse(
                    start=0,
                    end=16 * 24 * 60,  # [min]
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
                        "SCDOSE_dul": Q_(1.5, "mg"),
                    },
                )]
            )

        # console.print(tcsims.keys())
        return tcsims

    def fit_mappings(self) -> Dict[str, FitMapping]:

        mappings = {}
        for group in self.groups:
            if group == "DUL15SC":
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
                        route = Route.IV,
                        application_form = ApplicationForm.SOLUTION,
                        dosing = Dosing.SINGLE,
                        health = Health.HEALTHY,
                        fasting = Fasting.NR,
                        coadministration = Coadministration.NONE,
                        injection_site = InjectionSite.ABDOMEN  # FIXME
                    )
                )
        return mappings

    def figures(self) -> Dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig42",
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for group in self.groups:
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
            fig.sid: fig,
        }


if __name__ == "__main__":
    run_experiments(FDAGBCN, output_dir=FDAGBCN.__name__)
