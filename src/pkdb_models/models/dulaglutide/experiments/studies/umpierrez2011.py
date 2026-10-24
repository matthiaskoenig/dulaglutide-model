"""Simulation experiment of the study Umpierrez2011.

Phase 2 trial EGO: 262 overweight or obese patients with type 2 diabetes on
two oral antihyperglycemic medications (metformin with a sulfonylurea 73 %, a
thiazolidinedione 13 % or a DPP-4 inhibitor 8 %, continued) received placebo
or dulaglutide (LY2189265) s.c. once weekly for 16 weeks: 0.5 mg for 4 weeks
then 1.0 mg, 1.0 mg, or 1.0 mg for 4 weeks then 2.0 mg. LS mean changes (SE)
of the HbA1c (Fig2A), of the FPG at 16 weeks (Fig3) and of the body weight
(Fig5); Fig2B (observed means of fewer patients each visit) is not used. The
FPG baselines are not reported.
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


class Umpierrez2011(DulaglutideSimulationExperiment):
    """Simulation experiment of Umpierrez2011."""

    # weekly doses; the placebo arm receives s.c. injections of placebo
    doses: ClassVar[dict[str, list[float]]] = {
        "PLAC": [0.0] * 16,  # [mg]
        "DUL0510": [0.5] * 4 + [1.0] * 12,  # [mg]
        "DUL1010": [1.0] * 16,  # [mg]
        "DUL1020": [1.0] * 4 + [2.0] * 12,  # [mg]
    }
    interventions: ClassVar[list[str]] = list(doses.keys())
    # Table 1
    bodyweights: ClassVar[dict[str, float]] = {
        "PLAC": 94.7,  # [kg]
        "DUL0510": 94.8,  # [kg]
        "DUL1010": 96.7,  # [kg]
        "DUL1020": 98.6,  # [kg]
    }
    bmis: ClassVar[dict[str, float]] = {
        "PLAC": 33.9,  # [kg/m^2]
        "DUL0510": 33.7,  # [kg/m^2]
        "DUL1010": 33.9,  # [kg/m^2]
        "DUL1020": 34.2,  # [kg/m^2]
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "PLAC": 8.05,  # [%]
        "DUL0510": 8.25,  # [%]
        "DUL1010": 8.25,  # [%]
        "DUL1020": 8.43,  # [%]
    }
    # the FPG baselines are not reported, estimated from the HbA1c
    fpgs: ClassVar[dict[str, float]] = {
        k: DulaglutideSimulationExperiment.fpg_from_hba1c(v) for k, v in hba1cs.items()
    }  # [mM]
    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL0510": "tab:green",
        "DUL1010": "tab:blue",
        "DUL1020": "tab:orange",
    }
    # observable: dataset prefix
    info: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",
        "hba1c": "hba1c",
        "BW": "bodyweight",
        "fpg_change": "fpg_change",  # Fig3
        "hba1c_change": "hba1c_change",  # Fig2a
        "BW_change": "bodyweight_change",  # Fig5
    }
    # the patients of the last visit (Fig2A, Fig3, Fig5), the counts of the
    # data change between the visits and a fit mapping takes one count
    counts: ClassVar[dict[str, dict[str, int]]] = {
        "hba1c": {"PLAC": 59, "DUL0510": 58, "DUL1010": 59, "DUL1020": 54},
        "fpg": {"PLAC": 53, "DUL0510": 47, "DUL1010": 52, "DUL1020": 51},
        "bodyweight": {"PLAC": 59, "DUL0510": 59, "DUL1010": 59, "DUL1020": 56},
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
        for fig_id in ["Fig2a", "Fig3", "Fig5"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                # the LS means of Fig2A are labeled `hba1c_change_lsmean_*`
                label = str(label).replace("_lsmean", "")
                # the absolute series of the curation are derived below
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
            doses = self.doses[intervention]
            height = 100 * math.sqrt(
                self.bodyweights[intervention] / self.bmis[intervention]
            )
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                # weekly doses in weeks 0 to 15, the end of treatment at week 16
                end=len(doses) * week,
                preinit_changes={
                    **self.default_changes(),
                    **self.baseline_changes(
                        bodyweight=self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mM"),
                    ),
                    "HEIGHT": Q(height, "cm"),
                    # dose in week 0
                    "SCDOSE_dul": Q(doses[0], "mg"),
                },
                changes=[
                    self.add_doses(k * week, {"SCDOSE_dul": Q(dose, "mg")})
                    for k, dose in enumerate(doses)
                    if k > 0
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
                        count=self.counts[name.removesuffix("_change")][intervention],
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
                        # two oral drugs, mostly metformin and a sulfonylurea
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
            sid="Fig2_3_5",
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
                    # no count: the patients differ between the visits and
                    # the panels, one legend entry per arm
                    label=intervention,
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Umpierrez2011, output_dir=Umpierrez2011.__name__)
