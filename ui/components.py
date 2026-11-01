"""Shared UI Components, Styling, and State Management for ProcessCompass."""

import streamlit as st
from db.database import DatabaseManager
from ui.theme import inject_theme, render_page_header, render_kpi_card, render_empty_state_html
from ui.format import format_currency, get_currency_symbol, get_active_currency, CURRENCY_OPTIONS


def init_app_state():
    """Initialize database, active project, and default currency in session state."""
    if "currency" not in st.session_state:
        st.session_state.currency = "INR"

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
    """Inject polished, modern CSS styling via theme engine."""
    inject_theme()
