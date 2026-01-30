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


class FDAGBDO(DulaglutideSimulationExperiment):
    """Simulation experiment of FDA_GBDO.

    Hepatic impairment.
    """
    groups = ["control", "mildH", "modH", "sevH"]
    colors = {
        "control":   "black",
        "mildH":   "#5bc0de",
        "modH":    "#2ca0c2",
        "sevH":    "#1f77b4"
    }
    bodyweights = {  # [kg]
        "control":  80,
        "mildH":    80,
        "modH":     80,
        "sevH":     80,
    }
    hepatic_function_values = {  # [kg]
        "control":  DulaglutideSimulationExperiment.cirrhosis_map["Control"],
        "mildH":    DulaglutideSimulationExperiment.cirrhosis_map["Mild cirrhosis"],
        "modH":     DulaglutideSimulationExperiment.cirrhosis_map["Moderate cirrhosis"],
        "sevH":     DulaglutideSimulationExperiment.cirrhosis_map["Severe cirrhosis"],
    }
    hepatic_functions = {
        "control": "Control",
        "mildH":    "Mild cirrhosis",
        "modH":   "Moderate cirrhosis",
        "sevH":  "Severe cirrhosis",
    }

    def datasets(self) -> Dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig45", "Fig45M"]:
            full_sid = f"{self.sid}_{fig_id}"
            console.print(f"[debug] Using sid={self.sid}, full_sid={full_sid}")
            df = load_pkdb_dataframe(f"{self.sid}_{fig_id}", data_path=self.data_path)
            for label, df_label in df.groupby("label"):
                dset = DataSet.from_df(df_label, self.ureg)
                # filter individual readings
                if label.startswith("indiv_"):
                    continue
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
        for group in self.groups:
            # rf_value = DulaglutideSimulationExperiment.hepatic_map[self.hepatic_functions[group]]
            rf_value = self.hepatic_function_values[group]
            tcsims[f"dul_{group}"] = TimecourseSim(
                [Timecourse(
                    start=0,
                    end=18 * 24 * 60,  # [min]
                    steps=1000,
                    changes={
                        **self.default_changes(),

                        # physiological changes
                        "BW0": Q_(self.bodyweights[group], "kg"),

                        # healthy (2/48 T2DM)
                        "hba1c0": Q_(self.hba1c_healthy, "dimensionless"),
                        "hba1c": Q_(self.hba1c_healthy, "dimensionless"),
                        "fpg0": Q_(self.fpg_healthy, "mM"),
                        "[fpg]": Q_(self.fpg_healthy, "mM"),

                        # hepatic function
                        #"KI__f_hepatic_function": Q_(rf_value, "dimensionless"),

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
            mappings[f"fm_dul_{group}"] = FitMapping(
                self,
                reference = FitData(
                    self,
                    dataset=f"dulaglutide_{group}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean",
                    count="count",
                ),
                observable = FitData(
                    self, task = f"task_dul_{group}", xid="time", yid="[Cve_dul]",
                ),
                metadata = DulaglutideMappingMetaData(
                    tissue = Tissue.PLASMA,
                    route = Route.SC,
                    application_form = ApplicationForm.SOLUTION,
                    dosing = Dosing.SINGLE,
                    health = Health.HEALTHY if group == "control" else Health.HEPATIC_IMPAIRMENT,
                    fasting = Fasting.NR,
                    coadministration = Coadministration.NONE
                )
            )
        return mappings

    def figures(self) -> Dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig42",
            num_cols=4,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(xaxis=Axis(self.label_time, unit=self.unit_time), legend=True)
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)
        plots[1].set_yaxis(self.label_dm, unit=self.unit_dm)
        plots[2].set_yaxis(self.label_dm_urine, unit=self.unit_dm_urine)
        plots[3].set_yaxis(self.label_dm_feces, unit=self.unit_dm_feces)

        for group in self.groups:
            # simulation
            for k, sid in enumerate(["[Cve_dul]", "[Cve_dm]", "Aurine_dm", "Afeces_dm"]):
                # simulation
                plots[k].add_data(
                    task=f"task_dul_{group}",
                    xid="time",
                    yid=sid,
                    label=group,
                    color=self.colors[group],
                )

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
    run_experiments(FDAGBDO, output_dir=FDAGBDO.__name__)
