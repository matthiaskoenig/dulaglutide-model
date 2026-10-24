"""Simulation experiment of the study Gerstein2019."""

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


class Gerstein2019(DulaglutideSimulationExperiment):
    """Simulation experiment of Gerstein2019 (REWIND).

    Cardiovascular outcome trial in 9901 patients with type 2 diabetes:
    dulaglutide 1.5 mg SC weekly (n=4949) or placebo (n=4952) for a median of
    5.4 years, added to up to two oral drugs with or without basal insulin.
    Intention to treat: the drug was taken 82 % of the follow-up time and other
    glucose-lowering drugs were added (more in the placebo arm), which the
    simulation of 100 % adherence without add-on therapy does not describe.
    Fig. 4: least squares means of the HbA1c and the body weight, no SD.
    """

    interventions: ClassVar[list[str]] = ["PLAC", "DUL15"]
    doses: ClassVar[dict[str, float]] = {
        "PLAC": 0,  # mg
        "DUL15": 1.5,  # mg
    }
    bodyweights: ClassVar[dict[str, float]] = {
        "PLAC": 88.94,  # kg
        "DUL15": 88.48,  # kg
    }
    bmi: ClassVar[float] = 32.3  # [kg/m^2]
    # baselines of Fig. 4a (Table 1: 7.3 / 7.4 %); the FPG is not reported and
    # is estimated from the HbA1c
    hba1cs: ClassVar[dict[str, float]] = {
        "PLAC": 7.352,  # percent
        "DUL15": 7.353,  # percent
    }

    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL15": "tab:blue",
    }
    info: ClassVar[dict[str, str]] = {
        # sid: label_prefix
        "hba1c": "hba1c",  # Fig4a
        "BW": "bodyweight",  # Fig4b
    }
    tissues: ClassVar[Mapping[str, Tissue]] = {
        "hba1c": Tissue.BLOOD,
        "BW": Tissue.NONE,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig4a", "Fig4b"]:
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
                end=261 * week,
                preinit_changes={
                    **self.default_changes(),
                    # baselines, height from body weight and BMI
                    **self.baseline_changes(
                        self.bodyweights[intervention],
                        hba1c=self.hba1cs[intervention],
                    ),
                    "HEIGHT": Q(
                        100 * (self.bodyweights[intervention] / self.bmi) ** 0.5,
                        "cm",
                    ),
                    # dose, week 0
                    "SCDOSE_dul": dose,
                },
                # weekly doses
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 261)], {"SCDOSE_dul": dose}
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
                        # least squares means without SD
                        yid_sd=None,
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
            sid="Fig4",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__} (T2DM)",
            # the legends inside the panels cover data: one legend per row, right
            # of the grid (the panels of a row show the same groups)
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[1].set_yaxis(self.label_bodyweight, unit=self.unit_bodyweight)

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
                    yid_sd=None,
                    count="count",
                    label=intervention,
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Gerstein2019, output_dir=Gerstein2019.__name__)
