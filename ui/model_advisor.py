"""Process Model Advisor UI with Interactive Weights & Plain-English Justifications."""

import streamlit as st
import pandas as pd
import plotly.express as px

from core.advisor import evaluate_models, DEFAULT_CRITERIA_WEIGHTS, CRITERIA_KEYS
from ui.theme import render_page_header, render_empty_state_html, apply_plotly_theme


def render_model_advisor_page():
    render_page_header(
        title="Software Process Model Advisor",
        subtitle="Multi-criteria weighted decision engine evaluating Waterfall, Incremental, Spiral, Scrum, XP, and Unified Process.",
        module_tag="VTU 24CS51: Module 1",
        co_tag="CO1: Formulate & Select Process Lifecycles",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.markdown(
            render_empty_state_html(
                icon="🧭",
                title="No Active Project Selected",
                description="Please select or configure a project benchmark in 'Project Setup' to view lifecycle recommendations.",
            ),
            unsafe_allow_html=True,
        )
        return

    # Editable weights section in an expander
    with st.expander("⚙️ Customize Multi-Criteria Importance Weights (VTU Scoring Matrix)", expanded=False):
        st.markdown(
            "<div style='font-size: 0.86rem; color: var(--pc-text-muted); margin-bottom: 8px;'>"
            "Tune criteria weights (0.5 = low influence, 4.0 = critical governing factor) to tailor the algorithmic scoring model."
            "</div>",
            unsafe_allow_html=True,
        )
        w_cols = st.columns(4)
        custom_weights = {}

        for idx, crit in enumerate(CRITERIA_KEYS):
            col = w_cols[idx % 4]
            readable_name = crit.replace("_", " ").title()
            default_val = float(DEFAULT_CRITERIA_WEIGHTS.get(crit, 2.0))
            custom_weights[crit] = col.slider(
                readable_name,
                min_value=0.5,
                max_value=4.0,
                value=default_val,
                step=0.5,
                key=f"weight_{crit}",
            )

    # Evaluate models
    result = evaluate_models(active, custom_weights=custom_weights)
    top_model = result.top_model

    # Top recommendation showcase - modern card with "Best Fit" badge
    st.markdown(
        f"""
        <div class="pc-card" style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(13, 148, 136, 0.06)); border: 1px solid rgba(37, 99, 235, 0.25); margin: 16px 0 22px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.5rem;">🏆</span>
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; color: var(--pc-primary-dark, #1E40AF);">Top Recommendation</div>
                        <div style="font-size: 1.45rem; font-weight: 800; color: var(--pc-text-main, #0F172A);">{top_model.model_name}</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: linear-gradient(135deg, #2563EB, #1E40AF); color: #FFFFFF; font-weight: 800; font-size: 0.95rem; padding: 6px 14px; border-radius: 9999px; box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);">
                        ★ {top_model.percentage}% Compatibility Match
                    </span>
                </div>
            </div>
            <p style="margin: 8px 0 0 0; font-size: 0.94rem; color: var(--pc-text-main, #0F172A); line-height: 1.55;">
                {top_model.justification}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Visualizations & Comparison
    col_chart, col_rank = st.columns([1.3, 1.0])

    with col_chart:
        st.markdown("#### 📊 Model Alignment Ranking")
        df_models = pd.DataFrame([
            {
                "Model": m.model_name,
                "Match (%)": m.percentage,
                "Raw Score": m.score,
                "Rank": f"#{m.rank}",
            }
            for m in result.ranked_models
        ])

        fig = px.bar(
            df_models,
            x="Match (%)",
            y="Model",
            orientation="h",
            color="Match (%)",
            color_continuous_scale="Blues",
            text="Match (%)",
        )
        fig.update_layout(
            yaxis={"autorange": "reversed"},
            xaxis={"range": [0, 105]},
            height=340,
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig = apply_plotly_theme(fig, title=f"Suitability Distribution for '{active.get('name')}'", height=340, show_legend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_rank:
        st.markdown("#### 📋 Score Leaderboard")
        st.dataframe(
            df_models[["Rank", "Model", "Match (%)", "Raw Score"]],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown(
            f"""
            <div style="background: var(--pc-card-subtle, #F1F5F9); border-radius: 8px; padding: 10px 12px; border: 1px solid var(--pc-border, #E2E8F0); font-size: 0.8rem; color: var(--pc-text-muted, #64748B); line-height: 1.45; margin-top: 8px;">
                <b>Executive Summary:</b> {result.executive_summary}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Detailed Justifications & Why Alternatives Scored Lower
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔍 Comparative Trade-Off Analysis & Justifications")
    st.markdown(
        "<div style='font-size: 0.9rem; color: var(--pc-text-muted); margin-bottom: 12px;'>"
        "Engineering decision-support demands understanding <b>not only why the winner was chosen</b>, "
        "but the specific structural bottlenecks and risk factors <b>why alternative lifecycles scored lower</b>."
        "</div>",
        unsafe_allow_html=True,
    )

    for m in result.ranked_models:
        with st.expander(f"Rank #{m.rank}: {m.model_name} — {m.percentage}% Match", expanded=(m.rank <= 2)):
            c_just, c_det = st.columns([2, 1])
            with c_just:
                st.write(m.justification)
            with c_det:
                if m.strengths:
                    st.markdown("**Aligned Drivers:**")
                    for s in m.strengths:
                        st.markdown(f"- ✅ {s}")
                if m.drawbacks:
                    st.markdown("**Friction Points:**")
                    for d in m.drawbacks:
                        st.markdown(f"- ⚠️ {d}")
