"""ProcessCompass: Decision-Support Tool for Software Engineering & Project Management.

VTU 24CS51 Software Engineering & Project Management.
Author: YUVAN HARSHAJ
Stack: Python, Streamlit, SQLite, Plotly, ReportLab, pytest.
"""

import streamlit as st

# Streamlit Page Configuration must be the first command
st.set_page_config(
    page_title="ProcessCompass | SEPM Decision Support",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.components import init_app_state, inject_custom_styles
from ui.format import format_currency, get_currency_symbol
from ui.project_setup import render_project_setup_page
from ui.model_advisor import render_model_advisor_page
from ui.agile_lab import render_agile_lab_page
from ui.effort_estimator import render_effort_estimator_page
from ui.risk_register import render_risk_register_page
from ui.business_case import render_business_case_page
from ui.quality_scorecard import render_quality_scorecard_page
from ui.report_view import render_report_page


def main():
    # Initialize SQLite database and session state
    init_app_state()
    inject_custom_styles()

    # Sidebar Header & Brand
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 6px 0 14px 0;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: linear-gradient(135deg, #2563EB, #1E40AF); border-radius: 12px; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25); margin-bottom: 8px;">
                <span style="font-size: 1.4rem;">🧭</span>
            </div>
            <h2 style="margin: 0; color: var(--pc-primary-dark, #1E40AF); font-size: 1.45rem; font-weight: 800; letter-spacing: -0.02em;">ProcessCompass</h2>
            <p style="margin: 2px 0 0 0; color: var(--pc-text-muted, #64748B); font-size: 0.8rem; font-weight: 600;">
                VTU 24CS51 Decision Support
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Currency Selector (INR ₹ default, USD $, EUR €)
    curr_map = {"₹ INR": "INR", "$ USD": "USD", "€ EUR": "EUR"}
    inv_curr_map = {"INR": "₹ INR", "USD": "$ USD", "EUR": "€ EUR"}
    current_curr = st.session_state.get("currency", "INR")
    default_curr_idx = ["INR", "USD", "EUR"].index(current_curr) if current_curr in ["INR", "USD", "EUR"] else 0

    st.sidebar.markdown(
        """<div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--pc-text-muted); margin-bottom: 4px;">Display Currency</div>""",
        unsafe_allow_html=True,
    )
    selected_curr_label = st.sidebar.radio(
        "Display Currency",
        options=["₹ INR", "$ USD", "€ EUR"],
        index=default_curr_idx,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.currency = curr_map[selected_curr_label]

    # Active Project Snapshot in Sidebar
    active = st.session_state.get("current_project")
    if active:
        formatted_budget = format_currency(active.get("budget", 0), compact=True)
        st.sidebar.markdown(
            f"""
            <div style="background: var(--pc-card-subtle, #F1F5F9); border-radius: 10px; padding: 10px 14px; margin: 12px 0 16px 0; border: 1px solid var(--pc-border, #E2E8F0); border-left: 4px solid var(--pc-primary, #2563EB);">
                <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--pc-text-muted, #64748B); font-weight: 700; letter-spacing: 0.04em;">Active Benchmark</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: var(--pc-text-main, #0F172A); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 1px;">
                    {active.get('name', 'None')}
                </div>
                <div style="font-size: 0.78rem; color: var(--pc-text-muted, #64748B); margin-top: 4px;">
                    👥 {active.get('team_size', 0)} Engineers &bull; ⏱️ {active.get('duration', 0)} Mos &bull; 💰 {formatted_budget}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Navigation Menu with Query Param Support
    pages = {
        "⚙️ Project Setup": render_project_setup_page,
        "🧭 Process Model Advisor": render_model_advisor_page,
        "⚡ Agile Lab": render_agile_lab_page,
        "📐 Effort Estimator": render_effort_estimator_page,
        "⚠️ Risk Register": render_risk_register_page,
        "💰 Business Case": render_business_case_page,
        "🎯 Quality Scorecard": render_quality_scorecard_page,
        "📄 Consolidated Report": render_report_page,
    }

    page_slug_map = {
        "setup": "⚙️ Project Setup",
        "advisor": "🧭 Process Model Advisor",
        "agile": "⚡ Agile Lab",
        "estimator": "📐 Effort Estimator",
        "risks": "⚠️ Risk Register",
        "business": "💰 Business Case",
        "quality": "🎯 Quality Scorecard",
        "report": "📄 Consolidated Report",
    }

    page_param = st.query_params.get("page", None)
    default_page = page_slug_map.get(page_param, "⚙️ Project Setup") if page_param else "⚙️ Project Setup"
    default_idx = list(pages.keys()).index(default_page) if default_page in pages else 0

    selected_page_name = st.sidebar.radio(
        "Navigation",
        options=list(pages.keys()),
        index=default_idx,
        label_visibility="collapsed",
    )

    # Syllabus info box in sidebar
    st.sidebar.markdown(
        """
        <div style="margin-top: 20px; padding: 12px; background: rgba(30, 41, 59, 0.03); border-radius: 10px; border: 1px solid var(--pc-border, #E2E8F0); font-size: 0.77rem; color: var(--pc-text-muted, #64748B); line-height: 1.45;">
            <div style="font-weight: 700; color: var(--pc-text-main, #0F172A); margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                <span>📚</span> <span>VTU Syllabus Mapping (24CS51)</span>
            </div>
            <div>&bull; M1: Process Model Advisor (CO1)</div>
            <div>&bull; M2: Agile Lab (CO2)</div>
            <div>&bull; M3: Setup & Business Case (CO3)</div>
            <div>&bull; M4: Estimation & Risk (CO4)</div>
            <div>&bull; M5: McCall Quality & Metrics (CO5)</div>
            <div>&bull; Synthesis: Consolidated Report (CO1–CO5)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Academic metadata footer
    st.sidebar.markdown(
        """
        <div style="margin-top: 16px; padding: 10px; text-align: center; font-size: 0.73rem; color: var(--pc-text-subtle, #94A3B8); line-height: 1.4;">
            <div><b>Author:</b> YUVAN HARSHAJ</div>
            <div>VTU Dept. of Computer Science &bull; Sem V</div>
            <div style="margin-top: 4px;">ProcessCompass v2.0 &bull; MIT License</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Route to selected page
    page_func = pages[selected_page_name]
    page_func()


if __name__ == "__main__":
    main()
