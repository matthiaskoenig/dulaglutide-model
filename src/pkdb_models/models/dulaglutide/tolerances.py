"""The absolute tolerances of the integrator for the dulaglutide model.

The species of dulaglutide have amounts far below the states of the
pharmacodynamics, so they get tolerances of their own scale.
"""

from sbmlsim.model.tolerances import AbsoluteTolerance

#: the vessels and the organs of the body model
_VESSELS: tuple[str, ...] = ("ar", "ve", "po", "hv")
_ORGANS: tuple[str, ...] = ("ki", "li", "lu", "ad", "gu", "re")

#: the species of dulaglutide: the plasma of the vessels and the organs, the
#: interstitial space of the tissues and the amounts catabolized and degraded
#: at the injection site. A dose of 0.75 mg is 1.3e-5 mmole (59.7 kDa), the
#: amounts in the plasma of the small organs go down to 1e-12 mmole at the end
#: of the studies, far below the default tolerance of 1e-10 and the states of
#: the pharmacodynamics (glucose up to 10 mmole, body fat in kg)
DULAGLUTIDE_STATES: tuple[str, ...] = (
    *(f"C{cid}_dul" for cid in _VESSELS),
    *(f"C{cid}_plasma_dul" for cid in _ORGANS),
    *(f"C{cid}_dul" for cid in _ORGANS),
    "Acat_dul",
    "Asc_deg_dul",
)


def absolute_tolerance(value: float, dulaglutide: float) -> AbsoluteTolerance:
    """Get the absolute tolerance of the integrator for the dulaglutide model.

    Args:
        value: tolerance of every state but the dulaglutide states (the doses
            and the depot in mg, the pharmacodynamics).
        dulaglutide: tolerance of the amounts of the dulaglutide states [mmole].

    Returns:
        The absolute tolerance per state.
    """
    return AbsoluteTolerance(
        amount=value,
        concentration=value,
        other=value,
        ids=dict.fromkeys(DULAGLUTIDE_STATES, dulaglutide),
    )


#: the absolute tolerance of the simulation experiments
ABSOLUTE_TOLERANCE = absolute_tolerance(1e-10, dulaglutide=1e-18)
