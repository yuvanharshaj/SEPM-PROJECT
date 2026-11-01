"""Risk Register, Exposure Analysis & Heat Map UI."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.risk import (
    analyze_risk_register,
    RISK_CATEGORIES,
)
from ui.theme import render_page_header, render_kpi_card, render_empty_state_html, apply_plotly_theme
from ui.format import format_currency, get_currency_symbol
from db.database import DatabaseManager


def render_risk_register_page():
    render_page_header(
        title="Software Risk Register & Exposure Analysis",
        subtitle="Identify, quantify, and prioritize project risks using Risk Exposure (RE = P x I) and RMMM strategies.",
        module_tag="VTU 24CS51: Module 4",
        co_tag="CO4: Assess Project Risks, Exposure & Formulate RMMM Plans",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.markdown(
            render_empty_state_html(
                icon="⚠️",
                title="No Active Project Selected",
                description="Please select or configure a project benchmark in 'Project Setup' to view or record risks.",
            ),
            unsafe_allow_html=True,
        )
        return

    db: DatabaseManager = st.session_state.db
    current_risks = active.get("risks", [])
    sym = get_currency_symbol()

    # Process risks
    summary = analyze_risk_register(current_risks)

    # 1. Top KPI Cards
    crit_count = sum(1 for r in summary.ranked_risks if r.severity_level == "Critical")
    k_cols = st.columns(4)
    with k_cols[0]:
        st.markdown(
            render_kpi_card(
                label="Identified Risks",
                value=f"{summary.total_risks} Risks",
                subtitle="Active Risk Log",
                icon="📋",
                accent_color="#2563EB",
            ),
            unsafe_allow_html=True,
        )
    with k_cols[1]:
        st.markdown(
            render_kpi_card(
                label="Total Exposure (P x I)",
                value=format_currency(summary.total_exposure, compact=True),
                subtitle=format_currency(summary.total_exposure, compact=False, precision=0),
                icon="💸",
                accent_color="#EF4444",
            ),
            unsafe_allow_html=True,
        )
    with k_cols[2]:
        st.markdown(
            render_kpi_card(
                label="Peak Single Exposure",
                value=format_currency(summary.max_single_exposure, compact=True),
                subtitle=format_currency(summary.max_single_exposure, compact=False, precision=0),
                icon="⚡",
                accent_color="#F59E0B",
            ),
            unsafe_allow_html=True,
        )
    with k_cols[3]:
        st.markdown(
            render_kpi_card(
                label="Critical Severity",
                value=f"{crit_count} Critical",
                subtitle="Requires Urgent CCB Review",
                icon="🚨",
                accent_color="#DC2626" if crit_count > 0 else "#10B981",
            ),
            unsafe_allow_html=True,
        )

    # 2. Top-3 Critical Risks Banner Cards
    if summary.ranked_risks:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🚨 Priority Threat Vectors (Top Exposure)")
        top_cols = st.columns(min(3, len(summary.ranked_risks)))
        for i, r in enumerate(summary.ranked_risks[:3]):
            with top_cols[i]:
                sev_color = "#DC2626" if r.severity_level == "Critical" else ("#F59E0B" if r.severity_level == "High" else "#2563EB")
                st.markdown(
                    f"""
                    <div class="pc-card" style="padding: 14px; margin-bottom: 12px; border-top: 3px solid {sev_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 800; font-size: 0.85rem; color: var(--pc-primary-dark, #1E40AF);">{r.id} &bull; Rank #{r.rank}</span>
                            <span style="font-size: 0.7rem; font-weight: 700; padding: 2px 7px; border-radius: 9999px; background: rgba(0,0,0,0.06); color: {sev_color};">{r.severity_level}</span>
                        </div>
                        <div style="font-weight: 700; font-size: 0.88rem; color: var(--pc-text-main, #0F172A); margin-bottom: 6px; min-height: 38px; line-height: 1.35;">
                            {r.description}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--pc-text-muted, #64748B); border-top: 1px solid var(--pc-border, #E2E8F0); padding-top: 6px; margin-top: 4px;">
                            <span>P: <b>{r.probability:.2f}</b></span>
                            <span>Imp: <b>{format_currency(r.impact_cost, compact=True)}</b></span>
                            <span>Exp: <b style="color: {sev_color};">{format_currency(r.exposure, compact=True)}</b></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 3. Add New Risk Expander
    with st.expander("➕ Register a New Project Risk to RMMM Plan", expanded=False):
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
                r_imp = st.number_input(f"Impact Cost ({sym})", min_value=100.0, value=1000000.0, step=100000.0)
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
                    st.success(f"Risk '{r_code}' recorded successfully!")
                    st.rerun()

    # 4. Risk Table & Heat Map Views
    tab_list, tab_matrix = st.tabs(["📋 Prioritized Risk Register (By Exposure)", "🔥 Risk Matrix & Exposure Heatmap"])

    with tab_list:
        if not summary.ranked_risks:
            st.info("No risks currently logged for this project.")
        else:
            df_risks = pd.DataFrame([
                {
                    "Rank": f"#{r.rank}",
                    "Risk ID": r.id,
                    "Category": r.category,
                    "Description": r.description,
                    "Prob (P)": f"{r.probability:.2f}",
                    f"Impact ({sym})": format_currency(r.impact_cost, compact=False, precision=0),
                    f"Exposure ({sym})": format_currency(r.exposure, compact=False, precision=0),
                    "Severity": r.severity_level,
                    "Mitigation Plan (RMMM)": r.mitigation,
                }
                for r in summary.ranked_risks
            ])

            st.dataframe(df_risks, use_container_width=True, hide_index=True)

            # Option to delete a selected risk
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                risk_id_map = {r.id: f"{r.id}: {r.description}" for r in summary.ranked_risks}
                risk_to_remove = st.selectbox(
                    "Select a risk to delete:",
                    options=list(risk_id_map.keys()),
                    format_func=lambda x: risk_id_map.get(x, x),
                )
            with del_col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete Selected Risk", use_container_width=True):
                    active["risks"] = [r for r in current_risks if r.get("id") != risk_to_remove]
                    db.save_complete_project(active)
                    st.warning(f"Risk {risk_to_remove} deleted from register.")
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
                    "Low": "#10B981",
                    "Medium": "#F59E0B",
                    "High": "#FB8C00",
                    "Critical": "#EF4444",
                },
            )
            fig_scatter.update_traces(textposition="top center")
            fig_scatter = apply_plotly_theme(
                fig_scatter,
                title="Risk Exposure Distribution (Bubble Size = Exposure)",
                height=420,
            )
            fig_scatter.update_xaxes(range=[0, 1.05], title_text="Probability (0.0 to 1.0)")
            fig_scatter.update_yaxes(title_text=f"Impact Cost ({sym})")
            st.plotly_chart(fig_scatter, use_container_width=True)

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
            textfont={"size": 13, "family": "'Plus Jakarta Sans', sans-serif"},
        ))
        fig_heat = apply_plotly_theme(fig_heat, title="Risk Concentration Grid", height=290, show_legend=False)
        st.plotly_chart(fig_heat, use_container_width=True)
