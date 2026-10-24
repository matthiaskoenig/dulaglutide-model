"""Base class of the dulaglutide simulation experiments.

The conventions of the experiments:

- The model starts healthy: `hba1c0` 5 %, `fpg0` 5 mM, `BW0` 75 kg, male
  (`SEX` 0), 170 cm (`HEIGHT`). An experiment sets the baselines of its
  subjects only by `BW0`, `hba1c0` and `fpg0` (and `HEIGHT`, `SEX` where the
  study reports them), see `baseline_changes`: the HbA1c, the hemoglobin and
  the FPG start at their baselines and the HbA1c is at steady state at them
  (initial assignments), so the states `hba1c`, `hb`, `[fpg]` and the
  assigned `hb0` are not set.
- The trial effect on the FPG (`f_trial_fpg`, diet, exercise and adherence) is
  a parameter of the model and acts in every arm of a trial, placebo included;
  the subjects at the normal FPG (healthy, 5 mM) have no trial or drug effect.
- A subcutaneous dose is `SCDOSE_dul` (repeated doses add to the depot), an
  intravenous bolus `IVDOSE_dul`, an infusion the rate `Ri_dul` [mg/min] which
  a change sets to 0 at the end of the infusion. An intramuscular dose is
  simulated as a subcutaneous dose (relative bioavailability IM/SC 0.96, the
  same tmax, FDAGBDR) with the route `Route.IM` in the metadata.
- The model has no renal or hepatic mechanism of the elimination of
  dulaglutide (protein catabolism), the groups of impaired renal and hepatic
  function simulate the control.
"""

from collections.abc import Iterable, Mapping
from typing import Any, ClassVar, NamedTuple

import pandas as pd
from pkpdsim.experiment import PKPDSimulationExperiment
from pkpdsim.metadata import Tissue
from sbmlsim import Q
from sbmlsim.units import Quantity

from pkdb_models.models.dulaglutide import MODEL
from pkdb_models.models.dulaglutide.dulaglutide_pk import calculate_dulaglutide_pk


class MolecularWeights(NamedTuple):
    """Molecular weights for the conversion of the data."""

    dul: Quantity
    glc: Quantity


