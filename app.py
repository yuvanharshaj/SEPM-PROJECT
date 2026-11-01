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
from ui.project_setup import render_project_setup_page
from ui.model_advisor import render_model_advisor_page
from ui.effort_estimator import render_effort_estimator_page
from ui.risk_register import render_risk_register_page
from ui.business_case import render_business_case_page
from ui.quality_scorecard import render_quality_scorecard_page
from ui.report_view import render_report_page


def main():
    # Initialize SQLite database and session state
    init_app_state()
    inject_custom_styles()

    # Sidebar Navigation
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 10px 0 15px 0;">
            <h2 style="margin: 0; color: #0D47A1; font-size: 1.6rem;">🧭 ProcessCompass</h2>
            <p style="margin: 3px 0 0 0; color: #546E7A; font-size: 0.85rem; font-weight: 500;">
                VTU 24CS51 Decision-Support Tool
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Active Project Snapshot in Sidebar
    active = st.session_state.get("current_project")
    if active:
        st.sidebar.markdown(
            f"""
            <div style="background-color: #F1F5F9; border-radius: 8px; padding: 10px 12px; margin-bottom: 15px; border-left: 4px solid #1976D2;">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 700;">Active Project</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {active.get('name', 'None')}
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-top: 2px;">
                    👥 {active.get('team_size', 0)} Engineers &bull; ⏱️ {active.get('duration', 0)} Mos &bull; 💵 ${active.get('budget', 0):,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Navigation Menu with Query Param Support
    pages = {
        "⚙️ Project Setup": render_project_setup_page,
        "🧭 Process Model Advisor": render_model_advisor_page,
        "📐 Effort Estimator": render_effort_estimator_page,
        "⚠️ Risk Register": render_risk_register_page,
        "💰 Business Case": render_business_case_page,
        "🎯 Quality Scorecard": render_quality_scorecard_page,
        "📄 Consolidated Report": render_report_page,
    }

    page_slug_map = {
        "setup": "⚙️ Project Setup",
        "advisor": "🧭 Process Model Advisor",
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
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
            <b>VTU Syllabus Alignment (24CS51):</b><br>
            &bull; Mod 1: Process Models & Agile<br>
            &bull; Mod 3: COCOMO & Function Points<br>
            &bull; Mod 4: RMMM & Project Economics<br>
            &bull; Mod 5: McCall Quality Assurance
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div style="margin-top: 20px; text-align: center; font-size: 0.75rem; color: #94A3B8;">
            ProcessCompass v1.0 &bull; MIT License<br>
            Built for VTU Computer Science (24CS51)
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Route to selected page
    page_func = pages[selected_page_name]
    page_func()


if __name__ == "__main__":
    main()
