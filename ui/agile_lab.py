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
from ui.theme import render_page_header, render_kpi_card, render_empty_state_html, apply_plotly_theme
from db.database import DatabaseManager


def render_agile_lab_page():
    render_page_header(
        title="Agile Lab & Iteration Studio",
        subtitle="Compare agile methodologies, plan release velocity, and analyze Beck's flattened cost-of-change curve.",
        module_tag="VTU 24CS51: Module 2",
        co_tag="CO2: Interpret Agile Principles & Formulate Iterations",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.markdown(
            render_empty_state_html(
                icon="⚡",
                title="No Active Project Selected",
                description="Please select or configure a project benchmark in 'Project Setup' to use the Agile Lab.",
            ),
            unsafe_allow_html=True,
        )
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
        st.markdown(
            "<div style='font-size: 0.88rem; color: var(--pc-text-muted); margin-bottom: 12px;'>"
            "Taxonomy mapping the core agile process models from VTU 24CS51 Module 2 against team structures and cadence:"
            "</div>",
            unsafe_allow_html=True,
        )

        df_frameworks = pd.DataFrame(AGILE_FRAMEWORKS).rename(columns={
            "name": "Methodology",
            "focus": "Core Philosophy & Focus",
            "team_size": "Team Size",
            "iteration_style": "Iteration Cadence",
            "key_practices": "Signature Engineering Practices",
            "best_fit": "Optimal Project Profile",
        })

        st.dataframe(df_frameworks, use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔍 Deep Dive by Methodology")
        sel_method = st.selectbox(
            "Select Methodology for Detailed Breakdown:",
            options=[f["name"] for f in AGILE_FRAMEWORKS],
            index=0,
        )
        selected_info = next(f for f in AGILE_FRAMEWORKS if f["name"] == sel_method)

        st.markdown(
            f"""
            <div class="pc-card" style="border-left: 4px solid var(--pc-primary, #2563EB); margin-top: 10px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: var(--pc-text-muted);">Framework</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: var(--pc-text-main); margin-bottom: 6px;">{selected_info['name']}</div>
                        <div style="font-size: 0.88rem; color: var(--pc-text-main); margin-bottom: 4px;"><b>Primary Focus:</b> {selected_info['focus']}</div>
                        <div style="font-size: 0.85rem; color: var(--pc-text-muted);"><b>Recommended Team:</b> {selected_info['team_size']}</div>
                        <div style="font-size: 0.85rem; color: var(--pc-text-muted);"><b>Iteration Style:</b> {selected_info['iteration_style']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: var(--pc-text-muted);">Engineering Rigor</div>
                        <div style="font-size: 0.88rem; color: var(--pc-text-main); margin: 6px 0;"><b>Signature Practices:</b> {selected_info['key_practices']}</div>
                        <div style="font-size: 0.85rem; color: var(--pc-accent, #0D9488); font-weight: 600;"><b>Optimal Fit:</b> {selected_info['best_fit']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------------------
    # TAB B: SPRINT PLANNER & BURNDOWN
    # -----------------------------------------------------------------
    with tab_sprint:
        st.markdown("### 🎯 Agile Sprint Capacity & Release Schedule")
        st.markdown(
            f"<div style='font-size: 0.88rem; color: var(--pc-text-muted); margin-bottom: 12px;'>"
            f"Configuring sprint iterations for active benchmark: <b>{active.get('name', 'N/A')}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

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

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Elevated KPI cards
        m_cols = st.columns(4)
        with m_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="Sprints Required",
                    value=f"{sprint_plan.sprints_needed} Sprints",
                    subtitle=f"{sprint_plan.total_weeks} Total Weeks",
                    icon="🏃",
                    accent_color="#2563EB",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Release Schedule",
                    value=sprint_plan.finish_date,
                    subtitle=f"{sprint_plan.total_calendar_days} Calendar Days",
                    icon="📅",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[2]:
            st.markdown(
                render_kpi_card(
                    label="Team Velocity",
                    value=f"{velocity:.0f} pts",
                    subtitle=f"Per {sprint_len}-wk Sprint",
                    icon="⚡",
                    accent_color="#10B981",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="Backlog Volume",
                    value=f"{backlog_pts:.0f} pts",
                    subtitle="Scope Commitment",
                    icon="📦",
                    accent_color="#8B5CF6",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📉 Projected Release Burndown Chart")
        df_burn = pd.DataFrame(sprint_plan.burndown_schedule)

        fig_burn = go.Figure()

        # Ideal burndown
        fig_burn.add_trace(go.Scatter(
            x=df_burn["sprint"],
            y=df_burn["ideal_remaining_points"],
            mode="lines+markers",
            name="Ideal Burndown Trajectory",
            line=dict(color="#2563EB", width=3, dash="dash"),
            marker=dict(size=7),
        ))

        # Projected remaining
        fig_burn.add_trace(go.Scatter(
            x=df_burn["sprint"],
            y=df_burn["projected_remaining_points"],
            mode="lines+markers",
            name="Projected Remaining Points",
            line=dict(color="#EF4444", width=3),
            marker=dict(size=7),
        ))

        # Points burned cumulative bar
        fig_burn.add_trace(go.Bar(
            x=df_burn["sprint"],
            y=df_burn["points_burned"],
            name="Cumulative Points Delivered",
            marker_color="#10B981",
            opacity=0.35,
        ))

        fig_burn = apply_plotly_theme(
            fig_burn,
            title=f"Release Burndown for {active.get('name')} ({sprint_plan.sprints_needed} Sprints)",
            height=390,
            show_legend=True,
        )
        fig_burn.update_xaxes(title_text="Sprint Iterations")
        fig_burn.update_yaxes(title_text="Story Points Remaining")
        st.plotly_chart(fig_burn, use_container_width=True)

        with st.expander("📋 Detailed Sprint Milestone Schedule"):
            st.dataframe(df_burn, use_container_width=True, hide_index=True)

    # -----------------------------------------------------------------
    # TAB C: AGILITY AND COST OF CHANGE
    # -----------------------------------------------------------------
    with tab_cost:
        st.markdown("### 📉 The Cost of Change Curve: Traditional vs Agile")
        st.markdown(
            "<div style='font-size: 0.9rem; color: var(--pc-text-muted); line-height: 1.55; margin-bottom: 16px;'>"
            "According to Barry Boehm's traditional engineering model, the cost to alter software escalates <b>exponentially</b> "
            "as a system advances through requirements, design, code, test, and production release. "
            "Kent Beck and agile pioneers demonstrated that via <b>Continuous Integration (CI), Test-Driven Development (TDD), "
            "automated regression suites, and simple design</b>, this curve is drastically <b>flattened</b>."
            "</div>",
            unsafe_allow_html=True,
        )

        cost_data = generate_cost_of_change_data()
        df_cost = pd.DataFrame(cost_data)

        col_c_chart, col_c_table = st.columns([1.5, 1.0])

        with col_c_chart:
            fig_cost = go.Figure()

            # Shaded risk avoidance band between traditional and agile
            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Traditional (Exponential)"],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            ))

            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Agile (Flattened Curve)"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(239, 68, 68, 0.12)",
                name="Traditional Escalation Risk Premium (Avoided by Agility)",
            ))

            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Traditional (Exponential)"],
                mode="lines+markers",
                name="Traditional (Boehm Exponential)",
                line=dict(color="#EF4444", width=3),
                marker=dict(size=8),
            ))

            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Agile (Flattened Curve)"],
                mode="lines+markers",
                name="Agile (Beck Flattened Curve)",
                line=dict(color="#10B981", width=3),
                marker=dict(size=8),
            ))

            fig_cost = apply_plotly_theme(
                fig_cost,
                title="Relative Cost to Rectify Defects Across Lifecycle",
                height=400,
                show_legend=True,
            )
            fig_cost.update_yaxes(type="log", title_text="Cost Multiplier (Log-Scale Normalized)")
            fig_cost.update_xaxes(title_text="Software Lifecycle Phase")
            st.plotly_chart(fig_cost, use_container_width=True)

        with col_c_table:
            st.markdown("#### 📊 Phase Escalation Multipliers")
            st.dataframe(
                df_cost[["Lifecycle Phase", "Traditional (Exponential)", "Agile (Flattened Curve)", "Ratio (Traditional / Agile)"]],
                use_container_width=True,
                hide_index=True,
            )
            st.markdown(
                """
                <div class="pc-card" style="border-left: 4px solid var(--pc-accent, #0D9488); padding: 14px; margin-top: 10px; font-size: 0.84rem; line-height: 1.5;">
                    <b>Key Takeaway (VTU Module 2):</b><br>
                    In traditional phased lifecycles, defects undetected until post-release can cost up to <b>100x</b> their requirements-phase cost.
                    Agile technical rigor constrains this escalation to under <b>4x</b>.
                </div>
                """,
                unsafe_allow_html=True,
            )
