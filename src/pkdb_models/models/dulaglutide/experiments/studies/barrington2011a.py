"""Simulation experiment of the study Barrington2011a."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    AdministrationSite,
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


class Barrington2011a(DulaglutideSimulationExperiment):
    """Simulation experiment of Barrington2011a.

    Five weekly subcutaneous doses (abdomen) of 0.05 to 8 mg or placebo in
    patients with type 2 diabetes (n = 3 to 11 per arm) on diet or one oral
    antihyperglycemic medication (26 of 43 metformin, 2 a thiazolidinedione,
    the sulfonylureas switched to metformin). Plasma concentrations after the
    first and the fifth dose (Fig1, most concentrations of 0.05 mg below the
    limit of quantification), the change of the fasting plasma glucose of
    test meals on study days 3, 31 and 36 (2, 30 and 35 days after the first
    dose on study day 1, Fig2) and the changes of the HbA1c and the body
    weight at 5 weeks (LS means, Fig3).
    """

    bodyweights: ClassVar[dict[str, float]] = {  # kg
        "PLAC": 83.20,
        "DUL005": 81.40,
        "DUL03": 85.7,
        "DUL1": 89.5,
        "DUL3": 67,
        "DUL5": 88.6,
        "DUL8": 76.8,
    }
    interventions: ClassVar[list[str]] = list(bodyweights.keys())
    hba1cs: ClassVar[dict[str, float]] = {  # percent
        "PLAC": 7.40,
        "DUL005": 8.10,
        "DUL03": 8.20,
        "DUL1": 8.4,
        "DUL3": 7.0,
        "DUL5": 7.4,
        "DUL8": 7.3,
    }
    fpgs: ClassVar[dict[str, float]] = {  # mg/dl
        "PLAC": 158.40,
        "DUL005": 170.70,
        "DUL03": 185.50,
        "DUL1": 200.40,
        "DUL3": 145.20,
        "DUL5": 142.50,
        "DUL8": 177.30,
    }

    doses: ClassVar[dict[str, float]] = {
        "PLAC": 0,  # mg
        "DUL005": 0.05,  # mg
        "DUL03": 0.3,  # mg
        "DUL1": 1,  # mg
        "DUL3": 3,  # mg
        "DUL5": 5,  # mg
        "DUL8": 8,  # mg
    }
    colors: ClassVar[dict[str, str]] = {
        "PLAC": "black",
        "DUL005": "tab:orange",
        "DUL03": "tab:red",
        "DUL1": "tab:blue",
        "DUL3": "tab:pink",
        "DUL5": "tab:cyan",
        "DUL8": "tab:brown",
    }
    info_pk: ClassVar[dict[str, str]] = {
        # sid: name
        "[Cvep_dul]": "dulaglutide",  # Fig1
    }
    #: the absolute series (fitted) and the changes
    info_pd: ClassVar[dict[str, str]] = {
        # sid: name
        "[fpg]": "fpg",  # Fig2
        "hba1c": "hba1c",  # Fig3
        "BW": "bodyweight",  # Fig3
        "fpg_change": "fpg_change",  # Fig2
        "hba1c_change": "hba1c_change",  # Fig3
        "BW_change": "bodyweight_change",  # Fig3
    }

    def dose_label(self, intervention: str) -> str:
        """Get the label of an arm, its weekly dose or placebo."""
        dose = self.doses[intervention]
        return f"{dose} mg" if dose > 0 else "placebo"

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                # unit conversion
                if label.startswith("dulaglutide_"):
                    dset.unit_conversion("mean", 1 / self.Mr.dul)
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
                # five weekly doses, the last one is followed for 400 hr
                end=4 * week + 400,
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
                # weekly doses
                changes=[
                    self.add_doses(
                        [k * week for k in range(1, 5)], {"SCDOSE_dul": dose}
                    )
                ],
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        # pharmacokinetics, no data of placebo and the lowest dose
        for intervention in self.interventions:
            if intervention in {"PLAC", "DUL005"}:
                continue
            for sid, name in self.info_pk.items():
                mappings[f"fm_dul_{name}_{intervention}"] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=f"{name}_{intervention}",
                        xid="time",
                        yid="mean",
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
                        administration_site=AdministrationSite.ABDOMEN,
                        health=Health.T2DM,
                        fasting=Fasting.NR,
                        # diet or metformin (26/43) or a thiazolidinedione (2/43)
                        coadministration=Coadministration.ANTIHYPERGLYCEMIC_MEDICATION,
                    ),
                )

        # pharmacodynamics
        for intervention in self.interventions:
            for sid, name in self.info_pd.items():
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
                        administration_site=AdministrationSite.ABDOMEN,
                        health=Health.T2DM,
                        fasting=Fasting.NR,
                        # diet or metformin (26/43) or a thiazolidinedione (2/43)
                        coadministration=Coadministration.ANTIHYPERGLYCEMIC_MEDICATION,
                    ),
                )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        # pharmacokinetics
        fig_pk = Figure(
            experiment=self,
            sid="Fig1_pk",
            name=f"{self.__class__.__name__} (T2DM)",
            settings={"legend_scope": "row"},
        )
        plots = fig_pk.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for intervention in self.interventions:
            for sid, name in self.info_pk.items():
                # simulation
                plots[0].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=self.dose_label(intervention),
                    color=self.colors[intervention],
                )

                # no data of placebo and the lowest dose
                if intervention in {"PLAC", "DUL005"}:
                    continue

                # data
                plots[0].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label=self.dose_label(intervention),
                    color=self.colors[intervention],
                )

        # pharmacodynamics
        fig_pd = Figure(
            experiment=self,
            sid="Fig2_Fig3_pd",
            num_rows=2,
            num_cols=3,
            name=f"{self.__class__.__name__} (T2DM)",
            settings={"legend_scope": "row"},
        )
        plots = fig_pd.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_fpg, unit=self.unit_fpg)
        plots[1].set_yaxis(self.label_hba1c, unit=self.unit_hba1c)
        plots[2].set_yaxis(self.label_bodyweight, unit=self.unit_bodyweight)
        plots[3].set_yaxis(self.label_fpg_change, unit=self.unit_fpg)
        plots[4].set_yaxis(self.label_hba1c_change, unit=self.unit_hba1c)
        plots[5].set_yaxis(self.label_bodyweight_change, unit=self.unit_bodyweight)

        for intervention in self.interventions:
            for kp, (sid, name) in enumerate(self.info_pd.items()):
                # simulation
                plots[kp].add_data(
                    task=f"task_dul_{intervention}",
                    xid="time",
                    yid=sid,
                    label=self.dose_label(intervention),
                    color=self.colors[intervention],
                )
                # data
                plots[kp].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=self.dose_label(intervention),
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig_pk, fig_pd)


if __name__ == "__main__":
    MODEL.run_experiments(Barrington2011a, output_dir=Barrington2011a.__name__)
