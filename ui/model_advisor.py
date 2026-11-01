"""Process model advisor and lifecycle evaluation."""

import streamlit as st
import pandas as pd
import plotly.express as px

from core.advisor import evaluate_models, DEFAULT_CRITERIA_WEIGHTS, CRITERIA_KEYS
from ui.components import render_page_header
from ui.theme import apply_plotly_theme


def render_model_advisor_page():
    render_page_header(
        title="Process model advisor",
        caption="Multi-criteria weighted evaluation across predictive, iterative, and agile lifecycles.",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.info("No active project loaded. Configure a project in Setup.")
        return

    # Secondary material in an expander
    with st.expander("Evaluation criteria weights"):
        st.caption("Adjust relative weights from 0.5 (low influence) to 4.0 (critical factor).")
        w_cols = st.columns(4)
        custom_weights = {}
        for idx, crit in enumerate(CRITERIA_KEYS):
            col = w_cols[idx % 4]
            name = crit.replace("_", " ").capitalize()
            default_val = float(DEFAULT_CRITERIA_WEIGHTS.get(crit, 2.0))
            custom_weights[crit] = col.slider(
                name,
                min_value=0.5,
                max_value=4.0,
                value=default_val,
                step=0.5,
                key=f"weight_{crit}",
            )

    result = evaluate_models(active, custom_weights=custom_weights)
    top_model = result.top_model

    # 3 Metrics in simple bordered containers
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        with st.container(border=True):
            st.metric("Top recommendation", top_model.model_name)
    with m_col2:
        with st.container(border=True):
            st.metric("Compatibility match", f"{top_model.percentage}%")
    with m_col3:
        with st.container(border=True):
            st.metric("Models evaluated", len(result.ranked_models))

    st.markdown("## Lifecycle ranking")
    df_models = pd.DataFrame([
        {
            "Rank": f"#{m.rank}",
            "Model": m.model_name,
            "Match (%)": m.percentage,
            "Raw score": m.score,
            "Suitability": "Recommended" if m.rank == 1 else "Alternative",
        }
        for m in result.ranked_models
    ])

    col_chart, col_tbl = st.columns([1.2, 1.0])
    with col_chart:
        fig = px.bar(
            df_models,
            x="Match (%)",
            y="Model",
            orientation="h",
            color="Match (%)",
            color_continuous_scale=["#94a3b8", "#1d4ed8"],
            text="Match (%)",
        )
        fig.update_layout(
            yaxis={"autorange": "reversed", "title": ""},
            xaxis={"range": [0, 105], "title": "Match percentage"},
            coloraxis_showscale=False,
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig = apply_plotly_theme(fig, height=320)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

    with col_tbl:
        st.dataframe(
            df_models[["Rank", "Model", "Match (%)", "Raw score", "Suitability"]],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(result.executive_summary)

    # Rationale and trade-offs in secondary expanders
    st.markdown("## Comparative analysis")
    for m in result.ranked_models:
        with st.expander(f"Rank {m.rank}: {m.model_name} ({m.percentage}%)", expanded=(m.rank == 1)):
            st.write(m.justification)
            if m.strengths:
                st.markdown("**Aligned characteristics:**")
                for s in m.strengths:
                    st.markdown(f"- {s}")
            if m.drawbacks:
                st.markdown("**Friction points:**")
                for d in m.drawbacks:
                    st.markdown(f"- {d}")
