"""Simulation experiment of the study Pratley2018.

SUSTAIN 7, an open-label phase 3b trial: 1,199 patients with type 2 diabetes
on metformin received semaglutide 0.5 or 1.0 mg (not simulated) or
dulaglutide 0.75 mg (n=299) or 1.5 mg (n=299) s.c. once weekly without dose
escalation for 40 weeks. Estimated means (MMRM) of the HbA1c (Fig2A), the FPG
(Fig2C) and the body weight (Fig2G) from the overall baseline of all arms
(8.23 %, 9.71 mM, 95.25 kg); the error bars are SE (their half widths at 40
weeks equal the reported SEs), though the caption names 95 % CIs. The changes
are the estimated means minus the overall baseline, the absolute series of an
arm its baseline (Table 1) plus the change.
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


class Pratley2018(DulaglutideSimulationExperiment):
    """Simulation experiment of Pratley2018."""

    interventions: ClassVar[list[str]] = ["DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "DUL075": 0.75,  # [mg]
        "DUL15": 1.5,  # [mg]
    }
    # Table 1
    bodyweights: ClassVar[dict[str, float]] = {
        "DUL075": 95.6,  # [kg]
        "DUL15": 93.4,  # [kg]
    }
    bmis: ClassVar[dict[str, float]] = {
        "DUL075": 33.6,  # [kg/m^2]
        "DUL15": 33.1,  # [kg/m^2]
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "DUL075": 8.2,  # [%]
        "DUL15": 8.2,  # [%]
    }
    fpgs: ClassVar[dict[str, float]] = {
        "DUL075": 9.7,  # [mM]
        "DUL15": 9.6,  # [mM]
    }
    weeks: ClassVar[int] = 40
    colors: ClassVar[dict[str, str]] = {
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    # observable: dataset prefix
    info: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",
        "hba1c": "hba1c",
        "BW": "bodyweight",
        "fpg_change": "fpg_change",  # Fig2c
        "hba1c_change": "hba1c_change",  # Fig2a
        "BW_change": "bodyweight_change",  # Fig2g
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
        for fig_id in ["Fig2a", "Fig2c", "Fig2g"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                # the absolute series of the figure start at the overall
                # baseline, not at the baseline of the arm
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
                # weekly doses in weeks 0 to 39
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
                        route=Route.SC,
                        application_form=ApplicationForm.SOLUTION,
                        dosing=Dosing.MULTIPLE,
                        health=Health.T2DM,
                        fasting=Fasting.NR,
                        coadministration=Coadministration.METFORMIN,
                        data=PKPDData.PD,
                        data_type=DataType.MEAN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
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
    MODEL.run_experiments(Pratley2018, output_dir=Pratley2018.__name__)
