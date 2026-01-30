"""
Reusable functionality for multiple simulation experiments.
"""

from collections import namedtuple
from typing import Dict
import pandas as pd

from pkdb_models.models.dulaglutide.dulaglutide_pk import calculate_dulaglutide_pk
from pkdb_models.models.dulaglutide import MODEL_PATH
from sbmlsim.experiment import SimulationExperiment
from sbmlsim.model import AbstractModel
from sbmlsim.task import Task


# Constants for conversion
MolecularWeights = namedtuple("MolecularWeights", "dul dm glc")


# Helper function to convert fpg (mg/dl) to fpg (mM)
def convert_fpg(value: float, unit: str = "mg/dl"):
    if unit == "mg/dl":
        return value / 18.0182
    elif unit == "mM":
        return value

class DulaglutideSimulationExperiment(SimulationExperiment):
    """Base class for all SimulationExperiments."""

    font = {"weight": "bold", "size": 22}
    scan_font = {"weight": "bold", "size": 15}
    tick_font_size = 15
    legend_font_size = 9
    suptitle_font_size = 25

    # labels
    label_time = "time"
    label_dul = "dulaglutide plasma"
    label_dm = "dulaglutide metabolites \n"
    label_dmtot = "dulaglutide and metabolites \n"

    label_dm_urine = label_dm + "urine"
    label_dm_feces = label_dm + "feces"

    label_bodyweight = "bodyweight"
    label_bodyweight_change = "bodyweight change"
    label_bodyweight_ratio = "bodyweight ratio"
    label_hba1c = "HbA1c"
    label_hba1c_change = "HbA1c change"
    label_hba1c_ratio = "HbA1c ratio"
    label_fpg = "FPG"
    label_fpg_change = "FPG change"
    label_fpg_ratio = "FPG ratio"

    labels: Dict[str, str] = {
        "time": "time",
        "[Cve_dul]": label_dul,
        "[Cve_dm]": label_dm,
        "[Cve_dmtot]": label_dmtot,
        "Aurine_dm": label_dm_urine,
        "Afeces_dm": label_dm_feces,

        "BW": label_bodyweight,
        "BW_change": label_bodyweight_change,
        "BW_ratio": label_bodyweight_ratio,
        "hba1c": label_hba1c,
        "hba1c_change": label_hba1c_change,
        "hba1c_ratio": label_hba1c_ratio,
        "[fpg]": label_fpg,
        "fpg_change": label_fpg_change,
        "fpg_ratio": label_fpg_ratio,
    }

    # units
    unit_time = "week"
    unit_metabolite = "nM"
    unit_metabolite_urine = "µmole"
    unit_metabolite_feces = "µmole"
    unit_dul = unit_metabolite
    unit_dm = unit_metabolite
    unit_dmtot = unit_metabolite
    unit_dm_urine = unit_metabolite_urine
    unit_dm_feces = unit_metabolite_feces
    unit_bodyweight = "kg"
    unit_hba1c = "percent"
    unit_fpg = "mM"

    units: Dict[str, str] = {
        "time": unit_time,
        "[Cve_dul]": unit_dul,
        "[Cve_dm]": unit_dm,
        "[Cve_dmtot]": unit_dmtot,
        "Aurine_dm": unit_dm_urine,
        "Afeces_dm": unit_dm_feces,

        "BW": unit_bodyweight,
        "BW_change": unit_bodyweight,
        "BW_ratio": "dimensionless",
        "hba1c": unit_hba1c,
        "hba1c_change": unit_hba1c,
        "hba1c_ratio": "dimensionless",
        "[fpg]": unit_fpg,
        "fpg_change": unit_fpg,
        "fpg_ratio": "dimensionless",
    }

    # ----------- Default changes --------------
    hba1c_healthy = 0.05  # [-] = 5 %,
    fpg_healthy = 5.0  # [mM],

    @staticmethod
    def apg_from_hba1c(hba1c: float) -> float:
        """Calculate estimated mean glucose in [mM] from HBA1c in [percent]."""
        # apg = 1.75 * hba1c - 3.81  # [mM] Nathan2007
        apg = 1.98 * hba1c - 4.29  # [mM] Rohlfing

        return apg

        # ----------- Renal map --------------
    renal_map = {
        "Normal renal function": 101.0 / 101.0,  # 1.0,
        "Mild renal impairment": 50.0 / 101.0,  # 0.5
        "Moderate renal impairment": 35.0 / 101.0,  # 0.35
        "Severe renal impairment": 20.0 / 101.0,  # 0.20
        "End stage renal disease": 10.5 / 101.0,  # 0.1
    }
    renal_colors = {
        "Normal renal function": "black",
        "Mild renal impairment": "#66c2a4",
        "Moderate renal impairment": "#2ca25f",
        "Severe renal impairment": "#006d2c",
        "End stage renal disease": "#006d5e"
    }

    # ----------- Cirrhosis map --------------
    cirrhosis_map = {
        "Control": 0,
        "Mild cirrhosis": 0.3994897959183674,  # CPT A
        "Moderate cirrhosis": 0.6979591836734694,  # CPT B
        "Severe cirrhosis": 0.8127551020408164,  # CPT C
    }
    cirrhosis_colors = {
        "Control": "black",
        "Mild cirrhosis": "#74a9cf",  # CPT A
        "Moderate cirrhosis": "#2b8cbe",  # CPT B
        "Severe cirrhosis": "#045a8d",  # CPT C
    }

    def models(self) -> Dict[str, AbstractModel]:
        Q_ = self.Q_
        return {
            "model": AbstractModel(
                source=MODEL_PATH,
                language_type=AbstractModel.LanguageType.SBML,
                changes={},
            )
        }

    @staticmethod
    def _default_changes(Q_):
        """Default changes to simulations."""

        changes = {

            'EC50_FAT': Q_(1E-2, 'mM'),  # adjust EC50 for weight loss

            # 20250627_151812__bc9d8/DULAGLUTIDE_LSQ_CONTROL
            'Ksc_dul': Q_(0.00036025565931605973, '1/min'),  # [1e-06 - 0.1]
            'DUL2DM_k': Q_(0.0021305886683688447, 'l/min'),  # [1e-06 - 0.1]
            'KI__DMEX_k': Q_(0.049281819602663014, '1/min'),  # [1e-06 - 0.1]

            # 20250806_151626__b0dfd/DULAGLUTIDE_LSQ_PHARMACODYNAMICS
            'EC50_FAT': Q_(121.39836298612472, 'mmol/l'),  # [1e-06 - 1000.0]
            'Emax_FAT': Q_(9.058086828747667e-05, '1/min'),  # [1e-06 - 1000.0]
            'k_fpg': Q_(1.0382112207761474, 'l*l/min/mmole'),  # [1e-06 - 100.0]
        }

        return changes

    def default_changes(self: SimulationExperiment) -> Dict:
        """Default changes to simulations."""
        return DulaglutideSimulationExperiment._default_changes(Q_=self.Q_)

    def tasks(self) -> Dict[str, Task]:
        if self.simulations():
            return {
                f"task_{key}": Task(model="model", simulation=key)
                for key in self.simulations()
            }
        return {}

    def data(self) -> Dict:
        self.add_selections_data(
            selections=[
                "time",

                # dosing
                "IVDOSE_dul",
                "SCDOSE_dul",

                # venous plasma
                "[Cve_dul]",
                "[Cve_dm]",
                "[Cve_dmtot]",

                # urine
                "Aurine_dm",

                # feces
                "Afeces_dm",

                # cases
                'KI__f_renal_function',
                'f_cirrhosis',
                'BW',

                # pharmacodynamics
                "BW0",
                "BW",
                "BW_change",
                "BW_ratio",

                "hba1c0",
                "hba1c",
                "hba1c_change",
                "hba1c_ratio",

                "fpg0",
                "[fpg]",
                "fpg_change",
                "fpg_ratio",
            ]
        )
        return {}

    @property
    def Mr(self):
        return MolecularWeights(
            dul=self.Q_(3314.6, "g/mole"),
            dm=self.Q_(3314.6, "g/mole"),
            glc=self.Q_(180.16, "g/mole"),
        )
        # --- Pharmacokinetic parameters ---


    pk_labels = {
        "auc": "AUCend",
        "aucinf": "AUC",
        "cl": "Total clearance",
        "cl_renal": "Renal clearance",
        "cl_hepatic": "Hepatic clearance",
        "cmax": "Cmax",
        "thalf": "Half-life",
        "kel": "kel",
        "vd": "vd",
        "Aurine_dul": "Dulaglutide urine",
    }

    pk_units = {
        "auc": "µmole/l*hr",
        "aucinf": "µmole/l*hr",
        "cl": "ml/min",
        "cl_renal": "ml/min",
        "cl_hepatic": "ml/min",
        "cmax": "µmole/l",
        "thalf": "hr",
        "kel": "1/hr",
        "vd": "l",
        "Aurine_dul": "µmole",
    }
    def calculate_dulaglutide_pk(self, scans: list = []) -> Dict[str, pd.DataFrame]:
       """Calculate pk parameters for simulations (scans)"""
       pk_dfs = {}
       if scans:
           for sim_key in scans:
               xres = self.results[f"task_{sim_key}"]
               df = calculate_dulaglutide_pk(experiment=self, xres=xres)
               pk_dfs[sim_key] = df
       else:
           for sim_key in self._simulations.keys():
               xres = self.results[f"task_{sim_key}"]
               df = calculate_dulaglutide_pk(experiment=self, xres=xres)
               pk_dfs[sim_key] = df
       return pk_dfs

    # def calculate_rivaroxaban_pd(self, scans: list = []) -> Dict[str, pd.DataFrame]:
    #    """Calculate pd parameters for simulations (scans)"""
    #    pd_dfs = {}
    #    if scans:
    #        for sim_key in scans:
    #            xres = self.results[f"task_{sim_key}"]
    #            df = calculate_rivaroxaban_pd(experiment=self, xres=xres)
    #            pd_dfs[sim_key] = df
    #    else:
    #        for sim_key in self._simulations.keys():
    #            xres = self.results[f"task_{sim_key}"]
    #            df = calculate_rivaroxaban_pd(experiment=self, xres=xres)
    #            pd_dfs[sim_key] = df
    #    return pd_dfs