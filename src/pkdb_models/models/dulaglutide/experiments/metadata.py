from dataclasses import dataclass
from enum import Enum

from sbmlsim.fit.objects import MappingMetaData


class Tissue(str, Enum):
    PLASMA = "plasma"
    SERUM = "serum"
    URINE = "urine"
    FECES = "feces"


class Route(str, Enum):
    PO = "po"
    IM = "im"
    IV = "iv"
    SC = "sc"


class Dosing(str, Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"
    CONSTANT_INFUSION = "infusion"


class ApplicationForm(str, Enum):
    TABLET = "tablet"
    SOLUTION = "solution"
    CAPSULE = "capsule"
    MIXED = "mixed"  # mix of forms, e.g. po and iv
    NR = "not reported"

class InjectionSite(str, Enum):
    ABDOMEN = "abdomen"
    THIGH = "thigh"
    UPPER_ARM = "upper arm"
    NR = "not reported"


class Health(str, Enum):
    HEALTHY = "healthy"
    T2DM = "type 2 diabetes mellitus"
    HYPERTENSION = "hypertension"
    CIRRHOSIS = "cirrhosis"
    RENAL_IMPAIRMENT = "renal impairment"
    HEPATIC_IMPAIRMENT = "hepatic impairment"
    CHF = "congestive heart failure"
    T2DM_RENAL_IMPAIRMENT = "T2DM & renal impairment"
    OBESE = "obese"


class Fasting(str, Enum):
    NR = "not reported"
    FASTED = "fasted"
    FED = "fed"


class Coadministration(str, Enum):
    NONE = "none"  # only glimepiride
    DAPAGLIFLOZIN = "dapagliflozin"
    GEMIGLIPTIN = "gemipliptin"
    ROSUVASTATIN = "rosuvastatin"
    ANTIHYPERGLYCEMIC_MEDICATION = "antihyperglycemic medication"
    METFORMIN = "metformin"


@dataclass
class DulaglutideMappingMetaData(MappingMetaData):
    """Metadata for fitting experiment."""
    tissue: Tissue
    route: Route
    application_form: ApplicationForm
    dosing: Dosing
    health: Health
    fasting: Fasting
    coadministration: Coadministration
    injection_site: InjectionSite = InjectionSite.NR
    outlier: bool = False

    def to_dict(self):
        return {
            "tissue": self.tissue.name,
            "route": self.route.name,
            "application_form": self.application_form.name,
            "dosing": self.dosing.name,
            "injection_site": self.injection_site.name,
            "health": self.health.name,
            "fasting": self.fasting.name,
            "coadministration": self.coadministration.name,
            "outlier": self.outlier,
        }
