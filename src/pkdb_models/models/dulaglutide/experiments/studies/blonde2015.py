"""Simulation experiment of the study Blonde2015."""

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


class Blonde2015(DulaglutideSimulationExperiment):
    """Simulation experiment of Blonde2015 (AWARD-4).

    Dulaglutide 0.75 or 1.5 mg once weekly for 52 weeks (n = 293, 295)
    against insulin glargine (not simulated) in patients with type 2 diabetes
    on conventional insulin, every arm with prandial insulin lispro titrated
    to targets (and metformin in 76 %). HbA1c (Fig2B, mean and 95 % CI), its
    adjusted change at 26 and 52 weeks (text, Fig2A) and the change of the
    body weight (Fig2F). The model has no insulin: all mappings are
    validation data of the limitations of the model.
    """

    interventions: ClassVar[list[str]] = ["DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "DUL075": 0.75,  # mg
        "DUL15": 1.5,  # mg
    }
    bodyweights: ClassVar[dict[str, float]] = {
        "DUL075": 91.7,  # kg
        "DUL15": 91,  # kg
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "DUL075": 8.4,  # percent
        "DUL15": 8.46,  # percent
    }
    # the baseline of the fasting serum glucose is not reported: the estimate
    # from the HbA1c
    fpgs: ClassVar[dict[str, float]] = {
        k: DulaglutideSimulationExperiment.fpg_from_hba1c(v) for k, v in hba1cs.items()
    }  # [mM]

    colors: ClassVar[dict[str, str]] = {
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    #: the absolute series and the changes
    info: ClassVar[dict[str, str]] = {
        # sid: label_prefix
        "hba1c": "hba1c",  # Fig2b
        "BW": "bodyweight",  # Fig2f + baseline
        "hba1c_change": "hba1c_change",  # Fig2a
        "BW_change": "bodyweight_change",  # Fig2f
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2a", "Fig2b", "Fig2f"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dsets[label] = DataSet.from_df(df_label, self.ureg)
                # the absolute body weight: the baseline plus the change, with
                # the error of the change
                intervention = label.split("_")[-1]
                if (
                    label.startswith("bodyweight_change_")
                    and intervention in self.interventions
                ):
                    df_abs = df_label.copy()
                    df_abs["mean"] = df_abs["mean"] + self.bodyweights[intervention]
                    dsets[f"bodyweight_{intervention}"] = DataSet.from_df(
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
                end=52 * week,
                preinit_changes={
                    **self.default_changes(),
                    # physiological changes
                    **self.baseline_changes(
                        self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mM"),
                    ),
                    # dose, week 0
                    "SCDOSE_dul": dose,
                },
                # 52 weekly doses
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
                        # titrated insulin lispro (and insulin glargine before)
                        coadministration=Coadministration.INSULIN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__} (T2DM, insulin lispro)",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[1].set_yaxis(self.label_bodyweight, unit=self.unit_bodyweight)
        plots[2].set_yaxis(self.label_hba1c_change, unit=self.unit_hba1c)
        plots[3].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)

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
    MODEL.run_experiments(Blonde2015, output_dir=Blonde2015.__name__)
