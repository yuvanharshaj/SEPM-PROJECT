"""Process Model Selection & Recommendation Engine.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 1:
    Software Process Structure, Prescriptive Process Models (Waterfall, Incremental,
    Evolutionary/Spiral), Unified Process (UP), Agile Development (Scrum, Extreme Programming - XP).

Evaluation Criteria:
    1. Requirement Stability    : High, Medium, Low
    2. Team Size                : Small (<=8), Medium (9-25), Large (>25)
    3. Project Duration         : Short (<6 mos), Medium (6-18 mos), Long (>18 mos)
    4. Project Risk Level       : Low, Medium, High
    5. Customer Involvement     : Low, Medium, High
    6. Need for Early Delivery  : Low, Medium, High
    7. Team Experience          : Low (Novice), Medium (Average), High (Expert)

Scoring Mechanism:
    Total Score(Model) = sum(Weight_c * Compatibility(Model, Criteria_Value_c))
    Percentage = (Total Score / Max Possible Score) * 100
"""

from dataclasses import dataclass
from typing import Dict, List, Any


MODELS: List[str] = [
    "Waterfall",
    "Incremental",
    "Evolutionary/Spiral",
    "Scrum",
    "XP",
    "Unified Process",
]

CRITERIA_KEYS: List[str] = [
    "req_stability",
    "team_size",
    "duration",
    "risk_level",
    "customer_involvement",
    "early_delivery",
    "team_experience",
]

DEFAULT_CRITERIA_WEIGHTS: Dict[str, float] = {
    "req_stability": 2.5,
    "team_size": 1.5,
    "duration": 1.0,
    "risk_level": 2.5,
    "customer_involvement": 2.0,
    "early_delivery": 2.0,
    "team_experience": 1.5,
}

# Compatibility matrix: Model -> Criterion -> Value -> Score (1.0 to 5.0)
MODEL_COMPATIBILITY_MATRIX: Dict[str, Dict[str, Dict[str, float]]] = {
    "Waterfall": {
        "req_stability": {"High": 5.0, "Medium": 2.5, "Low": 1.0},
        "team_size": {"Small": 3.5, "Medium": 4.5, "Large": 4.0},
        "duration": {"Short": 3.0, "Medium": 4.5, "Long": 4.0},
        "risk_level": {"Low": 5.0, "Medium": 3.0, "Low-to-Med": 4.0, "High": 1.0},
        "customer_involvement": {"Low": 5.0, "Medium": 3.0, "High": 1.5},
        "early_delivery": {"Low": 5.0, "Medium": 2.5, "High": 1.0},
        "team_experience": {"Low": 3.0, "Medium": 4.5, "High": 5.0},
    },
    "Incremental": {
        "req_stability": {"High": 4.5, "Medium": 4.5, "Low": 2.5},
        "team_size": {"Small": 4.0, "Medium": 5.0, "Large": 4.0},
        "duration": {"Short": 3.5, "Medium": 5.0, "Long": 4.5},
        "risk_level": {"Low": 4.0, "Medium": 4.5, "High": 3.0},
        "customer_involvement": {"Low": 3.0, "Medium": 4.5, "High": 4.0},
        "early_delivery": {"Low": 3.0, "Medium": 4.5, "High": 5.0},
        "team_experience": {"Low": 3.5, "Medium": 4.5, "High": 5.0},
    },
    "Evolutionary/Spiral": {
        "req_stability": {"High": 3.5, "Medium": 4.5, "Low": 4.5},
        "team_size": {"Small": 2.5, "Medium": 4.5, "Large": 5.0},
        "duration": {"Short": 2.0, "Medium": 4.0, "Long": 5.0},
        "risk_level": {"Low": 2.0, "Medium": 4.0, "High": 5.0},
        "customer_involvement": {"Low": 2.0, "Medium": 4.0, "High": 5.0},
        "early_delivery": {"Low": 3.0, "Medium": 4.0, "High": 4.0},
        "team_experience": {"Low": 1.5, "Medium": 3.5, "High": 5.0},
    },
    "Scrum": {
        "req_stability": {"High": 3.0, "Medium": 4.5, "Low": 5.0},
        "team_size": {"Small": 5.0, "Medium": 4.5, "Large": 2.5},
        "duration": {"Short": 4.5, "Medium": 5.0, "Long": 4.0},
        "risk_level": {"Low": 3.5, "Medium": 4.5, "High": 4.5},
        "customer_involvement": {"Low": 1.0, "Medium": 3.5, "High": 5.0},
        "early_delivery": {"Low": 2.0, "Medium": 4.0, "High": 5.0},
        "team_experience": {"Low": 2.5, "Medium": 4.0, "High": 5.0},
    },
    "XP": {
        "req_stability": {"High": 2.5, "Medium": 4.0, "Low": 5.0},
        "team_size": {"Small": 5.0, "Medium": 3.0, "Large": 1.0},
        "duration": {"Short": 5.0, "Medium": 4.0, "Long": 3.0},
        "risk_level": {"Low": 3.0, "Medium": 4.0, "High": 4.0},
        "customer_involvement": {"Low": 1.0, "Medium": 3.0, "High": 5.0},
        "early_delivery": {"Low": 1.5, "Medium": 4.0, "High": 5.0},
        "team_experience": {"Low": 1.5, "Medium": 3.5, "High": 5.0},
    },
    "Unified Process": {
        "req_stability": {"High": 4.0, "Medium": 4.5, "Low": 3.5},
        "team_size": {"Small": 2.5, "Medium": 4.5, "Large": 5.0},
        "duration": {"Short": 2.0, "Medium": 4.5, "Long": 5.0},
        "risk_level": {"Low": 3.0, "Medium": 4.5, "High": 4.5},
        "customer_involvement": {"Low": 2.5, "Medium": 4.0, "High": 4.0},
        "early_delivery": {"Low": 3.0, "Medium": 4.0, "High": 3.5},
        "team_experience": {"Low": 2.0, "Medium": 4.0, "High": 5.0},
    },
}

