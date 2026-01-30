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


class Barrington2011(DulaglutideSimulationExperiment):
    """Simulation experiment of Barrington2011."""

    interventions = ["DUL01", "DUL03", "DUL1", "DUL3", "DUL6", "DUL12"]
    doses = {
        "DUL01": 0.1, #mg
        "DUL03": 0.3, #mg
        "DUL1" : 1,   #mg
        "DUL3" : 3,   #mg
        "DUL6" : 6,   #mg 
        "DUL12": 12   #mg
    }
    colors = {
        "DUL01": "tab:blue", 
        "DUL03": "tab:cyan", 
        "DUL1" : "tab:olive", 
        "DUL3" : "tab:orange", 
        "DUL6" : "tab:red", 
        "DUL12": "tab:brown"
    }

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
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
                        "BW0": Q_(74.6, "kg"),
                        "hba1c0": Q_(self.hba1c_healthy, "dimensionless"),
                        "hba1c": Q_(self.hba1c_healthy, "dimensionless"),
                        "fpg0": Q_(self.fpg_healthy, "mM"),
                        "[fpg]": Q_(self.fpg_healthy, "mM"),  # species

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
                    yid_sd=None,
                    count="count",
                ),
                observable = FitData(
                    self, task = f"task_dul_{intervention}", xid = "time", yid = f"[Cve_dul]",
                ),
                metadata = DulaglutideMappingMetaData(
                    tissue = Tissue.PLASMA,
                    route = Route.SC,
                    application_form = ApplicationForm.SOLUTION,
                    dosing = Dosing.SINGLE,
                    health = Health.HEALTHY,
                    fasting = Fasting.FASTED,
                    coadministration = Coadministration.NONE
                )
            )
        return mappings

    def figures(self) -> Dict[str, Figure]:

        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=1,
            num_cols=4,
            name=f"{self.__class__.__name__} (healthy)",
        )
        plots = fig.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)
        plots[1].set_yaxis(self.label_dm, unit=self.unit_dm)
        plots[2].set_yaxis(self.label_dm_urine, unit=self.unit_dm_urine)
        plots[3].set_yaxis(self.label_dm_feces, unit=self.unit_dm_feces)


        for intervention in self.interventions:
            for k, sid in enumerate(["[Cve_dul]", "[Cve_dm]", "Aurine_dm", "Afeces_dm"]):
                # simulation
                plots[k].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=intervention,
                    color=self.colors[intervention],
                )
            # data
            plots[0].add_data(
                dataset=f"dulaglutide_{intervention}",
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label=intervention,
                color=self.colors[intervention],
            )

        return {
            fig.sid: fig,
        }

if __name__ == "__main__":
    run_experiments(Barrington2011, output_dir=Barrington2011.__name__)
