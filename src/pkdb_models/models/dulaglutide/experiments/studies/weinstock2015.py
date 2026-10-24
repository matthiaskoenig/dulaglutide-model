"""Simulation experiment of the study Weinstock2015.

AWARD-5 over 104 weeks, an adaptive, double-blind trial of once weekly
dulaglutide 0.75 mg or 1.5 mg SC against sitagliptin 100 mg (not simulated)
in type 2 diabetes on metformin (>= 1500 mg/d, continued). The first 52 weeks
of the same arms are Nauck2014, which also has the placebo arm of the first
26 weeks. The data are least squares means with their standard errors: the
HbA1c over time (Fig 2B, MMRM), the change of the HbA1c at 104 weeks (Fig 2A,
ANCOVA with the last observation carried forward), the change of the FPG
(Fig 2D) and of the body weight (Fig 2E) over time. The absolute series of
the body weight is the baseline plus the change; the baseline FPG is not
reported (neither here nor in Nauck2014), it is estimated from the HbA1c with
`fpg_from_hba1c` as in Nauck2014, and the absolute FPG is this estimate plus
the change.

The measurements of weeks 0 to 52 are those of Nauck2014: the series after
52 weeks (`*_ext`) are the data of the second year only.
"""

from collections.abc import Mapping
from typing import ClassVar, override

import pandas as pd
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


class Weinstock2015(DulaglutideSimulationExperiment):
    """Simulation experiment of Weinstock2015."""

    interventions: ClassVar[list[str]] = ["DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "DUL075": 0.75,  # mg
        "DUL15": 1.5,  # mg
    }
    bodyweights: ClassVar[dict[str, float]] = {
        "DUL075": 86,  # kg
        "DUL15": 87,  # kg
    }
    bmis: ClassVar[dict[str, float]] = {
        "DUL075": 31,  # kg/m^2
        "DUL15": 31,  # kg/m^2
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "DUL075": 8.2,  # percent
        "DUL15": 8.1,  # percent
    }
    colors: ClassVar[dict[str, str]] = {
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    #: observable: data, the absolute series (first row of the figure) and
    #: the changes from baseline of the same measurements (second row)
    info: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",  # Fig2d
        "hba1c": "hba1c",  # Fig2b
        "BW": "bodyweight",  # Fig2e
        "fpg_change": "fpg_change",  # Fig2d
        "hba1c_change": "hba1c_change",  # Fig2b
        "BW_change": "bodyweight_change",  # Fig2e
    }
    #: the absolute series of the second year, the measurements of the first
    #: year are those of Nauck2014
    info_ext: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg_ext",
        "hba1c": "hba1c_ext",
        "BW": "bodyweight_ext",
    }
    #: the end of the first year [week], the end of Nauck2014
    week_ext: ClassVar[float] = 52
    tissues: ClassVar[Mapping[str, Tissue]] = {
        "[fpg]": Tissue.PLASMA,
        "hba1c": Tissue.BLOOD,
        "BW": Tissue.NONE,
        "fpg_change": Tissue.PLASMA,
        "hba1c_change": Tissue.BLOOD,
        "BW_change": Tissue.NONE,
    }

    def fpg_baseline(self, intervention: str) -> float:
        """Get the estimated baseline FPG of an arm [mM]."""
        return self.fpg_from_hba1c(self.hba1cs[intervention])

    @override
    def datasets(self) -> dict[str, DataSet]:
        dfs: dict[str, pd.DataFrame] = {}
        # Fig2a: the change of the HbA1c at 104 weeks (ANCOVA, LOCF), a
        # different analysis of the measurements of Fig2b, only shown
        for fig_id in ["Fig2a", "Fig2b", "Fig2d", "Fig2e"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                dfs[str(label)] = df_label
        for intervention in self.interventions:
            # the absolute FPG: the estimated baseline plus the change
            df = dfs[f"fpg_change_{intervention}"].copy()
            df["mean"] = df["mean"] + self.fpg_baseline(intervention)
            df["label"] = f"fpg_{intervention}"
            df["measurement_type"] = "concentration"
            dfs[f"fpg_{intervention}"] = df
            # the absolute series of the second year
            for name in ["fpg", "hba1c", "bodyweight"]:
                df = dfs[f"{name}_{intervention}"]
                dfs[f"{name}_ext_{intervention}"] = df[df["time"] > self.week_ext]

        return {label: DataSet.from_df(df, self.ureg) for label, df in dfs.items()}

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        week = 7 * 24  # [hr]
        for intervention in self.interventions:
            dose = Q(self.doses[intervention], "mg")
            bodyweight = self.bodyweights[intervention]
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=104 * week,
                preinit_changes={
                    **self.default_changes(),
                    **self.baseline_changes(
                        bodyweight,
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpg_baseline(intervention), "mM"),
                    ),
                    # height from body weight and BMI
                    "HEIGHT": Q(
                        100 * (bodyweight / self.bmis[intervention]) ** 0.5, "cm"
                    ),
                    # dose in week 0
                    "SCDOSE_dul": dose,
                },
                # 104 weekly doses
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 104)], {"SCDOSE_dul": dose}
                    )
                ],
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for sid, name in [*self.info.items(), *self.info_ext.items()]:
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
    MODEL.run_experiments(Weinstock2015, output_dir=Weinstock2015.__name__)
