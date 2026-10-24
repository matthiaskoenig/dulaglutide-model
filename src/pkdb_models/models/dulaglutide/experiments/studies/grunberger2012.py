"""Simulation experiment of the study Grunberger2012."""

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


class Grunberger2012(DulaglutideSimulationExperiment):
    """Simulation experiment of Grunberger2012.

    Placebo-controlled trial of dulaglutide 0.1, 0.5, 1.0 and 1.5 mg SC weekly
    for 12 weeks in 167 patients with type 2 diabetes on monotherapy (lifestyle,
    drug-naive or after a washout of metformin of 8 weeks). Fig. 3: HbA1c (a,
    mean and SD), its change (b) and the change of the FPG (d, least squares
    means and SE). The FPG at baseline is not reported.
    """

    interventions: ClassVar[list[str]] = ["PLAC", "DUL01", "DUL05", "DUL10", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "PLAC": 0,  # mg
        "DUL01": 0.1,  # mg
        "DUL05": 0.5,  # mg
        "DUL10": 1.0,  # mg
        "DUL15": 1.5,  # mg
    }
    bodyweights: ClassVar[dict[str, float]] = {
        "PLAC": 90.9,  # kg
        "DUL01": 87.1,  # kg
        "DUL05": 90.2,  # kg
        "DUL10": 86.9,  # kg
        "DUL15": 85.8,  # kg
    }
    bmis: ClassVar[dict[str, float]] = {
        "PLAC": 32.1,  # kg/m^2
        "DUL01": 32.9,  # kg/m^2
        "DUL05": 32.3,  # kg/m^2
        "DUL10": 32.2,  # kg/m^2
        "DUL15": 31.0,  # kg/m^2
    }
    hba1cs: ClassVar[dict[str, float]] = {
        # baselines at randomization (Fig. 3a), after the washout of metformin;
        # Table 1 reports the HbA1c at screening
        "PLAC": 7.69,  # 7.4, #percent
        "DUL01": 7.57,  # 7.1, #percent
        "DUL05": 7.59,  # 7.2, #percent
        "DUL10": 7.77,  # 7.3, #percent
        "DUL15": 7.61,  # 7.2, #percent
    }
    fpgs: ClassVar[dict[str, float]] = {
        k: DulaglutideSimulationExperiment.fpg_from_hba1c(v) for k, v in hba1cs.items()
    }  # [mM]

    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL01": "tab:red",
        "DUL05": "tab:orange",
        "DUL10": "tab:green",
        "DUL15": "tab:blue",
    }
    info: ClassVar[dict[str, str]] = {
        # sid: label_prefix
        "[fpg]": "fpg",  # Fig3d, estimated baseline + change
        "fpg_change": "fpg_change",  # Fig3d
        "hba1c": "hba1c",  # Fig3a
        "hba1c_change": "hba1c_change",  # Fig3b
    }
    tissues: ClassVar[Mapping[str, Tissue]] = {
        "[fpg]": Tissue.PLASMA,
        "fpg_change": Tissue.PLASMA,
        "hba1c": Tissue.BLOOD,
        "hba1c_change": Tissue.BLOOD,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig3ab", "Fig3d"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dsets[label] = DataSet.from_df(df_label, self.ureg)
                if label.startswith("fpg_change_"):
                    # the absolute FPG: the baseline is not reported, it is the
                    # baseline of the simulation (estimated from the HbA1c)
                    # plus the change, with the SD of the change
                    intervention = label.removeprefix("fpg_change_")
                    df_fpg = df_label.copy()
                    df_fpg["mean"] = df_fpg["mean"] + self.fpgs[intervention]
                    df_fpg["label"] = f"fpg_{intervention}"
                    dsets[f"fpg_{intervention}"] = DataSet.from_df(df_fpg, self.ureg)

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        week = 7 * 24  # [hr]
        for intervention in self.interventions:
            dose = Q(self.doses[intervention], "mg")
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=13 * week,
                preinit_changes={
                    **self.default_changes(),
                    # baselines, height from body weight and BMI
                    **self.baseline_changes(
                        self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mM"),
                    ),
                    "HEIGHT": Q(
                        100
                        * (self.bodyweights[intervention] / self.bmis[intervention])
                        ** 0.5,
                        "cm",
                    ),
                    # dose in week 0
                    "SCDOSE_dul": dose,
                },
                # weekly doses
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 13)], {"SCDOSE_dul": dose}
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
                        coadministration=Coadministration.NONE,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        # the panels of the publication: Fig. 3d, 3a, 3b
        pd_info = {
            "fpg_change": "fpg_change",
            "hba1c": "hba1c",
            "hba1c_change": "hba1c_change",
        }

        fig = Figure(
            experiment=self,
            sid="Fig3",
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
        plots[0].set_yaxis(self.label_fpg_change, unit=self.unit_fpg)
        plots[1].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[2].set_yaxis(self.label_hba1c_change, unit=self.unit_hba1c)

        for intervention in self.interventions:
            for kp, (sid, name) in enumerate(pd_info.items()):
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
    MODEL.run_experiments(Grunberger2012, output_dir=Grunberger2012.__name__)
