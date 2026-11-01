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
from ui.theme import render_page_header, render_kpi_card, render_empty_state_html
from ui.format import format_currency, get_currency_symbol, get_active_currency


def render_report_page():
    render_page_header(
        title="Consolidated Executive Project Report",
        subtitle="One-click decision-support synthesis uniting all VTU 24CS51 software engineering models.",
        module_tag="VTU 24CS51: Modules 1–5 Synthesis",
        co_tag="CO1–CO5: Comprehensive Decision Support for Software Engineering Management",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.markdown(
            render_empty_state_html(
                icon="📄",
                title="No Active Project Selected",
                description="Please select or configure a project benchmark in 'Project Setup' to generate a consolidated report.",
            ),
            unsafe_allow_html=True,
        )
        return

    curr = get_active_currency()
    sym = get_currency_symbol(curr)

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

    # Generate documents with currency
    pdf_bytes = generate_consolidated_pdf(report_bundle, currency=curr)
    csv_text = generate_consolidated_csv(report_bundle, currency=curr)
    proj_slug = active.get("name", "project").replace(" ", "_").lower()
    pdf_kb = len(pdf_bytes) / 1024.0
    csv_kb = len(csv_text.encode('utf-8')) / 1024.0

    # Top Download Action Bar
    st.markdown(
        f"""
        <div class="pc-card" style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(13, 148, 136, 0.05)); border: 1px solid rgba(37, 99, 235, 0.2); padding: 18px 24px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: var(--pc-primary-dark, #1E40AF); letter-spacing: 0.05em;">Export Artifacts &bull; VTU 24CS51 Viva Defense</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: var(--pc-text-main, #0F172A); margin-top: 2px;">
                        {active.get('name')} Decision Synthesis Report
                    </div>
                    <div style="font-size: 0.8rem; color: var(--pc-text-muted, #64748B); margin-top: 2px;">
                        Currency: <b>{curr} ({sym})</b> &bull; Ready for submission to evaluator committee
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_dl1, col_dl2, col_meta = st.columns([1.3, 1.3, 2.0])
    with col_dl1:
        st.download_button(
            label=f"📥 Download PDF Document ({pdf_kb:.1f} KB)",
            data=pdf_bytes,
            file_name=f"ProcessCompass_{proj_slug}_report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            label=f"📊 Download Raw CSV ({csv_kb:.1f} KB)",
            data=csv_text,
            file_name=f"ProcessCompass_{proj_slug}_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_meta:
        st.markdown(
            f"<div style='font-size: 0.82rem; color: var(--pc-text-muted); padding-top: 6px;'>"
            f"PDF includes DejaVu Sans TrueType typography with native <b>{sym}</b> currency glyphs and styling."
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4-Column KPI Summary Cards
    m_cols = st.columns(4)
    with m_cols[0]:
        st.markdown(
            render_kpi_card(
                label="Recommended Model",
                value=advisor_res.top_model.model_name,
                subtitle=f"{advisor_res.top_model.percentage}% Lifecycle Fit",
                icon="🧭",
                accent_color="#2563EB",
            ),
            unsafe_allow_html=True,
        )
    with m_cols[1]:
        st.markdown(
            render_kpi_card(
                label="COCOMO Labor",
                value=f"{cocomo_res.effort_pm:.1f} PM",
                subtitle=f"{cocomo_res.duration_months:.1f} Mos Schedule",
                icon="💼",
                accent_color="#0D9488",
            ),
            unsafe_allow_html=True,
        )
    with m_cols[2]:
        st.markdown(
            render_kpi_card(
                label="Risk Exposure",
                value=format_currency(risk_summary.total_exposure, compact=True),
                subtitle=f"{risk_summary.total_risks} Logged Risks",
                icon="⚠️",
                accent_color="#EF4444",
            ),
            unsafe_allow_html=True,
        )
    with m_cols[3]:
        st.markdown(
            render_kpi_card(
                label="Expected NPV (EMV)",
                value=format_currency(scenario_res.expected_npv, compact=True),
                subtitle=f"Nominal: {format_currency(biz_res.npv, compact=True)}",
                icon="💎",
                accent_color="#10B981" if scenario_res.expected_npv > 0 else "#EF4444",
            ),
            unsafe_allow_html=True,
        )

    # Executive Summary Card
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Executive Synthesis & Recommendation")
    st.markdown(
        f"""
        <div class="pc-card" style="border-left: 4px solid var(--pc-primary, #2563EB); font-size: 0.92rem; line-height: 1.6; color: var(--pc-text-main);">
            <div style="font-weight: 800; font-size: 1.05rem; color: var(--pc-primary-dark, #1E40AF); margin-bottom: 8px;">
                Executive Brief: {active.get('name')}
            </div>
            <div>&bull; <b>Recommended Lifecycle:</b> {advisor_res.top_model.model_name} (<b>{advisor_res.top_model.percentage}%</b> compatibility match)</div>
            <div>&bull; <b>Agile Release Trajectory:</b> {agile_plan.sprints_needed} Sprints ({agile_plan.total_weeks} weeks, target release <b>{agile_plan.finish_date}</b>)</div>
            <div>&bull; <b>Effort Sizing Synthesis:</b> COCOMO: <b>{cocomo_res.effort_pm:.1f} PM</b> ({cocomo_res.duration_months:.1f} Mos) | COSMIC: <b>{cosmic_res.total_cfp} CFP</b> ({cosmic_res.total_effort_pm:.1f} PM) | PERT: <b>{pert_res.total_expected:.0f} Hrs</b></div>
            <div>&bull; <b>Project Risk Exposure:</b> <b>{format_currency(risk_summary.total_exposure, compact=False, precision=0)}</b> across {risk_summary.total_risks} logged risk items</div>
            <div>&bull; <b>Economic Feasibility:</b> Nominal NPV = <b>{format_currency(biz_res.npv, compact=False, precision=0)}</b> | Expected NPV (EMV) = <b>{format_currency(scenario_res.expected_npv, compact=False, precision=0)}</b> | RADR Hurdle NPV = <b>{format_currency(radr_res.adjusted_npv, compact=False, precision=0)}</b> ({radr_res.adjusted_discount_rate_pct:.1f}%)</div>
            <div>&bull; <b>McCall Quality Assurance:</b> <b>{qual_res.overall_index:.2f} / 5.0</b> ({qual_res.overall_percentage:.1f}% compliance) &bull; <i>{qual_res.sqa_verdict}</i></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Section Previews matching PDF structure
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
                f"Impact ({sym})": format_currency(r.impact_cost, compact=False, precision=0),
                f"Exposure ({sym})": format_currency(r.exposure, compact=False, precision=0),
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
