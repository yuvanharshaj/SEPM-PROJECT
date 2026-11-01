"""Agile Lab UI: Frameworks Comparison, Sprint Planner & Cost of Change."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

from core.agile import (
    calculate_sprint_plan,
    generate_cost_of_change_data,
    AGILE_FRAMEWORKS,
)
from ui.components import render_page_header
from db.database import DatabaseManager


def render_agile_lab_page():
    render_page_header(
        title="Agile Lab & Iteration Studio",
        subtitle="Compare agile methodologies, plan release velocity, and analyze Beck's flattened cost-of-change curve.",
        module_tag="VTU 24CS51: Module 2 (Agile Development)",
        co_tag="CO2: Interpret Agile Principles and Formulate Agile Project Iterations",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.warning("Please select or initialize a project in 'Project Setup' first.")
        return

    tab_compare, tab_sprint, tab_cost = st.tabs([
        "📋 (a) Agile Frameworks Comparison",
        "🏃 (b) Sprint Capacity & Burndown Planner",
        "📉 (c) Agility & Cost of Change Analysis",
    ])

    # -----------------------------------------------------------------
    # TAB A: AGILE FRAMEWORKS COMPARISON
    # -----------------------------------------------------------------
    with tab_compare:
        st.markdown("### 🏆 Comprehensive Comparison of 7 Agile Lifecycles")
        st.caption("Detailed taxonomy covering core agile process models from VTU 24CS51 Module 2:")

        df_frameworks = pd.DataFrame(AGILE_FRAMEWORKS).rename(columns={
            "name": "Methodology",
            "focus": "Core Philosophy & Focus",
            "team_size": "Team Size",
            "iteration_style": "Iteration Cadence",
            "key_practices": "Signature Engineering Practices",
            "best_fit": "Optimal Project Profile",
        })

        st.dataframe(df_frameworks, use_container_width=True, hide_index=True)

        st.markdown("#### 🔍 Deep Dive by Methodology")
        sel_method = st.selectbox(
            "Select Methodology for Detailed Breakdown:",
            options=[f["name"] for f in AGILE_FRAMEWORKS],
            index=0,
        )
        selected_info = next(f for f in AGILE_FRAMEWORKS if f["name"] == sel_method)

        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.markdown(f"**Methodology:** `{selected_info['name']}`")
            st.markdown(f"**Primary Focus:** {selected_info['focus']}")
            st.markdown(f"**Recommended Team Size:** {selected_info['team_size']}")
            st.markdown(f"**Iteration Style:** {selected_info['iteration_style']}")
        with c_info2:
            st.markdown(f"**Signature Practices:**\n- {selected_info['key_practices'].replace(', ', '\n- ')}")
            st.markdown(f"**Best Fit Scenarios:** {selected_info['best_fit']}")

    # -----------------------------------------------------------------
    # TAB B: SPRINT PLANNER & BURNDOWN
    # -----------------------------------------------------------------
    with tab_sprint:
        st.markdown("### 🎯 Agile Sprint Capacity & Release Schedule")
        st.caption(f"Configuring sprint iterations for active project: **{active.get('name', 'N/A')}**")

        # Estimate a sensible default story point backlog from KLOC or duration if available
        nominal_kloc = float(active.get("kloc", 25.0))
        default_points = max(30.0, round(nominal_kloc * 5.0, 0))

        c_sp1, c_sp2, c_sp3, c_sp4 = st.columns(4)
        with c_sp1:
            backlog_pts = st.number_input(
                "Product Backlog (Story Points):",
                min_value=10.0,
                max_value=2000.0,
                value=float(default_points),
                step=10.0,
                help="Total estimated user story points in product backlog",
            )
        with c_sp2:
            velocity = st.number_input(
                "Team Velocity (Points / Sprint):",
                min_value=5.0,
                max_value=200.0,
                value=25.0,
                step=5.0,
                help="Historical or planned story points delivered per sprint",
            )
        with c_sp3:
            sprint_len = st.selectbox(
                "Sprint Duration:",
                options=[1, 2, 3, 4],
                index=1,
                format_func=lambda w: f"{w} Week{'s' if w > 1 else ''}",
            )
        with c_sp4:
            kickoff_date = st.date_input("Sprint 1 Kickoff Date:", value=date.today())

        sprint_plan = calculate_sprint_plan(
            backlog_points=backlog_pts,
            velocity_per_sprint=velocity,
            sprint_length_weeks=sprint_len,
            start_date=kickoff_date,
        )

        # Metric KPI cards
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Sprints Needed", f"{sprint_plan.sprints_needed} Sprints")
        with m2:
            st.metric("Delivery Duration", f"{sprint_plan.total_weeks} Weeks", f"{sprint_plan.total_calendar_days} Days")
        with m3:
            st.metric("Projected Release Date", sprint_plan.finish_date)
        with m4:
            st.metric("Burn Rate", f"{velocity:.0f} pts / {sprint_len} wk", f"Backlog: {backlog_pts:.0f} pts")

        # Interactive Burndown Chart
        st.markdown("#### 📉 Projected Release Burndown Chart")
        df_burn = pd.DataFrame(sprint_plan.burndown_schedule)

        fig_burn = go.Figure()

        # Ideal burndown
        fig_burn.add_trace(go.Scatter(
            x=df_burn["sprint"],
            y=df_burn["ideal_remaining_points"],
            mode="lines+markers",
            name="Ideal Burndown Trajectory",
            line=dict(color="#1976D2", width=3, dash="dash"),
        ))

        # Projected remaining
        fig_burn.add_trace(go.Scatter(
            x=df_burn["sprint"],
            y=df_burn["projected_remaining_points"],
            mode="lines+markers",
            name="Projected Remaining Points",
            line=dict(color="#E53935", width=3),
        ))

        # Points burned cumulative bar
        fig_burn.add_trace(go.Bar(
            x=df_burn["sprint"],
            y=df_burn["points_burned"],
            name="Cumulative Points Burned",
            marker_color="#81C784",
            opacity=0.45,
        ))

        fig_burn.update_layout(
            title=f"Release Burndown for {active.get('name')} ({sprint_plan.sprints_needed} Sprints)",
            yaxis_title="Story Points",
            xaxis_title="Sprint Iterations",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_burn, use_container_width=True)

        with st.expander("📋 Detailed Sprint Milestone Schedule"):
            st.dataframe(df_burn, use_container_width=True, hide_index=True)

    # -----------------------------------------------------------------
    # TAB C: AGILITY AND COST OF CHANGE
    # -----------------------------------------------------------------
    with tab_cost:
        st.markdown("### 📉 The Cost of Change Curve: Traditional vs Agile")
        st.markdown(
            "According to Barry Boehm's traditional engineering model, the cost to modify software grows **exponentially** "
            "as a system progresses through requirements, design, code, test, and release. "
            "Kent Beck and agile proponents demonstrated that through **Continuous Integration (CI), Test-Driven Development (TDD), "
            "pair programming, and automated regression suites**, the cost curve is drastically **flattened**."
        )

        cost_data = generate_cost_of_change_data()
        df_cost = pd.DataFrame(cost_data)

        col_c_chart, col_c_table = st.columns([1.5, 1.0])

        with col_c_chart:
            fig_cost = go.Figure()

            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Traditional (Exponential)"],
                mode="lines+markers",
                name="Traditional (Boehm Exponential)",
                line=dict(color="#D32F2F", width=3),
                marker=dict(size=8),
            ))

            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Agile (Flattened Curve)"],
                mode="lines+markers",
                name="Agile (Beck Flattened)",
                line=dict(color="#388E3C", width=3),
                marker=dict(size=8),
            ))

            fig_cost.update_layout(
                title="Relative Cost to Rectify or Alter Requirements",
                yaxis_title="Relative Cost Multiplier (Log-Scale Normalized)",
                yaxis_type="log",
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        with col_c_table:
            st.markdown("#### 📊 Phase Escalation Multipliers")
            st.dataframe(df_cost[["Lifecycle Phase", "Traditional (Exponential)", "Agile (Flattened Curve)", "Ratio (Traditional / Agile)"]], use_container_width=True, hide_index=True)
            st.info(
                "**Key Takeaway (VTU Module 2):**\n\n"
                "In traditional phased lifecycles, defects undetected until post-release can cost up to **100x** their requirements-phase cost. "
                "Agile technical rigor constrains this escalation to under **4x**."
            )
