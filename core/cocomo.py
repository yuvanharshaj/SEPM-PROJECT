"""COCOMO (Constructive Cost Model) Estimation Engine.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 3:
    Software Project Estimation, Empirical Estimation Models, Boehm's COCOMO Model.

Formulas:
    Effort (Person-Months)      : E = a * (KLOC)^b
    Development Time (Months)   : T = c * (Effort)^d
    Average Staffing (Persons)  : S = Effort / Time
    Productivity (LOC/PM)       : P = (KLOC * 1000) / Effort

Coefficients Table (Boehm Basic COCOMO):
    - Organic       : a = 2.4, b = 1.05, c = 2.5, d = 0.38
    - Semi-Detached : a = 3.0, b = 1.12, c = 2.5, d = 0.35
    - Embedded      : a = 3.6, b = 1.20, c = 2.5, d = 0.32
"""

from dataclasses import dataclass
from typing import Dict, Any, Literal


COCOMO_COEFFICIENTS: Dict[str, Dict[str, float]] = {
    "organic": {
        "a": 2.4,
        "b": 1.05,
        "c": 2.5,
        "d": 0.38,
        "description": "Small teams, familiar in-house environment, well-understood requirements.",
    },
    "semi-detached": {
        "a": 3.0,
        "b": 1.12,
        "c": 2.5,
        "d": 0.35,
        "description": "Medium teams with mixed experience, moderately rigid requirements.",
    },
    "embedded": {
        "a": 3.6,
        "b": 1.20,
        "c": 2.5,
        "d": 0.32,
        "description": "Complex projects with strict hardware/operational constraints and tight regulations.",
    },
}


@dataclass
class CocomoResult:
    mode: str
    kloc: float
    effort_pm: float
    duration_months: float
    avg_staff: float
    productivity_loc_pm: float
    a: float
    b: float
    c: float
    d: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "kloc": self.kloc,
            "effort_pm": round(self.effort_pm, 2),
            "duration_months": round(self.duration_months, 2),
            "avg_staff": round(self.avg_staff, 2),
            "productivity_loc_pm": round(self.productivity_loc_pm, 1),
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "d": self.d,
            "description": self.description,
        }


def calculate_cocomo(kloc: float, mode: Literal["organic", "semi-detached", "embedded"]) -> CocomoResult:
    """Calculate Basic COCOMO effort, duration, staffing, and productivity.

    Args:
        kloc: Thousands of lines of code (> 0).
        mode: Software mode ('organic', 'semi-detached', or 'embedded').

    Returns:
        CocomoResult with exact and rounded values.

    Raises:
        ValueError: If kloc <= 0 or mode is unrecognized.
    """
    mode_key = str(mode).strip().lower()
    if mode_key not in COCOMO_COEFFICIENTS:
        valid_modes = list(COCOMO_COEFFICIENTS.keys())
        raise ValueError(f"Invalid COCOMO mode '{mode}'. Choose from: {valid_modes}")

    if kloc <= 0:
        raise ValueError(f"KLOC must be strictly greater than 0, received {kloc}")

    coeff = COCOMO_COEFFICIENTS[mode_key]
    a, b, c, d = coeff["a"], coeff["b"], coeff["c"], coeff["d"]

    # Basic COCOMO Formulas (Boehm, 1981 / VTU 24CS51 Mod 3)
    effort = a * (kloc ** b)
    duration = c * (effort ** d)
    staff = effort / duration if duration > 0 else 0.0
    loc_total = kloc * 1000.0
    productivity = loc_total / effort if effort > 0 else 0.0

    return CocomoResult(
        mode=mode_key,
        kloc=float(kloc),
        effort_pm=effort,
        duration_months=duration,
        avg_staff=staff,
        productivity_loc_pm=productivity,
        a=a,
        b=b,
        c=c,
        d=d,
        description=coeff["description"],
    )

