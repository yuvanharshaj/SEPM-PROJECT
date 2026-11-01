"""UI smoke tests executing every page function with all 3 benchmark projects."""

import pytest
from streamlit.testing.v1 import AppTest
from db.database import DatabaseManager


@pytest.fixture(scope="module")
def sample_project_ids():
    db = DatabaseManager()
    projects = db.list_projects()
    return [p["id"] for p in projects]


@pytest.mark.parametrize("page_name", [
    "setup", "advisor", "agile", "estimator", "risk", "business", "quality", "report"
])
def test_all_pages_smoke(page_name, sample_project_ids):
    """Run each page function with each sample project and assert no exceptions occur."""
    def fn(p_name, project_id):
        import streamlit as st
        from db.database import DatabaseManager
        from ui.project_setup import render_project_setup_page
        from ui.model_advisor import render_model_advisor_page
        from ui.agile_lab import render_agile_lab_page
        from ui.effort_estimator import render_effort_estimator_page
        from ui.risk_register import render_risk_register_page
        from ui.business_case import render_business_case_page
        from ui.quality_scorecard import render_quality_scorecard_page
        from ui.report_view import render_report_page

        funcs = {
            "setup": render_project_setup_page,
            "advisor": render_model_advisor_page,
            "agile": render_agile_lab_page,
            "estimator": render_effort_estimator_page,
            "risk": render_risk_register_page,
            "business": render_business_case_page,
            "quality": render_quality_scorecard_page,
            "report": render_report_page,
        }
        st.session_state.currency = "INR"
        db = DatabaseManager()
        st.session_state.db = db
        st.session_state.current_project_id = project_id
        st.session_state.current_project = db.get_project_by_id(project_id)
        funcs[p_name]()

    for pid in sample_project_ids:
        at = AppTest.from_function(fn, args=(page_name, pid))
        at.run()
        assert not at.exception, f"Exception in {page_name} with project ID {pid}: {at.exception}"

