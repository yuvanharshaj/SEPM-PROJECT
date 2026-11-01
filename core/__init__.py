"""ProcessCompass Core Engineering & Estimation Modules.

Mapped to VTU 24CS51: Software Engineering & Project Management.
"""

from core.advisor import evaluate_models
from core.cocomo import calculate_cocomo
from core.function_points import calculate_function_points, fp_to_kloc
from core.risk import analyze_risk_register
from core.business_case import evaluate_business_case, evaluate_scenario_risk, evaluate_radr
from core.quality import evaluate_quality_scorecard
from core.agile import calculate_sprint_plan, generate_cost_of_change_data, AGILE_FRAMEWORKS
from core.cosmic import calculate_cosmic_ffp
from core.pert import calculate_pert
from core.report import generate_consolidated_csv, generate_consolidated_pdf

__all__ = [
    "evaluate_models",
    "calculate_cocomo",
    "calculate_function_points",
    "fp_to_kloc",
    "analyze_risk_register",
    "evaluate_business_case",
    "evaluate_scenario_risk",
    "evaluate_radr",
    "evaluate_quality_scorecard",
    "calculate_sprint_plan",
    "generate_cost_of_change_data",
    "AGILE_FRAMEWORKS",
    "calculate_cosmic_ffp",
    "calculate_pert",
    "generate_consolidated_csv",
    "generate_consolidated_pdf",
]
