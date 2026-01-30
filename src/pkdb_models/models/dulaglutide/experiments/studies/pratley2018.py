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


class Pratley2018(DulaglutideSimulationExperiment):
    """Simulation experiment of Pratley2018.

    """

    interventions = ["DUL075", "DUL15"]
    doses = {
        "DUL075": 0.75, # mg
        "DUL15" : 1.5   # mg
    }
    bodyweights = {
        "DUL075": 95.6, #kg
        "DUL15" : 93.4, #kg
    }
    hba1cs = {
        "DUL075": 8.2, #percent
        "DUL15" : 8.2, #percent
    }
    fpgs = {
        "DUL075": 9.7, #mmol/l
        "DUL15" : 9.6, #mmol/l
    }
    colors = {
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    info = {
        # sid: label_prefix
        "hba1c": "hba1c",  # Fig2a
        "hba1c_change": "hba1c_change",  # Fig2a
        "BW_change": "bodyweight_change",  # Fig2g
        "fpg_change": "fpg_change",  # Fig2c

    }

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2a", "Fig2c", "Fig2g"]:
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
                    # physiological changes
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
                [tc0] + [tc1 for _ in range(40)]
            )

        # console.print(tcsims.keys())
        return tcsims

    def fit_mappings(self) -> Dict[str, FitMapping]:

        mappings = {}
        for k, sid in enumerate(self.info):
            name = self.info[sid]

            for intervention in self.interventions:
                mappings[f"fm_dul_{intervention}__{name}"] = FitMapping(
                    self,
                    reference = FitData(
                        self,
                        dataset = f"{name}_{intervention}",
                        xid = "time",
                        yid = "mean",
                        yid_sd = "mean_sd",
                        count = "count",
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
                        coadministration = Coadministration.METFORMIN
                    )
                )
        return mappings

    def figures(self) -> Dict[str, Figure]:

        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[1].set_yaxis(self.label_hba1c_change, unit=self.unit_hba1c)
        plots[2].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)
        plots[3].set_yaxis(self.label_fpg_change, unit=self.unit_fpg)

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
    run_experiments(Pratley2018, output_dir=Pratley2018.__name__)