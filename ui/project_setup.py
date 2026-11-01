"""Project setup and baseline configuration."""

import streamlit as st
import pandas as pd
from db.database import DatabaseManager
from ui.components import render_page_header
from ui.format import format_currency, get_currency_symbol


def render_project_setup_page():
    render_page_header(
        title="Project setup",
        caption="Configure baseline parameters and constraints for downstream decision models.",
    )

    db: DatabaseManager = st.session_state.db
    all_projects = db.list_projects()
    active = st.session_state.get("current_project")
    sym = get_currency_symbol()

    if not active and all_projects:
        active = db.get_project_by_id(all_projects[0]["id"])
        st.session_state.current_project = active
        st.session_state.current_project_id = active["id"]

    # 4 Key metrics
    if active:
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            with st.container(border=True):
                st.metric("Team size", f"{active.get('team_size', 0)} staff")
        with m_col2:
            with st.container(border=True):
                st.metric("Duration", f"{active.get('duration', 0)} months")
        with m_col3:
            with st.container(border=True):
                st.metric("Budget", format_currency(active.get("budget", 0), compact=True))
        with m_col4:
            with st.container(border=True):
                st.metric("Requirement stability", str(active.get("req_stability", "Medium")))

    st.markdown("## Benchmark projects")
    df_samples = pd.DataFrame([
        {
            "ID": p["id"],
            "Project name": p["name"],
            "Team size": f"{p.get('team_size', 0)} staff",
            "Duration": f"{p.get('duration', 0)} mos",
            "Budget": format_currency(p.get("budget", 0), compact=True),
            "Stability": p.get("req_stability", "Medium"),
            "Risk": p.get("risk_level", "Medium"),
        }
        for p in all_projects
    ])
    st.dataframe(df_samples, use_container_width=True, hide_index=True)

    col_bench_act, col_reset = st.columns([3, 1])
    with col_bench_act:
        bench_map = {p["id"]: p["name"] for p in all_projects}
        sel_bench_id = st.selectbox(
            "Load benchmark",
            options=list(bench_map.keys()),
            format_func=lambda x: bench_map.get(x, str(x)),
            index=list(bench_map.keys()).index(active.get("id")) if active and active.get("id") in bench_map else 0,
            key="sel_bench_preload",
            label_visibility="collapsed",
        )
        if sel_bench_id != (active.get("id") if active else None):
            if st.button("Activate selected project"):
                st.session_state.current_project_id = sel_bench_id
                st.session_state.current_project = db.get_project_by_id(sel_bench_id)
                st.rerun()

    with col_reset:
        if st.button("Reset defaults", help="Reset database to 3 VTU benchmark projects"):
            db.reset_to_defaults()
            all_projects = db.list_projects()
            st.session_state.current_project_id = all_projects[0]["id"]
            st.session_state.current_project = db.get_project_by_id(all_projects[0]["id"])
            st.rerun()

    if not active:
        st.info("No active project loaded. Select or create a project above.")
        return

    st.markdown("## Edit project parameters")
    with st.form("edit_project_form"):
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Administrative parameters**")
            p_name = st.text_input("Project name", value=active.get("name", ""))
            p_desc = st.text_area("Scope description", value=active.get("description", ""), height=100)

            c1, c2, c3 = st.columns(3)
            with c1:
                p_team = st.number_input("Team size", min_value=1, max_value=500, value=int(active.get("team_size", 6)))
            with c2:
                p_dur = st.number_input("Duration (months)", min_value=1, max_value=120, value=int(active.get("duration", 8)))
            with c3:
                p_budget = st.number_input(f"Budget ({sym})", min_value=1000.0, value=float(active.get("budget", 5000000.0)), step=100000.0)

        with col_right:
            st.markdown("**Decision drivers**")
            levels = ["High", "Medium", "Low"]

            p_stability = st.selectbox(
                "Requirement stability",
                options=levels,
                index=levels.index(active.get("req_stability", "Medium")),
                help="High = fixed/frozen requirements; Low = frequent changes.",
            )
            p_involvement = st.selectbox(
                "Customer involvement",
                options=levels,
                index=levels.index(active.get("customer_involvement", "Medium")),
                help="High = continuous sprint feedback; Low = delivery handoff only.",
            )
            p_risk = st.selectbox(
                "Anticipated risk level",
                options=levels,
                index=levels.index(active.get("risk_level", "Medium")),
                help="High = unproven architecture, regulatory audits; Low = standard CRUD.",
            )

            c_drv1, c_drv2 = st.columns(2)
            with c_drv1:
                p_early = st.selectbox(
                    "Need for early delivery",
                    options=levels,
                    index=levels.index(active.get("early_delivery", "Medium")),
                )
            with c_drv2:
                p_exp = st.selectbox(
                    "Team experience",
                    options=levels,
                    index=levels.index(active.get("team_experience", "Medium")),
                )

        btn_save, btn_del = st.columns([3, 1])
        with btn_save:
            # Single primary button on page
            save_clicked = st.form_submit_button("Save changes", type="primary", use_container_width=True)
        with btn_del:
            delete_clicked = st.form_submit_button("Delete project", use_container_width=True)

        if save_clicked:
            active["name"] = p_name.strip()
            active["description"] = p_desc.strip()
            active["team_size"] = int(p_team)
            active["duration"] = int(p_dur)
            active["budget"] = float(p_budget)
            active["req_stability"] = p_stability
            active["customer_involvement"] = p_involvement
            active["risk_level"] = p_risk
            active["early_delivery"] = p_early
            active["team_experience"] = p_exp

            db.save_complete_project(active)
            st.session_state.current_project = db.get_project_by_id(active["id"])
            st.success("Project configuration updated.")
            st.rerun()

        if delete_clicked:
            if len(all_projects) <= 1:
                st.error("Cannot delete the only remaining project.")
            else:
                db.delete_project(active["id"])
                all_projects = db.list_projects()
                st.session_state.current_project_id = all_projects[0]["id"]
                st.session_state.current_project = db.get_project_by_id(all_projects[0]["id"])
                st.rerun()

    # Create new project in secondary expander
    with st.expander("Create new project"):
        with st.form("new_project_form"):
            new_name = st.text_input("Project name *")
            new_desc = st.text_area("Scope description")
            nc1, nc2, nc3 = st.columns(3)
            with nc1:
                new_team = st.number_input("Team size", min_value=1, max_value=500, value=6, key="new_team_input")
            with nc2:
                new_dur = st.number_input("Duration (months)", min_value=1, max_value=120, value=8, key="new_dur_input")
            with nc3:
                new_budget = st.number_input(f"Budget ({sym})", min_value=1000.0, value=5000000.0, step=100000.0, key="new_budget_input")

            create_btn = st.form_submit_button("Create project")
            if create_btn:
                if not new_name.strip():
                    st.error("Project name cannot be empty.")
                else:
                    new_data = {
                        "name": new_name.strip(),
                        "description": new_desc.strip(),
                        "team_size": int(new_team),
                        "duration": int(new_dur),
                        "budget": float(new_budget),
                        "req_stability": "Medium",
                        "customer_involvement": "Medium",
                        "risk_level": "Medium",
                        "early_delivery": "Medium",
                        "team_experience": "Medium",
                        "cocomo_mode": "organic",
                        "kloc": 25.0,
                        "risks": [],
                        "business_case": {
                            "initial_investment": float(new_budget),
                            "annual_benefits": [float(new_budget) * 0.4] * 5,
                            "annual_costs": [float(new_budget) * 0.1] * 5,
                            "discount_rate_pct": 10.0,
                        },
                        "quality_scores": {
                            "Correctness": 4.0, "Reliability": 4.0, "Efficiency": 3.5,
                            "Integrity": 4.0, "Usability": 4.0, "Maintainability": 4.0,
                            "Flexibility": 3.5, "Testability": 4.0, "Portability": 3.5,
                            "Reusability": 3.5, "Interoperability": 3.5,
                        },
                    }
                    new_id = db.save_complete_project(new_data)
                    st.session_state.current_project_id = new_id
                    st.session_state.current_project = db.get_project_by_id(new_id)
                    st.rerun()
