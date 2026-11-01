"""Unit tests for Consolidated Report Generation (PDF & CSV)."""

from core.report import generate_consolidated_csv, generate_consolidated_pdf
from sample_data.samples import SAMPLE_PROJECTS
from core.advisor import evaluate_models
from core.cocomo import calculate_cocomo
from core.function_points import calculate_function_points
from core.risk import analyze_risk_register
from core.business_case import evaluate_business_case, evaluate_scenario_risk, evaluate_radr
from core.quality import evaluate_quality_scorecard
from core.agile import calculate_sprint_plan
from core.cosmic import calculate_cosmic_ffp
from core.pert import calculate_pert
from db.database import DatabaseManager


def test_consolidated_report_generation():
    proj = SAMPLE_PROJECTS[0]
    advisor_res = evaluate_models(proj)
    agile_res = calculate_sprint_plan(100.0, 25.0, 2)
    cocomo_res = calculate_cocomo(proj["kloc"], proj["cocomo_mode"])
    fp_res = calculate_function_points(proj["fp_components"], proj["gsc_ratings"])
    cosmic_res = calculate_cosmic_ffp([
        {"process_id": "P-01", "name": "Auth", "entries": 2, "exits": 2, "reads": 1, "writes": 1}
    ])
    pert_res = calculate_pert([
        {"task_id": "T-01", "name": "Task 1", "category": "Dev", "optimistic": 10.0, "most_likely": 20.0, "pessimistic": 30.0}
    ])
    risk_summary = analyze_risk_register(proj["risks"])
    biz_res = evaluate_business_case(
        initial_investment=proj["business_case"]["initial_investment"],
        annual_benefits=proj["business_case"]["annual_benefits"],
        annual_costs=proj["business_case"]["annual_costs"],
        discount_rate_pct=proj["business_case"]["discount_rate_pct"],
    )
    scenario_res = evaluate_scenario_risk(
        base_investment=proj["business_case"]["initial_investment"],
        base_benefits=proj["business_case"]["annual_benefits"],
        base_costs=proj["business_case"]["annual_costs"],
    )
    radr_res = evaluate_radr(
        initial_investment=proj["business_case"]["initial_investment"],
        annual_benefits=proj["business_case"]["annual_benefits"],
        annual_costs=proj["business_case"]["annual_costs"],
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
        "agile": agile_res.to_dict(),
        "cocomo": cocomo_res.to_dict(),
        "fp": fp_res.to_dict(),
        "cosmic": cosmic_res.to_dict(),
        "pert": pert_res.to_dict(),
        "risks": {
            "total_risks": risk_summary.total_risks,
            "total_exposure": risk_summary.total_exposure,
            "ranked_risks": [r.to_dict() for r in risk_summary.ranked_risks],
        },
        "business_case": biz_res.to_dict(),
        "scenario": scenario_res.to_dict(),
        "radr": radr_res.to_dict(),
        "quality": qual_res.to_dict(),
    }

    # Test CSV
    csv_str = generate_consolidated_csv(bundle)
    assert "ProcessCompass Project Evaluation Summary" in csv_str
    assert proj["name"] in csv_str
    assert "AGILE LAB" in csv_str
    assert "COSMIC Function Points" in csv_str
    assert "PERT Expected Effort" in csv_str
    assert "Expected NPV (EMV)" in csv_str

    # Test PDF
    pdf_bytes = generate_consolidated_pdf(bundle)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")


def test_all_sample_projects_pdf_and_csv_generation():
    """Verify that every sample project in database can generate PDF and CSV without error."""
    db = DatabaseManager()
    projects = db.list_projects()
    assert len(projects) == 3

    for p_summary in projects:
        proj = db.get_project_by_id(p_summary["id"])
        assert proj is not None

        adv = evaluate_models(proj)
        cocomo = calculate_cocomo(proj["kloc"], proj["cocomo_mode"])
        fp = calculate_function_points(proj["fp_components"], proj["gsc_ratings"])
        risks = analyze_risk_register(proj.get("risks", []))
        biz = evaluate_business_case(
            initial_investment=proj["business_case"]["initial_investment"],
            annual_benefits=proj["business_case"]["annual_benefits"],
            annual_costs=proj["business_case"]["annual_costs"],
            discount_rate_pct=proj["business_case"]["discount_rate_pct"],
        )
        scen = evaluate_scenario_risk(
            base_investment=proj["business_case"]["initial_investment"],
            base_benefits=proj["business_case"]["annual_benefits"],
            base_costs=proj["business_case"]["annual_costs"],
            discount_rate_pct=proj["business_case"]["discount_rate_pct"],
        )
        radr = evaluate_radr(
            initial_investment=proj["business_case"]["initial_investment"],
            annual_benefits=proj["business_case"]["annual_benefits"],
            annual_costs=proj["business_case"]["annual_costs"],
            base_discount_rate_pct=proj["business_case"]["discount_rate_pct"],
        )
        qual = evaluate_quality_scorecard(proj["quality_scores"])
        agile = calculate_sprint_plan(120.0, 25.0, 2)
        cosmic = calculate_cosmic_ffp([
            {"process_id": "P-01", "name": "Transaction", "entries": 3, "exits": 3, "reads": 2, "writes": 2}
        ])
        pert = calculate_pert([
            {"task_id": "T-01", "name": "Sprint 1 Setup", "category": "Setup", "optimistic": 5.0, "most_likely": 10.0, "pessimistic": 20.0}
        ])

        bundle = {
            "project": proj,
            "advisor": {
                "top_model": adv.top_model.model_name,
                "ranked_models": [
                    {
                        "rank": m.rank,
                        "model_name": m.model_name,
                        "score": m.score,
                        "percentage": m.percentage,
                        "justification": m.justification,
                    }
                    for m in adv.ranked_models
                ],
                "executive_summary": adv.executive_summary,
            },
            "agile": agile.to_dict(),
            "cocomo": cocomo.to_dict(),
            "fp": fp.to_dict(),
            "cosmic": cosmic.to_dict(),
            "pert": pert.to_dict(),
            "risks": {
                "total_risks": risks.total_risks,
                "total_exposure": risks.total_exposure,
                "ranked_risks": [r.to_dict() for r in risks.ranked_risks],
            },
            "business_case": biz.to_dict(),
            "scenario": scen.to_dict(),
            "radr": radr.to_dict(),
            "quality": qual.to_dict(),
        }

        csv_str = generate_consolidated_csv(bundle)
        pdf_bytes = generate_consolidated_pdf(bundle)

        assert len(csv_str) > 500
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF")
