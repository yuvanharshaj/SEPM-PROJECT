"""Unit tests for Consolidated Report Generation (PDF & CSV)."""

from core.report import generate_consolidated_csv, generate_consolidated_pdf
from sample_data.samples import SAMPLE_PROJECTS
from core.advisor import evaluate_models
from core.cocomo import calculate_cocomo
from core.function_points import calculate_function_points
from core.risk import analyze_risk_register
from core.business_case import evaluate_business_case
from core.quality import evaluate_quality_scorecard


def test_consolidated_report_generation():
    proj = SAMPLE_PROJECTS[0]
    advisor_res = evaluate_models(proj)
    cocomo_res = calculate_cocomo(proj["kloc"], proj["cocomo_mode"])
    fp_res = calculate_function_points(proj["fp_components"], proj["gsc_ratings"])
    risk_summary = analyze_risk_register(proj["risks"])
    biz_res = evaluate_business_case(
        initial_investment=proj["business_case"]["initial_investment"],
        annual_benefits=proj["business_case"]["annual_benefits"],
        annual_costs=proj["business_case"]["annual_costs"],
        discount_rate_pct=proj["business_case"]["discount_rate_pct"],
    )
    qual_res = evaluate_quality_scorecard(proj["quality_scores"])

    bundle = {
        "project": proj,
        "advisor": {
            "top_model": advisor_res.top_model.model_name,
            "ranked_models": [
                {
                    "rank": m.rank,
                    "model_name": m.model_name,
                    "score": m.score,
                    "percentage": m.percentage,
                    "justification": m.justification,
                }
                for m in advisor_res.ranked_models
            ],
            "executive_summary": advisor_res.executive_summary,
        },
        "cocomo": cocomo_res.to_dict(),
        "fp": fp_res.to_dict(),
        "risks": {
            "total_risks": risk_summary.total_risks,
            "total_exposure": risk_summary.total_exposure,
            "ranked_risks": [r.to_dict() for r in risk_summary.ranked_risks],
        },
        "business_case": biz_res.to_dict(),
        "quality": qual_res.to_dict(),
    }

    # Test CSV
    csv_str = generate_consolidated_csv(bundle)
    assert "ProcessCompass Project Evaluation Summary" in csv_str
    assert proj["name"] in csv_str
    assert "COCOMO Mode" in csv_str
    assert "Net Present Value" in csv_str

    # Test PDF
    pdf_bytes = generate_consolidated_pdf(bundle)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

