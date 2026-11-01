"""McCall's Software Quality Model & Quality Scorecard Engine.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 5:
    Software Quality Concepts, Quality Assurance, McCall's Software Quality Factors,
    Software Metrics for Quality, ISO 9126 / McCall Quality Matrix.

Pillars & Factors (11 Factors across 3 Categories):
    1. Product Operation:
       - Correctness
       - Reliability
       - Efficiency
       - Integrity
       - Usability

    2. Product Revision:
       - Maintainability
       - Flexibility
       - Testability

    3. Product Transition:
       - Portability
       - Reusability
       - Interoperability

Scoring:
    Each factor is scored on a 1 to 5 Likert scale:
    1 = Deficient / Critical Risk
    2 = Sub-optimal / Requires Remediation
    3 = Acceptable / Baseline Compliance
    4 = High Quality / Industry Standard
    5 = Exemplary / State of the Art
"""

from dataclasses import dataclass
from typing import Dict, List, Any


MCCALL_TAXONOMY: Dict[str, Dict[str, str]] = {
    "Product Operation": {
        "Correctness": "Extent to which software satisfies its specification and user objectives without logical defects.",
        "Reliability": "Extent to which the system performs its intended function with specified precision under stated conditions.",
        "Efficiency": "Amount of computing resources (CPU, RAM, bandwidth, battery) required to perform functions.",
        "Integrity": "Extent to which unauthorized access to software or sensitive data can be controlled and prevented.",
        "Usability": "Effort required to learn, operate, prepare input for, and interpret output from the software.",
    },
    "Product Revision": {
        "Maintainability": "Effort required to locate and fix an error in operational software.",
        "Flexibility": "Effort required to modify an operational program to incorporate changing requirements.",
        "Testability": "Effort required to test a program to ensure it executes its intended functions.",
    },
    "Product Transition": {
        "Portability": "Effort required to transfer software across different hardware, OS, or cloud platforms.",
        "Reusability": "Extent to which software modules or architecture can be reused in other applications.",
        "Interoperability": "Effort required to couple this system with other external software systems and APIs.",
    },
}

ALL_FACTORS: List[str] = [
    factor for cat in MCCALL_TAXONOMY.values() for factor in cat.keys()
]


@dataclass
class QualityCategoryResult:
    category_name: str
    factor_scores: Dict[str, float]
    average_score: float
    percentage: float


@dataclass
class QualityScorecardResult:
    categories: Dict[str, QualityCategoryResult]
    overall_index: float  # 1.0 to 5.0
    overall_percentage: float  # 0 to 100%
    factor_scores: Dict[str, float]
    strengths: List[str]
    areas_for_improvement: List[str]
    sqa_verdict: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_index": round(self.overall_index, 2),
            "overall_percentage": round(self.overall_percentage, 1),
            "factor_scores": {k: round(v, 2) for k, v in self.factor_scores.items()},
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "sqa_verdict": self.sqa_verdict,
            "categories": {
                c_name: {
                    "average_score": round(c_res.average_score, 2),
                    "percentage": round(c_res.percentage, 1),
                    "factors": c_res.factor_scores,
                }
                for c_name, c_res in self.categories.items()
            },
        }


def evaluate_quality_scorecard(ratings: Dict[str, float | int]) -> QualityScorecardResult:
    """Evaluate McCall Quality Scorecard across all 11 factors.

    Args:
        ratings: Dict mapping factor names to values between 1.0 and 5.0.

    Returns:
        QualityScorecardResult with category averages, overall MQI, and SQA recommendations.
    """
    factor_scores: Dict[str, float] = {}
    categories_res: Dict[str, QualityCategoryResult] = {}
    strengths: List[str] = []
    weaknesses: List[str] = []

    for cat_name, factors in MCCALL_TAXONOMY.items():
        cat_scores: Dict[str, float] = {}
        for factor in factors:
            val = float(ratings.get(factor, 3.0))
            val = max(1.0, min(5.0, val))
            factor_scores[factor] = val
            cat_scores[factor] = val

            if val >= 4.5:
                strengths.append(f"{factor} ({cat_name}) - Score: {val:.1f}/5.0")
            elif val <= 2.5:
                weaknesses.append(f"{factor} ({cat_name}) - Score: {val:.1f}/5.0 (Requires SQA focus)")

        cat_avg = sum(cat_scores.values()) / len(cat_scores)
        cat_pct = (cat_avg / 5.0) * 100.0
        categories_res[cat_name] = QualityCategoryResult(
            category_name=cat_name,
            factor_scores=cat_scores,
            average_score=cat_avg,
            percentage=cat_pct,
        )

    all_values = list(factor_scores.values())
    overall_index = sum(all_values) / len(all_values)
    overall_pct = (overall_index / 5.0) * 100.0

    if overall_index >= 4.0:
        verdict = f"Grade A (Excellent): Robust software quality posture ({overall_index:.2f}/5.0, {overall_pct:.1f}%)."
    elif overall_index >= 3.0:
        verdict = f"Grade B (Acceptable): Adequate baseline compliance ({overall_index:.2f}/5.0, {overall_pct:.1f}%). Prioritize weaker attributes."
    else:
        verdict = f"Grade C (Deficient): High technical debt risk ({overall_index:.2f}/5.0, {overall_pct:.1f}%). SQA intervention strongly advised."

    return QualityScorecardResult(
        categories=categories_res,
        overall_index=overall_index,
        overall_percentage=overall_pct,
        factor_scores=factor_scores,
        strengths=strengths,
        areas_for_improvement=weaknesses,
        sqa_verdict=verdict,
    )
