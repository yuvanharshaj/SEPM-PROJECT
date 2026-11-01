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
from ui.components import render_page_header
from db.database import DatabaseManager


def render_quality_scorecard_page():
    render_page_header(
        title="McCall's Software Quality Scorecard",
        subtitle="Holistic quality assurance evaluation across Product Operation, Revision, and Transition factors.",
        module_tag="VTU 24CS51: Module 5 (Software Quality Assurance)",
        co_tag="CO5: Formulate SQA Strategies Using McCall's Factor Taxonomy",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.warning("Please select or initialize a project in 'Project Setup' first.")
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
                    curr_val = float(saved_scores.get(factor, 3.5))
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

        # Prepare Polar Data
        categories = list(res.factor_scores.keys())
        values = list(res.factor_scores.values())
        # Close the loop on polar chart
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]

        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            fillcolor='rgba(21, 101, 192, 0.25)',
            line=dict(color='#1565C0', width=2),
            name="Achieved Rating",
        ))

        # Add target baseline circle (at 4.0)
        baseline_closed = [4.0] * len(categories_closed)
        fig_radar.add_trace(go.Scatterpolar(
            r=baseline_closed,
            theta=categories_closed,
            line=dict(color='#2E7D32', width=1.5, dash='dot'),
            name="Industry Target (4.0)",
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5.0], tickvals=[1, 2, 3, 4, 5]),
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            height=380,
            margin=dict(l=40, r=40, t=20, b=40),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # Scorecard Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("McCall Quality Index (MQI)", f"{res.overall_index:.2f} / 5.0")
    with m2:
        op_avg = res.categories["Product Operation"].average_score
        st.metric("Operation Pillar", f"{op_avg:.2f} / 5.0")
    with m3:
        rev_avg = res.categories["Product Revision"].average_score
        st.metric("Revision Pillar", f"{rev_avg:.2f} / 5.0")
    with m4:
        tra_avg = res.categories["Product Transition"].average_score
        st.metric("Transition Pillar", f"{tra_avg:.2f} / 5.0")

    # Verdict Banner
    st.info(f"**SQA Audit Summary:** {res.sqa_verdict}")

    col_str, col_weak = st.columns(2)
    with col_str:
        st.markdown("#### ✅ Demonstrated Strengths")
        if res.strengths:
            for s in res.strengths:
                st.markdown(f"- {s}")
        else:
            st.write("No factors rated at or above 4.5 currently.")

    with col_weak:
        st.markdown("#### ⚠️ High Priority SQA Remediation Areas")
        if res.areas_for_improvement:
            for w in res.areas_for_improvement:
                st.markdown(f"- {w}")
        else:
            st.write("All quality factors meet or exceed acceptable baseline (≥ 2.6).")

    if st.button("💾 Persist Quality Audit to Active Project", type="primary"):
        active["quality_scores"] = user_ratings
        db.save_complete_project(active)
        st.success("McCall Quality scores saved to SQLite!")
