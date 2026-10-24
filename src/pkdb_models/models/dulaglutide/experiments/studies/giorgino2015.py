"""Simulation experiment of the study Giorgino2015."""

from collections.abc import Mapping
from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
    Dosing,
    Fasting,
    Health,
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


class Giorgino2015(DulaglutideSimulationExperiment):
    """Simulation experiment of Giorgino2015 (AWARD-2).

    Dulaglutide 1.5 mg (n=273) or 0.75 mg (n=272) SC weekly for 78 weeks in
    patients with type 2 diabetes on metformin and glimepiride (insulin glargine
    arm not simulated). Fig. 2: least squares means and SE of the HbA1c (b), the
    fasting serum glucose (d) and the change of the body weight (f); the
    absolute body weight is the baseline of Table 1 plus the change.
    """

    interventions: ClassVar[list[str]] = ["DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "DUL075": 0.75,  # mg
        "DUL15": 1.5,  # mg
    }
    bodyweights: ClassVar[dict[str, float]] = {
        "DUL075": 86,  # kg
        "DUL15": 85,  # kg
    }
    bmis: ClassVar[dict[str, float]] = {
        "DUL075": 32,  # kg/m^2
        "DUL15": 31,  # kg/m^2
    }
    # baselines of Fig. 2b (Table 1: 8.1 / 8.2 %)
    hba1cs: ClassVar[dict[str, float]] = {
        "DUL075": 8.117,  # percent
        "DUL15": 8.175,  # percent
    }
    fpgs: ClassVar[dict[str, float]] = {
        "DUL075": 161,  # mg/dl
        "DUL15": 165,  # mg/dl
    }
    colors: ClassVar[dict[str, str]] = {
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    info: ClassVar[dict[str, str]] = {
        # sid: label_prefix
        "[fpg]": "fpg",  # Fig2d
        "hba1c": "hba1c",  # Fig2b
        "BW": "bodyweight",  # Fig2f, baseline + change
        "BW_change": "bodyweight_change",  # Fig2f
    }
    tissues: ClassVar[Mapping[str, Tissue]] = {
        "[fpg]": Tissue.SERUM,
        "hba1c": Tissue.BLOOD,
        "BW": Tissue.NONE,
        "BW_change": Tissue.NONE,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2b", "Fig2d", "Fig2f"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("fpg_"):
                    dset.unit_conversion("mean", 1 / self.Mr.glc)

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
                end=81 * week,
                preinit_changes={
                    **self.default_changes(),
                    # baselines, height from body weight and BMI
                    **self.baseline_changes(
                        self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mg/dl") / self.Mr.glc,
                    ),
                    "HEIGHT": Q(
                        100
                        * (self.bodyweights[intervention] / self.bmis[intervention])
                        ** 0.5,
                        "cm",
                    ),
                    # dose, week 0
                    "SCDOSE_dul": dose,
                },
                # weekly doses
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 81)], {"SCDOSE_dul": dose}
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
                        coadministration=Coadministration.ANTIHYPERGLYCEMIC_MEDICATION,
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
            name=f"{self.__class__.__name__} (T2DM)",
            # the legends inside the panels cover data: one legend per row, right
            # of the grid (the panels of a row show the same groups)
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_fpg, unit=self.unit_fpg)
        plots[1].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[2].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)

        panels = {sid: name for sid, name in self.info.items() if sid != "BW"}
        for intervention in self.interventions:
            for kp, (sid, name) in enumerate(panels.items()):
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

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Giorgino2015, output_dir=Giorgino2015.__name__)
