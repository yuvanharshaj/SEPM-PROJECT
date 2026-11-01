"""Risk Management, Risk Exposure (RE) & Heat Map Analysis.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 4:
    Risk Management, Reactive vs Proactive Risk Strategies, Software Risks,
    Risk Identification, Risk Projection (Risk Table), Risk Refinement,
    Risk Mitigation, Monitoring and Management (RMMM) Plan.

Formulas:
    Risk Exposure (RE) = Probability (P) * Impact (I)
    Total Project Exposure = sum(RE_i) for i in 1..N
"""

from dataclasses import dataclass
from typing import Dict, List, Any


RISK_CATEGORIES: List[str] = [
    "Technical",
    "Requirements & Scope",
    "Project Management & Schedule",
    "Financial & Budget",
    "Operational & Human Resources",
    "Security & Compliance",
]


@dataclass
class RiskItem:
    id: str
    description: str
    category: str
    probability: float  # 0.0 to 1.0
    impact_cost: float   # in currency units
    mitigation: str
    exposure: float = 0.0
    severity_level: str = "Medium"
    rank: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category,
            "probability": round(self.probability, 2),
            "impact_cost": round(self.impact_cost, 2),
            "mitigation": self.mitigation,
            "exposure": round(self.exposure, 2),
            "severity_level": self.severity_level,
            "rank": self.rank,
        }


@dataclass
class RiskRegisterSummary:
    total_risks: int
    total_exposure: float
    max_single_exposure: float
    risks_by_category: Dict[str, int]
    exposure_by_category: Dict[str, float]
    ranked_risks: List[RiskItem]
    matrix_grid: Dict[str, Dict[str, int]]  # prob_band x impact_band counts


def classify_severity(probability: float, impact_cost: float, max_impact: float) -> str:
    """Classify risk into Low, Medium, High, or Critical based on normalized coordinates."""
    norm_impact = (impact_cost / max_impact) if max_impact > 0 else 0.5
    score = probability * norm_impact

    if score >= 0.50 or (probability >= 0.7 and norm_impact >= 0.6):
        return "Critical"
    elif score >= 0.25 or (probability >= 0.5 and norm_impact >= 0.4):
        return "High"
    elif score >= 0.10:
        return "Medium"
    return "Low"


def analyze_risk_register(risks: List[Dict[str, Any]]) -> RiskRegisterSummary:
    """Process a list of risks, compute risk exposures, rank them, and generate matrix summaries.

    Args:
        risks: List of dicts with 'id', 'description', 'category', 'probability', 'impact_cost', 'mitigation'.

    Returns:
        RiskRegisterSummary with ranked risks, exposures, and heat map data.
    """
    if not risks:
        return RiskRegisterSummary(
            total_risks=0,
            total_exposure=0.0,
            max_single_exposure=0.0,
            risks_by_category={},
            exposure_by_category={},
            ranked_risks=[],
            matrix_grid={"High": {"High": 0, "Med": 0, "Low": 0},
                         "Medium": {"High": 0, "Med": 0, "Low": 0},
                         "Low": {"High": 0, "Med": 0, "Low": 0}},
        )

    processed_items: List[RiskItem] = []
    max_impact = max((float(r.get("impact_cost", 0.0)) for r in risks), default=1.0)
    if max_impact <= 0:
        max_impact = 1.0

    total_exposure = 0.0
    cat_counts: Dict[str, int] = {cat: 0 for cat in RISK_CATEGORIES}
    cat_exposure: Dict[str, float] = {cat: 0.0 for cat in RISK_CATEGORIES}

    # Grid: Prob (High, Medium, Low) vs Impact (High, Medium, Low)
    matrix_grid = {
        "High": {"High": 0, "Medium": 0, "Low": 0},
        "Medium": {"High": 0, "Medium": 0, "Low": 0},
        "Low": {"High": 0, "Medium": 0, "Low": 0},
    }

    for idx, r in enumerate(risks, start=1):
        rid = str(r.get("id", f"R-{idx:02d}"))
        desc = str(r.get("description", f"Risk {idx}"))
        cat = str(r.get("category", "Technical"))
        if cat not in cat_counts:
            cat_counts[cat] = 0
            cat_exposure[cat] = 0.0

        p = float(r.get("probability", 0.3))
        p = max(0.0, min(1.0, p))
        impact = float(r.get("impact_cost", 0.0))
        if impact < 0:
            impact = 0.0
        mitigation = str(r.get("mitigation", "Standard monitoring"))

        # Risk Exposure = P * I (VTU 24CS51 Module 4)
        exposure = p * impact
        total_exposure += exposure

        cat_counts[cat] += 1
        cat_exposure[cat] += exposure

        severity = classify_severity(p, impact, max_impact)

        # Prob band
        p_band = "High" if p >= 0.67 else ("Medium" if p >= 0.33 else "Low")
        # Impact band relative to max
        i_ratio = impact / max_impact
        i_band = "High" if i_ratio >= 0.67 else ("Medium" if i_ratio >= 0.33 else "Low")
        matrix_grid[p_band][i_band] += 1

        item = RiskItem(
            id=rid,
            description=desc,
            category=cat,
            probability=p,
            impact_cost=impact,
            mitigation=mitigation,
            exposure=exposure,
            severity_level=severity,
        )
        processed_items.append(item)

    # Rank descending by Exposure
    processed_items.sort(key=lambda x: x.exposure, reverse=True)
    for rank, item in enumerate(processed_items, start=1):
        item.rank = rank

    max_exposure = processed_items[0].exposure if processed_items else 0.0

    return RiskRegisterSummary(
        total_risks=len(processed_items),
        total_exposure=round(total_exposure, 2),
        max_single_exposure=round(max_exposure, 2),
        risks_by_category={k: v for k, v in cat_counts.items() if v > 0},
        exposure_by_category={k: round(v, 2) for k, v in cat_exposure.items() if v > 0},
        ranked_risks=processed_items,
        matrix_grid=matrix_grid,
    )

