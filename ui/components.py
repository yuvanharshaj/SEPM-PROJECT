"""Shared UI Components, Styling, and State Management for ProcessCompass."""

import streamlit as st
from db.database import DatabaseManager


def init_app_state():
    """Initialize database and default session state variables."""
    if "db" not in st.session_state:
        st.session_state.db = DatabaseManager()

    db: DatabaseManager = st.session_state.db
    projects = db.list_projects()

    if "current_project_id" not in st.session_state or not st.session_state.current_project_id:
        if projects:
            st.session_state.current_project_id = projects[0]["id"]
        else:
            st.session_state.current_project_id = None

    if "current_project" not in st.session_state:
        if st.session_state.current_project_id:
            st.session_state.current_project = db.get_project_by_id(st.session_state.current_project_id)
        else:
            st.session_state.current_project = None


def reload_current_project():
    """Refresh active project data from database."""
    db: DatabaseManager = st.session_state.db
    if st.session_state.get("current_project_id"):
        st.session_state.current_project = db.get_project_by_id(st.session_state.current_project_id)


def inject_custom_styles():
    """Inject polished, modern CSS styling."""
    st.markdown("""
    <style>
    /* Global Container Adjustments */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Academic Badge */
    .syllabus-badge {
        display: inline-block;
        background-color: #E3F2FD;
        color: #0D47A1;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 4px 10px;
        border-radius: 12px;
        border: 1px solid #BBDEFB;
        margin-bottom: 8px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #0F172A;
        font-weight: 700;
        font-size: 1.6rem;
    }

    /* Callout Card */
    .compass-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Footer styling */
    .footer-text {
        text-align: center;
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, module_tag: str, co_tag: str):
    """Render consistent page header with academic syllabus badges."""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <span class="syllabus-badge">{module_tag} &bull; {co_tag}</span>
            <h1 style="margin: 0; padding-top: 4px; font-size: 2.1rem; color: #0F172A;">{title}</h1>
            <p style="margin: 4px 0 0 0; color: #475569; font-size: 1.05rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
