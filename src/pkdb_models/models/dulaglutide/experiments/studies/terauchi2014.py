"""Simulation experiment of the study Terauchi2014.

Phase 2 dose finding in Japan: 145 patients with type 2 diabetes on diet and
exercise (oral drugs washed out) received placebo (n=37) or dulaglutide 0.25
mg (n=36), 0.5 mg (n=37) or 0.75 mg (n=35) s.c. once weekly for 12 weeks. LS
mean changes of the HbA1c (Fig1b) and the FPG (Fig1d) over time, the 95 % CI
at 12 weeks (Fig1a, Fig1c), and of the body weight at 12 weeks (Table 2, SE).
The first author is Yasuo Terauchi (the study was misspelled Teraruchi2014).
"""

import math
from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
    DataType,
    Dosing,
    Fasting,
    Health,
    PKPDData,
    PKPDMappingMetaData,
    Route,
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


class Terauchi2014(DulaglutideSimulationExperiment):
    """Simulation experiment of Terauchi2014."""

    # the placebo arm receives weekly s.c. injections of placebo
    interventions: ClassVar[list[str]] = ["PLAC", "DUL025", "DUL05", "DUL075"]
    doses: ClassVar[dict[str, float]] = {
        "PLAC": 0,  # [mg]
        "DUL025": 0.25,  # [mg]
        "DUL05": 0.5,  # [mg]
        "DUL075": 0.75,  # [mg]
    }
    # Table 1
    bodyweights: ClassVar[dict[str, float]] = {
        "PLAC": 76.4,  # [kg]
        "DUL025": 74.0,  # [kg]
        "DUL05": 72.1,  # [kg]
        "DUL075": 75.8,  # [kg]
    }
    bmis: ClassVar[dict[str, float]] = {
        "PLAC": 27.4,  # [kg/m^2]
        "DUL025": 26.8,  # [kg/m^2]
        "DUL05": 26.7,  # [kg/m^2]
        "DUL075": 27.1,  # [kg/m^2]
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "PLAC": 8.0,  # [%]
        "DUL025": 8.1,  # [%]
        "DUL05": 8.0,  # [%]
        "DUL075": 8.0,  # [%]
    }
    # 160, 159, 151, 157 mg/dl
    fpgs: ClassVar[dict[str, float]] = {
        "PLAC": 8.88,  # [mM]
        "DUL025": 8.82,  # [mM]
        "DUL05": 8.38,  # [mM]
        "DUL075": 8.71,  # [mM]
    }
    weeks: ClassVar[int] = 12
    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL025": "tab:red",
        "DUL05": "tab:green",
        "DUL075": "tab:blue",
    }
    # observable: dataset prefix
    info: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",
        "hba1c": "hba1c",
        "BW": "bodyweight",
        "fpg_change": "fpg_change",  # Fig1d
        "hba1c_change": "hba1c_change",  # Fig1b
        "BW_change": "bodyweight_change",  # Tab2
    }
    # the changes of the figure
    info_changes: ClassVar[dict[str, str]] = {
        "fpg_change": "fpg_change",
        "hba1c_change": "hba1c_change",
        "BW_change": "bodyweight_change",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1b", "Fig1d", "Tab2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                # the absolute series of the curation are derived below
                if "_change_" in label:
                    dsets[label] = DataSet.from_df(df_label, self.ureg)

        # the absolute series: the baseline of the arm and the change
        baselines = {
            "hba1c": (self.hba1cs, "percent"),
            "fpg": (self.fpgs, "mM"),
            "bodyweight": (self.bodyweights, "kg"),
        }
        for intervention in self.interventions:
            for name, (values, unit) in baselines.items():
                dset = dsets[f"{name}_change_{intervention}"].copy()
                dset["mean"] += Q(values[intervention], unit).to(dset.uinfo["mean"]).m
                dsets[f"{name}_{intervention}"] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        week = 7 * 24  # [hr]
        for intervention in self.interventions:
            dose = Q(self.doses[intervention], "mg")
            height = 100 * math.sqrt(
                self.bodyweights[intervention] / self.bmis[intervention]
            )
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=self.weeks * week,
                preinit_changes={
                    **self.default_changes(),
                    **self.baseline_changes(
                        bodyweight=self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mM"),
                    ),
                    "HEIGHT": Q(height, "cm"),
                    # dose in week 0
                    "SCDOSE_dul": dose,
                },
                # weekly doses in weeks 0 to 11
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, self.weeks)], {"SCDOSE_dul": dose}
                    )
                ],
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for sid, name in self.info.items():
            for intervention in self.interventions:
                mappings[f"fm_dul_{intervention}__{name}"] = FitMapping(
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
                        self,
                        task=f"task_dul_{intervention}",
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=self.tissues[sid],
                        # the placebo arm: s.c. injections of placebo
                        route=Route.SC,
                        application_form=ApplicationForm.SOLUTION,
                        dosing=Dosing.MULTIPLE,
                        health=Health.T2DM,
                        fasting=Fasting.NR,
                        # monotherapy, oral drugs washed out
                        coadministration=Coadministration.NONE,
                        data=PKPDData.PD,
                        data_type=DataType.MEAN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Tab2",
            num_rows=1,
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        # one legend for the row of panels, which share their curves
        fig.settings = {**fig.settings, "legend_scope": "row"}
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_fpg_change, unit=self.unit_fpg)
        plots[1].set_yaxis(self.label_hba1c_change, unit=self.unit_hba1c)
        plots[2].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)

        for intervention in self.interventions:
            for kp, (sid, name) in enumerate(self.info_changes.items()):
                plots[kp].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=intervention,
                    color=self.colors[intervention],
                )
                plots[kp].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=intervention,
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Terauchi2014, output_dir=Terauchi2014.__name__)
