"""Consolidated project report and document export."""

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
from ui.format import format_currency, get_currency_symbol, get_active_currency


def render_report_page():
    render_page_header(
        title="Consolidated report",
        caption="Integrated decision-support synthesis uniting all software engineering models.",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.info("No active project loaded. Configure a project in Setup.")
        return

    curr = get_active_currency()
    sym = get_currency_symbol(curr)

    # Gather data across all modules
    advisor_res = evaluate_models(active)
    nominal_kloc = float(active.get("kloc", 25.0))
    backlog_pts = max(30.0, round(nominal_kloc * 5.0, 0))
    agile_plan = calculate_sprint_plan(
        backlog_points=backlog_pts,
        velocity_per_sprint=25.0,
        sprint_length_weeks=2,
    )

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

    risk_summary = analyze_risk_register(active.get("risks", []))

    bc_data = active.get("business_case") or {
        "initial_investment": float(active.get("budget", 5000000.0)),
        "annual_benefits": [2000000.0, 3000000.0, 4000000.0, 4800000.0, 5500000.0],
        "annual_costs": [500000.0, 600000.0, 700000.0, 750000.0, 800000.0],
        "discount_rate_pct": 10.0,
    }
    init_inv = float(bc_data.get("initial_investment", 5000000.0))
    ann_bens = bc_data.get("annual_benefits", [2000000.0] * 5)
    ann_costs = bc_data.get("annual_costs", [500000.0] * 5)
    disc_rate = float(bc_data.get("discount_rate_pct", 10.0))

    biz_res = evaluate_business_case(init_inv, ann_bens, ann_costs, disc_rate)
    scenario_res = evaluate_scenario_risk(init_inv, ann_bens, ann_costs, disc_rate)
    radr_res = evaluate_radr(init_inv, ann_bens, ann_costs, disc_rate, risk_premium_pct=3.0)

    q_scores = active.get("quality_scores") or {f: 3.8 for f in ALL_FACTORS}
    qual_res = evaluate_quality_scorecard(q_scores)

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

    pdf_bytes = generate_consolidated_pdf(report_bundle, currency=curr)
    csv_text = generate_consolidated_csv(report_bundle, currency=curr)
    proj_slug = active.get("name", "project").replace(" ", "_").lower()
    pdf_kb = len(pdf_bytes) / 1024.0
    csv_kb = len(csv_text.encode('utf-8')) / 1024.0

    # Key metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("Recommended model", advisor_res.top_model.model_name, f"{advisor_res.top_model.percentage}% match")
    with m2:
        with st.container(border=True):
            st.metric("COCOMO effort", f"{cocomo_res.effort_pm:.1f} PM", f"{cocomo_res.duration_months:.1f} mos")
    with m3:
        with st.container(border=True):
            st.metric("Risk exposure", format_currency(risk_summary.total_exposure, compact=True), f"{risk_summary.total_risks} risks")
    with m4:
        with st.container(border=True):
            st.metric("Expected NPV", format_currency(scenario_res.expected_npv, compact=True))

    st.markdown("## Document export")
    col_dl1, col_dl2 = st.columns([1, 1])
    with col_dl1:
        # Single primary button on page
        st.download_button(
            label=f"Download PDF report ({pdf_kb:.1f} KB)",
            data=pdf_bytes,
            file_name=f"ProcessCompass_{proj_slug}_report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            label=f"Download CSV data ({csv_kb:.1f} KB)",
            data=csv_text,
            file_name=f"ProcessCompass_{proj_slug}_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("## Synthesis preview")
    c_sec1, c_sec2 = st.columns(2)
    with c_sec1:
        st.markdown("**1. Process lifecycle scores**")
        df_models = pd.DataFrame([
            {"Rank": f"#{m.rank}", "Model": m.model_name, "Fit (%)": f"{m.percentage}%", "Score": m.score}
            for m in advisor_res.ranked_models
        ])
        st.dataframe(df_models, use_container_width=True, hide_index=True)

    with c_sec2:
        st.markdown("**2. Sizing and effort comparison**")
        df_est = pd.DataFrame([
            {"Technique": "Basic COCOMO", "Metric": f"{cocomo_res.kloc:.1f} KLOC", "Effort": f"{cocomo_res.effort_pm:.1f} PM"},
            {"Technique": "Function Points", "Metric": f"{fp_res.afp:.0f} AFP", "Effort": "Parametric"},
            {"Technique": "COSMIC FFP", "Metric": f"{cosmic_res.total_cfp} CFP", "Effort": f"{cosmic_res.total_effort_pm:.1f} PM"},
            {"Technique": "PERT Three-point", "Metric": f"{pert_res.total_tasks} tasks", "Effort": f"{pert_res.total_expected:.0f} hours"},
            {"Technique": "Agile Sprint Plan", "Metric": f"{agile_plan.total_story_points:.0f} points", "Effort": f"{agile_plan.sprints_needed} sprints"},
        ])
        st.dataframe(df_est, use_container_width=True, hide_index=True)

    st.markdown("**3. Monitored risks**")
    if risk_summary.ranked_risks:
        df_r = pd.DataFrame([
            {
                "ID": r.id,
                "Category": r.category,
                "Probability": f"{r.probability:.2f}",
                f"Impact ({sym})": format_currency(r.impact_cost, compact=False, precision=0),
                f"Exposure ({sym})": format_currency(r.exposure, compact=False, precision=0),
                "Mitigation": r.mitigation,
            }
            for r in risk_summary.ranked_risks[:3]
        ])
        st.dataframe(df_r, use_container_width=True, hide_index=True)
    else:
        st.write("No active risks recorded.")

    st.markdown("**4. McCall quality compliance**")
    q_data = [
        {"Pillar": cat, "Score": f"{c_res.average_score:.2f} / 5.0", "Compliance": f"{c_res.percentage:.1f}%"}
        for cat, c_res in qual_res.categories.items()
    ]
    st.dataframe(pd.DataFrame(q_data), use_container_width=True, hide_index=True)
