"""Consolidated Project Report & Export UI (PDF & CSV)."""

import streamlit as st
import pandas as pd

from core.advisor import evaluate_models
from core.cocomo import calculate_cocomo
from core.function_points import calculate_function_points
from core.risk import analyze_risk_register
from core.business_case import evaluate_business_case
from core.quality import evaluate_quality_scorecard, ALL_FACTORS
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
    # 1. Advisor
    advisor_res = evaluate_models(active)

    # 2. COCOMO
    kloc_val = float(active.get("kloc", 25.0))
    mode_val = active.get("cocomo_mode", "organic")
    cocomo_res = calculate_cocomo(kloc_val, mode_val)

    # 3. FP
    fp_comps = active.get("fp_components") or {
        "EI": {"low": 10, "average": 15, "high": 5},
        "EO": {"low": 8, "average": 12, "high": 4},
        "EQ": {"low": 10, "average": 15, "high": 4},
        "ILF": {"low": 4, "average": 8, "high": 3},
        "EIF": {"low": 2, "average": 4, "high": 2},
    }
    gsc_rats = active.get("gsc_ratings") or [3] * 14
    fp_res = calculate_function_points(fp_comps, gsc_rats)

    # 4. Risk
    risk_summary = analyze_risk_register(active.get("risks", []))

    # 5. Business Case
    bc_data = active.get("business_case") or {
        "initial_investment": float(active.get("budget", 60000.0)),
        "annual_benefits": [30000.0, 45000.0, 55000.0, 65000.0, 75000.0],
        "annual_costs": [8000.0, 9000.0, 10000.0, 10000.0, 11000.0],
        "discount_rate_pct": 10.0,
    }
    biz_res = evaluate_business_case(
        initial_investment=float(bc_data.get("initial_investment", 60000.0)),
        annual_benefits=bc_data.get("annual_benefits", [30000.0] * 5),
        annual_costs=bc_data.get("annual_costs", [8000.0] * 5),
        discount_rate_pct=float(bc_data.get("discount_rate_pct", 10.0)),
    )

    # 6. Quality
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
        st.caption(f"Ready for export & academic project evaluation for VTU 24CS51.")

    st.markdown("---")

    # Executive Summary Card
    st.markdown("### 📋 Executive Synthesis & Recommendation")
    st.info(
        f"**Project '{active.get('name')}':**\n\n"
        f"• **Recommended Lifecycle:** {advisor_res.top_model.model_name} ({advisor_res.top_model.percentage}% match)\n\n"
        f"• **Effort & Schedule:** {cocomo_res.effort_pm:.1f} Person-Months across {cocomo_res.duration_months:.1f} Months "
        f"({cocomo_res.avg_staff:.1f} avg team size) for {cocomo_res.kloc:.1f} KLOC ({fp_res.afp:.0f} Adjusted FP)\n\n"
        f"• **Risk Exposure:** ${risk_summary.total_exposure:,.0f} across {risk_summary.total_risks} logged risks\n\n"
        f"• **Economic Feasibility:** NPV = ${biz_res.npv:,.2f}, ROI = {biz_res.roi_pct:.1f}%, Payback = "
        f"{f'{biz_res.payback_period_years:.2f} yrs' if biz_res.payback_period_years else 'N/A'}\n\n"
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
        st.metric("Project NPV", f"${biz_res.npv:,.0f}", f"ROI {biz_res.roi_pct:.1f}%")

    # Section Previews
    st.markdown("#### 1. Lifecycle Scoring Breakdown")
    df_models = pd.DataFrame([
        {"Rank": f"#{m.rank}", "Model": m.model_name, "Fit (%)": f"{m.percentage}%", "Score": m.score}
        for m in advisor_res.ranked_models
    ])
    st.dataframe(df_models, use_container_width=True, hide_index=True)

    st.markdown("#### 2. Key Risks Requiring Active Monitoring")
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

    st.markdown("#### 3. McCall Quality Pillars")
    q_data = [
        {"Pillar": cat, "Score": f"{c_res.average_score:.2f} / 5.0", "Compliance": f"{c_res.percentage:.1f}%"}
        for cat, c_res in qual_res.categories.items()
    ]
    st.dataframe(pd.DataFrame(q_data), use_container_width=True, hide_index=True)

