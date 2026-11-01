"""McCall's Quality Scorecard UI & Polar Radar Analysis."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.quality import (
    evaluate_quality_scorecard,
    MCCALL_TAXONOMY,
    ALL_FACTORS,
)
from ui.theme import render_page_header, render_kpi_card, render_empty_state_html, apply_plotly_theme
from db.database import DatabaseManager


def render_quality_scorecard_page():
    render_page_header(
        title="McCall's Software Quality Assurance Scorecard",
        subtitle="Holistic quality governance evaluating Product Operation, Revision, and Transition pillars.",
        module_tag="VTU 24CS51: Module 5",
        co_tag="CO5: Formulate SQA Strategies Using McCall's Factor Taxonomy",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.markdown(
            render_empty_state_html(
                icon="🎯",
                title="No Active Project Selected",
                description="Please select or configure a project benchmark in 'Project Setup' to view McCall quality assurance scores.",
            ),
            unsafe_allow_html=True,
        )
        return

    db: DatabaseManager = st.session_state.db
    saved_scores = active.get("quality_scores") or {f: 3.8 for f in ALL_FACTORS}

    # Layout: Form for inputs & Radar Chart display
    col_inputs, col_chart = st.columns([1.2, 1.0])

    user_ratings = {}

    with col_inputs:
        st.markdown("### 📝 Factor Compliance Checklist (Rating 1 to 5)")
        st.caption("1 = Deficient / Critical Risk, 3 = Baseline Compliance, 5 = Exemplary / Industry Standard")

        for cat_name, factors in MCCALL_TAXONOMY.items():
            with st.expander(f"📁 {cat_name} Factors", expanded=(cat_name == "Product Operation")):
                for factor, desc in factors.items():
                    curr_val = float(saved_scores.get(factor, 3.8))
                    user_ratings[factor] = st.slider(
                        f"**{factor}**",
                        min_value=1.0,
                        max_value=5.0,
                        value=curr_val,
                        step=0.1,
                        help=desc,
                        key=f"qual_{factor}",
                    )

    # Evaluate Scorecard
    res = evaluate_quality_scorecard(user_ratings)

    with col_chart:
        st.markdown("### 🕸️ Quality Posture Radar Chart")

        categories = list(res.factor_scores.keys())
        values = list(res.factor_scores.values())
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]

        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(37, 99, 235, 0.22)",
            line=dict(color="#2563EB", width=2.5),
            name="Achieved Rating",
        ))

        baseline_closed = [4.0] * len(categories_closed)
        fig_radar.add_trace(go.Scatterpolar(
            r=baseline_closed,
            theta=categories_closed,
            line=dict(color="#10B981", width=1.5, dash="dot"),
            name="Industry Benchmark (4.0)",
        ))

        fig_radar = apply_plotly_theme(fig_radar, title="McCall Factor Distribution", height=390, show_legend=True)
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5.0], tickvals=[1, 2, 3, 4, 5], gridcolor="rgba(148, 163, 184, 0.2)"),
                angularaxis=dict(gridcolor="rgba(148, 163, 184, 0.2)"),
                bgcolor="rgba(0,0,0,0)",
            ),
            legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Scorecard Metrics
    m_cols = st.columns(4)
    with m_cols[0]:
        st.markdown(
            render_kpi_card(
                label="McCall Quality Index",
                value=f"{res.overall_index:.2f} / 5.0",
                subtitle=f"{res.overall_percentage:.1f}% Overall Compliance",
                icon="🎯",
                accent_color="#2563EB",
            ),
            unsafe_allow_html=True,
        )
    with m_cols[1]:
        op_avg = res.categories["Product Operation"].average_score
        st.markdown(
            render_kpi_card(
                label="Product Operation",
                value=f"{op_avg:.2f} / 5.0",
                subtitle="Reliability, Integrity, Usability",
                icon="⚙️",
                accent_color="#0D9488",
            ),
            unsafe_allow_html=True,
        )
    with m_cols[2]:
        rev_avg = res.categories["Product Revision"].average_score
        st.markdown(
            render_kpi_card(
                label="Product Revision",
                value=f"{rev_avg:.2f} / 5.0",
                subtitle="Maintainability, Testability",
                icon="🔧",
                accent_color="#10B981",
            ),
            unsafe_allow_html=True,
        )
    with m_cols[3]:
        tra_avg = res.categories["Product Transition"].average_score
        st.markdown(
            render_kpi_card(
                label="Product Transition",
                value=f"{tra_avg:.2f} / 5.0",
                subtitle="Portability, Interoperability",
                icon="🚀",
                accent_color="#8B5CF6",
            ),
            unsafe_allow_html=True,
        )

    # Category Pillar Cards with Progress Bars & Status Pills
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🏛️ Three McCall Quality Pillars")
    c_pcols = st.columns(3)
    for idx, (c_name, c_info) in enumerate(res.categories.items()):
        with c_pcols[idx]:
            score = c_info.average_score
            verdict = "Strong" if score >= 4.0 else ("Adequate" if score >= 3.0 else "Needs Work")
            pill_color = "#10B981" if verdict == "Strong" else ("#F59E0B" if verdict == "Adequate" else "#EF4444")
            pct = c_info.percentage

            st.markdown(
                f"""
                <div class="pc-card" style="padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 700; font-size: 0.95rem; color: var(--pc-text-main);">{c_name}</span>
                        <span style="background: rgba(0,0,0,0.06); color: {pill_color}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                            {verdict}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px;">
                        <span style="color: var(--pc-text-muted);">Pillar Score</span>
                        <span style="font-weight: 800; color: var(--pc-text-main);">{score:.2f} / 5.0 ({pct:.1f}%)</span>
                    </div>
                    <div style="background: var(--pc-border); border-radius: 9999px; height: 6px; overflow: hidden; margin-bottom: 10px;">
                        <div style="background: {pill_color}; height: 100%; width: {pct}%;"></div>
                    </div>
                    <div style="font-size: 0.78rem; color: var(--pc-text-muted); line-height: 1.4;">
                        Factors: {", ".join(c_info.factors.keys())}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="pc-card" style="border-left: 4px solid var(--pc-primary, #2563EB); padding: 14px; margin: 10px 0;">
            <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: var(--pc-text-muted);">SQA Audit Verdict</div>
            <div style="font-size: 0.95rem; font-weight: 600; color: var(--pc-text-main); margin-top: 2px;">{res.sqa_verdict}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_str, col_weak = st.columns(2)
    with col_str:
        st.markdown("#### ✅ Demonstrated Strengths")
        if res.strengths:
            for s in res.strengths:
                st.markdown(f"- **{s}**")
        else:
            st.write("No factors rated at or above 4.5 currently.")

    with col_weak:
        st.markdown("#### ⚠️ High Priority SQA Remediation Areas")
        if res.areas_for_improvement:
            for w in res.areas_for_improvement:
                st.markdown(f"- **{w}**")
        else:
            st.write("All quality factors meet or exceed acceptable baseline (≥ 2.6).")

    if st.button("💾 Persist Quality Audit to Active Project", type="primary"):
        active["quality_scores"] = user_ratings
        db.save_complete_project(active)
        st.success("McCall Quality scores saved to SQLite database!")
