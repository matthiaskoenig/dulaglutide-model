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


class Zhang2023(DulaglutideSimulationExperiment):
    """Simulation experiment of Zhang2023."""

    interventions = ["DULP", "DULF"]
    bodyweights = {
        "DULP"  : 63.43, #kg
        "DULF"  : 65.98  #kg
    }
    doses = {
        "DULP" : 0.75, #mg
        "DULF" : 0.75, #mg
    }
    colors = {
        # pilot study
        "DULP"  : "tab:blue",
        # formal study
        "DULF"  : "black",
    }

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2"]:
            df = load_pkdb_dataframe(f"{self.sid}_{fig_id}", data_path=self.data_path)
            for label, df_label in df.groupby("label"):
                dset = DataSet.from_df(df_label, self.ureg)
                # unit conversion
                if label.startswith("dulaglutide_"):
                    dset.unit_conversion("mean", 1 / self.Mr.dul)

                dsets[label] = dset

        # console.print(dsets)
        # console.print(dsets.keys())
        return dsets

    def simulations(self) -> Dict[str, TimecourseSim]:
        Q_ = self.Q_
        tcsims = {}
        for intervention in self.interventions:
            tcsims[f"dul_{intervention}"] = TimecourseSim(
                [Timecourse(
                    start=0,
                    end=18 * 24 * 60,  # [min]
                    steps=1000,
                    changes={
                        **self.default_changes(),

                        # physiological changes (healthy)
                        "BW0": Q_(self.bodyweights[intervention], "kg"),
                        "hba1c0": Q_(self.hba1c_healthy, "percent"),
                        "hba1c": Q_(self.hba1c_healthy, "percent"),
                        "fpg0": Q_(self.fpg_healthy, "mM"),
                        "[fpg]": Q_(self.fpg_healthy, "mM"),

                        # dose
                        "SCDOSE_dul": Q_(self.doses[intervention], "mg"),
                    },
                )]
            )

        # console.print(tcsims.keys())
        return tcsims

    def fit_mappings(self) -> Dict[str, FitMapping]:

        mappings = {}
        for intervention in self.interventions:
            mappings[f"fm_dul_{intervention}"] = FitMapping(
                self,
                reference = FitData(
                    self,
                    dataset=f"dulaglutide_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable = FitData(
                    self, task = f"task_dul_{intervention}", xid="time", yid=f"[Cve_dul]",
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
        return mappings

    def figures(self) -> Dict[str, Figure]:

        fig = Figure(
            experiment=self,
            sid="Fig2",
            name=f"{self.__class__.__name__} (Healthy)",
        )
        plots = fig.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for intervention in self.interventions:
            # simulation
            plots[0].add_data(
                task=f"task_dul_{intervention}",
                xid="time",
                yid=f"[Cve_dul]",
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

        return {
            fig.sid: fig,
        }


if __name__ == "__main__":
    run_experiments(Zhang2023, output_dir=Zhang2023.__name__)
