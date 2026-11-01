"""McCall software quality scorecard and polar radar analysis."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.quality import (
    evaluate_quality_scorecard,
    MCCALL_TAXONOMY,
    ALL_FACTORS,
)
from ui.components import render_page_header
from ui.theme import apply_plotly_theme
from db.database import DatabaseManager


def render_quality_scorecard_page():
    render_page_header(
        title="Quality scorecard",
        caption="McCall software quality model evaluation across operation, revision, and transition.",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.info("No active project loaded. Configure a project in Setup.")
        return

    db: DatabaseManager = st.session_state.db
    saved_scores = active.get("quality_scores") or {f: 3.8 for f in ALL_FACTORS}

    col_inputs, col_chart = st.columns([1.1, 1.0])
    user_ratings = {}

    with col_inputs:
        st.markdown("## Factor compliance checklist")
        st.caption("Rating scale: 1 (deficient), 3 (baseline compliance), 5 (exemplary).")

        for cat_name, factors in MCCALL_TAXONOMY.items():
            with st.expander(cat_name, expanded=(cat_name == "Product Operation")):
                for factor, desc in factors.items():
                    curr_val = float(saved_scores.get(factor, 3.8))
                    user_ratings[factor] = st.slider(
                        factor,
                        min_value=1.0,
                        max_value=5.0,
                        value=curr_val,
                        step=0.1,
                        help=desc,
                        key=f"q_{factor}",
                    )

    res = evaluate_quality_scorecard(user_ratings)

    with col_chart:
        st.markdown("## Quality profile")
        categories = list(res.factor_scores.keys())
        values = list(res.factor_scores.values())
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(29, 78, 216, 0.15)",
            line=dict(color="#1d4ed8", width=2),
            name="Achieved score",
        ))
        baseline_closed = [4.0] * len(categories_closed)
        fig_radar.add_trace(go.Scatterpolar(
            r=baseline_closed,
            theta=categories_closed,
            line=dict(color="#64748b", width=1.5, dash="dot"),
            name="Target (4.0)",
        ))

        fig_radar = apply_plotly_theme(fig_radar, height=360)
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5.0], tickvals=[1, 2, 3, 4, 5]),
                angularaxis=dict(gridcolor="rgba(148, 163, 184, 0.2)"),
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=40, r=40, t=20, b=40),
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("McCall Index (MQI)", f"{res.overall_index:.2f} / 5.0")
    with m2:
        op_avg = res.categories["Product Operation"].average_score
        with st.container(border=True):
            st.metric("Operation", f"{op_avg:.2f} / 5.0")
    with m3:
        rev_avg = res.categories["Product Revision"].average_score
        with st.container(border=True):
            st.metric("Revision", f"{rev_avg:.2f} / 5.0")
    with m4:
        tra_avg = res.categories["Product Transition"].average_score
        with st.container(border=True):
            st.metric("Transition", f"{tra_avg:.2f} / 5.0")

    st.caption(f"Audit summary: {res.sqa_verdict}")

    st.markdown("## Quality pillars")
    pillar_records = []
    for c_name, c_info in res.categories.items():
        score = c_info.average_score
        verdict = "Strong" if score >= 4.0 else ("Adequate" if score >= 3.0 else "Needs improvement")
        pillar_records.append({
            "Pillar": c_name,
            "Average score": f"{score:.2f} / 5.0",
            "Compliance (%)": f"{c_info.percentage:.1f}%",
            "Status": verdict,
            "Factors included": ", ".join(c_info.factor_scores.keys()),
        })
    st.dataframe(pd.DataFrame(pillar_records), use_container_width=True, hide_index=True)

    with st.expander("Strengths and remediation areas"):
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("**Demonstrated strengths:**")
            if res.strengths:
                for s in res.strengths:
                    st.markdown(f"- {s}")
            else:
                st.write("No factors rated above 4.5.")
        with col_w:
            st.markdown("**Remediation areas:**")
            if res.areas_for_improvement:
                for w in res.areas_for_improvement:
                    st.markdown(f"- {w}")
            else:
                st.write("All factors meet the acceptable baseline.")

    if st.button("Save quality scorecard to project", type="primary"):
        active["quality_scores"] = user_ratings
        db.save_complete_project(active)
        st.success("Quality scores saved.")
