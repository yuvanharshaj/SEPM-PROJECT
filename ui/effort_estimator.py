"""Effort & Size Estimator UI: Basic COCOMO, Albrecht FPA, COSMIC FFP, and PERT."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.cocomo import calculate_cocomo, COCOMO_COEFFICIENTS
from core.function_points import (
    calculate_function_points,
    FP_COMPLEXITY_WEIGHTS,
    GENERAL_SYSTEM_CHARACTERISTICS,
    LANGUAGE_LOC_FACTORS,
)
from core.cosmic import calculate_cosmic_ffp
from core.pert import calculate_pert
from ui.theme import render_page_header, render_kpi_card, render_empty_state_html, apply_plotly_theme
from db.database import DatabaseManager


def render_effort_estimator_page():
    render_page_header(
        title="Software Effort & Sizing Workbench",
        subtitle="Empirical & algorithmic estimation: Boehm's Basic COCOMO, Albrecht's FPA, COSMIC FFP, and PERT 3-point analysis.",
        module_tag="VTU 24CS51: Module 4 & 5",
        co_tag="CO4: Algorithmic & Decomposition Effort Estimation",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.markdown(
            render_empty_state_html(
                icon="📐",
                title="No Active Project Selected",
                description="Please select or configure a project benchmark in 'Project Setup' to perform sizing and effort estimation.",
            ),
            unsafe_allow_html=True,
        )
        return

    db: DatabaseManager = st.session_state.db

    # Summary Comparison Card at the top
    curr_kloc = float(active.get("kloc", 25.0))
    curr_mode = active.get("cocomo_mode", "organic")
    cocomo_quick = calculate_cocomo(curr_kloc, curr_mode)

    st.markdown(
        f"""
        <div class="pc-card" style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(13, 148, 136, 0.05)); border: 1px solid rgba(37, 99, 235, 0.2); margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: var(--pc-primary-dark, #1E40AF); letter-spacing: 0.04em;">Estimation Baseline &bull; {active.get('name', 'N/A')}</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: var(--pc-text-main, #0F172A); margin-top: 2px;">
                        {curr_kloc:.1f} KLOC Codebase &bull; {curr_mode.title()} Lifecycle
                    </div>
                </div>
                <div style="display: flex; gap: 16px; font-size: 0.88rem; font-weight: 600; color: var(--pc-text-muted, #64748B);">
                    <span>Effort: <b style="color: var(--pc-primary, #2563EB);">{cocomo_quick.effort_pm:.1f} PM</b></span>
                    <span>&bull;</span>
                    <span>Duration: <b style="color: var(--pc-accent, #0D9488);">{cocomo_quick.duration_months:.1f} Mos</b></span>
                    <span>&bull;</span>
                    <span>Staff: <b style="color: var(--pc-text-main, #0F172A);">{cocomo_quick.avg_staff:.1f} Engineers</b></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_cocomo, tab_fp, tab_cosmic, tab_pert = st.tabs([
        "📐 (a) Basic COCOMO Model",
        "🔢 (b) Function Point Analysis (FPA)",
        "🌌 (c) COSMIC Full Function Points",
        "🎯 (d) Bottom-Up / PERT Three-Point",
    ])

    # -------------------------------------------------------------
    # TAB A: BASIC COCOMO
    # -------------------------------------------------------------
    with tab_cocomo:
        st.markdown("### Boehm's Basic COCOMO Formulation")
        st.latex(r"Effort = a \cdot (\text{KLOC})^b \quad [\text{Person-Months}]")
        st.latex(r"Time = c \cdot (Effort)^d \quad [\text{Months}], \quad Staff = \frac{Effort}{Time} \quad [\text{Persons}]")

        col_in1, col_in2 = st.columns([1, 1])

        with col_in1:
            modes = ["organic", "semi-detached", "embedded"]
            selected_mode = st.selectbox(
                "Development Mode:",
                options=modes,
                index=modes.index(curr_mode) if curr_mode in modes else 0,
                format_func=lambda x: f"{x.title()} Mode — {COCOMO_COEFFICIENTS[x]['description']}",
            )

        with col_in2:
            input_kloc = st.number_input(
                "Estimated Codebase Size (KLOC - Thousands of LOC):",
                min_value=0.5,
                max_value=2000.0,
                value=curr_kloc,
                step=1.0,
                help="1 KLOC = 1,000 physical source lines of code",
            )

        coeff = COCOMO_COEFFICIENTS[selected_mode]
        st.caption(
            f"**Active Empirical Constants ({selected_mode.title()}):** "
            f"a = {coeff['a']}, b = {coeff['b']}, c = {coeff['c']}, d = {coeff['d']}"
        )

        cocomo_res = calculate_cocomo(input_kloc, selected_mode)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        m_cols = st.columns(4)
        with m_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="Required Effort",
                    value=f"{cocomo_res.effort_pm:.1f} PM",
                    subtitle="Person-Months of labor",
                    icon="💼",
                    accent_color="#2563EB",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Development Schedule",
                    value=f"{cocomo_res.duration_months:.1f} Mos",
                    subtitle="Nominal calendar duration",
                    icon="⏱️",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[2]:
            st.markdown(
                render_kpi_card(
                    label="Staffing Capacity",
                    value=f"{cocomo_res.avg_staff:.1f} Staff",
                    subtitle="Average team size",
                    icon="👥",
                    accent_color="#10B981",
                ),
                unsafe_allow_html=True,
            )
        with m_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="Productivity Rate",
                    value=f"{cocomo_res.productivity_loc_pm:.0f}",
                    subtitle="LOC / Person-Month",
                    icon="⚡",
                    accent_color="#8B5CF6",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📈 Multi-Mode Comparative Sensitivity")
        kloc_range = [max(1.0, input_kloc * f) for f in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]]
        comparison_records = []
        for m in modes:
            for k in kloc_range:
                res = calculate_cocomo(k, m)
                comparison_records.append({
                    "KLOC": round(k, 1),
                    "Mode": m.title(),
                    "Effort (PM)": round(res.effort_pm, 1),
                    "Duration (Mos)": round(res.duration_months, 1),
                })
        df_comp = pd.DataFrame(comparison_records)

        fig_cocomo = px.line(
            df_comp,
            x="KLOC",
            y="Effort (PM)",
            color="Mode",
            markers=True,
        )
        fig_cocomo = apply_plotly_theme(fig_cocomo, title="Effort Scaling Across COCOMO Modes", height=340)
        st.plotly_chart(fig_cocomo, use_container_width=True)

        if st.button("💾 Persist COCOMO Parameters to Active Project"):
            active["cocomo_mode"] = selected_mode
            active["kloc"] = float(input_kloc)
            db.save_complete_project(active)
            st.success("COCOMO sizing parameters saved to SQLite database!")

    # -------------------------------------------------------------
    # TAB B: FUNCTION POINTS (Albrecht FPA)
    # -------------------------------------------------------------
    with tab_fp:
        st.markdown("### Albrecht's Function Point Analysis (FPA)")
        st.latex(r"UFP = \sum (\text{Component Count} \times \text{Weight})")
        st.latex(r"VAF = 0.65 + \left( 0.01 \times \sum_{i=1}^{14} F_i \right), \quad AFP = UFP \times VAF")

        saved_fp = active.get("fp_components") or {
            "EI": {"low": 10, "average": 15, "high": 5},
            "EO": {"low": 8, "average": 12, "high": 4},
            "EQ": {"low": 10, "average": 15, "high": 4},
            "ILF": {"low": 4, "average": 8, "high": 3},
            "EIF": {"low": 2, "average": 4, "high": 2},
        }
        saved_gsc = active.get("gsc_ratings") or [3] * 14

        st.markdown("#### 1. Information Domain Characteristics (UFP)")
        st.caption("Count user transactions and logical files across Low, Average, and High complexity:")

        comp_inputs = {}
        for comp_key, weights in FP_COMPLEXITY_WEIGHTS.items():
            st.markdown(f"**{weights['name']}** *(Weights: Low={weights['low']}, Avg={weights['average']}, High={weights['high']})*")
            c_low, c_avg, c_high = st.columns(3)
            with c_low:
                cnt_low = st.number_input(
                    f"{comp_key} Low",
                    min_value=0,
                    value=int(saved_fp.get(comp_key, {}).get("low", 0)),
                    key=f"fp_{comp_key}_low",
                )
            with c_avg:
                cnt_avg = st.number_input(
                    f"{comp_key} Average",
                    min_value=0,
                    value=int(saved_fp.get(comp_key, {}).get("average", 0)),
                    key=f"fp_{comp_key}_avg",
                )
            with c_high:
                cnt_high = st.number_input(
                    f"{comp_key} High",
                    min_value=0,
                    value=int(saved_fp.get(comp_key, {}).get("high", 0)),
                    key=f"fp_{comp_key}_high",
                )
            comp_inputs[comp_key] = {"low": cnt_low, "average": cnt_avg, "high": cnt_high}

        st.markdown("---")
        st.markdown("#### 2. 14 General System Characteristics (GSCs / TDI)")
        with st.expander("Expand to Rate 14 Technical Environmental Factors (0 = No Influence, 5 = Strongest)", expanded=False):
            gsc_cols = st.columns(2)
            gsc_ratings = []
            for idx, gsc_name in enumerate(GENERAL_SYSTEM_CHARACTERISTICS):
                col = gsc_cols[idx % 2]
                default_score = saved_gsc[idx] if idx < len(saved_gsc) else 3
                val = col.slider(
                    f"{idx+1}. {gsc_name}",
                    min_value=0,
                    max_value=5,
                    value=int(default_score),
                    key=f"gsc_{idx}",
                )
                gsc_ratings.append(val)

        fp_result = calculate_function_points(comp_inputs, gsc_ratings)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        f_cols = st.columns(4)
        with f_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="Unadjusted FP",
                    value=f"{fp_result.ufp:.0f}",
                    subtitle="Raw Information Domain",
                    icon="📊",
                    accent_color="#2563EB",
                ),
                unsafe_allow_html=True,
            )
        with f_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Total Degree (TDI)",
                    value=f"{fp_result.tdi} / 70",
                    subtitle="Environmental Rating",
                    icon="🌐",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with f_cols[2]:
            st.markdown(
                render_kpi_card(
                    label="Adjustment (VAF)",
                    value=f"{fp_result.vaf:.4f}",
                    subtitle="Multiplier (0.65 - 1.35)",
                    icon="⚙️",
                    accent_color="#F59E0B",
                ),
                unsafe_allow_html=True,
            )
        with f_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="Adjusted FP (AFP)",
                    value=f"{fp_result.afp:.1f}",
                    subtitle="Final Normalized Sizing",
                    icon="🎯",
                    accent_color="#10B981",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 3. Language Gear Factors & Equivalent Sizing (FP ➡️ KLOC)")
        df_lang = pd.DataFrame([
            {
                "Language": lang,
                "LOC / FP": factor,
                "Equivalent KLOC": round(kloc_val, 2),
                "Equivalent Lines of Code": f"{kloc_val * 1000:,.0f}",
            }
            for lang, kloc_val in fp_result.kloc_by_language.items()
            for factor in [LANGUAGE_LOC_FACTORS[lang]]
        ])

        col_lang_tbl, col_lang_action = st.columns([2, 1])
        with col_lang_tbl:
            st.dataframe(df_lang, use_container_width=True, hide_index=True)

        with col_lang_action:
            st.markdown("##### 🔗 Connect FP to COCOMO")
            target_lang = st.selectbox("Select Target Language:", options=list(LANGUAGE_LOC_FACTORS.keys()), index=0)
            target_kloc = fp_result.kloc_by_language.get(target_lang, 20.0)
            st.info(f"Target Size: **{target_kloc:.2f} KLOC** in {target_lang}")

            if st.button("Apply FP Sizing to Project COCOMO", type="primary", use_container_width=True):
                active["kloc"] = round(target_kloc, 2)
                active["fp_components"] = comp_inputs
                active["gsc_ratings"] = gsc_ratings
                db.save_complete_project(active)
                st.success(f"Updated Project KLOC to {target_kloc:.2f} KLOC and saved FPA configuration!")
                st.rerun()

    # -------------------------------------------------------------
    # TAB C: COSMIC FULL FUNCTION POINTS (ISO/IEC 19761)
    # -------------------------------------------------------------
    with tab_cosmic:
        st.markdown("### COSMIC Full Function Points (FFP - ISO/IEC 19761)")
        st.markdown(
            "COSMIC measures functional size by identifying distinct **data movements** across functional boundaries. "
            "Each **Entry (E)**, **Exit (X)**, **Read (R)**, or **Write (W)** represents exactly **1 CFP**."
        )
        st.latex(r"\text{Process Size (CFP)} = E + X + R + W, \quad \text{Total Size} = \sum \text{CFP}_i")

        if "cosmic_processes" not in st.session_state:
            st.session_state.cosmic_processes = [
                {"process_id": "P-01", "name": "User Registration & KYC", "entries": 4, "exits": 3, "reads": 2, "writes": 2},
                {"process_id": "P-02", "name": "Authentication & Token Issuance", "entries": 2, "exits": 2, "reads": 2, "writes": 1},
                {"process_id": "P-03", "name": "Core Transaction Processing", "entries": 5, "exits": 4, "reads": 4, "writes": 3},
                {"process_id": "P-04", "name": "Reporting & Analytics Export", "entries": 2, "exits": 5, "reads": 4, "writes": 0},
            ]

        col_c_cfg1, col_c_cfg2 = st.columns(2)
        with col_c_cfg1:
            prod_hours = st.slider(
                "Productivity (Hours per CFP):",
                min_value=4.0,
                max_value=30.0,
                value=12.0,
                step=1.0,
                help="Industry average: 8–16 hours per COSMIC Function Point",
            )
        with col_c_cfg2:
            team_sz = int(active.get("team_size", 5))
            st.caption(f"Active project team size: **{team_sz} engineers**")

        cosmic_res = calculate_cosmic_ffp(
            st.session_state.cosmic_processes,
            productivity_hours_per_cfp=prod_hours,
            team_size=team_sz,
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        cm_cols = st.columns(4)
        with cm_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="COSMIC Size",
                    value=f"{cosmic_res.total_cfp} CFP",
                    subtitle="Data Movements",
                    icon="🌌",
                    accent_color="#2563EB",
                ),
                unsafe_allow_html=True,
            )
        with cm_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Labor Hours",
                    value=f"{cosmic_res.total_effort_hours:,.0f} Hrs",
                    subtitle=f"{prod_hours:.0f} hrs / CFP",
                    icon="⏳",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with cm_cols[2]:
            st.markdown(
                render_kpi_card(
                    label="Person-Months",
                    value=f"{cosmic_res.total_effort_pm:.1f} PM",
                    subtitle="160 hrs / month",
                    icon="💼",
                    accent_color="#10B981",
                ),
                unsafe_allow_html=True,
            )
        with cm_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="Schedule Time",
                    value=f"{cosmic_res.estimated_duration_months:.1f} Mos",
                    subtitle=f"{team_sz} staff team",
                    icon="⏱️",
                    accent_color="#8B5CF6",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        col_c_tbl, col_c_chart = st.columns([1.4, 1.0])

        with col_c_tbl:
            st.markdown("#### 📋 Functional Processes Table")
            df_cosmic = pd.DataFrame([p.to_dict() for p in cosmic_res.processes]).rename(columns={
                "process_id": "ID",
                "name": "Functional Process Name",
                "entries": "Entries (E)",
                "exits": "Exits (X)",
                "reads": "Reads (R)",
                "writes": "Writes (W)",
                "cfp": "Total CFP",
            })
            st.dataframe(df_cosmic, use_container_width=True, hide_index=True)

        with col_c_chart:
            st.markdown("#### 📊 Movement Type Distribution")
            df_movements = pd.DataFrame({
                "Data Movement": ["Entries (E)", "Exits (X)", "Reads (R)", "Writes (W)"],
                "Count (CFP)": [cosmic_res.total_entries, cosmic_res.total_exits, cosmic_res.total_reads, cosmic_res.total_writes],
            })
            fig_move = px.pie(
                df_movements,
                names="Data Movement",
                values="Count (CFP)",
                color_discrete_sequence=["#2563EB", "#0D9488", "#F59E0B", "#8B5CF6"],
                hole=0.45,
            )
            fig_move = apply_plotly_theme(fig_move, title="Data Movements", height=280)
            st.plotly_chart(fig_move, use_container_width=True)

        with st.expander("➕ Add Functional Process to COSMIC Model"):
            with st.form("add_cosmic_proc_form"):
                cp_id = st.text_input("Process ID", value=f"P-{len(st.session_state.cosmic_processes)+1:02d}")
                cp_name = st.text_input("Process Name", placeholder="e.g. Audit Log Dispatcher")
                c_e, c_x, c_r, c_w = st.columns(4)
                with c_e:
                    val_e = st.number_input("Entries (E)", min_value=0, value=2)
                with c_x:
                    val_x = st.number_input("Exits (X)", min_value=0, value=2)
                with c_r:
                    val_r = st.number_input("Reads (R)", min_value=0, value=1)
                with c_w:
                    val_w = st.number_input("Writes (W)", min_value=0, value=1)

                add_p_btn = st.form_submit_button("Add Process", type="primary")
                if add_p_btn:
                    if cp_name.strip():
                        st.session_state.cosmic_processes.append({
                            "process_id": cp_id,
                            "name": cp_name.strip(),
                            "entries": int(val_e),
                            "exits": int(val_x),
                            "reads": int(val_r),
                            "writes": int(val_w),
                        })
                        st.success(f"Added process '{cp_name}'!")
                        st.rerun()

    # -------------------------------------------------------------
    # TAB D: BOTTOM-UP / THREE-POINT (PERT)
    # -------------------------------------------------------------
    with tab_pert:
        st.markdown("### Bottom-Up & Three-Point (PERT) Estimator")
        st.markdown(
            "Decomposes the project Work Breakdown Structure (WBS) into granular tasks. "
            "For each task, estimates are provided across three scenarios to model a Beta probability distribution:"
        )
        st.latex(r"E_i = \frac{O_i + 4M_i + P_i}{6}, \quad SD_i = \frac{P_i - O_i}{6}, \quad V_i = SD_i^2")
        st.latex(r"E_{\text{total}} = \sum E_i, \quad SD_{\text{total}} = \sqrt{\sum V_i}")

        if "pert_tasks" not in st.session_state:
            st.session_state.pert_tasks = [
                {"task_id": "WBS-01", "name": "System Architecture & API Specs", "category": "Architecture", "optimistic": 20.0, "most_likely": 35.0, "pessimistic": 60.0},
                {"task_id": "WBS-02", "name": "Frontend Responsive Dashboard", "category": "Frontend", "optimistic": 40.0, "most_likely": 65.0, "pessimistic": 110.0},
                {"task_id": "WBS-03", "name": "Backend Microservices & DB Models", "category": "Backend", "optimistic": 60.0, "most_likely": 95.0, "pessimistic": 150.0},
                {"task_id": "WBS-04", "name": "Security Hardening & OAuth Integration", "category": "Security", "optimistic": 15.0, "most_likely": 30.0, "pessimistic": 55.0},
                {"task_id": "WBS-05", "name": "Integration & End-to-End Testing", "category": "QA / Testing", "optimistic": 25.0, "most_likely": 45.0, "pessimistic": 80.0},
            ]

        pert_res = calculate_pert(st.session_state.pert_tasks)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        p_cols = st.columns(4)
        with p_cols[0]:
            st.markdown(
                render_kpi_card(
                    label="Expected Effort",
                    value=f"{pert_res.total_expected:.1f} Hrs",
                    subtitle=f"{pert_res.total_expected / 160.0:.2f} Person-Months",
                    icon="🎯",
                    accent_color="#2563EB",
                ),
                unsafe_allow_html=True,
            )
        with p_cols[1]:
            st.markdown(
                render_kpi_card(
                    label="Std Deviation (σ)",
                    value=f"±{pert_res.combined_sd:.2f} Hrs",
                    subtitle=f"Variance: {pert_res.combined_variance:.1f}",
                    icon="📏",
                    accent_color="#0D9488",
                ),
                unsafe_allow_html=True,
            )
        with p_cols[2]:
            st.markdown(
                render_kpi_card(
                    label="90% Range",
                    value=f"{pert_res.confidence_90_range[0]:.0f}–{pert_res.confidence_90_range[1]:.0f} H",
                    subtitle="Z = 1.645 Confidence",
                    icon="🔒",
                    accent_color="#10B981",
                ),
                unsafe_allow_html=True,
            )
        with p_cols[3]:
            st.markdown(
                render_kpi_card(
                    label="WBS Scope",
                    value=f"{pert_res.total_tasks} Tasks",
                    subtitle="Decomposed Work Items",
                    icon="📋",
                    accent_color="#8B5CF6",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        col_p_tbl, col_p_chart = st.columns([1.4, 1.0])

        with col_p_tbl:
            st.markdown("#### 📋 WBS Task Estimates (Hours)")
            df_pert = pd.DataFrame([t.to_dict() for t in pert_res.tasks]).rename(columns={
                "task_id": "WBS ID",
                "name": "Task Name",
                "category": "Category",
                "optimistic": "Opt (O)",
                "most_likely": "Likely (M)",
                "pessimistic": "Pess (P)",
                "expected": "Expected (E)",
                "standard_deviation": "SD",
            })
            st.dataframe(df_pert[["WBS ID", "Task Name", "Category", "Opt (O)", "Likely (M)", "Pess (P)", "Expected (E)", "SD"]], use_container_width=True, hide_index=True)

        with col_p_chart:
            st.markdown("#### 🎯 Statistical Confidence Intervals")
            df_conf = pd.DataFrame([
                {"Level": "68% (±1.00σ)", "Lower (Hrs)": f"{pert_res.confidence_68_range[0]:.1f}", "Upper (Hrs)": f"{pert_res.confidence_68_range[1]:.1f}"},
                {"Level": "90% (±1.645σ)", "Lower (Hrs)": f"{pert_res.confidence_90_range[0]:.1f}", "Upper (Hrs)": f"{pert_res.confidence_90_range[1]:.1f}"},
                {"Level": "95% (±1.96σ)", "Lower (Hrs)": f"{pert_res.confidence_95_range[0]:.1f}", "Upper (Hrs)": f"{pert_res.confidence_95_range[1]:.1f}"},
            ])
            st.dataframe(df_conf, use_container_width=True, hide_index=True)

            if pert_res.category_breakdown:
                fig_cat = px.bar(
                    x=list(pert_res.category_breakdown.keys()),
                    y=list(pert_res.category_breakdown.values()),
                    labels={"x": "WBS Category", "y": "Expected Effort (Hours)"},
                    color=list(pert_res.category_breakdown.keys()),
                )
                fig_cat = apply_plotly_theme(fig_cat, title="Effort by WBS Category", height=240, show_legend=False)
                st.plotly_chart(fig_cat, use_container_width=True)

        with st.expander("➕ Add WBS Task to PERT Estimator"):
            with st.form("add_pert_task_form"):
                pt_id = st.text_input("Task ID", value=f"WBS-{len(st.session_state.pert_tasks)+1:02d}")
                pt_name = st.text_input("Task Name", placeholder="e.g. CI/CD Deployment Pipeline Setup")
                pt_cat = st.selectbox("Category", ["Architecture", "Backend", "Frontend", "Security", "QA / Testing", "DevOps"])
                co1, co2, co3 = st.columns(3)
                with co1:
                    po = st.number_input("Optimistic Hours (O)", min_value=1.0, value=10.0, step=2.0)
                with co2:
                    pm = st.number_input("Most Likely Hours (M)", min_value=1.0, value=20.0, step=2.0)
                with co3:
                    pp = st.number_input("Pessimistic Hours (P)", min_value=1.0, value=40.0, step=5.0)

                add_task_btn = st.form_submit_button("Add Task", type="primary")
                if add_task_btn:
                    if po > pm or pm > pp:
                        st.error("Estimates must satisfy: Optimistic <= Most Likely <= Pessimistic")
                    elif pt_name.strip():
                        st.session_state.pert_tasks.append({
                            "task_id": pt_id,
                            "name": pt_name.strip(),
                            "category": pt_cat,
                            "optimistic": float(po),
                            "most_likely": float(pm),
                            "pessimistic": float(pp),
                        })
                        st.success(f"Added task '{pt_name}' to PERT estimator!")
                        st.rerun()
