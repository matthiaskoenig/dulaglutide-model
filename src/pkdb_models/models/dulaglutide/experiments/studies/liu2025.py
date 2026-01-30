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

from sbmlsim.plot import Figure
Figure.legend_position: str = "outside"

class Liu2025(DulaglutideSimulationExperiment):
    """Simulation experiment of Liu2025."""
    # FIXME: add plot hba1c and hbac1_change

    interventions = ["LY05008", "DUL15"]
    doses = {
        "DUL15": 1.5,  # [mg]
        "LY05008": 1.5,  # [mg]
    }
    colors = {
        "DUL15": "black",
        "LY05008": "tab:blue",
    }
    bodyweights = {
        "DUL15": 73.94,
        "LY05008": 73.40,
    }
    hba1cs = {
        "DUL15": 8.09,
        "LY05008": 8.23,
    }
    fpgs = {k: DulaglutideSimulationExperiment.apg_from_hba1c(v) for k, v in hba1cs.items()}  # [mM]

    info_pk = {
        #sid: name
        "[Cve_dul]": "dulaglutide",
    }

    info_pd = {
        #sid: name
        "hba1c_change": "hba1c_change", # Tab2
    }

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig3", "Tab2"]:
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
                [tc0] + [tc1 for _ in range(24)]
            )

        # console.print(tcsims.keys())
        return tcsims

    def fit_mappings(self) -> Dict[str, FitMapping]:

        mappings = {}
        # pharmacokinetics
        for intervention in self.interventions:
            for sid, name in self.info_pk.items():
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
                        self, task = f"task_dul_{intervention}", xid = "time", yid = f"[Cve_dul]",
                    ),
                    metadata = DulaglutideMappingMetaData(
                        tissue = Tissue.PLASMA,
                        route = Route.SC,
                        application_form = ApplicationForm.SOLUTION,
                        dosing = Dosing.MULTIPLE,
                        health = Health.HEALTHY,
                        fasting = Fasting.NR,
                        coadministration = Coadministration.METFORMIN
                    )
                )

        #pharmacodynamics
        for intervention in self.interventions:
            for sid, name in self.info_pd.items():
                mappings[f"fm_dul_{name}_{intervention}"] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=f"{name}_{intervention}",
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self, task=f"task_dul_{intervention}", xid="time", yid=sid,
                    ),
                    metadata=DulaglutideMappingMetaData(
                        tissue=Tissue.PLASMA,
                        route=Route.SC,
                        application_form=ApplicationForm.SOLUTION,
                        dosing=Dosing.MULTIPLE,
                        health=Health.T2DM,
                        fasting=Fasting.NR,
                        coadministration=Coadministration.NONE
                    )
                )
        
        return mappings

    def figures(self) -> Dict[str, Figure]:
        
        #pharmacokinetics
        fig_pk = Figure(
            experiment=self,
            sid="Fig2_pk",
            name=f"{self.__class__.__name__} (T2DM)",
        )
        plots = fig_pk.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for intervention in self.interventions:
            # simulation
            plots[0].add_data(
                task=f"task_dul_{intervention}",
                xid="time",
                yid=f"[Cve_dul]",
                label=f"dul {intervention}",
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

        # pharmacodynamics
        fig_pd = Figure(
            experiment=self,
            sid="Fig3_pd",
            name=f"{self.__class__.__name__} (T2DM)",
        )
        plots = fig_pd.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_hba1c_change, unit=self.unit_hba1c)

        for intervention in self.interventions:
            for sid, name in self.info_pd.items():

                # simulation
                plots[0].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=intervention,
                    color=self.colors[intervention],
                )
                # data
                plots[0].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=intervention,
                    color=self.colors[intervention],
                )

        return {
            fig_pk.sid: fig_pk,
            fig_pd.sid: fig_pd
        }

if __name__ == "__main__":
    run_experiments(Liu2025, output_dir=Liu2025.__name__)
