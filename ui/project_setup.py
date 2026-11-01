"""Project Setup & SQLite Persistence UI."""

import streamlit as st
from db.database import DatabaseManager
from ui.components import render_page_header, reload_current_project


def render_project_setup_page():
    render_page_header(
        title="Project Setup & Profile Configuration",
        subtitle="Define project parameters, organizational constraints, and requirements profile for downstream decision models.",
        module_tag="VTU 24CS51: Module 1 & 2",
        co_tag="CO1: Formulate Software Requirements & Process Constraints",
    )

    db: DatabaseManager = st.session_state.db
    all_projects = db.list_projects()

    # Top Toolbar: Active Project Selection & Management
    col_sel, col_new, col_reset = st.columns([3, 1.2, 1.2])

    with col_sel:
        proj_options = {p["id"]: p["name"] for p in all_projects}
        curr_id = st.session_state.get("current_project_id")
        # Ensure curr_id is valid
        if curr_id not in proj_options and proj_options:
            curr_id = list(proj_options.keys())[0]
            st.session_state.current_project_id = curr_id

        selected_id = st.selectbox(
            "📁 Select Active Project:",
            options=list(proj_options.keys()),
            format_func=lambda x: f"{proj_options[x]} (ID: {x})",
            index=list(proj_options.keys()).index(curr_id) if curr_id in proj_options else 0,
            key="proj_selector",
        )
        if selected_id != st.session_state.current_project_id:
            st.session_state.current_project_id = selected_id
            st.session_state.current_project = db.get_project_by_id(selected_id)
            st.rerun()

    with col_new:
        st.write("")
        st.write("")
        if st.button("➕ Create New", use_container_width=True):
            st.session_state.show_create_modal = True

    with col_reset:
        st.write("")
        st.write("")
        if st.button("🔄 Reset Samples", help="Reset database to 3 VTU benchmark projects", use_container_width=True):
            db.reset_to_defaults()
            all_projects = db.list_projects()
            st.session_state.current_project_id = all_projects[0]["id"]
            st.session_state.current_project = db.get_project_by_id(all_projects[0]["id"])
            st.success("Database restored to default sample projects!")
            st.rerun()

    # Optional Create New Form
    if st.session_state.get("show_create_modal", False):
        with st.expander("📝 Create New Project", expanded=True):
            with st.form("new_project_form"):
                new_name = st.text_input("Project Name *", placeholder="e.g. Smart Logistics Tracking Platform")
                new_desc = st.text_area("Project Description", placeholder="Outline scope, end-users, and operational environment...")
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_team = st.number_input("Team Size (Staff)", min_value=1, max_value=500, value=6)
                with c2:
                    new_dur = st.number_input("Duration (Months)", min_value=1, max_value=120, value=8)
                with c3:
                    new_budget = st.number_input("Budget ($ / ₹)", min_value=1000.0, value=75000.0, step=5000.0)

                submitted = st.form_submit_button("Save & Activate Project", type="primary")
                if submitted:
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
                        st.session_state.show_create_modal = False
                        st.success(f"Project '{new_name}' created successfully!")
                        st.rerun()

    # Active Project Form
    active = st.session_state.get("current_project")
    if not active:
        st.warning("No active project loaded.")
        return

    st.markdown("---")

    # Overview KPI Cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Team Size", f"{active.get('team_size', 0)} Engineers")
    with m2:
        st.metric("Planned Duration", f"{active.get('duration', 0)} Months")
    with m3:
        st.metric("Allocated Budget", f"${float(active.get('budget', 0)):,.0f}")
    with m4:
        st.metric("Requirement Stability", active.get("req_stability", "Medium"))
    with m5:
        st.metric("Risk Profile", active.get("risk_level", "Medium"))

    st.markdown("### ⚙️ Edit Project Configuration")

    with st.form("edit_project_form"):
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("#### 📌 Administrative Profile")
            p_name = st.text_input("Project Name", value=active.get("name", ""))
            p_desc = st.text_area("Description & Objectives", value=active.get("description", ""), height=110)

            c_sub1, c_sub2, c_sub3 = st.columns(3)
            with c_sub1:
                p_team = st.number_input("Team Size", min_value=1, max_value=1000, value=int(active.get("team_size", 6)))
            with c_sub2:
                p_dur = st.number_input("Duration (Mos)", min_value=1, max_value=120, value=int(active.get("duration", 8)))
            with c_sub3:
                p_budget = st.number_input("Budget ($ / ₹)", min_value=100.0, value=float(active.get("budget", 50000.0)), step=5000.0)

        with col_right:
            st.markdown("#### 🎯 Process Model & Decision Drivers")
            levels = ["High", "Medium", "Low"]

            p_stability = st.selectbox(
                "Requirement Stability (Volatility)",
                options=levels,
                index=levels.index(active.get("req_stability", "Medium")),
                help="High = strictly fixed/defined; Low = dynamic, frequently changing requirements.",
            )

            p_involvement = st.selectbox(
                "Customer Involvement Level",
                options=levels,
                index=levels.index(active.get("customer_involvement", "Medium")),
                help="High = on-site stakeholder or sprint reviews; Low = customer signs off only at delivery.",
            )

            p_risk = st.selectbox(
                "Anticipated Technical & Project Risk",
                options=levels,
                index=levels.index(active.get("risk_level", "Medium")),
                help="High = unproven hardware, tight regulatory mandates; Low = routine CRUD software.",
            )

            c_drv1, c_drv2 = st.columns(2)
            with c_drv1:
                p_early = st.selectbox(
                    "Need for Early Delivery",
                    options=levels,
                    index=levels.index(active.get("early_delivery", "Medium")),
                    help="Need to release MVP / working increments rapidly.",
                )
            with c_drv2:
                p_exp = st.selectbox(
                    "Team Experience Level",
                    options=levels,
                    index=levels.index(active.get("team_experience", "Medium")),
                    help="Experience with domain, technology stack, and methodologies.",
                )

        btn_save, btn_del = st.columns([4, 1])
        with btn_save:
            save_clicked = st.form_submit_button("💾 Save Project Changes", type="primary", use_container_width=True)
        with btn_del:
            delete_clicked = st.form_submit_button("🗑️ Delete Project", use_container_width=True)

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
            st.success("Project updated and saved to SQLite!")
            st.rerun()

        if delete_clicked:
            if len(all_projects) <= 1:
                st.error("Cannot delete the only remaining project. Create another project first.")
            else:
                db.delete_project(active["id"])
                all_projects = db.list_projects()
                st.session_state.current_project_id = all_projects[0]["id"]
                st.session_state.current_project = db.get_project_by_id(all_projects[0]["id"])
                st.warning(f"Project '{active['name']}' deleted.")
                st.rerun()

