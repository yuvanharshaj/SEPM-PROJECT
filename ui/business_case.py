"""Business case, capital budgeting, and economic feasibility."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from core.business_case import (
    evaluate_business_case,
    evaluate_scenario_risk,
    evaluate_radr,
)
from ui.components import render_page_header
from ui.theme import apply_plotly_theme
from ui.format import format_currency, get_currency_symbol
from db.database import DatabaseManager


def render_business_case_page():
    render_page_header(
        title="Business case",
        caption="Discounted cash flows, NPV, ROI, payback horizon, and scenario risk evaluation.",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.info("No active project loaded. Configure a project in Setup.")
        return

    db: DatabaseManager = st.session_state.db
    sym = get_currency_symbol()

    saved_biz = active.get("business_case") or {
        "initial_investment": float(active.get("budget", 5000000.0)),
        "annual_benefits": [2000000.0, 3000000.0, 4000000.0, 4800000.0, 5500000.0],
        "annual_costs": [500000.0, 600000.0, 700000.0, 750000.0, 800000.0],
        "discount_rate_pct": 10.0,
    }

    tab_base, tab_scenarios, tab_radr = st.tabs([
        "Capital budgeting",
        "Scenario evaluation",
        "Risk-adjusted discount rate",
    ])

    # -------------------------------------------------------------
    # TAB 1: CAPITAL BUDGETING (NPV, ROI, PAYBACK)
    # -------------------------------------------------------------
    with tab_base:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            initial_inv = st.number_input(
                f"Initial investment ({sym})",
                min_value=1000.0,
                value=float(saved_biz.get("initial_investment", 5000000.0)),
                step=100000.0,
            )
        with col_p2:
            discount_rate = st.slider(
                "Discount rate (%)",
                min_value=1.0,
                max_value=25.0,
                value=float(saved_biz.get("discount_rate_pct", 10.0)),
                step=0.5,
            )

        st.markdown("## 5-Year projections")
        default_benefits = saved_biz.get("annual_benefits", [2000000.0] * 5)
        default_costs = saved_biz.get("annual_costs", [500000.0] * 5)

        year_cols = st.columns(5)
        user_benefits = []
        user_costs = []
        for yr in range(1, 6):
            with year_cols[yr - 1]:
                st.markdown(f"**Year {yr}**")
                b_val = default_benefits[yr - 1] if yr - 1 < len(default_benefits) else 2000000.0
                c_val = default_costs[yr - 1] if yr - 1 < len(default_costs) else 500000.0
                b_input = st.number_input(f"Benefit Y{yr}", min_value=0.0, value=float(b_val), step=100000.0, key=f"b_{yr}")
                c_input = st.number_input(f"Cost Y{yr}", min_value=0.0, value=float(c_val), step=50000.0, key=f"c_{yr}")
                user_benefits.append(b_input)
                user_costs.append(c_input)

        biz_result = evaluate_business_case(
            initial_investment=initial_inv,
            annual_benefits=user_benefits,
            annual_costs=user_costs,
            discount_rate_pct=discount_rate,
        )

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.metric("Net Present Value", format_currency(biz_result.npv, compact=True), f"{biz_result.discounted_roi_pct:.1f}% disc ROI")
        with m2:
            with st.container(border=True):
                st.metric("Simple ROI", f"{biz_result.roi_pct:.1f}%")
        with m3:
            pb_str = f"{biz_result.payback_period_years:.2f} yrs" if biz_result.payback_period_years else "Unrecovered"
            with st.container(border=True):
                st.metric("Payback period", pb_str)
        with m4:
            with st.container(border=True):
                st.metric("Total net profit", format_currency(biz_result.net_profit, compact=True))

        st.caption(f"Verdict: {biz_result.summary_verdict}")

        st.markdown("## Cumulative cash flow")
        df_flows = pd.DataFrame([yf.to_dict() for yf in biz_result.yearly_flows])

        fig_cf = go.Figure()
        fig_cf.add_trace(go.Bar(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["net_cash_flow"],
            name="Annual net flow",
            marker_color=["#94a3b8" if val < 0 else "#64748b" for val in df_flows["net_cash_flow"]],
        ))
        fig_cf.add_trace(go.Scatter(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["cumulative_cash_flow"],
            mode="lines+markers",
            name="Cumulative cash flow",
            line=dict(color="#1d4ed8", width=2.5),
            marker=dict(size=6),
        ))
        fig_cf.add_trace(go.Scatter(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["cumulative_discounted"],
            mode="lines+markers",
            name="Cumulative discounted",
            line=dict(color="#475569", width=2, dash="dash"),
            marker=dict(size=6),
        ))
        fig_cf.add_hline(y=0, line_dash="dot", line_color="#94a3b8", annotation_text="Break-even threshold")

        if biz_result.payback_period_years:
            pb_label = f"Year {min(5, int(biz_result.payback_period_years) + 1)}"
            fig_cf.add_annotation(
                x=pb_label,
                y=0,
                text=f"Break-even: {biz_result.payback_period_years:.2f} yrs",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#1d4ed8",
                font=dict(color="#1d4ed8", size=11),
            )

        fig_cf = apply_plotly_theme(fig_cf, height=340)
        fig_cf.update_yaxes(title_text=f"Amount ({sym})")
        st.plotly_chart(fig_cf, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

        with st.expander("Cash flow accounting table"):
            st.dataframe(df_flows, use_container_width=True, hide_index=True)

        if st.button("Save business case to project", type="primary"):
            active["business_case"] = {
                "initial_investment": float(initial_inv),
                "annual_benefits": [float(b) for b in user_benefits],
                "annual_costs": [float(c) for c in user_costs],
                "discount_rate_pct": float(discount_rate),
            }
            db.save_complete_project(active)
            st.success("Financial parameters saved.")

    # -------------------------------------------------------------
    # TAB 2: SCENARIOS (EXPECTED NPV / EMV)
    # -------------------------------------------------------------
    with tab_scenarios:
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            p_opt = st.slider("Optimistic probability (p1)", min_value=0.05, max_value=0.50, value=0.25, step=0.05)
        with sc2:
            p_likely = st.slider("Likely probability (p2)", min_value=0.20, max_value=0.80, value=0.50, step=0.05)
        with sc3:
            p_pess = round(max(0.05, 1.0 - (p_opt + p_likely)), 2)
            st.metric("Pessimistic probability (p3)", f"{p_pess:.2f}")

        scenario_res = evaluate_scenario_risk(
            base_investment=initial_inv,
            base_benefits=user_benefits,
            base_costs=user_costs,
            discount_rate_pct=discount_rate,
            probabilities=(p_opt, p_likely, p_pess),
        )

        sm1, sm2, sm3 = st.columns(3)
        with sm1:
            with st.container(border=True):
                st.metric("Expected NPV (EMV)", format_currency(scenario_res.expected_npv, compact=True))
        with sm2:
            with st.container(border=True):
                st.metric("Expected ROI", f"{scenario_res.expected_roi_pct:.1f}%")
        with sm3:
            with st.container(border=True):
                st.metric("NPV standard deviation", f"±{format_currency(scenario_res.npv_standard_deviation, compact=True)}")

        st.caption(f"Risk assessment: {scenario_res.risk_summary}")

        df_sc = pd.DataFrame([
            {
                "Scenario": s.name,
                "Probability": f"{s.probability:.2f}",
                f"Initial capex ({sym})": format_currency(s.initial_investment, compact=False, precision=0),
                f"Scenario NPV ({sym})": format_currency(s.npv, compact=False, precision=0),
                "ROI (%)": f"{s.roi_pct:.1f}%",
                "Payback (yrs)": f"{s.payback_years:.2f}" if s.payback_years else "Unrecovered",
            }
            for s in scenario_res.scenarios
        ])
        st.dataframe(df_sc, use_container_width=True, hide_index=True)

        df_plot = pd.DataFrame([s.to_dict() for s in scenario_res.scenarios])
        fig_sc_bar = px.bar(
            df_plot,
            x="name",
            y="npv",
            color="name",
            color_discrete_sequence=["#1d4ed8", "#475569", "#94a3b8"],
        )
        fig_sc_bar.add_hline(y=scenario_res.expected_npv, line_dash="dash", line_color="#1d4ed8", annotation_text=f"Expected NPV: {format_currency(scenario_res.expected_npv, compact=True)}")
        fig_sc_bar = apply_plotly_theme(fig_sc_bar, height=300)
        fig_sc_bar.update_xaxes(title_text="Scenario")
        fig_sc_bar.update_yaxes(title_text=f"NPV ({sym})")
        st.plotly_chart(fig_sc_bar, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

    # -------------------------------------------------------------
    # TAB 3: RADR
    # -------------------------------------------------------------
    with tab_radr:
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.write(f"Base discount rate: **{discount_rate:.1f}%**")
        with r_col2:
            risk_prem = st.slider("Risk premium (%)", min_value=0.5, max_value=10.0, value=3.0, step=0.5)

        radr_res = evaluate_radr(
            initial_investment=initial_inv,
            annual_benefits=user_benefits,
            annual_costs=user_costs,
            base_discount_rate_pct=discount_rate,
            risk_premium_pct=risk_prem,
        )

        rm1, rm2, rm3 = st.columns(3)
        with rm1:
            with st.container(border=True):
                st.metric("Adjusted hurdle rate", f"{radr_res.adjusted_discount_rate_pct:.1f}%", f"+{risk_prem:.1f}% premium")
        with rm2:
            with st.container(border=True):
                st.metric("Base NPV", format_currency(radr_res.base_npv, compact=True))
        with rm3:
            with st.container(border=True):
                st.metric("Risk-adjusted NPV", format_currency(radr_res.adjusted_npv, compact=True))

        st.caption(f"Status: {radr_res.summary}")
