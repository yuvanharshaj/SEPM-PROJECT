"""Shared UI components, state management, and page headers."""

import streamlit as st
from db.database import DatabaseManager
from ui.theme import inject_theme
from ui.format import format_currency, get_currency_symbol, get_active_currency


def init_app_state():
    """Initialize database and default session state variables."""
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

    if "current_project" not in st.session_state or not st.session_state.current_project:
        if st.session_state.current_project_id:
            st.session_state.current_project = db.get_project_by_id(st.session_state.current_project_id)
        else:
            st.session_state.current_project = None


def reload_current_project():
    """Refresh active project data from database."""
    db: DatabaseManager = st.session_state.db
    if st.session_state.get("current_project_id"):
        st.session_state.current_project = db.get_project_by_id(st.session_state.current_project_id)


def render_page_header(title: str, caption: str):
    """Render minimal, sentence-case page header with popover project/currency controls."""
    init_app_state()
    inject_theme()

    db: DatabaseManager = st.session_state.db
    projects = db.list_projects()
    active = st.session_state.get("current_project") or (projects[0] if projects else {})
    active_name = active.get("name", "Project")
    curr = st.session_state.get("currency", "INR")
    pop_label = f"{active_name} · {curr}"

    col_title, col_ctrl = st.columns([3.5, 1.2], vertical_alignment="top")
    with col_title:
        st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
        st.caption(caption)

    with col_ctrl:
        with st.popover(pop_label, use_container_width=True):
            st.markdown("**Active project**")
            proj_dict = {p["id"]: p["name"] for p in projects}
            curr_id = st.session_state.get("current_project_id")
            if curr_id not in proj_dict and projects:
                curr_id = projects[0]["id"]
            selected_id = st.selectbox(
                "Active project",
                options=list(proj_dict.keys()),
                format_func=lambda x: proj_dict.get(x, str(x)),
                index=list(proj_dict.keys()).index(curr_id) if curr_id in proj_dict else 0,
                key=f"header_proj_{title}",
                label_visibility="collapsed",
            )
            if selected_id != st.session_state.get("current_project_id"):
                st.session_state.current_project_id = selected_id
                st.session_state.current_project = db.get_project_by_id(selected_id)
                st.rerun()

            st.markdown("**Currency**")
            currencies = ["INR", "USD", "EUR"]
            curr_labels = {"INR": "INR (₹)", "USD": "USD ($)", "EUR": "EUR (€)"}
            selected_curr = st.selectbox(
                "Currency",
                options=currencies,
                format_func=lambda c: curr_labels.get(c, c),
                index=currencies.index(curr) if curr in currencies else 0,
                key=f"header_curr_{title}",
                label_visibility="collapsed",
            )
            if selected_curr != st.session_state.get("currency"):
                st.session_state.currency = selected_curr
                st.rerun()
