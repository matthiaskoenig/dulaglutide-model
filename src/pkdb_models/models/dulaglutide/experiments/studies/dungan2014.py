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


class Dungan2014(DulaglutideSimulationExperiment):
    """Simulation experiment of Dungan2014."""

    interventions = ["DUL15"]
    bodyweights = {
        "DUL15": 93.8  #kg
    }
    hba1cs = {
        "DUL15": 8.1  #percent 
    }
    fpgs = {k: DulaglutideSimulationExperiment.apg_from_hba1c(v) for k, v in hba1cs.items()}  # [mM]
    doses = {
        "DUL15": 1.5  # mg
    }
    colors = {
        "DUL15": "tab:blue",
    }
    info = {
        "hba1c": "hba1c",  #Fig2B
        "BW_change": "bodyweight_change",  # Fig2F

    }

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2b", "Fig2f"]:
            df = load_pkdb_dataframe(f"{self.sid}_{fig_id}", data_path=self.data_path)
            for label, df_label in df.groupby("label"):
                dset = DataSet.from_df(df_label, self.ureg)

                dsets[label] = dset

        # console.print(dsets)
        # console.print(dsets.keys())
        return dsets

    def simulations(self) -> Dict[str, TimecourseSim]:
        Q_ = self.Q_
        tcsims = {}
        for intervention in self.interventions:
            tc0 = Timecourse(
                start = 0,
                end = 168*60,
                steps = 1000,
                changes = {
                    **self.default_changes(),
                    #physiological changes
                    "BW0": Q_(self.bodyweights[intervention], "kg"),
                    "hba1c0": Q_(self.hba1cs[intervention], "percent"),
                    "hba1c": Q_(self.hba1cs[intervention], "percent"),
                    "fpg0": Q_(self.fpgs[intervention], "mM"),
                    "[fpg]": Q_(self.fpgs[intervention], "mM"),

                    #dose (SCDOSE)
                    "SCDOSE_dul": Q_(self.doses[intervention], "mg")
                },
            )
            tc1 = Timecourse(
                start = 0,
                end = 168*60, #[min]
                steps = 1000,
                changes = {
                    "SCDOSE_dul": Q_(self.doses[intervention], "mg")
                },
            )
            tcsims[f"dul_{intervention}"] = TimecourseSim(
                [tc0] + [tc1 for _ in range(26)]
            )

        # console.print(tcsims.keys())
        return tcsims

    def fit_mappings(self) -> Dict[str, FitMapping]:

        mappings = {}
        for intervention in self.interventions:
            for sid, name in self.info.items():

                mappings[f"fm_dul_{name}_{intervention}"] = FitMapping(
                    self,
                    reference = FitData(
                        self,
                        dataset=f"{name}_{intervention}",
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable = FitData(
                        self, task = f"task_dul_{intervention}", xid = "time", yid = sid,
                    ),
                    metadata = DulaglutideMappingMetaData(
                        tissue = Tissue.PLASMA,
                        route = Route.SC,
                        application_form = ApplicationForm.SOLUTION,
                        dosing = Dosing.MULTIPLE,
                        health = Health.T2DM,
                        fasting = Fasting.NR,
                        coadministration = Coadministration.ANTIHYPERGLYCEMIC_MEDICATION
                    )
                )
        return mappings

    def figures(self) -> Dict[str, Figure]:

        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__} (T2DM)",
        )
        plots = fig.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[1].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)

        for intervention in self.interventions:
            for kp, sid in enumerate(self.info):
                name = self.info[sid]

                # simulation
                plots[kp].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=intervention,
                    color=self.colors[intervention],
                )

                # data
                plots[kp].add_data(
                    dataset=f"{name}_{intervention}",
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
    run_experiments(Dungan2014, output_dir=Dungan2014.__name__)
