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
from ui.theme import render_page_header, render_kpi_card, render_empty_state_html, apply_plotly_theme
from ui.format import format_currency, get_currency_symbol
from db.database import DatabaseManager


def render_business_case_page():
    render_page_header(
        title="Project Business Case & Economic Feasibility",
        subtitle="Evaluate project financial viability using Discounted Cash Flows, NPV, ROI, Payback, and Scenario Risk Analysis.",
        module_tag="VTU 24CS51: Module 3",
        co_tag="CO3: Analyze Economic Feasibility & Project Cash Flows",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.markdown(
            render_empty_state_html(
                icon="💰",
                title="No Active Project Selected",
                description="Please select or configure a project benchmark in 'Project Setup' to view economic feasibility.",
            ),
            unsafe_allow_html=True,
        )
        return

    db: DatabaseManager = st.session_state.db
    sym = get_currency_symbol()

    saved_biz = active.get("business_case") or {
        "initial_investment": float(active.get("budget", 5000000.0)),
        "annual_benefits": [2000000.0, 3000000.0, 4000000.0, 4800000.0, 5500000.0],
        "annual_costs": [500000.0, 600000.0, 700000.0, 750000.0, 800000.0],
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
        st.markdown("### 💰 Capital Budgeting Parameters")

        col_p1, col_p2 = st.columns([1, 1])
        with col_p1:
            initial_inv = st.number_input(
                f"Initial Capital Investment ({sym}):",
                min_value=1000.0,
                value=float(saved_biz.get("initial_investment", 5000000.0)),
                step=100000.0,
                help="Upfront development and procurement costs incurred in Year 0",
            )
        with col_p2:
            discount_rate = st.slider(
                "Cost of Capital / Discount Rate (%):",
                min_value=1.0,
                max_value=25.0,
                value=float(saved_biz.get("discount_rate_pct", 10.0)),
                step=0.5,
                help="Annual opportunity cost of capital or hurdle rate",
            )

        st.markdown("#### 📅 5-Year Cash Flow Projections")
        st.caption("Forecast anticipated revenue/savings (Benefits) and operational maintenance (Recurring Costs):")

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

                b_input = st.number_input(f"Benefit Y{yr}", min_value=0.0, value=float(b_val), step=100000.0, key=f"ben_{yr}")
                c_input = st.number_input(f"Cost Y{yr}", min_value=0.0, value=float(c_val), step=50000.0, key=f"cost_{yr}")
                user_benefits.append(b_input)
                user_costs.append(c_input)

        biz_result = evaluate_business_case(
            initial_investment=initial_inv,
            annual_benefits=user_benefits,
            annual_costs=user_costs,
            discount_rate_pct=discount_rate,
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # 3 Large KPI Cards (NPV, ROI, Payback) + Total Profit
        m_cols = st.columns(4)
        with m_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="Net Present Value (NPV)",
                    value=format_currency(biz_result.npv, compact=True),
                    subtitle=f"{biz_result.discounted_roi_pct:.1f}% Discounted ROI",
                    delta=f"{biz_result.discounted_roi_pct:.1f}%",
                    delta_type="up" if biz_result.npv > 0 else "down",
                    icon="💎",
                    accent_color="#2563EB" if biz_result.npv > 0 else "#EF4444",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Simple Return on Invest",
                    value=f"{biz_result.roi_pct:.1f}%",
                    subtitle="Net Profit / Capex",
                    delta=f"{biz_result.roi_pct:.1f}%",
                    delta_type="up" if biz_result.roi_pct > 0 else "down",
                    icon="📈",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[2]:
            pb_str = f"{biz_result.payback_period_years:.2f} Yrs" if biz_result.payback_period_years else "Unrecovered"
            st.markdown(
                render_kpi_card(
                    label="Payback Period",
                    value=pb_str,
                    subtitle="Capital Recovery Horizon",
                    icon="⏱️",
                    accent_color="#10B981" if biz_result.payback_period_years and biz_result.payback_period_years <= 3.0 else "#F59E0B",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="Total Net Profit",
                    value=format_currency(biz_result.net_profit, compact=True),
                    subtitle=format_currency(biz_result.net_profit, compact=False, precision=0),
                    icon="💰",
                    accent_color="#8B5CF6",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
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
            marker_color=["#EF4444" if val < 0 else "#10B981" for val in df_flows["net_cash_flow"]],
        ))

        fig_cf.add_trace(go.Scatter(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["cumulative_cash_flow"],
            mode="lines+markers",
            name="Cumulative Cash Flow (Undiscounted)",
            line=dict(color="#2563EB", width=3),
            marker=dict(size=7),
        ))

        fig_cf.add_trace(go.Scatter(
            x=[f"Year {y}" for y in df_flows["year"]],
            y=df_flows["cumulative_discounted"],
            mode="lines+markers",
            name="Cumulative Discounted (NPV Trajectory)",
            line=dict(color="#8B5CF6", width=2, dash="dash"),
            marker=dict(size=7),
        ))

        fig_cf.add_hline(y=0, line_dash="dot", line_color="#64748B", annotation_text=f"Break-Even Threshold ({sym}0)")

        # Callout dot at payback / break-even if available
        if biz_result.payback_period_years:
            pb_year_label = f"Year {min(5, int(biz_result.payback_period_years) + 1)}"
            fig_cf.add_annotation(
                x=pb_year_label,
                y=0,
                text=f"★ Break-Even: {biz_result.payback_period_years:.2f} Yrs",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#10B981",
                font=dict(color="#10B981", size=11, family="'Plus Jakarta Sans', sans-serif"),
                bgcolor="rgba(16, 185, 129, 0.1)",
                bordercolor="#10B981",
            )

        fig_cf = apply_plotly_theme(
            fig_cf,
            title="Cash Flow Forecast & Capital Recovery Trajectory",
            height=390,
            show_legend=True,
        )
        fig_cf.update_yaxes(title_text=f"Amount ({sym})")
        fig_cf.update_xaxes(title_text="Project Lifecycle Timeline")
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
            st.success("Business case projections saved to SQLite database!")

    # -----------------------------------------------------------------
    # TAB B: SCENARIO RISK EVALUATION (EXPECTED NPV / EMV)
    # -----------------------------------------------------------------
    with tab_scenarios:
        st.markdown("### 🎲 Risk Evaluation via Scenario Modeling")
        st.markdown(
            "<div style='font-size: 0.9rem; color: var(--pc-text-muted); line-height: 1.5; margin-bottom: 12px;'>"
            "Software investments face commercial and technical volatility. By weighting <b>Optimistic</b>, "
            "<b>Most Likely</b>, and <b>Pessimistic</b> cash flow outcomes by assigned probabilities, "
            "we compute the <b>Expected Monetary Value (EMV) / Expected NPV</b> and standard deviation."
            "</div>",
            unsafe_allow_html=True,
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

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        sm_cols = st.columns(4)
        with sm_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="Expected NPV (EMV)",
                    value=format_currency(scenario_res.expected_npv, compact=True),
                    subtitle=f"Nominal: {format_currency(biz_result.npv, compact=True)}",
                    icon="🎯",
                    accent_color="#2563EB",
                ),
                unsafe_allow_html=True,
            )
        with sm_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Expected ROI",
                    value=f"{scenario_res.expected_roi_pct:.1f}%",
                    subtitle="Probability Weighted",
                    icon="📈",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with sm_cols[2]:
            st.markdown(
                render_kpi_card(
                    label="NPV Volatility (σ)",
                    value=f"±{format_currency(scenario_res.npv_standard_deviation, compact=True)}",
                    subtitle="Standard Deviation",
                    icon="📊",
                    accent_color="#F59E0B",
                ),
                unsafe_allow_html=True,
            )
        with sm_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="Probability Split",
                    value=f"{p_opt:.2f}/{p_likely:.2f}/{p_pess:.2f}",
                    subtitle="Opt / Likely / Pess",
                    icon="🎲",
                    accent_color="#8B5CF6",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.info(f"**Risk Profile Assessment:** {scenario_res.risk_summary}")

        df_sc = pd.DataFrame([
            {
                "Scenario": s.name,
                "Probability (p)": f"{s.probability:.2f}",
                f"Initial Capex ({sym})": format_currency(s.initial_investment, compact=False, precision=0),
                f"Scenario NPV ({sym})": format_currency(s.npv, compact=False, precision=0),
                "ROI (%)": f"{s.roi_pct:.1f}%",
                "Payback (Yrs)": f"{s.payback_years:.2f}" if s.payback_years else "Unrecovered",
            }
            for s in scenario_res.scenarios
        ])
        st.dataframe(df_sc, use_container_width=True, hide_index=True)

        # Bar chart of scenario NPVs
        df_plot = pd.DataFrame([s.to_dict() for s in scenario_res.scenarios])
        fig_sc_bar = px.bar(
            df_plot,
            x="name",
            y="npv",
            color="name",
            color_discrete_map={"Optimistic": "#10B981", "Most Likely": "#2563EB", "Pessimistic": "#EF4444"},
        )
        fig_sc_bar.add_hline(
            y=scenario_res.expected_npv,
            line_dash="dash",
            line_color="#8B5CF6",
            annotation_text=f"Expected NPV: {format_currency(scenario_res.expected_npv, compact=True)}",
        )
        fig_sc_bar = apply_plotly_theme(
            fig_sc_bar,
            title="NPV Distribution Across Economic Scenarios",
            height=320,
            show_legend=False,
        )
        fig_sc_bar.update_xaxes(title_text="Scenario")
        fig_sc_bar.update_yaxes(title_text=f"NPV ({sym})")
        st.plotly_chart(fig_sc_bar, use_container_width=True)

    # -----------------------------------------------------------------
    # TAB C: RISK-ADJUSTED DISCOUNT RATE (RADR)
    # -----------------------------------------------------------------
    with tab_radr:
        st.markdown("### 📈 Risk-Adjusted Discount Rate (RADR)")
        st.markdown(
            "<div style='font-size: 0.9rem; color: var(--pc-text-muted); line-height: 1.5; margin-bottom: 12px;'>"
            "Under the RADR approach, higher-risk software engineering initiatives require a higher <b>hurdle rate</b>. "
            "A <b>risk premium</b> is added to the base cost of capital to reflect architectural and execution risks."
            "</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"r_{\text{adjusted}} = r_{\text{base}} + r_{\text{risk\_premium}}, \quad \text{NPV}_{\text{RADR}} = -C_0 + \sum_{t=1}^N \frac{\text{NCF}_t}{(1 + r_{\text{adjusted}})^t}")

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.markdown(f"**Base Discount Rate:** `{discount_rate:.1f}%`")
        with r_col2:
            risk_prem = st.slider("Risk Premium (%):", min_value=0.5, max_value=10.0, value=3.0, step=0.5, help="Extra risk margin added to hurdle rate")

        radr_res = evaluate_radr(
            initial_investment=initial_inv,
            annual_benefits=user_benefits,
            annual_costs=user_costs,
            base_discount_rate_pct=discount_rate,
            risk_premium_pct=risk_prem,
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        rm_cols = st.columns(4)
        with rm_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="Adjusted Hurdle Rate",
                    value=f"{radr_res.adjusted_discount_rate_pct:.1f}%",
                    subtitle=f"+{risk_prem:.1f}% Risk Margin",
                    icon="📈",
                    accent_color="#2563EB",
                ),
                unsafe_allow_html=True,
            )
        with rm_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Base NPV",
                    value=format_currency(radr_res.base_npv, compact=True),
                    subtitle=f"At {discount_rate:.1f}% hurdle",
                    icon="💎",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with rm_cols[2]:
            st.markdown(
                render_kpi_card(
                    label="Risk-Adjusted NPV",
                    value=format_currency(radr_res.adjusted_npv, compact=True),
                    subtitle=f"Penalty: -{format_currency(abs(radr_res.npv_delta), compact=True)}",
                    icon="⚖️",
                    accent_color="#F59E0B" if radr_res.adjusted_npv > 0 else "#EF4444",
                ),
                unsafe_allow_html=True,
            )
        with rm_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="Adjusted Payback",
                    value=f"{radr_res.adjusted_payback:.2f} Yrs" if radr_res.adjusted_payback else "Exceeds Life",
                    subtitle="Under Risk Premium",
                    icon="⏱️",
                    accent_color="#8B5CF6",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if radr_res.is_viable_at_radr:
            st.success(f"✅ **{radr_res.summary}**")
        else:
            st.warning(f"⚠️ **{radr_res.summary}**")
