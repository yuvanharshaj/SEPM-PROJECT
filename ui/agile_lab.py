"""Agile frameworks comparison, sprint planner, and cost of change."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

from core.agile import (
    calculate_sprint_plan,
    generate_cost_of_change_data,
    AGILE_FRAMEWORKS,
)
from ui.components import render_page_header
from ui.theme import apply_plotly_theme


def render_agile_lab_page():
    render_page_header(
        title="Agile lab",
        caption="Methodology taxonomy, sprint capacity planning, and cost-of-change curve analysis.",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.info("No active project loaded. Configure a project in Setup.")
        return

    tab_compare, tab_sprint, tab_cost = st.tabs([
        "Frameworks",
        "Sprint planner",
        "Cost of change",
    ])

    # TAB 1: FRAMEWORKS COMPARISON
    with tab_compare:
        st.markdown("## Methodology comparison")
        df_frameworks = pd.DataFrame(AGILE_FRAMEWORKS).rename(columns={
            "name": "Methodology",
            "focus": "Core focus",
            "team_size": "Team size",
            "iteration_style": "Iteration cadence",
            "key_practices": "Signature practices",
            "best_fit": "Optimal profile",
        })
        st.dataframe(df_frameworks, use_container_width=True, hide_index=True)

        st.markdown("## Method details")
        sel_method = st.selectbox(
            "Select methodology",
            options=[f["name"] for f in AGILE_FRAMEWORKS],
            index=0,
            label_visibility="collapsed",
        )
        selected_info = next(f for f in AGILE_FRAMEWORKS if f["name"] == sel_method)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown(f"**Focus:** {selected_info['focus']}")
            st.markdown(f"**Team size:** {selected_info['team_size']}")
            st.markdown(f"**Cadence:** {selected_info['iteration_style']}")
        with col_d2:
            st.markdown(f"**Signature practices:** {selected_info['key_practices']}")
            st.markdown(f"**Best fit:** {selected_info['best_fit']}")

    # TAB 2: SPRINT PLANNER
    with tab_sprint:
        nominal_kloc = float(active.get("kloc", 25.0))
        default_points = max(30.0, round(nominal_kloc * 5.0, 0))

        col_in1, col_in2, col_in3, col_in4 = st.columns(4)
        with col_in1:
            backlog_pts = st.number_input(
                "Backlog story points",
                min_value=10.0,
                max_value=2000.0,
                value=float(default_points),
                step=10.0,
            )
        with col_in2:
            velocity = st.number_input(
                "Velocity (points / sprint)",
                min_value=5.0,
                max_value=200.0,
                value=25.0,
                step=5.0,
            )
        with col_in3:
            sprint_len = st.selectbox(
                "Sprint length",
                options=[1, 2, 3, 4],
                index=1,
                format_func=lambda w: f"{w} week{'s' if w > 1 else ''}",
            )
        with col_in4:
            kickoff_date = st.date_input("Start date", value=date.today())

        sprint_plan = calculate_sprint_plan(
            backlog_points=backlog_pts,
            velocity_per_sprint=velocity,
            sprint_length_weeks=sprint_len,
            start_date=kickoff_date,
        )

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            with st.container(border=True):
                st.metric("Sprints required", f"{sprint_plan.sprints_needed}")
        with m_col2:
            with st.container(border=True):
                st.metric("Planned duration", f"{sprint_plan.total_weeks} weeks")
        with m_col3:
            with st.container(border=True):
                st.metric("Target release", sprint_plan.finish_date)
        with m_col4:
            with st.container(border=True):
                st.metric("Burn velocity", f"{velocity:.0f} pts / sprint")

        st.markdown("## Release burndown")
        df_burn = pd.DataFrame(sprint_plan.burndown_schedule)

        fig_burn = go.Figure()
        fig_burn.add_trace(go.Scatter(
            x=df_burn["sprint"],
            y=df_burn["ideal_remaining_points"],
            mode="lines+markers",
            name="Ideal trajectory",
            line=dict(color="#64748b", width=2, dash="dash"),
            marker=dict(size=6),
        ))
        fig_burn.add_trace(go.Scatter(
            x=df_burn["sprint"],
            y=df_burn["projected_remaining_points"],
            mode="lines+markers",
            name="Projected remaining",
            line=dict(color="#1d4ed8", width=2.5),
            marker=dict(size=6),
        ))
        fig_burn.add_trace(go.Bar(
            x=df_burn["sprint"],
            y=df_burn["points_burned"],
            name="Points completed",
            marker_color="#94a3b8",
            opacity=0.35,
        ))

        fig_burn = apply_plotly_theme(fig_burn, height=340)
        fig_burn.update_xaxes(title_text="Sprint")
        fig_burn.update_yaxes(title_text="Story points")
        st.plotly_chart(fig_burn, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

        with st.expander("Milestone schedule"):
            st.dataframe(df_burn, use_container_width=True, hide_index=True)

    # TAB 3: COST OF CHANGE
    with tab_cost:
        st.caption(
            "Barry Boehm's empirical data shows defect correction costs grow exponentially in traditional phased models. "
            "Kent Beck's agile practices (TDD, automated regression, continuous integration) flatten this curve."
        )

        cost_data = generate_cost_of_change_data()
        df_cost = pd.DataFrame(cost_data)

        col_c_chart, col_c_table = st.columns([1.3, 1.0])
        with col_c_chart:
            fig_cost = go.Figure()
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
                fillcolor="rgba(148, 163, 184, 0.15)",
                name="Escalation risk delta",
            ))
            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Traditional (Exponential)"],
                mode="lines+markers",
                name="Traditional (Boehm)",
                line=dict(color="#475569", width=2.5),
                marker=dict(size=6),
            ))
            fig_cost.add_trace(go.Scatter(
                x=df_cost["Lifecycle Phase"],
                y=df_cost["Agile (Flattened Curve)"],
                mode="lines+markers",
                name="Agile (Beck)",
                line=dict(color="#1d4ed8", width=2.5),
                marker=dict(size=6),
            ))

            fig_cost = apply_plotly_theme(fig_cost, height=340)
            fig_cost.update_yaxes(type="log", title_text="Relative cost multiplier (log scale)")
            fig_cost.update_xaxes(title_text="Phase")
            st.plotly_chart(fig_cost, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

        with col_c_table:
            st.markdown("## Phase multipliers")
            st.dataframe(
                df_cost[["Lifecycle Phase", "Traditional (Exponential)", "Agile (Flattened Curve)", "Ratio (Traditional / Agile)"]],
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "Syllabus note: Traditional phased lifecycles can experience up to a 100x defect correction multiplier post-release. "
                "Continuous feedback and automated verification constrain this multiplier below 4x."
            )
