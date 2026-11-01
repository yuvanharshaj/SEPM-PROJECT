"""Project Setup & SQLite Persistence UI."""

import streamlit as st
from db.database import DatabaseManager
from ui.theme import render_page_header, render_kpi_card
from ui.format import format_currency, get_currency_symbol


def render_project_setup_page():
    render_page_header(
        title="Project Setup & Profile Configuration",
        subtitle="Define project scope, organizational constraints, and requirements drivers for downstream decision models.",
        module_tag="VTU 24CS51: Module 1 & 3",
        co_tag="CO1 & CO3: Requirements Formulation & Project Baseline",
    )

    db: DatabaseManager = st.session_state.db
    all_projects = db.list_projects()
    sym = get_currency_symbol()

    # 1. Hero Section
    st.markdown(
        f"""
        <div class="pc-card" style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(13, 148, 136, 0.06)); border: 1px solid rgba(37, 99, 235, 0.18); margin-bottom: 22px;">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="max-width: 820px;">
                    <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(37, 99, 235, 0.12); color: var(--pc-primary-dark, #1E40AF); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 3px 10px; border-radius: 9999px; margin-bottom: 8px;">
                        <span>🎓 Academic Decision Engine</span>
                    </div>
                    <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: var(--pc-text-main, #0F172A); letter-spacing: -0.01em;">
                        Welcome to ProcessCompass
                    </h3>
                    <p style="margin: 6px 0 0 0; font-size: 0.92rem; color: var(--pc-text-muted, #64748B); line-height: 1.55;">
                        ProcessCompass evaluates software engineering parameters across VTU 24CS51 syllabus modules:
                        <b>Process Model Selection (CO1)</b>, <b>Agile Sprint Planning & Cost Curves (CO2)</b>, <b>Economic Viability & EMV (CO3)</b>,
                        <b>Parametric Estimation (COCOMO, FPA, COSMIC, PERT) & Risk Heatmaps (CO4)</b>, and <b>McCall Quality Assurance (CO5)</b>.
                    </p>
                </div>
                <div style="background: var(--pc-card-bg, #FFFFFF); padding: 12px 18px; border-radius: 12px; border: 1px solid var(--pc-border, #E2E8F0); text-align: center; min-width: 170px;">
                    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: var(--pc-text-muted, #64748B);">Total Benchmarks</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: var(--pc-primary, #2563EB); margin-top: 2px;">{len(all_projects)}</div>
                    <div style="font-size: 0.72rem; color: var(--pc-text-subtle, #94A3B8);">SQLite Backed</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Three Benchmark Quick-Load Cards
    st.markdown("#### ⚡ Preloaded VTU Benchmarks")
    b_cols = st.columns(3)

    benchmark_meta = [
        {"name": "College ERP System", "tag": "Semi-Detached", "icon": "🎓", "color": "#2563EB", "desc": "Campus admin suite, 15k students, 14 staff, moderate volatility."},
        {"name": "Mobile Banking App", "tag": "Agile / Scrum", "icon": "📱", "color": "#0D9488", "desc": "Fintech platform with UPI/IMPS, biometric login, high velocity."},
        {"name": "Embedded IoT Medical Device", "tag": "Waterfall / Embedded", "icon": "🏥", "color": "#F59E0B", "desc": "Cortex-M4 safety-critical wearable, strict FDA audit standards."},
    ]

    for idx, b_info in enumerate(benchmark_meta):
        with b_cols[idx]:
            match_proj = next((p for p in all_projects if p["name"] == b_info["name"]), None)
            proj_data = db.get_project_by_id(match_proj["id"]) if match_proj else None
            b_budget = format_currency(proj_data.get("budget", 0), compact=True) if proj_data else "N/A"
            b_team = f"{proj_data.get('team_size', 0)} Engineers" if proj_data else ""
            b_dur = f"{proj_data.get('duration', 0)} Mos" if proj_data else ""

            st.markdown(
                f"""
                <div class="pc-card" style="padding: 16px; margin-bottom: 12px; border-top: 3px solid {b_info['color']};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 1.3rem;">{b_info['icon']}</span>
                        <span style="font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; background: rgba(0,0,0,0.05); color: {b_info['color']};">{b_info['tag']}</span>
                    </div>
                    <div style="font-weight: 700; font-size: 0.98rem; color: var(--pc-text-main, #0F172A); margin-bottom: 4px;">{b_info['name']}</div>
                    <div style="font-size: 0.8rem; color: var(--pc-text-muted, #64748B); line-height: 1.4; margin-bottom: 10px; min-height: 38px;">{b_info['desc']}</div>
                    <div style="font-size: 0.78rem; font-weight: 600; color: var(--pc-text-main, #0F172A); margin-bottom: 12px;">
                        💰 {b_budget} &bull; 👥 {b_team} &bull; ⏱️ {b_dur}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if match_proj:
                is_active = (st.session_state.get("current_project_id") == match_proj["id"])
                btn_label = "✅ Currently Active" if is_active else f"Load {b_info['name'].split()[0]}"
                if st.button(btn_label, key=f"btn_bench_{idx}", disabled=is_active, use_container_width=True):
                    st.session_state.current_project_id = match_proj["id"]
                    st.session_state.current_project = db.get_project_by_id(match_proj["id"])
                    st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Active Project Selector Toolbar
    col_sel, col_new, col_reset = st.columns([3, 1.2, 1.2])

    with col_sel:
        proj_options = {p["id"]: p["name"] for p in all_projects}
        curr_id = st.session_state.get("current_project_id")
        if curr_id not in proj_options and proj_options:
            curr_id = list(proj_options.keys())[0]
            st.session_state.current_project_id = curr_id

        selected_id = st.selectbox(
            "📁 Active Project Profile:",
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
        if st.button("➕ New Project", use_container_width=True):
            st.session_state.show_create_modal = not st.session_state.get("show_create_modal", False)

    with col_reset:
        st.write("")
        st.write("")
        if st.button("🔄 Reset Defaults", help="Reset SQLite database to the 3 default benchmarks", use_container_width=True):
            db.reset_to_defaults()
            all_projects = db.list_projects()
            st.session_state.current_project_id = all_projects[0]["id"]
            st.session_state.current_project = db.get_project_by_id(all_projects[0]["id"])
            st.success("Database restored to default sample projects!")
            st.rerun()

    # Optional Create New Form
    if st.session_state.get("show_create_modal", False):
        with st.expander("📝 Register New Project Specification", expanded=True):
            with st.form("new_project_form"):
                new_name = st.text_input("Project Name *", placeholder="e.g. Distributed Warehouse Inventory System")
                new_desc = st.text_area("Scope & Operational Objectives", placeholder="Outline scope, architecture, key stakeholder expectations...")
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_team = st.number_input("Team Size (Staff)", min_value=1, max_value=500, value=8)
                with c2:
                    new_dur = st.number_input("Duration (Months)", min_value=1, max_value=120, value=10)
                with c3:
                    new_budget = st.number_input(f"Allocated Budget ({sym})", min_value=1000.0, value=5000000.0, step=100000.0)

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
                            "kloc": 30.0,
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
                        st.success(f"Project '{new_name}' created and activated!")
                        st.rerun()

    active = st.session_state.get("current_project")
    if not active:
        st.warning("No active project loaded.")
        return

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4. Overview KPI Cards (Modern animated cards)
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.markdown(
            render_kpi_card(
                label="Team Staffing",
                value=f"{active.get('team_size', 0)} Engineers",
                subtitle="Core Project Team",
                icon="👥",
                accent_color="#2563EB",
            ),
            unsafe_allow_html=True,
        )
    with kpi_cols[1]:
        st.markdown(
            render_kpi_card(
                label="Schedule Horizon",
                value=f"{active.get('duration', 0)} Mos",
                subtitle="Planned Delivery",
                icon="⏱️",
                accent_color="#0D9488",
            ),
            unsafe_allow_html=True,
        )
    with kpi_cols[2]:
        st.markdown(
            render_kpi_card(
                label="Capital Budget",
                value=format_currency(active.get("budget", 0), compact=True),
                subtitle=format_currency(active.get("budget", 0), compact=False, precision=0),
                icon="💰",
                accent_color="#10B981",
            ),
            unsafe_allow_html=True,
        )
    with kpi_cols[3]:
        st.markdown(
            render_kpi_card(
                label="Req Volatility",
                value=str(active.get("req_stability", "Medium")),
                subtitle="Change Frequency",
                icon="📊",
                accent_color="#8B5CF6",
            ),
            unsafe_allow_html=True,
        )
    with kpi_cols[4]:
        st.markdown(
            render_kpi_card(
                label="Risk Exposure",
                value=str(active.get("risk_level", "Medium")),
                subtitle="Project Risk Level",
                icon="⚠️",
                accent_color="#F59E0B",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 5. Edit Form in 2-Column Cards
    with st.form("edit_project_form"):
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown(
                """
                <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; color: var(--pc-text-main, #0F172A); display: flex; align-items: center; gap: 6px;">
                    <span>📌</span> <span>Administrative & Scope Profile</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            p_name = st.text_input("Project Name", value=active.get("name", ""))
            p_desc = st.text_area("Scope Description & System Boundaries", value=active.get("description", ""), height=115)

            c_sub1, c_sub2, c_sub3 = st.columns(3)
            with c_sub1:
                p_team = st.number_input("Team Size", min_value=1, max_value=1000, value=int(active.get("team_size", 6)))
            with c_sub2:
                p_dur = st.number_input("Duration (Mos)", min_value=1, max_value=120, value=int(active.get("duration", 8)))
            with c_sub3:
                p_budget = st.number_input(f"Budget ({sym})", min_value=100.0, value=float(active.get("budget", 5000000.0)), step=100000.0)

        with col_right:
            st.markdown(
                """
                <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; color: var(--pc-text-main, #0F172A); display: flex; align-items: center; gap: 6px;">
                    <span>🎯</span> <span>VTU Decision & Process Drivers</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            levels = ["High", "Medium", "Low"]

            p_stability = st.selectbox(
                "Requirement Stability (Volatility)",
                options=levels,
                index=levels.index(active.get("req_stability", "Medium")),
                help="High = fixed/frozen requirements; Low = frequent mid-course changes.",
            )

            p_involvement = st.selectbox(
                "Customer Involvement Level",
                options=levels,
                index=levels.index(active.get("customer_involvement", "Medium")),
                help="High = weekly agile collaboration; Low = handoff only at final acceptance.",
            )

            p_risk = st.selectbox(
                "Anticipated Technical & Schedule Risk",
                options=levels,
                index=levels.index(active.get("risk_level", "Medium")),
                help="High = safety-critical, unfamiliar stack, strict audits; Low = standard architecture.",
            )

            c_drv1, c_drv2 = st.columns(2)
            with c_drv1:
                p_early = st.selectbox(
                    "Need for Early Delivery",
                    options=levels,
                    index=levels.index(active.get("early_delivery", "Medium")),
                    help="Need to deliver early working increments / MVP quickly.",
                )
            with c_drv2:
                p_exp = st.selectbox(
                    "Team Experience Level",
                    options=levels,
                    index=levels.index(active.get("team_experience", "Medium")),
                    help="Familiarity with technology stack, toolchains, and software engineering processes.",
                )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        btn_save, btn_del = st.columns([4, 1])
        with btn_save:
            save_clicked = st.form_submit_button("💾 Save Project Configuration", type="primary", use_container_width=True)
        with btn_del:
            delete_clicked = st.form_submit_button("🗑️ Delete", use_container_width=True)

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
            st.success("Project updated and persisted to SQLite!")
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
