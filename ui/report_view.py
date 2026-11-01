"""Consolidated Project Report & Export UI (PDF & CSV)."""

import streamlit as st
import pandas as pd

from core.advisor import evaluate_models
from core.cocomo import calculate_cocomo
from core.function_points import calculate_function_points
from core.risk import analyze_risk_register
from core.business_case import evaluate_business_case, evaluate_scenario_risk, evaluate_radr
from core.quality import evaluate_quality_scorecard, ALL_FACTORS
from core.agile import calculate_sprint_plan
from core.cosmic import calculate_cosmic_ffp
from core.pert import calculate_pert
from core.report import generate_consolidated_csv, generate_consolidated_pdf
from ui.components import render_page_header


def render_report_page():
    render_page_header(
        title="Consolidated Executive Project Report",
        subtitle="One-click decision-support synthesis uniting all VTU 24CS51 software engineering models.",
        module_tag="VTU 24CS51: Modules 1–5 Synthesis",
        co_tag="CO1–CO5: Comprehensive Decision Support for Software Engineering Management",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.warning("Please select or initialize a project in 'Project Setup' first.")
        return

    # Gather data across all modules
    # 1. Advisor (M1)
    advisor_res = evaluate_models(active)

    # 2. Agile Lab (M2)
    nominal_kloc = float(active.get("kloc", 25.0))
    backlog_pts = max(30.0, round(nominal_kloc * 5.0, 0))
    agile_plan = calculate_sprint_plan(
        backlog_points=backlog_pts,
        velocity_per_sprint=25.0,
        sprint_length_weeks=2,
    )

    # 3. Effort Estimation (M4 & M5)
    kloc_val = float(active.get("kloc", 25.0))
    mode_val = active.get("cocomo_mode", "organic")
    cocomo_res = calculate_cocomo(kloc_val, mode_val)

    fp_comps = active.get("fp_components") or {
        "EI": {"low": 10, "average": 15, "high": 5},
        "EO": {"low": 8, "average": 12, "high": 4},
        "EQ": {"low": 10, "average": 15, "high": 4},
        "ILF": {"low": 4, "average": 8, "high": 3},
        "EIF": {"low": 2, "average": 4, "high": 2},
    }
    gsc_rats = active.get("gsc_ratings") or [3] * 14
    fp_res = calculate_function_points(fp_comps, gsc_rats)

    cosmic_data = st.session_state.get("cosmic_processes", [
        {"process_id": "P-01", "name": "Core Process", "entries": 4, "exits": 3, "reads": 2, "writes": 2}
    ])
    cosmic_res = calculate_cosmic_ffp(cosmic_data, productivity_hours_per_cfp=12.0, team_size=int(active.get("team_size", 5)))

    pert_tasks = st.session_state.get("pert_tasks", [
        {"task_id": "T-01", "name": "Core WBS Task", "category": "Dev", "optimistic": 20.0, "most_likely": 40.0, "pessimistic": 70.0}
    ])
    pert_res = calculate_pert(pert_tasks)

    # 4. Risk Register (M4)
    risk_summary = analyze_risk_register(active.get("risks", []))

    # 5. Business Case & Scenario Risk (M3)
    bc_data = active.get("business_case") or {
        "initial_investment": float(active.get("budget", 60000.0)),
        "annual_benefits": [30000.0, 45000.0, 55000.0, 65000.0, 75000.0],
        "annual_costs": [8000.0, 9000.0, 10000.0, 10000.0, 11000.0],
        "discount_rate_pct": 10.0,
    }
    init_inv = float(bc_data.get("initial_investment", 60000.0))
    ann_bens = bc_data.get("annual_benefits", [30000.0] * 5)
    ann_costs = bc_data.get("annual_costs", [8000.0] * 5)
    disc_rate = float(bc_data.get("discount_rate_pct", 10.0))

    biz_res = evaluate_business_case(init_inv, ann_bens, ann_costs, disc_rate)
    scenario_res = evaluate_scenario_risk(init_inv, ann_bens, ann_costs, disc_rate)
    radr_res = evaluate_radr(init_inv, ann_bens, ann_costs, disc_rate, risk_premium_pct=3.0)

    # 6. Quality Scorecard (M5)
    q_scores = active.get("quality_scores") or {f: 3.8 for f in ALL_FACTORS}
    qual_res = evaluate_quality_scorecard(q_scores)

    # Bundle for report generators
    report_bundle = {
        "project": active,
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
        "agile": agile_plan.to_dict(),
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

    # Top Download Buttons
    col_dl1, col_dl2, col_meta = st.columns([1.2, 1.2, 2.5])

    with col_dl1:
        pdf_bytes = generate_consolidated_pdf(report_bundle)
        proj_slug = active.get("name", "project").replace(" ", "_").lower()
        st.download_button(
            label="📥 Download PDF Summary",
            data=pdf_bytes,
            file_name=f"ProcessCompass_{proj_slug}_report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    with col_dl2:
        csv_text = generate_consolidated_csv(report_bundle)
        st.download_button(
            label="📊 Download CSV Data",
            data=csv_text,
            file_name=f"ProcessCompass_{proj_slug}_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_meta:
        st.caption("Ready for academic project evaluation & viva defense (VTU 24CS51).")

    st.markdown("---")

    # Executive Summary Card
    st.markdown("### 📋 Executive Synthesis & Recommendation")
    st.info(
        f"**Project '{active.get('name')}':**\n\n"
        f"• **Recommended Lifecycle:** {advisor_res.top_model.model_name} ({advisor_res.top_model.percentage}% match)\n\n"
        f"• **Agile Release Schedule:** {agile_plan.sprints_needed} Sprints ({agile_plan.total_weeks} weeks, target {agile_plan.finish_date})\n\n"
        f"• **Effort Estimates:** COCOMO: {cocomo_res.effort_pm:.1f} PM ({cocomo_res.duration_months:.1f} Mos) | "
        f"COSMIC: {cosmic_res.total_cfp} CFP ({cosmic_res.total_effort_pm:.1f} PM) | PERT: {pert_res.total_expected:.0f} Hrs\n\n"
        f"• **Risk Exposure:** ${risk_summary.total_exposure:,.0f} across {risk_summary.total_risks} logged risks\n\n"
        f"• **Economic Feasibility:** Nominal NPV = ${biz_res.npv:,.2f} | Expected NPV (EMV) = ${scenario_res.expected_npv:,.2f} | "
        f"RADR Hurdle NPV = ${radr_res.adjusted_npv:,.2f} ({radr_res.adjusted_discount_rate_pct:.1f}%)\n\n"
        f"• **Software Quality Index:** {qual_res.overall_index:.2f}/5.0 ({qual_res.overall_percentage:.1f}% compliance) - {qual_res.sqa_verdict}"
    )

    # 4-Column High-Level Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Top Lifecycle", advisor_res.top_model.model_name, f"{advisor_res.top_model.percentage}% fit")
    with c2:
        st.metric("Estimated Effort", f"{cocomo_res.effort_pm:.1f} PM", f"{cocomo_res.duration_months:.1f} Mos")
    with c3:
        st.metric("Total Risk Exposure", f"${risk_summary.total_exposure:,.0f}", f"{risk_summary.total_risks} risks")
    with c4:
        st.metric("Expected NPV", f"${scenario_res.expected_npv:,.0f}", f"Nominal: ${biz_res.npv:,.0f}")

    # Section Previews
    c_sec1, c_sec2 = st.columns(2)
    with c_sec1:
        st.markdown("#### 1. Lifecycle Scoring Breakdown")
        df_models = pd.DataFrame([
            {"Rank": f"#{m.rank}", "Model": m.model_name, "Fit (%)": f"{m.percentage}%", "Score": m.score}
            for m in advisor_res.ranked_models
        ])
        st.dataframe(df_models, use_container_width=True, hide_index=True)

    with c_sec2:
        st.markdown("#### 2. Agile Iterations & Sizing Comparison")
        df_est_summary = pd.DataFrame([
            {"Technique": "Boehm Basic COCOMO", "Metric / Size": f"{cocomo_res.kloc:.1f} KLOC", "Effort": f"{cocomo_res.effort_pm:.1f} PM"},
            {"Technique": "Albrecht Function Points", "Metric / Size": f"{fp_res.afp:.0f} AFP", "Effort": "Parametric Sizing"},
            {"Technique": "COSMIC Full FP", "Metric / Size": f"{cosmic_res.total_cfp} CFP", "Effort": f"{cosmic_res.total_effort_pm:.1f} PM"},
            {"Technique": "Bottom-Up PERT", "Metric / Size": f"{pert_res.total_tasks} WBS Tasks", "Effort": f"{pert_res.total_expected:.0f} Hours"},
            {"Technique": "Agile Sprint Plan", "Metric / Size": f"{agile_plan.total_story_points:.0f} Story Points", "Effort": f"{agile_plan.sprints_needed} Sprints"},
        ])
        st.dataframe(df_est_summary, use_container_width=True, hide_index=True)

    st.markdown("#### 3. Key Risks Requiring Active Monitoring")
    if risk_summary.ranked_risks:
        df_r = pd.DataFrame([
            {
                "ID": r.id,
                "Category": r.category,
                "Probability": f"{r.probability:.2f}",
                "Impact ($)": f"${r.impact_cost:,.0f}",
                "Exposure ($)": f"${r.exposure:,.0f}",
                "Mitigation": r.mitigation,
            }
            for r in risk_summary.ranked_risks[:3]
        ])
        st.dataframe(df_r, use_container_width=True, hide_index=True)
    else:
        st.write("No active risks recorded.")

    st.markdown("#### 4. McCall Quality Pillars")
    q_data = [
        {"Pillar": cat, "Score": f"{c_res.average_score:.2f} / 5.0", "Compliance": f"{c_res.percentage:.1f}%"}
        for cat, c_res in qual_res.categories.items()
    ]
    st.dataframe(pd.DataFrame(q_data), use_container_width=True, hide_index=True)
