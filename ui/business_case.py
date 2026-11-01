"""Business Case, Cost-Benefit Analysis & Economic Feasibility UI."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.business_case import evaluate_business_case
from ui.components import render_page_header
from db.database import DatabaseManager


def render_business_case_page():
    render_page_header(
        title="Project Business Case & Economic Feasibility",
        subtitle="Evaluate project financial viability using Discounted Cash Flows, NPV, ROI, and Payback Period.",
        module_tag="VTU 24CS51: Module 4 (Project Evaluation & Cost-Benefit)",
        co_tag="CO4: Analyze Economic Feasibility & Forecast Project Cash Flows",
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

    # Calculate business case
    biz_result = evaluate_business_case(
        initial_investment=initial_inv,
        annual_benefits=user_benefits,
        annual_costs=user_costs,
        discount_rate_pct=discount_rate,
    )

    st.markdown("---")

    # Financial Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        npv_color = "normal" if biz_result.npv >= 0 else "inverse"
        st.metric("Net Present Value (NPV)", f"${biz_result.npv:,.2f}", delta=f"{biz_result.discounted_roi_pct:.1f}% Disc ROI")
    with m2:
        st.metric("Simple ROI", f"{biz_result.roi_pct:.1f}%", help="Total Net Benefit / Initial Investment")
    with m3:
        pb_str = f"{biz_result.payback_period_years:.2f} Yrs" if biz_result.payback_period_years else "Unrecovered"
        st.metric("Payback Period", pb_str, help="Time to recover initial capital investment")
    with m4:
        st.metric("Total Net Profit", f"${biz_result.net_profit:,.2f}")

    # Verdict Banner
    if biz_result.is_financially_viable:
        st.success(f"✅ **{biz_result.summary_verdict}**")
    else:
        st.error(f"⚠️ **{biz_result.summary_verdict}**")

    # Cumulative Cash Flow Chart
    st.markdown("#### 📊 Cumulative Cash Flow & Break-Even Trajectory")
    df_flows = pd.DataFrame([yf.to_dict() for yf in biz_result.yearly_flows])

    fig_cf = go.Figure()

    # Net annual cash flow bars
    fig_cf.add_trace(go.Bar(
        x=[f"Year {y}" for y in df_flows["year"]],
        y=df_flows["net_cash_flow"],
        name="Annual Net Flow",
        marker_color=["#EF5350" if val < 0 else "#66BB6A" for val in df_flows["net_cash_flow"]],
    ))

    # Cumulative line
    fig_cf.add_trace(go.Scatter(
        x=[f"Year {y}" for y in df_flows["year"]],
        y=df_flows["cumulative_cash_flow"],
        mode="lines+markers",
        name="Cumulative Cash Flow (Undiscounted)",
        line=dict(color="#1976D2", width=3),
    ))

    # Discounted Cumulative line
    fig_cf.add_trace(go.Scatter(
        x=[f"Year {y}" for y in df_flows["year"]],
        y=df_flows["cumulative_discounted"],
        mode="lines+markers",
        name="Cumulative Discounted (NPV Trajectory)",
        line=dict(color="#7B1FA2", width=2, dash="dash"),
    ))

    # Zero break-even line
    fig_cf.add_hline(y=0, line_dash="dot", line_color="#37474F", annotation_text="Break-Even Threshold ($0)")

    fig_cf.update_layout(
        title="Cash Flow Forecast & Capital Recovery",
        yaxis_title="Amount ($ / ₹)",
        xaxis_title="Timeline",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
    )
    st.plotly_chart(fig_cf, use_container_width=True)

    # Data Table
    with st.expander("📋 Detailed Cash Flow Accounting Table"):
        st.dataframe(df_flows, use_container_width=True, hide_index=True)

    # Save button
    if st.button("💾 Persist Financial Projections to Active Project", type="primary"):
        active["business_case"] = {
            "initial_investment": float(initial_inv),
            "annual_benefits": [float(b) for b in user_benefits],
            "annual_costs": [float(c) for c in user_costs],
            "discount_rate_pct": float(discount_rate),
        }
        db.save_complete_project(active)
        st.success("Business case projections saved to SQLite!")