MODEL_DESCRIPTIONS: Dict[str, str] = {
    "Waterfall": "Linear-sequential lifecycle with strict phase gates (Requirements -> Design -> Code -> Test -> Deploy). Best when requirements are fixed, fully understood upfront, and risk is low.",
    "Incremental": "Delivers core functionality in release stages/increments. Provides working software early while permitting modular progression.",
    "Evolutionary/Spiral": "Iterative risk-driven model (Boehm). Couples prototyping with systematic milestone checkpoints, excelling in high-risk, mission-critical systems.",
    "Scrum": "Agile framework with short fixed-length sprints (1-4 weeks), cross-functional teams, sprint backlogs, and continuous customer feedback. Excels with evolving requirements.",
    "XP": "Extreme Programming emphasizes technical rigor: continuous integration, test-driven development (TDD), pair programming, and on-site customer presence for rapid small-team delivery.",
    "Unified Process": "Use-case driven, architecture-centric, iterative framework (Inception, Elaboration, Construction, Transition). Tailored for large enterprise object-oriented systems.",
}


@dataclass
class ScoredModel:
    model_name: str
    score: float
    max_score: float
    percentage: float
    rank: int
    strengths: List[str]
    drawbacks: List[str]
    justification: str


@dataclass
class AdvisorResult:
    top_model: ScoredModel
    ranked_models: List[ScoredModel]
    executive_summary: str
    detailed_justifications: Dict[str, str]


def _normalize_value(criterion: str, raw_value: Any) -> str:
    """Normalize input value to match matrix categories."""
    if criterion == "team_size":
        if isinstance(raw_value, (int, float)):
            if raw_value <= 8:
                return "Small"
            elif raw_value <= 25:
                return "Medium"
            return "Large"
        val = str(raw_value).capitalize()
        return val if val in ["Small", "Medium", "Large"] else "Medium"

    if criterion == "duration":
        if isinstance(raw_value, (int, float)):
            if raw_value <= 6:
                return "Short"
            elif raw_value <= 18:
                return "Medium"
            return "Long"
        val = str(raw_value).capitalize()
        return val if val in ["Short", "Medium", "Long"] else "Medium"

    # Stability, Risk, Involvement, Early Delivery, Experience
    val = str(raw_value).capitalize()
    if val in ["High", "Medium", "Low"]:
        return val
    return "Medium"


