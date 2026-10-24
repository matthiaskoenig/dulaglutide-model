"""Simulation experiment of the study Morioka2024.

Phase 3 trial GBGQ in Japan: 586 adults with type 2 diabetes on one oral
antihyperglycemic medication (sulfonylurea, biguanide, alpha-glucosidase
inhibitor, thiazolidinedione, glinide or SGLT2 inhibitor continued; a DPP-4
inhibitor stopped, 39 %) received dulaglutide 0.75 mg (n=195) or 1.5 mg
(n=391) s.c. once weekly for 52 weeks without dose escalation. LS mean changes
(SE, MMRM) of the HbA1c (Fig1), the fasting serum glucose (Fig2) and the body
weight (Fig3) at 8, 16, 26, 38 and 52 weeks.
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


class Morioka2024(DulaglutideSimulationExperiment):
    """Simulation experiment of Morioka2024."""

    interventions: ClassVar[list[str]] = ["DUL075", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "DUL075": 0.75,  # [mg]
        "DUL15": 1.5,  # [mg]
    }
    # the baselines of the analysed population (captions of Fig1 to Fig3)
    bodyweights: ClassVar[dict[str, float]] = {
        "DUL075": 71.3,  # [kg]
        "DUL15": 72.8,  # [kg]
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "DUL075": 8.69,  # [%]
        "DUL15": 8.68,  # [%]
    }
    # fasting serum glucose 179.3 mg/dl in both arms
    fpgs: ClassVar[dict[str, float]] = {
        "DUL075": 179.3 / 18.016,  # [mM]
        "DUL15": 179.3 / 18.016,  # [mM]
    }
    # Table 1, the height follows from the body weight and the BMI
    bmis: ClassVar[dict[str, float]] = {
        "DUL075": 26.1,  # [kg/m^2]
        "DUL15": 26.6,  # [kg/m^2]
    }
    bodyweights_tab1: ClassVar[dict[str, float]] = {
        "DUL075": 71.1,  # [kg]
        "DUL15": 72.7,  # [kg]
    }
    weeks: ClassVar[int] = 52
    colors: ClassVar[dict[str, str]] = {
        "DUL075": "tab:green",
        "DUL15": "tab:blue",
    }
    # observable: dataset prefix
    info: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",
        "hba1c": "hba1c",
        "BW": "bodyweight",
        "fpg_change": "fpg_change",  # Fig2
        "hba1c_change": "hba1c_change",  # Fig1
        "BW_change": "bodyweight_change",  # Fig3
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
        for fig_id in ["Fig1", "Fig2", "Fig3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                # the absolute series of the curation start at the rounded
                # baselines of Table 1, they are derived below
                if "_change_" in label:
                    dsets[label] = DataSet.from_df(df_label, self.ureg)

        # the absolute series: the baseline of the arm and the change
        baselines = {
            "hba1c": (self.hba1cs, "percent"),
            "fpg": (self.fpgs, "mM"),
            "bodyweight": (self.bodyweights, "kg"),
        }
        for label in [k for k in dsets if "_change_" in k]:
            name, intervention = label.split("_change_")
            values, unit = baselines[name]
            dset = dsets[label].copy()
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
                self.bodyweights_tab1[intervention] / self.bmis[intervention]
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
                        route=Route.SC,
                        application_form=ApplicationForm.SOLUTION,
                        dosing=Dosing.MULTIPLE,
                        health=Health.T2DM,
                        fasting=Fasting.NR,
                        # one oral antihyperglycemic medication (61 %, the
                        # DPP-4 inhibitors stopped at randomization)
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
            sid="Fig1_3",
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
    MODEL.run_experiments(Morioka2024, output_dir=Morioka2024.__name__)
