"""Simulation experiment of the study Dungan2016."""

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


class Dungan2016(DulaglutideSimulationExperiment):
    """Simulation experiment of Dungan2016 (AWARD-8).

    Dulaglutide 1.5 mg once weekly (n = 239) or placebo (n = 60) for 24 weeks
    added to glimepiride (at least half of the maximal dose) in patients with
    type 2 diabetes. HbA1c (Fig2B, MMRM), the change of the fasting serum
    glucose at 24 weeks (Fig2D, ANCOVA) and the change of the body weight
    (Fig2F) as LS means with SE. The sulfonylurea is the coadministration of
    all arms (the trial effect and the hypoglycaemia of the background, which
    the model does not describe).
    """

    interventions: ClassVar[list[str]] = ["PLAC", "DUL15"]
    bodyweights: ClassVar[dict[str, float]] = {
        "PLAC": 89.5,  # kg
        "DUL15": 84.5,  # kg
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "PLAC": 8.4,  # percent
        "DUL15": 8.4,  # percent
    }
    fpgs: ClassVar[dict[str, float]] = {
        "PLAC": 175.1,  # [mg/dl]
        "DUL15": 177.6,  # [mg/dl]
    }
    doses: ClassVar[dict[str, float]] = {
        "PLAC": 0,  # mg
        "DUL15": 1.5,  # mg
    }
    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL15": "tab:blue",
    }
    #: the absolute series (fitted) and the changes
    info: ClassVar[dict[str, str]] = {
        "hba1c": "hba1c",  # Fig2B
        "[fpg]": "fpg",  # Fig2D + baseline
        "BW": "bodyweight",  # Fig2F
        "hba1c_change": "hba1c_change",  # Fig2B
        "fpg_change": "fpg_change",  # Fig2D
        "BW_change": "bodyweight_change",  # Fig2F
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2B", "Fig2D", "Fig2F"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)

                dsets[label] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        week = 7 * 24  # [hr]
        for intervention in self.interventions:
            dose = Q(self.doses[intervention], "mg")
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=24 * week,
                preinit_changes={
                    **self.default_changes(),
                    # physiological changes
                    **self.baseline_changes(
                        self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mg/dl") / self.Mr.glc,
                    ),
                    # dose, week 0
                    "SCDOSE_dul": dose,
                },
                # 24 weekly doses
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 24)], {"SCDOSE_dul": dose}
                    )
                ],
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for intervention in self.interventions:
            for sid, name in self.info.items():
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
                        # added to glimepiride
                        coadministration=Coadministration.GLIMEPIRIDE,
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
            name=f"{self.__class__.__name__} (T2DM, glimepiride)",
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
            dose = self.doses[intervention]
            label = f"{dose} mg" if dose > 0 else "placebo"
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
    MODEL.run_experiments(Dungan2016, output_dir=Dungan2016.__name__)