def evaluate_models(
    project_characteristics: Dict[str, Any],
    custom_weights: Dict[str, float] | None = None,
) -> AdvisorResult:
    """Evaluate and rank software process models against project parameters.

    Args:
        project_characteristics: Dict containing keys:
            - req_stability: 'High' | 'Medium' | 'Low'
            - team_size: int or 'Small' | 'Medium' | 'Large'
            - duration: int (months) or 'Short' | 'Medium' | 'Long'
            - risk_level: 'High' | 'Medium' | 'Low'
            - customer_involvement: 'High' | 'Medium' | 'Low'
            - early_delivery: 'High' | 'Medium' | 'Low'
            - team_experience: 'High' | 'Medium' | 'Low'
        custom_weights: Optional overrides for DEFAULT_CRITERIA_WEIGHTS.

    Returns:
        AdvisorResult containing ranked models and plain-English explanations.
    """
    weights = DEFAULT_CRITERIA_WEIGHTS.copy()
    if custom_weights:
        weights.update(custom_weights)

    # Normalize inputs
    norm_chars: Dict[str, str] = {}
    for crit in CRITERIA_KEYS:
        val = project_characteristics.get(crit, "Medium")
        norm_chars[crit] = _normalize_value(crit, val)

    max_possible_score = sum(weights.get(crit, 1.0) * 5.0 for crit in CRITERIA_KEYS)

    scored_list = []
    for model_name in MODELS:
        compat = MODEL_COMPATIBILITY_MATRIX[model_name]
        total_score = 0.0
        strengths = []
        drawbacks = []

        for crit in CRITERIA_KEYS:
            crit_val = norm_chars[crit]
            score_crit = compat.get(crit, {}).get(crit_val, 3.0)
            weight = weights.get(crit, 1.0)
            total_score += score_crit * weight

            readable_crit = crit.replace("_", " ").title()
            if score_crit >= 4.5:
                strengths.append(f"Highly compatible with {readable_crit} ({crit_val})")
            elif score_crit <= 2.0:
                drawbacks.append(f"Challenged by {readable_crit} ({crit_val})")

        pct = (total_score / max_possible_score) * 100.0 if max_possible_score > 0 else 0.0
        scored_list.append({
            "model_name": model_name,
            "score": round(total_score, 2),
            "max_score": round(max_possible_score, 2),
            "percentage": round(pct, 1),
            "strengths": strengths,
            "drawbacks": drawbacks,
        })

    # Sort descending by score
    scored_list.sort(key=lambda x: x["score"], reverse=True)

    ranked_models: List[ScoredModel] = []
    detailed_justifications: Dict[str, str] = {}

    top_entry = scored_list[0]
    top_name = top_entry["model_name"]

    for rank, entry in enumerate(scored_list, start=1):
        name = entry["model_name"]
        pct = entry["percentage"]
        st = entry["strengths"]
        dr = entry["drawbacks"]

        if rank == 1:
            justification = (
                f"**{name}** emerges as the premier recommendation with a suitability score of {pct}%. "
                f"It excels because your project profile aligns directly with its core strengths: "
                f"{'; '.join(st[:3]) if st else 'balanced project dynamics'}. "
                f"{MODEL_DESCRIPTIONS[name]}"
            )
        else:
            reasons = []
            if dr:
                reasons.append(f"it faces friction regarding {', '.join(dr[:2])}")
            diff = round(top_entry["percentage"] - pct, 1)
            reasons.append(f"trails the top model by {diff}% in fit efficiency")
            justification = (
                f"**{name}** scored {pct}% (Rank #{rank}). While viable, {' and '.join(reasons)}. "
                f"Key trade-off: {MODEL_DESCRIPTIONS[name]}"
            )

        detailed_justifications[name] = justification
        ranked_models.append(
            ScoredModel(
                model_name=name,
                score=entry["score"],
                max_score=entry["max_score"],
                percentage=pct,
                rank=rank,
                strengths=st,
                drawbacks=dr,
                justification=justification,
            )
        )

    exec_summary = (
        f"Based on VTU 24CS51 process model evaluation criteria, **{ranked_models[0].model_name}** "
        f"is recommended with {ranked_models[0].percentage}% alignment. "
        f"The primary differentiating factors were Requirement Stability ({norm_chars['req_stability']}), "
        f"Risk Level ({norm_chars['risk_level']}), and Early Delivery Need ({norm_chars['early_delivery']})."
    )

    return AdvisorResult(
        top_model=ranked_models[0],
        ranked_models=ranked_models,
        executive_summary=exec_summary,
        detailed_justifications=detailed_justifications,
    )
