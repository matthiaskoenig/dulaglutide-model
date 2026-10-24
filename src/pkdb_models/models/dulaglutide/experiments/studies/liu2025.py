"""Simulation experiment of the study Liu2025.

Phase 3 equivalence trial in China: 440 adults with type 2 diabetes on
metformin (1.5-2.0 g/d) received 1.5 mg of the biosimilar LY05008 or of
dulaglutide (Trulicity) s.c. once weekly for 24 weeks (doses on days 1 to 162).
Trough concentrations before the doses of days 29 to 141 and on day 169
(Fig3, mean and SD), the HbA1c change (Fig2 at 12 weeks with the means of the
text, Table 2 at 24 weeks, mean and SD) and the FPG and body weight change
(Table 6, LS mean and SE). The FPG baselines are not reported.
"""

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


class Liu2025(DulaglutideSimulationExperiment):
    """Simulation experiment of Liu2025."""

    interventions: ClassVar[list[str]] = ["LY05008", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "DUL15": 1.5,  # [mg]
        "LY05008": 1.5,  # [mg]
    }
    colors: ClassVar[dict[str, str]] = {
        "DUL15": "black",
        "LY05008": "tab:blue",
    }
    # Table 1
    bodyweights: ClassVar[dict[str, float]] = {
        "DUL15": 73.94,  # [kg]
        "LY05008": 73.40,  # [kg]
    }
    heights: ClassVar[dict[str, float]] = {
        "DUL15": 165.53,  # [cm]
        "LY05008": 165.57,  # [cm]
    }
    hba1cs: ClassVar[dict[str, float]] = {
        "DUL15": 8.09,  # [%]
        "LY05008": 8.23,  # [%]
    }
    # the FPG baselines are not reported, estimated from the HbA1c
    fpgs: ClassVar[dict[str, float]] = {
        k: DulaglutideSimulationExperiment.fpg_from_hba1c(v) for k, v in hba1cs.items()
    }  # [mM]
    # weekly doses on days 1 to 162, the end of treatment on day 169
    weeks: ClassVar[int] = 24

    # observable: dataset prefix
    info_pk: ClassVar[dict[str, str]] = {
        "[Cvep_dul]": "dulaglutide",  # Fig3
    }
    info_pd: ClassVar[dict[str, str]] = {
        "[fpg]": "fpg",
        "hba1c": "hba1c",
        "BW": "bodyweight",
        "fpg_change": "fpg_change",  # Tab6
        "hba1c_change": "hba1c_change",  # Fig2, Tab2
        "BW_change": "bodyweight_change",  # Tab6
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
        for fig_id in ["Fig3", "Tab2", "Tab6"]:
            df = self.load_dataframe(fig_id)
            if fig_id == "Fig3":
                # the pre-dose sample of day 1 is below the limit of
                # quantification in all but 3 patients per arm
                df = df[df["time"] > 0]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("dulaglutide_"):
                    dset.unit_conversion("mean", 1 / self.Mr.dul)
                dsets[label] = dset

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
        end = self.weeks * week + 24  # [hr]
        for intervention in self.interventions:
            dose = Q(self.doses[intervention], "mg")
            simulations[f"dul_{intervention}"] = Simulation(
                time_unit="hr",
                end=end,
                preinit_changes={
                    **self.default_changes(),
                    **self.baseline_changes(
                        bodyweight=self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                        fpg=Q(self.fpgs[intervention], "mM"),
                    ),
                    "HEIGHT": Q(self.heights[intervention], "cm"),
                    # dose in week 0
                    "SCDOSE_dul": dose,
                },
                # weekly doses
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
        for sid, name in {**self.info_pk, **self.info_pd}.items():
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
                        # metformin 1.5-2.0 g/d in all patients
                        coadministration=Coadministration.METFORMIN,
                        data=PKPDData.PK if sid in self.info_pk else PKPDData.PD,
                        data_type=DataType.MEAN,
                    ),
                )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        # pharmacokinetics
        fig_pk = Figure(
            experiment=self,
            sid="Fig3",
            name=f"{self.__class__.__name__} (T2DM)",
        )
        fig_pk.settings = {**fig_pk.settings, "legend_position": "outside"}
        plots = fig_pk.create_plots(
            xaxis=Axis(self.label_time, unit="day"), legend=True
        )
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for intervention in self.interventions:
            for sid, name in self.info_pk.items():
                plots[0].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=intervention,
                    color=self.colors[intervention],
                )
                plots[0].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=intervention,
                    color=self.colors[intervention],
                )

        # pharmacodynamics, the changes from baseline
        fig_pd = Figure(
            experiment=self,
            sid="Fig2_Tab6",
            num_rows=1,
            num_cols=3,
            name=f"{self.__class__.__name__} (T2DM)",
        )
        # one legend for the row of panels, which share their curves
        fig_pd.settings = {**fig_pd.settings, "legend_scope": "row"}
        plots = fig_pd.create_plots(
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

        return self.figures_by_sid(fig_pk, fig_pd)


if __name__ == "__main__":
    MODEL.run_experiments(Liu2025, output_dir=Liu2025.__name__)
