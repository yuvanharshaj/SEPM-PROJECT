"""Risk Register, Exposure Analysis & Heat Map UI."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.risk import (
    analyze_risk_register,
    RISK_CATEGORIES,
    RiskItem,
)
from ui.components import render_page_header
from db.database import DatabaseManager


def render_risk_register_page():
    render_page_header(
        title="Software Risk Register & Exposure Analysis",
        subtitle="Identify, quantify, and prioritize project risks using Risk Exposure (RE = P x I) and RMMM strategies.",
        module_tag="VTU 24CS51: Module 4 (Risk Management & RMMM)",
        co_tag="CO4: Assess Project Risks, Exposure and Formulate Mitigation Strategies",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.warning("Please select or initialize a project in 'Project Setup' first.")
        return

    db: DatabaseManager = st.session_state.db
    current_risks = active.get("risks", [])

    # Process risks
    summary = analyze_risk_register(current_risks)

    # Top KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Identified Risks", summary.total_risks)
    with k2:
        st.metric("Total Risk Exposure (Cost)", f"${summary.total_exposure:,.0f}")
    with k3:
        st.metric("Max Single Risk Exposure", f"${summary.max_single_exposure:,.0f}")
    with k4:
        crit_count = sum(1 for r in summary.ranked_risks if r.severity_level == "Critical")
        st.metric("Critical Risks", crit_count)

    st.markdown("---")

    # Add New Risk Form
    with st.expander("➕ Register a New Project Risk", expanded=False):
        with st.form("add_risk_form"):
            c_r1, c_r2 = st.columns([1, 2])
            with c_r1:
                r_code = st.text_input("Risk Identifier", value=f"R-{len(current_risks)+1:02d}")
                r_cat = st.selectbox("Risk Category", options=RISK_CATEGORIES)
            with c_r2:
                r_desc = st.text_input("Risk Description *", placeholder="e.g. Memory leak in high-throughput network daemon")

            c_r3, c_r4, c_r5 = st.columns([1, 1, 2])
            with c_r3:
                r_prob = st.slider("Probability (P)", min_value=0.05, max_value=0.95, value=0.35, step=0.05)
            with c_r4:
                r_imp = st.number_input("Impact Cost ($ / ₹)", min_value=100.0, value=25000.0, step=5000.0)
            with c_r5:
                r_mit = st.text_input("Mitigation / RMMM Action Plan", placeholder="e.g. Profile heap weekly using Valgrind")

            add_submitted = st.form_submit_button("Add Risk to Register", type="primary")
            if add_submitted:
                if not r_desc.strip():
                    st.error("Please provide a description of the risk.")
                else:
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
                    st.success(f"Risk '{r_code}' recorded!")
                    st.rerun()

    # Risk Table & Heat Map Views
    tab_list, tab_matrix = st.tabs(["📋 Prioritized Risk Register (By Exposure)", "🔥 Risk Matrix & Exposure Heatmap"])

    with tab_list:
        if not summary.ranked_risks:
            st.info("No risks currently logged for this project.")
        else:
            df_risks = pd.DataFrame([r.to_dict() for r in summary.ranked_risks])
            df_display = df_risks.rename(columns={
                "rank": "Rank",
                "id": "Risk ID",
                "category": "Category",
                "description": "Description",
                "probability": "Prob (P)",
                "impact_cost": "Impact ($)",
                "exposure": "Exposure (P x I)",
                "severity_level": "Severity",
                "mitigation": "Mitigation Plan (RMMM)",
            })

            st.dataframe(
                df_display[["Rank", "Risk ID", "Category", "Description", "Prob (P)", "Impact ($)", "Exposure (P x I)", "Severity", "Mitigation Plan (RMMM)"]],
                use_container_width=True,
                hide_index=True,
            )

            # Option to delete a selected risk
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                risk_to_remove = st.selectbox(
                    "Select a risk to delete:",
                    options=[r.id for r in summary.ranked_risks],
                    format_func=lambda x: f"{x}: next(r.description for r in summary.ranked_risks if r.id == x)",
                )
            with del_col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete Selected Risk", use_container_width=True):
                    active["risks"] = [r for r in current_risks if r.get("id") != risk_to_remove]
                    db.save_complete_project(active)
                    st.warning(f"Risk {risk_to_remove} deleted.")
                    st.rerun()

    with tab_matrix:
        st.markdown("#### 🎯 2D Risk Projection Matrix (Probability vs Impact)")

        if summary.ranked_risks:
            df_scatter = pd.DataFrame([
                {
                    "Risk ID": r.id,
                    "Description": r.description,
                    "Probability": r.probability,
                    "Impact": r.impact_cost,
                    "Exposure": r.exposure,
                    "Category": r.category,
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
                text="Risk ID",
                hover_data=["Description", "Category", "Exposure"],
                color_discrete_map={
                    "Low": "#4CAF50",
                    "Medium": "#FFB300",
                    "High": "#FB8C00",
                    "Critical": "#E53935",
                },
                title="Risk Table Projection (Bubble Size = Risk Exposure)",
            )
            fig_scatter.update_traces(textposition="top center")
            fig_scatter.update_layout(
                xaxis=dict(range=[0, 1.05], title="Probability (0.0 to 1.0)"),
                yaxis=dict(title="Impact Cost ($)"),
                height=420,
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # 3x3 Heat Map Grid Breakdown
        st.markdown("#### 🧩 3x3 Likelihood vs Consequence Grid")
        grid_data = summary.matrix_grid
        z_matrix = [
            [grid_data["High"]["Low"], grid_data["High"]["Medium"], grid_data["High"]["High"]],
            [grid_data["Medium"]["Low"], grid_data["Medium"]["Medium"], grid_data["Medium"]["High"]],
            [grid_data["Low"]["Low"], grid_data["Low"]["Medium"], grid_data["Low"]["High"]],
        ]

        fig_heat = go.Figure(data=go.Heatmap(
            z=z_matrix,
            x=["Low Consequence", "Medium Consequence", "High Consequence"],
            y=["High Likelihood", "Medium Likelihood", "Low Likelihood"],
            colorscale="YlOrRd",
            text=[[f"{val} Risks" for val in row] for row in z_matrix],
            texttemplate="%{text}",
            textfont={"size": 14},
        ))
        fig_heat.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)
