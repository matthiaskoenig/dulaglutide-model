"""Simulation experiment of the study Nauck2014.

AWARD-5, an adaptive phase 2/3 trial: 1,098 patients with type 2 diabetes on
metformin (>= 1,500 mg/d) received dulaglutide 1.5 mg (n=304) or 0.75 mg
(n=302) s.c. once weekly, sitagliptin 100 mg (n=315, not simulated) or
placebo (n=177, switched to sitagliptin after 26 weeks), 52 weeks of the 104
weeks of treatment. LS means (SE, MMRM) of the HbA1c (Fig2B), the change of the
FPG (Fig2D, mg/dl) and of the body weight (Fig2E). The FPG baselines are not
reported. Weinstock2015 reports weeks 0 to 104 of the same trial.
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


class Nauck2014(DulaglutideSimulationExperiment):
    """Simulation experiment of Nauck2014."""

    # the placebo arm receives weekly s.c. injections of placebo
    interventions: ClassVar[list[str]] = ["PLAC", "DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "PLAC": 0,  # [mg]
        "DUL075": 0.75,  # [mg]
        "DUL15": 1.5,  # [mg]
    }
    # Table 1
    bodyweights: ClassVar[dict[str, float]] = {
        "PLAC": 87,  # [kg]
        "DUL075": 86,  # [kg]
        "DUL15": 87,  # [kg]
    }
    bmis: ClassVar[dict[str, float]] = {
        "PLAC": 31,  # [kg/m^2]
        "DUL075": 31,  # [kg/m^2]
        "DUL15": 31,  # [kg/m^2]
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "PLAC": 8.1,  # [%]
        "DUL075": 8.2,  # [%]
        "DUL15": 8.1,  # [%]
    }
    # the FPG baselines are not reported, estimated from the HbA1c
    fpgs: ClassVar[dict[str, float]] = {
        k: DulaglutideSimulationExperiment.fpg_from_hba1c(v) for k, v in hba1cs.items()
    }  # [mM]
    weeks: ClassVar[int] = 52
    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    # observable: dataset prefix
    info: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",
        "hba1c": "hba1c",  # Fig2b
        "BW": "bodyweight",
        "fpg_change": "fpg_change",  # Fig2d
        "BW_change": "bodyweight_change",  # Fig2e
    }
    # the panels of the figure
    info_figure: ClassVar[dict[str, str]] = {
        "fpg_change": "fpg_change",
        "hba1c": "hba1c",
        "BW_change": "bodyweight_change",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2b", "Fig2d", "Fig2e"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                # the measured absolute HbA1c and the changes of the FPG and the
                # body weight; the curation derives the other series from them
                if label.startswith("hba1c_change_") or (
                    label.startswith("bodyweight_") and "_change_" not in label
                ):
                    continue
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("fpg_change_"):
                    dset.unit_conversion("mean", 1 / self.Mr.glc)
                dsets[label] = dset

        # the absolute series of the FPG and the body weight: the baseline of
        # the arm and the change
        baselines = {
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
                # weekly doses in weeks 0 to 51
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
        plots[1].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[2].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)

        for intervention in self.interventions:
            for kp, (sid, name) in enumerate(self.info_figure.items()):
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
    MODEL.run_experiments(Nauck2014, output_dir=Nauck2014.__name__)
