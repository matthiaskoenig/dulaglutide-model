"""Simulation experiment of the study FDAGBCM."""

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


class FDAGBCM(DulaglutideSimulationExperiment):
    """Simulation experiment of FDAGBCM (study H9X-MC-GBCM, FDA review BLA 125469).

    A single subcutaneous dose of 1.5 mg in groups of normal (n = 16) and
    impaired renal function (mild, moderate, severe, end stage renal disease,
    n = 8 each) by the creatinine clearance (Cockcroft-Gault), plasma
    concentrations over 14 days (Fig42, arithmetic mean and SD). The SD of
    the data copy is the mean times the CV of Cmax of Table 46 per group: the
    error bars of Fig42 are drawn in one color and cannot be assigned to the
    groups (the control had a CV of 10 % instead of the 29 % of Cmax). The
    groups of impaired renal function are validation data of the populations:
    the model has no renal elimination of dulaglutide and simulates them as
    the control (AUC +12 to +28 %, Cmax +11 to +23 % without a relation to the
    creatinine clearance, Table 46, Fig21).
    """

    groups: ClassVar[list[str]] = ["control", "mildR", "modR", "sevR", "ESR"]
    colors: ClassVar[dict[str, str]] = {
        "control": "black",
        "mildR": "#9dd8f0",
        "modR": "#5bc0de",
        "sevR": "#2ca0c2",
        "ESR": "#1f77b4",
    }
    bodyweights: ClassVar[dict[str, float]] = {  # [kg]
        "control": 79.6,
        "mildR": 75.59,
        "modR": 78.25,
        "sevR": 80.7,
        "ESR": 75.58,
    }
    # the creatinine clearance of the groups [ml/min] (Cockcroft-Gault, mean),
    # relative to the normal 101 ml/min of `renal_map`; the model has no renal
    # mechanism, the values document the groups
    renal_function_values: ClassVar[dict[str, float]] = {  # [-]
        "control": 89.9 / 101,  # normal renal function
        "mildR": 55.70 / 101,  # mild renal impairment
        "modR": 39.30 / 101,  # moderate renal impairment
        "sevR": 25.80 / 101,  # severe renal impairment
        "ESR": 10.30 / 101,  # end stage renal disease
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig42"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                # unit conversion
                if label.startswith("dulaglutide_"):
                    dset.unit_conversion("mean", 1 / self.Mr.dul)

                dsets[label] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations: dict[str, Simulation] = {}
        for group in self.groups:
            simulations[f"dul_{group}"] = Simulation(
                time_unit="hr",
                end=18 * 24,
                preinit_changes={
                    **self.default_changes(),
                    # physiological changes, healthy glucose (2 of 48 with
                    # type 2 diabetes); no renal function of the model: the
                    # groups simulate the control (no renal elimination of
                    # dulaglutide)
                    **self.baseline_changes(self.bodyweights[group]),
                    # dose
                    "SCDOSE_dul": Q(1.5, "mg"),
                },
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in self.groups:
            mappings[f"fm_dul_{group}"] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=f"dulaglutide_{group}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task=f"task_dul_{group}",
                    xid="time",
                    yid="[Cvep_dul]",
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.PLASMA,
                    route=Route.SC,
                    application_form=ApplicationForm.SOLUTION,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY
                    if group == "control"
                    else Health.RENAL_IMPAIRMENT,
                    fasting=Fasting.NR,
                    coadministration=Coadministration.NONE,
                ),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig42",
            name=self.__class__.__name__,
        )
        plots = fig.create_plots(
            xaxis=Axis(self.label_time, unit=self.unit_time), legend=True
        )
        plots[0].set_yaxis(self.label_dul, unit=self.unit_dul)

        for group in self.groups:
            # simulation
            plots[0].add_data(
                task=f"task_dul_{group}",
                xid="time",
                yid="[Cvep_dul]",
                label=group,
                color=self.colors[group],
            )
            # data
            plots[0].add_data(
                dataset=f"dulaglutide_{group}",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=group,
                color=self.colors[group],
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(FDAGBCM, output_dir=FDAGBCM.__name__)
