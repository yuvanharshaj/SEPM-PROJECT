"""Process Model Advisor UI with Interactive Weights & Plain-English Justifications."""

import streamlit as st
import pandas as pd
import plotly.express as px

from core.advisor import evaluate_models, DEFAULT_CRITERIA_WEIGHTS, CRITERIA_KEYS, MODELS
from ui.components import render_page_header


def render_model_advisor_page():
    render_page_header(
        title="Software Process Model Advisor",
        subtitle="Multi-criteria weighted decision support evaluating Waterfall, Incremental, Spiral, Scrum, XP, and Unified Process.",
        module_tag="VTU 24CS51: Module 1 (Software Process Structure)",
        co_tag="CO1: Evaluate & Select Appropriate Software Process Lifecycles",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.warning("Please select or initialize a project in 'Project Setup' first.")
        return

    # Editable weights section in an expander
    with st.expander("⚙️ Customize Evaluation Criteria Importance Weights", expanded=False):
        st.info("Adjust the relative importance multiplier (1.0 = standard, 3.0 = critical priority) for each dimension.")
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

    # Top recommendation showcase
    st.markdown("### 🏆 Recommended Process Lifecycle")
    st.success(
        f"**Primary Recommendation: {top_model.model_name} ({top_model.percentage}% Compatibility Match)**\n\n"
        f"{top_model.justification}"
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
            title=f"Suitability Distribution for '{active.get('name')}'",
        )
        fig.update_layout(
            yaxis={"autorange": "reversed"},
            xaxis={"range": [0, 100]},
            margin=dict(l=20, r=20, t=40, b=20),
            height=340,
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_rank:
        st.markdown("#### 📋 Score Leaderboard")
        st.dataframe(
            df_models[["Rank", "Model", "Match (%)", "Raw Score"]],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(result.executive_summary)

    # Detailed Justifications & Why Alternatives Scored Lower
    st.markdown("---")
    st.markdown("### 🔍 Comparative Trade-Off Analysis & Justifications")
    st.markdown(
        "A rigorous engineering evaluation requires explaining **not only why the winner won**, "
        "but also the concrete technical and organizational reasons **why the other lifecycles fell short**."
    )

    for m in result.ranked_models:
        with st.expander(f"Rank #{m.rank}: {m.model_name} — {m.percentage}% Suitability", expanded=(m.rank <= 2)):
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

