"""Function Point Analysis (FPA) & Code Size Conversion Engine.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 3:
    Software Measurement and Metrics, Function-Oriented Metrics (Albrecht's FPA),
    Value Adjustment Factor (VAF), Language Gear Factors.

Formulas:
    1. Unadjusted Function Points (UFP):
       UFP = sum(Count_i * ComplexityWeight_i) across 5 Information Domain Elements:
             - External Inputs (EI)
             - External Outputs (EO)
             - External Inquiries (EQ)
             - Internal Logical Files (ILF)
             - External Interface Files (EIF)

    2. Total Degree of Influence (TDI):
       TDI = sum(F_i) for i = 1 to 14, where F_i in [0, 5] (14 General System Characteristics)

    3. Value Adjustment Factor (VAF):
       VAF = 0.65 + (0.01 * TDI)  -- ranges from 0.65 (all 0) to 1.35 (all 5)

    4. Adjusted Function Points (AFP):
       AFP = UFP * VAF

    5. Equivalent Size Conversion:
       KLOC = (AFP * LOC_per_FP) / 1000
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


FP_COMPLEXITY_WEIGHTS: Dict[str, Dict[str, int]] = {
    "EI": {"low": 3, "average": 4, "high": 6, "name": "External Inputs (EI)"},
    "EO": {"low": 4, "average": 5, "high": 7, "name": "External Outputs (EO)"},
    "EQ": {"low": 3, "average": 3, "high": 6, "name": "External Inquiries (EQ)"},
    "ILF": {"low": 7, "average": 10, "high": 15, "name": "Internal Logical Files (ILF)"},
    "EIF": {"low": 5, "average": 7, "high": 10, "name": "External Interface Files (EIF)"},
}

GENERAL_SYSTEM_CHARACTERISTICS: List[str] = [
    "Data Communications",
    "Distributed Data Processing",
    "Performance Objectives",
    "Heavily Used Configuration",
    "Transaction Rate",
    "On-line Data Entry",
    "End-User Efficiency",
    "On-line Update",
    "Complex Processing",
    "Reusability of Code",
    "Installation Ease",
    "Operational Ease",
    "Multiple Sites Deployment",
    "Facilitate Change / Extensibility",
]

# Average LOC per Function Point by programming language (QSM / Jones benchmark data)
LANGUAGE_LOC_FACTORS: Dict[str, int] = {
    "Python": 53,
    "Java": 55,
    "C++": 53,
    "C#": 54,
    "JavaScript": 50,
    "TypeScript": 52,
    "C": 128,
    "SQL": 25,
    "HTML / CSS / Web": 40,
    "Assembly": 320,
}


@dataclass
class FunctionPointResult:
    ufp: float
    tdi: int
    vaf: float
    afp: float
    component_breakdown: Dict[str, Dict[str, int]]
    factors_ratings: List[int]
    kloc_by_language: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ufp": round(self.ufp, 2),
            "tdi": self.tdi,
            "vaf": round(self.vaf, 4),
            "afp": round(self.afp, 2),
            "component_breakdown": self.component_breakdown,
            "factors_ratings": self.factors_ratings,
            "kloc_by_language": {lang: round(val, 3) for lang, val in self.kloc_by_language.items()},
        }


def calculate_ufp(components: Dict[str, Dict[str, int]]) -> float:
    """Calculate Unadjusted Function Points (UFP).

    Args:
        components: Dict where keys are 'EI', 'EO', 'EQ', 'ILF', 'EIF',
                    and values are dicts with 'low', 'average', 'high' counts.

    Returns:
        float: total UFP score.
    """
    total = 0
    for comp_key, weights in FP_COMPLEXITY_WEIGHTS.items():
        comp_counts = components.get(comp_key, {})
        for complexity in ["low", "average", "high"]:
            count = comp_counts.get(complexity, 0)
            if count < 0:
                raise ValueError(f"Counts cannot be negative: {comp_key}.{complexity} = {count}")
            total += count * weights[complexity]
    return float(total)


def calculate_function_points(
    components: Dict[str, Dict[str, int]],
    gsc_ratings: List[int],
    target_languages: List[str] | None = None,
) -> FunctionPointResult:
    """Full Albrecht Function Point calculation.

    Args:
        components: Breakdown of counts across 5 domain characteristics.
        gsc_ratings: Exactly 14 integer ratings, each from 0 (no influence) to 5 (strong influence).
        target_languages: Optional list of language names to compute equivalent KLOC for.

    Returns:
        FunctionPointResult with UFP, TDI, VAF, AFP, and language KLOCs.
    """
    if len(gsc_ratings) != 14:
        raise ValueError(f"Exactly 14 General System Characteristics must be provided, got {len(gsc_ratings)}")

    for i, val in enumerate(gsc_ratings):
        if not (0 <= val <= 5):
            raise ValueError(f"GSC factor #{i+1} ('{GENERAL_SYSTEM_CHARACTERISTICS[i]}') must be 0-5, got {val}")

    ufp = calculate_ufp(components)
    tdi = sum(gsc_ratings)
    # Standard Albrecht VAF formula
    vaf = 0.65 + (0.01 * tdi)
    afp = ufp * vaf

    # Convert to equivalent KLOC for target or all standard languages
    langs = target_languages if target_languages else list(LANGUAGE_LOC_FACTORS.keys())
    kloc_map: Dict[str, float] = {}
    for lang in langs:
        factor = LANGUAGE_LOC_FACTORS.get(lang, 53)
        kloc_map[lang] = (afp * factor) / 1000.0

    return FunctionPointResult(
        ufp=ufp,
        tdi=tdi,
        vaf=vaf,
        afp=afp,
        component_breakdown=components,
        factors_ratings=gsc_ratings,
        kloc_by_language=kloc_map,
    )


def fp_to_kloc(afp: float, language: str = "Python") -> float:
    """Convert an AFP count to KLOC for a specific programming language."""
    if afp < 0:
        raise ValueError(f"AFP cannot be negative: {afp}")
    factor = LANGUAGE_LOC_FACTORS.get(language, 53)
    return (afp * factor) / 1000.0

