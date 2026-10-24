"""Simulation experiment of the study Chen2018."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
    Dosing,
    Fasting,
    Health,
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


class Chen2018(DulaglutideSimulationExperiment):
    """Simulation experiment of Chen2018 (AWARD-CHN2).

    Dulaglutide 0.75 or 1.5 mg once weekly for 26 weeks as monotherapy in East
    Asian patients with type 2 diabetes (n = 239 per arm, all oral
    antihyperglycemic medication stopped in a lead-in of 2 weeks), against
    glimepiride (not simulated). The changes of the HbA1c (Fig2B), the fasting
    blood glucose at 26 weeks (Fig2D, LSM (SE) of the text) and the body
    weight (Fig2F) are LS means with SE. The absolute series of the fits are
    the baselines of the simulations plus the changes.
    """

    interventions: ClassVar[list[str]] = ["DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "DUL075": 0.75,  # mg
        "DUL15": 1.5,  # mg
    }
    # the body weight is not reported, the BMI is 25.8 (DUL15) and 26.2 kg/m2
    # (DUL075, Table 1): 72 kg at 1.66 m
    bodyweight: ClassVar[float] = 72.0  # [kg]
    hba1cs: ClassVar[dict[str, float]] = {
        "DUL075": 8.0,  # percent
        "DUL15": 8.0,  # percent
    }
    # the baseline of the fasting blood glucose is not reported: the estimate
    # from the HbA1c (`fpg_from_hba1c`)
    fpgs: ClassVar[dict[str, float]] = {
        k: DulaglutideSimulationExperiment.fpg_from_hba1c(v) for k, v in hba1cs.items()
    }  # [mM]

    colors: ClassVar[dict[str, str]] = {
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    #: the absolute series (fitted) and the changes (the data of the paper)
    info: ClassVar[dict[str, str]] = {
        # sid: label_prefix
        "hba1c": "hba1c",  # Fig2B
        "[fpg]": "fpg",  # Fig2D + baseline
        "BW": "bodyweight",  # Fig2F + baseline
        "hba1c_change": "hba1c_change",  # Fig2B
        "fpg_change": "fpg_change",  # Fig2D
        "BW_change": "bodyweight_change",  # Fig2F
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2b", "Fig2d", "Fig2f"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dsets[label] = DataSet.from_df(df_label, self.ureg)
                # the absolute series: the baseline of the simulation plus the
                # change, with the error of the change
                intervention = label.split("_")[-1]
                if intervention not in self.interventions:
                    continue
                baseline = {
                    "fpg_change_": self.fpgs[intervention],  # [mM]
                    "bodyweight_change_": self.bodyweight,  # [kg]
                }
                for prefix, value in baseline.items():
                    if label.startswith(prefix):
                        df_abs = df_label.copy()
                        df_abs["mean"] = df_abs["mean"] + value
                        dsets[label.replace("_change", "")] = DataSet.from_df(
                            df_abs, self.ureg
                        )

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        week = 7 * 24  # [hr]
        for intervention in self.interventions:
            dose = Q(self.doses[intervention], "mg")
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=26 * week,
                preinit_changes={
                    **self.default_changes(),
                    # physiological changes
                    **self.baseline_changes(
                        self.bodyweight,
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mM"),
                    ),
                    # dose, week 0
                    "SCDOSE_dul": dose,
                },
                # 26 weekly doses
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 26)], {"SCDOSE_dul": dose}
                    )
                ],
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for sid, name in self.info.items():
            for intervention in self.interventions:
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
                        # monotherapy, the oral medication stopped in the lead-in
                        coadministration=Coadministration.NONE,
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
            name=f"{self.__class__.__name__} (T2DM)",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[1].set_yaxis(self.label_fpg, unit=self.unit_fpg)
        plots[2].set_yaxis(self.label_bodyweight, unit=self.unit_bodyweight)
        plots[3].set_yaxis(self.label_hba1c_change, unit=self.unit_hba1c)
        plots[4].set_yaxis(self.label_fpg_change, unit=self.unit_fpg)
        plots[5].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)

        for intervention in self.interventions:
            label = f"{self.doses[intervention]} mg"
            for kp, (sid, name) in enumerate(self.info.items()):
                # simulation
                plots[kp].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=label,
                    color=self.colors[intervention],
                )

                # data
                plots[kp].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=label,
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Chen2018, output_dir=Chen2018.__name__)
