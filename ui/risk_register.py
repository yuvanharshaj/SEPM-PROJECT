"""Risk register and quantitative exposure analysis."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.risk import analyze_risk_register, RISK_CATEGORIES
from ui.components import render_page_header
from ui.theme import apply_plotly_theme
from ui.format import format_currency, get_currency_symbol
from db.database import DatabaseManager


def render_risk_register_page():
    render_page_header(
        title="Risk register",
        caption="Identify, quantify, and prioritize risks using Risk Exposure (RE = P x I).",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.info("No active project loaded. Configure a project in Setup.")
        return

    db: DatabaseManager = st.session_state.db
    current_risks = active.get("risks", [])
    sym = get_currency_symbol()
    summary = analyze_risk_register(current_risks)

    crit_count = sum(1 for r in summary.ranked_risks if r.severity_level == "Critical")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        with st.container(border=True):
            st.metric("Total risks", f"{summary.total_risks}")
    with k2:
        with st.container(border=True):
            st.metric("Total exposure", format_currency(summary.total_exposure, compact=True))
    with k3:
        with st.container(border=True):
            st.metric("Max exposure", format_currency(summary.max_single_exposure, compact=True))
    with k4:
        with st.container(border=True):
            st.metric("Critical risks", f"{crit_count}")

    tab_table, tab_matrix = st.tabs(["Prioritized register", "Risk matrix"])

    with tab_table:
        if not summary.ranked_risks:
            st.info("No risks currently logged for this project.")
        else:
            df_risks = pd.DataFrame([
                {
                    "Rank": f"#{r.rank}",
                    "ID": r.id,
                    "Category": r.category,
                    "Description": r.description,
                    "Probability": f"{r.probability:.2f}",
                    f"Impact ({sym})": format_currency(r.impact_cost, compact=False, precision=0),
                    f"Exposure ({sym})": format_currency(r.exposure, compact=False, precision=0),
                    "Severity": r.severity_level,
                    "Mitigation": r.mitigation,
                }
                for r in summary.ranked_risks
            ])
            st.dataframe(df_risks, use_container_width=True, hide_index=True)

            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                risk_id_map = {r.id: f"{r.id}: {r.description}" for r in summary.ranked_risks}
                risk_to_remove = st.selectbox(
                    "Delete risk",
                    options=list(risk_id_map.keys()),
                    format_func=lambda x: risk_id_map.get(x, x),
                    label_visibility="collapsed",
                )
            with del_col2:
                if st.button("Delete risk"):
                    active["risks"] = [r for r in current_risks if r.get("id") != risk_to_remove]
                    db.save_complete_project(active)
                    st.rerun()

    with tab_matrix:
        if summary.ranked_risks:
            df_scatter = pd.DataFrame([
                {
                    "ID": r.id,
                    "Description": r.description,
                    "Probability": r.probability,
                    "Impact": r.impact_cost,
                    "Exposure": r.exposure,
                    "Severity": r.severity_level,
                }
                for r in summary.ranked_risks
            ])

            fig_scatter = px.scatter(
                df_scatter,
                x="Probability",
                y="Impact",
                size="Exposure",
                color="Severity",
                text="ID",
                hover_data=["Description", "Exposure"],
                color_discrete_map={
                    "Low": "#64748b",
                    "Medium": "#94a3b8",
                    "High": "#d97706",
                    "Critical": "#dc2626",
                },
            )
            fig_scatter.update_traces(textposition="top center")
            fig_scatter = apply_plotly_theme(fig_scatter, height=340)
            fig_scatter.update_xaxes(range=[0, 1.05], title_text="Probability (0.0 to 1.0)")
            fig_scatter.update_yaxes(title_text=f"Impact cost ({sym})")
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

        st.markdown("## Likelihood and consequence grid")
        grid_data = summary.matrix_grid
        z_matrix = [
            [grid_data["High"]["Low"], grid_data["High"]["Medium"], grid_data["High"]["High"]],
            [grid_data["Medium"]["Low"], grid_data["Medium"]["Medium"], grid_data["Medium"]["High"]],
            [grid_data["Low"]["Low"], grid_data["Low"]["Medium"], grid_data["Low"]["High"]],
        ]
        fig_heat = go.Figure(data=go.Heatmap(
            z=z_matrix,
            x=["Low", "Medium", "High"],
            y=["High", "Medium", "Low"],
            colorscale=[[0, "#f8fafc"], [1, "#1d4ed8"]],
            text=[[f"{val} risks" for val in row] for row in z_matrix],
            texttemplate="%{text}",
            textfont={"size": 12},
            showscale=False,
        ))
        fig_heat = apply_plotly_theme(fig_heat, height=260)
        fig_heat.update_xaxes(title_text="Consequence")
        fig_heat.update_yaxes(title_text="Likelihood")
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

    with st.expander("Register new risk"):
        with st.form("add_risk_form"):
            c1, c2 = st.columns([1, 2])
            with c1:
                r_code = st.text_input("Risk ID", value=f"R-{len(current_risks)+1:02d}")
                r_cat = st.selectbox("Category", options=RISK_CATEGORIES)
            with c2:
                r_desc = st.text_input("Description *")

            c3, c4, c5 = st.columns([1, 1, 2])
            with c3:
                r_prob = st.slider("Probability", min_value=0.05, max_value=0.95, value=0.35, step=0.05)
            with c4:
                r_imp = st.number_input(f"Impact ({sym})", min_value=100.0, value=1000000.0, step=100000.0)
            with c5:
                r_mit = st.text_input("Mitigation plan")

            if st.form_submit_button("Add risk", type="primary"):
                if r_desc.strip():
                    new_risk_entry = {
                        "id": r_code.strip(),
                        "category": r_cat,
                        "description": r_desc.strip(),
                        "probability": float(r_prob),
                        "impact_cost": float(r_imp),
                        "mitigation": r_mit.strip() or "Standard monitoring",
                    }
                    current_risks.append(new_risk_entry)
                    active["risks"] = current_risks
                    db.save_complete_project(active)
                    st.rerun()
                else:
                    st.error("Description is required.")
