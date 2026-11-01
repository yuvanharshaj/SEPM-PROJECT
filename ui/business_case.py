"""Business Case, Cost-Benefit Analysis & Economic Feasibility UI."""

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
from db.database import DatabaseManager


def render_business_case_page():
    render_page_header(
        title="Project Business Case & Economic Feasibility",
        subtitle="Evaluate project financial viability using Discounted Cash Flows, NPV, ROI, Payback, and Scenario Risk Evaluation.",
        module_tag="VTU 24CS51: Module 3 (Project Evaluation & Cost-Benefit)",
        co_tag="CO3: Analyze Economic Feasibility & Forecast Project Cash Flows",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.warning("Please select or initialize a project in 'Project Setup' first.")
        return

    db: DatabaseManager = st.session_state.db

    saved_biz = active.get("business_case") or {
        "initial_investment": float(active.get("budget", 60000.0)),
        "annual_benefits": [30000.0, 45000.0, 55000.0, 65000.0, 75000.0],
        "annual_costs": [8000.0, 9000.0, 10000.0, 10000.0, 11000.0],
        "discount_rate_pct": 10.0,
    }

    tab_nominal, tab_scenarios, tab_radr = st.tabs([
        "💰 (a) Base Capital Budgeting (NPV & ROI)",
        "🎲 (b) Scenario Risk Evaluation (Expected NPV)",
        "📈 (c) Risk-Adjusted Discount Rate (RADR)",
    ])

    # -----------------------------------------------------------------
    # TAB A: BASE CAPITAL BUDGETING
    # -----------------------------------------------------------------
    with tab_nominal:
        st.markdown("### 💰 Financial Parameters")

        col_p1, col_p2 = st.columns([1, 1])
        with col_p1:
            initial_inv = st.number_input(
                "Initial Capital Investment ($ / ₹):",
                min_value=1000.0,
                value=float(saved_biz.get("initial_investment", 60000.0)),
                step=5000.0,
                help="Upfront development and procurement costs incurred in Year 0",
            )
        with col_p2:
            discount_rate = st.slider(
                "Cost of Capital / Discount Rate (%):",
                min_value=1.0,
                max_value=25.0,
                value=float(saved_biz.get("discount_rate_pct", 10.0)),
                step=0.5,
                help="Annual opportunity cost of capital or required rate of return",
            )

        st.markdown("#### 📅 5-Year Cash Flow Projections")
        st.caption("Forecast anticipated revenue/savings (Benefits) and operational maintenance (Recurring Costs):")

        default_benefits = saved_biz.get("annual_benefits", [30000.0] * 5)
        default_costs = saved_biz.get("annual_costs", [8000.0] * 5)

        year_cols = st.columns(5)
        user_benefits = []
        user_costs = []

        for yr in range(1, 6):
            with year_cols[yr - 1]:
                st.markdown(f"**Year {yr}**")
                b_val = default_benefits[yr - 1] if yr - 1 < len(default_benefits) else 30000.0
                c_val = default_costs[yr - 1] if yr - 1 < len(default_costs) else 8000.0

                b_input = st.number_input(f"Benefit Y{yr}", min_value=0.0, value=float(b_val), step=2000.0, key=f"ben_{yr}")
                c_input = st.number_input(f"Cost Y{yr}", min_value=0.0, value=float(c_val), step=1000.0, key=f"cost_{yr}")
                user_benefits.append(b_input)
                user_costs.append(c_input)

        biz_result = evaluate_business_case(
            initial_investment=initial_inv,
            annual_benefits=user_benefits,
            annual_costs=user_costs,
            discount_rate_pct=discount_rate,
        )

        st.markdown("---")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Net Present Value (NPV)", f"${biz_result.npv:,.2f}", delta=f"{biz_result.discounted_roi_pct:.1f}% Disc ROI")
        with m2:
            st.metric("Simple ROI", f"{biz_result.roi_pct:.1f}%", help="Total Net Benefit / Initial Investment")
        with m3:
            pb_str = f"{biz_result.payback_period_years:.2f} Yrs" if biz_result.payback_period_years else "Unrecovered"
            st.metric("Payback Period", pb_str, help="Time to recover initial capital investment")
        with m4:
            st.metric("Total Net Profit", f"${biz_result.net_profit:,.2f}")

        if biz_result.is_financially_viable:
            st.success(f"✅ **{biz_result.summary_verdict}**")
        else:
            st.error(f"⚠️ **{biz_result.summary_verdict}**")

        st.markdown("#### 📊 Cumulative Cash Flow & Break-Even Trajectory")
        df_flows = pd.DataFrame([yf.to_dict() for yf in biz_result.yearly_flows])

        fig_cf = go.Figure()

        fig_cf.add_trace(go.Bar(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["net_cash_flow"],
            name="Annual Net Flow",
            marker_color=["#EF5350" if val < 0 else "#66BB6A" for val in df_flows["net_cash_flow"]],
        ))

        fig_cf.add_trace(go.Scatter(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["cumulative_cash_flow"],
            mode="lines+markers",
            name="Cumulative Cash Flow (Undiscounted)",
            line=dict(color="#1976D2", width=3),
        ))

        fig_cf.add_trace(go.Scatter(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["cumulative_discounted"],
            mode="lines+markers",
            name="Cumulative Discounted (NPV Trajectory)",
            line=dict(color="#7B1FA2", width=2, dash="dash"),
        ))

        fig_cf.add_hline(y=0, line_dash="dot", line_color="#37474F", annotation_text="Break-Even Threshold ($0)")

        fig_cf.update_layout(
            title="Cash Flow Forecast & Capital Recovery",
            yaxis_title="Amount ($ / ₹)",
            xaxis_title="Timeline",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_cf, use_container_width=True)

        with st.expander("📋 Detailed Cash Flow Accounting Table"):
            st.dataframe(df_flows, use_container_width=True, hide_index=True)

        if st.button("💾 Persist Financial Projections to Active Project", type="primary"):
            active["business_case"] = {
                "initial_investment": float(initial_inv),
                "annual_benefits": [float(b) for b in user_benefits],
                "annual_costs": [float(c) for c in user_costs],
                "discount_rate_pct": float(discount_rate),
            }
            db.save_complete_project(active)
            st.success("Business case projections saved to SQLite!")

    # -----------------------------------------------------------------
    # TAB B: SCENARIO RISK EVALUATION (EXPECTED NPV / EMV)
    # -----------------------------------------------------------------
    with tab_scenarios:
        st.markdown("### 🎲 Risk Evaluation via Scenario Modeling")
        st.markdown(
            "Software investments face market and operational uncertainties. By weighting **Optimistic**, "
            "**Most Likely**, and **Pessimistic** cash flow realizations by their assigned probabilities, "
            "we compute the **Expected Monetary Value (EMV) / Expected NPV** and evaluate downside volatility."
        )
        st.latex(r"E(\text{NPV}) = \sum_{i} p_i \cdot \text{NPV}_i, \quad \sigma(\text{NPV}) = \sqrt{\sum_{i} p_i \cdot (\text{NPV}_i - E(\text{NPV}))^2}")

        sc_col1, sc_col2, sc_col3 = st.columns(3)
        with sc_col1:
            p_opt = st.slider("Optimistic Probability (p1):", min_value=0.05, max_value=0.50, value=0.25, step=0.05)
        with sc_col2:
            p_likely = st.slider("Most Likely Probability (p2):", min_value=0.20, max_value=0.80, value=0.50, step=0.05)
        with sc_col3:
            p_pess = round(max(0.05, 1.0 - (p_opt + p_likely)), 2)
            st.metric("Pessimistic Probability (p3)", f"{p_pess:.2f}", help="Auto-balanced so sum(p) = 1.0")

        scenario_res = evaluate_scenario_risk(
            base_investment=initial_inv,
            base_benefits=user_benefits,
            base_costs=user_costs,
            discount_rate_pct=discount_rate,
            probabilities=(p_opt, p_likely, p_pess),
        )

        sm1, sm2, sm3, sm4 = st.columns(4)
        with sm1:
            st.metric("Expected NPV (EMV)", f"${scenario_res.expected_npv:,.2f}", f"Nominal: ${biz_result.npv:,.2f}")
        with sm2:
            st.metric("Expected ROI", f"{scenario_res.expected_roi_pct:.1f}%")
        with sm3:
            st.metric("NPV Volatility (SD)", f"±${scenario_res.npv_standard_deviation:,.2f}")
        with sm4:
            st.metric("Probability Balance", f"{p_opt:.2f} / {p_likely:.2f} / {p_pess:.2f}")

        st.info(f"**Risk Profile Assessment:** {scenario_res.risk_summary}")

        df_sc = pd.DataFrame([s.to_dict() for s in scenario_res.scenarios]).rename(columns={
            "name": "Scenario",
            "probability": "Probability (p)",
            "initial_investment": "Initial Capex ($)",
            "npv": "Scenario NPV ($)",
            "roi_pct": "ROI (%)",
            "payback_years": "Payback (Yrs)",
        })
        st.dataframe(df_sc[["Scenario", "Probability (p)", "Initial Capex ($)", "Scenario NPV ($)", "ROI (%)", "Payback (Yrs)"]], use_container_width=True, hide_index=True)

        fig_sc_bar = px.bar(
            df_sc,
            x="Scenario",
            y="Scenario NPV ($)",
            color="Scenario",
            text="Scenario NPV ($)",
            color_discrete_map={"Optimistic": "#43A047", "Most Likely": "#1E88E5", "Pessimistic": "#E53935"},
            title="NPV Distribution Across Economic Scenarios",
        )
        fig_sc_bar.add_hline(y=scenario_res.expected_npv, line_dash="dash", line_color="#7B1FA2", annotation_text=f"Expected NPV: ${scenario_res.expected_npv:,.0f}")
        fig_sc_bar.update_layout(height=320, margin=dict(l=20, r=20, t=35, b=20))
        st.plotly_chart(fig_sc_bar, use_container_width=True)

    # -----------------------------------------------------------------
    # TAB C: RISK-ADJUSTED DISCOUNT RATE (RADR)
    # -----------------------------------------------------------------
    with tab_radr:
        st.markdown("### 📈 Risk-Adjusted Discount Rate (RADR)")
        st.markdown(
            "Under the RADR approach, high-risk software initiatives require a higher **hurdle rate**. "
            "A **risk premium** is added to the base cost of capital to reflect technological and execution risks."
        )
        st.latex(r"r_{\text{adjusted}} = r_{\text{base}} + r_{\text{risk\_premium}}, \quad \text{NPV}_{\text{RADR}} = -C_0 + \sum_{t=1}^N \frac{\text{NCF}_t}{(1 + r_{\text{adjusted}})^t}")

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.write(f"**Base Discount Rate:** `{discount_rate:.1f}%`")
        with r_col2:
            risk_prem = st.slider("Risk Premium (%):", min_value=0.5, max_value=10.0, value=3.0, step=0.5, help="Extra risk margin added to hurdle rate")

        radr_res = evaluate_radr(
            initial_investment=initial_inv,
            annual_benefits=user_benefits,
            annual_costs=user_costs,
            base_discount_rate_pct=discount_rate,
            risk_premium_pct=risk_prem,
        )

        rm1, rm2, rm3, rm4 = st.columns(4)
        with rm1:
            st.metric("Adjusted Hurdle Rate", f"{radr_res.adjusted_discount_rate_pct:.1f}%", f"+{risk_prem:.1f}% Premium")
        with rm2:
            st.metric("Base NPV", f"${radr_res.base_npv:,.2f}")
        with rm3:
            st.metric("Risk-Adjusted NPV", f"${radr_res.adjusted_npv:,.2f}", f"Delta: ${radr_res.npv_delta:,.2f}")
        with rm4:
            st.metric("RADR Payback", f"{radr_res.adjusted_payback:.2f} Yrs" if radr_res.adjusted_payback else "Exceeds Life")

        if radr_res.is_viable_at_radr:
            st.success(f"✅ **{radr_res.summary}**")
        else:
            st.warning(f"⚠️ **{radr_res.summary}**")