class DulaglutideSimulationExperiment(PKPDSimulationExperiment):
    """Base class of the dulaglutide simulation experiments."""

    pkpd_model = MODEL
    selections = (
        "time",
        # dosing
        "IVDOSE_dul",
        "Ri_dul",
        "SCDOSE_dul",
        "SCDEPOT_dul",
        # venous plasma
        "[Cvep_dul]",
        # mass balance [mmole]
        "Abody_dul",
        "Acat_dul",
        "Asc_deg_dul",
        # pharmacodynamics
        "BW0",
        "BW",
        "BW_change",
        "BW_ratio",
        "LBW0",
        "FAT",
        "SAT",
        "hba1c0",
        "hba1c",
        "hba1c_change",
        "hba1c_ratio",
        "fpg0",
        "[fpg]",
        "fpg_change",
        "fpg_ratio",
    )

    font: ClassVar[dict[str, Any]] = {"weight": "bold", "size": 22}
    scan_font: ClassVar[dict[str, Any]] = {"weight": "bold", "size": 15}
    tick_font_size: ClassVar[int] = 15
    legend_font_size: ClassVar[int] = 9
    suptitle_font_size: ClassVar[int] = 25

    # labels
    label_time: ClassVar[str] = "time"
    label_dul: ClassVar[str] = "dulaglutide plasma"

    label_bodyweight: ClassVar[str] = "bodyweight"
    label_bodyweight_change: ClassVar[str] = "bodyweight change"
    label_bodyweight_ratio: ClassVar[str] = "bodyweight ratio"
    label_hba1c: ClassVar[str] = "HbA1c"
    label_hba1c_change: ClassVar[str] = "HbA1c change"
    label_hba1c_ratio: ClassVar[str] = "HbA1c ratio"
    label_fpg: ClassVar[str] = "FPG"
    label_fpg_change: ClassVar[str] = "FPG change"
    label_fpg_ratio: ClassVar[str] = "FPG ratio"

    labels: ClassVar[Mapping[str, str]] = {
        "time": "time",
        "[Cvep_dul]": label_dul,
        "Abody_dul": "dulaglutide body",
        "Acat_dul": "dulaglutide catabolized",
        "Asc_deg_dul": "dulaglutide degraded SC",
        "BW": label_bodyweight,
        "BW_change": label_bodyweight_change,
        "BW_ratio": label_bodyweight_ratio,
        "LBW0": "lean body weight",
        "FAT": "fat weight",
        "SAT": "subcutaneous fat",
        "hba1c": label_hba1c,
        "hba1c_change": label_hba1c_change,
        "hba1c_ratio": label_hba1c_ratio,
        "[fpg]": label_fpg,
        "fpg_change": label_fpg_change,
        "fpg_ratio": label_fpg_ratio,
        "IVDOSE_dul": "IV dose dulaglutide",
        "SCDOSE_dul": "SC dose dulaglutide",
        "SCDEPOT_dul": "SC depot dulaglutide",
    }

    # units
    unit_time: ClassVar[str] = "week"
    unit_dul: ClassVar[str] = "nM"
    unit_amount: ClassVar[str] = "nmole"
    unit_bodyweight: ClassVar[str] = "kg"
    unit_hba1c: ClassVar[str] = "percent"
    unit_fpg: ClassVar[str] = "mM"

    units: ClassVar[Mapping[str, str]] = {
        "time": unit_time,
        "[Cvep_dul]": unit_dul,
        "Abody_dul": unit_amount,
        "Acat_dul": unit_amount,
        "Asc_deg_dul": unit_amount,
        "BW": unit_bodyweight,
        "BW_change": unit_bodyweight,
        "BW_ratio": "dimensionless",
        "LBW0": unit_bodyweight,
        "FAT": unit_bodyweight,
        "SAT": unit_bodyweight,
        "hba1c": unit_hba1c,
        "hba1c_change": unit_hba1c,
        "hba1c_ratio": "dimensionless",
        "[fpg]": unit_fpg,
        "fpg_change": unit_fpg,
        "fpg_ratio": "dimensionless",
        "IVDOSE_dul": "mg",
        "SCDOSE_dul": "mg",
        "SCDEPOT_dul": "mg",
    }

    #: the tissues of the data of the observables, the tissue of the metadata
    #: of a fit mapping; a study with serum data overrides it
    tissues: ClassVar[Mapping[str, Tissue]] = {
        "[Cvep_dul]": Tissue.PLASMA,
        "[fpg]": Tissue.PLASMA,
        "fpg_change": Tissue.PLASMA,
        "hba1c": Tissue.BLOOD,
        "hba1c_change": Tissue.BLOOD,
        "BW": Tissue.NONE,
        "BW_change": Tissue.NONE,
    }

    # ----------- Healthy subjects (the defaults of the model) --------------
    hba1c_healthy: ClassVar[float] = 0.05  # [-] = 5 %
    fpg_healthy: ClassVar[float] = 5.0  # [mM]

    @staticmethod
    def apg_from_hba1c(hba1c: float) -> float:
        """Calculate estimated mean glucose in [mM] from HBA1c in [percent]."""
        # Nathan2008: AG [mg/dl] = 28.7 * A1C - 46.7; other relations are
        # 1.75 * hba1c - 3.81 (Nathan2007) and 1.98 * hba1c - 4.29 (Rohlfing2002)
        return 1.59 * hba1c - 2.59

    @staticmethod
    def fpg_from_hba1c(hba1c: float) -> float:
        """Calculate estimated fasting plasma glucose in [mM] from HBA1c in [percent]."""
        # fit to our data; Al-Lawati2007 has hba1c = 0.419 * fpg + 4.66, i.e.
        # fpg = 2.386 * hba1c - 11.1
        return 1.11 * hba1c + 0.2605

    def baseline_changes(
        self,
        bodyweight: float,
        hba1c: float | None = None,
        fpg: Quantity | None = None,
    ) -> dict[str, Quantity]:
        """Get the changes of the baselines of the subjects of a simulation.

        Args:
            bodyweight: body weight [kg].
            hba1c: HbA1c [percent], healthy (5 %) if `None`.
            fpg: fasting plasma glucose, estimated from the HbA1c with
                `fpg_from_hba1c` if `None` and the HbA1c is given, healthy
                (5 mM) if both are `None`.

        Returns:
            The changes of `BW0`, `hba1c0` and `fpg0`.
        """
        if hba1c is None:
            hba1c = 100 * self.hba1c_healthy
            if fpg is None:
                fpg = Q(self.fpg_healthy, "mM")
        elif fpg is None:
            fpg = Q(self.fpg_from_hba1c(hba1c), "mM")
        return {
            "BW0": Q(bodyweight, "kg"),
            "hba1c0": Q(hba1c, "percent"),
            "fpg0": fpg,
        }

    # molecular weights of dulaglutide and glucose
    Mr: ClassVar[MolecularWeights] = MolecularWeights(
        dul=Q(59670, "g/mole"),
        glc=Q(180.16, "g/mole"),
    )

    # --- Pharmacokinetic parameters ---
    # keys are the parameters of the non-compartmental analysis of pkpdutils,
    # see `dulaglutide_pk`; AUC and Cmax in nmole (`PK_UNITS` of the base has
    # µmole), the labels are those of the base
    pk_units: ClassVar[Mapping[str, str]] = {
        "auc_last": "nmole/l*hr",
        "auc_inf_obs": "nmole/l*hr",
        "cmax": "nmole/l",
        "tmax": "hr",
        "thalf": "hr",
        "lambda_z": "1/hr",
        "cl_f": "l/hr",
        "vz_f": "l",
    }

    def calculate_dulaglutide_pk(
        self, scans: Iterable[str] | None = None
    ) -> dict[str, pd.DataFrame]:
        """Calculate the pharmacokinetic parameters of the scans.

        Args:
            scans: keys of the simulations, all simulations by default.

        Returns:
            The parameters of every scan by simulation key, per draw of the
            fitted parameters in a run over them (`uncertainty`), see
            `dulaglutide_pk.calculate_dulaglutide_pk`.
        """
        keys = self._simulations if scans is None else scans
        across = None if self.uncertainty is None else self.uncertainty.id
        return {
            key: calculate_dulaglutide_pk(
                experiment=self, res=self.results[f"task_{key}"], across=across
            )
            for key in keys
        }
