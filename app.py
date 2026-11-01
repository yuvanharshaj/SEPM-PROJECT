"""ProcessCompass: Decision-support tool for software engineering management."""

import streamlit as st

st.set_page_config(
    page_title="ProcessCompass",
    page_icon=":material/explore:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui.components import init_app_state
from ui.project_setup import render_project_setup_page
from ui.model_advisor import render_model_advisor_page
from ui.agile_lab import render_agile_lab_page
from ui.effort_estimator import render_effort_estimator_page
from ui.risk_register import render_risk_register_page
from ui.business_case import render_business_case_page
from ui.quality_scorecard import render_quality_scorecard_page
from ui.report_view import render_report_page


def main():
    init_app_state()

    pages = [
        st.Page(render_project_setup_page, title="Setup", icon=":material/settings:", url_path="setup", default=True),
        st.Page(render_model_advisor_page, title="Process", icon=":material/account_tree:", url_path="process"),
        st.Page(render_agile_lab_page, title="Agile", icon=":material/bolt:", url_path="agile"),
        st.Page(render_effort_estimator_page, title="Estimate", icon=":material/calculate:", url_path="estimate"),
        st.Page(render_risk_register_page, title="Risk", icon=":material/warning:", url_path="risk"),
        st.Page(render_business_case_page, title="Business", icon=":material/trending_up:", url_path="business"),
        st.Page(render_quality_scorecard_page, title="Quality", icon=":material/verified:", url_path="quality"),
        st.Page(render_report_page, title="Report", icon=":material/description:", url_path="report"),
    ]

    nav = st.navigation(pages, position="top")
    nav.run()


if __name__ == "__main__":
    main()
