"""Simulation experiment of the study Wysham2014.

AWARD-1, a randomized 52-week trial of once weekly dulaglutide 0.75 mg or
1.5 mg SC against exenatide 10 ug twice daily (open label, not simulated) and
placebo (26 weeks, then switched to dulaglutide) in type 2 diabetes on a
background of metformin (1500-3000 mg/d) and pioglitazone (30-45 mg/d), both
titrated to the maximally tolerated dose in a lead-in of up to 12 weeks. The
data are least squares means with their standard errors: the HbA1c over time
(Fig 2B, MMRM), the change of the HbA1c at 26 and 52 weeks (Fig 2A, ANCOVA
with the last observation carried forward, the primary endpoint), the change
of the fasting serum glucose (Fig 2D) and of the body weight (Fig 2F). The
absolute series of the FPG and the body weight are the baseline plus the
change.

The placebo arm shows what the model does not describe: its HbA1c falls by
0.65 % in 13 weeks with an FPG change of -0.1 to -0.6 mM (the effect of the
titrated pioglitazone, still building up), and it gains 1.4 kg in 26 weeks
(pioglitazone).
"""

from collections.abc import Mapping
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
    Tissue,
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


class Wysham2014(DulaglutideSimulationExperiment):
    """Simulation experiment of Wysham2014."""

    interventions: ClassVar[list[str]] = ["PLAC", "DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "PLAC": 0,  # mg
        "DUL075": 0.75,  # mg
        "DUL15": 1.5,  # mg
    }
    bodyweights: ClassVar[dict[str, float]] = {
        "PLAC": 94,  # kg
        "DUL075": 96,  # kg
        "DUL15": 96,  # kg
    }
    bmis: ClassVar[dict[str, float]] = {
        "PLAC": 33,  # kg/m^2
        "DUL075": 33,  # kg/m^2
        "DUL15": 33,  # kg/m^2
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "PLAC": 8.1,  # percent
        "DUL075": 8.1,  # percent
        "DUL15": 8.1,  # percent
    }
    # fasting serum glucose (Table 1, 166, 159 and 162 mg/dl)
    fpgs: ClassVar[dict[str, float]] = {
        "PLAC": 9.21,  # mmol/l
        "DUL075": 8.82,  # mmol/l
        "DUL15": 8.99,  # mmol/l
    }
    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    #: observable: data, the absolute series (first row of the figure) and
    #: the changes from baseline of the same measurements (second row)
    info: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",  # Fig2d
        "hba1c": "hba1c",  # Fig2b
        "BW": "bodyweight",  # Fig2f
        "fpg_change": "fpg_change",  # Fig2d
        "hba1c_change": "hba1c_change",  # Fig2b
        "BW_change": "bodyweight_change",  # Fig2f
    }
    tissues: ClassVar[Mapping[str, Tissue]] = {
        "[fpg]": Tissue.SERUM,
        "hba1c": Tissue.BLOOD,
        "BW": Tissue.NONE,
        "fpg_change": Tissue.SERUM,
        "hba1c_change": Tissue.BLOOD,
        "BW_change": Tissue.NONE,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        # Fig2a: the change of the HbA1c at 26 and 52 weeks (ANCOVA, LOCF), a
        # different analysis of the measurements of Fig2b, only shown
        for fig_id in ["Fig2a", "Fig2b", "Fig2d", "Fig2f"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                dsets[str(label)] = DataSet.from_df(df_label, self.ureg)

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        week = 7 * 24  # [hr]
        for intervention in self.interventions:
            dose = Q(self.doses[intervention], "mg")
            bodyweight = self.bodyweights[intervention]
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=52 * week,
                preinit_changes={
                    **self.default_changes(),
                    **self.baseline_changes(
                        bodyweight,
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mM"),
                    ),
                    # height from body weight and BMI
                    "HEIGHT": Q(
                        100 * (bodyweight / self.bmis[intervention]) ** 0.5, "cm"
                    ),
                    # dose in week 0
                    "SCDOSE_dul": dose,
                },
                # 52 weekly doses (placebo: weekly injections without drug,
                # the placebo arm is followed for 26 weeks)
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 52)], {"SCDOSE_dul": dose}
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
                        # placebo: weekly SC injections without drug
                        route=Route.SC,
                        application_form=ApplicationForm.SOLUTION,
                        dosing=Dosing.MULTIPLE,
                        health=Health.T2DM,
                        fasting=Fasting.NR,
                        # metformin and pioglitazone
                        coadministration=Coadministration.ANTIHYPERGLYCEMIC_MEDICATION,
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
            num_rows=2,
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        for kp, sid in enumerate(self.info):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])

        for intervention in self.interventions:
            for kp, (sid, name) in enumerate(self.info.items()):
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
            # the change of the HbA1c, ANCOVA with LOCF (Fig2a)
            plots[4].add_data(
                dataset=f"hba1c_change_ancova_{intervention}",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=f"{intervention} (ANCOVA)",
                color=self.colors[intervention],
                marker="D",
                linestyle="",
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Wysham2014, output_dir=Wysham2014.__name__)
