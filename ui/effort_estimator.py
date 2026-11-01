"""Software effort and sizing estimation workbench."""

import streamlit as st
import pandas as pd
import plotly.express as px

from core.cocomo import calculate_cocomo, COCOMO_COEFFICIENTS
from core.function_points import (
    calculate_function_points,
    FP_COMPLEXITY_WEIGHTS,
    GENERAL_SYSTEM_CHARACTERISTICS,
    LANGUAGE_LOC_FACTORS,
)
from core.cosmic import calculate_cosmic_ffp
from core.pert import calculate_pert
from ui.components import render_page_header
from ui.theme import apply_plotly_theme
from db.database import DatabaseManager


def render_effort_estimator_page():
    render_page_header(
        title="Effort estimator",
        caption="Empirical and decomposition models: Basic COCOMO, Albrecht FPA, COSMIC FFP, and PERT.",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.info("No active project loaded. Configure a project in Setup.")
        return

    db: DatabaseManager = st.session_state.db

    tab_cocomo, tab_fp, tab_cosmic, tab_pert = st.tabs([
        "COCOMO",
        "Function points",
        "COSMIC FFP",
        "PERT",
    ])

    # -------------------------------------------------------------
    # TAB 1: BASIC COCOMO
    # -------------------------------------------------------------
    with tab_cocomo:
        curr_mode = active.get("cocomo_mode", "organic")
        curr_kloc = float(active.get("kloc", 25.0))

        col_in1, col_in2 = st.columns(2)
        with col_in1:
            modes = ["organic", "semi-detached", "embedded"]
            selected_mode = st.selectbox(
                "Development mode",
                options=modes,
                index=modes.index(curr_mode) if curr_mode in modes else 0,
                format_func=lambda x: f"{x.capitalize()} mode: {COCOMO_COEFFICIENTS[x]['description']}",
            )
        with col_in2:
            input_kloc = st.number_input(
                "Estimated size (KLOC)",
                min_value=0.5,
                max_value=2000.0,
                value=curr_kloc,
                step=1.0,
            )

        cocomo_res = calculate_cocomo(input_kloc, selected_mode)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.metric("Effort", f"{cocomo_res.effort_pm:.1f} PM")
        with m2:
            with st.container(border=True):
                st.metric("Schedule", f"{cocomo_res.duration_months:.1f} months")
        with m3:
            with st.container(border=True):
                st.metric("Average staff", f"{cocomo_res.avg_staff:.1f} staff")
        with m4:
            with st.container(border=True):
                st.metric("Productivity", f"{cocomo_res.productivity_loc_pm:.0f} LOC/PM")

        st.markdown("## Sensitivity analysis")
        kloc_range = [max(1.0, input_kloc * f) for f in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]]
        comparison_records = []
        for m in modes:
            for k in kloc_range:
                res = calculate_cocomo(k, m)
                comparison_records.append({
                    "KLOC": round(k, 1),
                    "Mode": m.capitalize(),
                    "Effort (PM)": round(res.effort_pm, 1),
                })
        df_comp = pd.DataFrame(comparison_records)

        fig_cocomo = px.line(
            df_comp,
            x="KLOC",
            y="Effort (PM)",
            color="Mode",
            markers=True,
            color_discrete_sequence=["#1d4ed8", "#475569", "#94a3b8"],
        )
        fig_cocomo = apply_plotly_theme(fig_cocomo, height=320)
        st.plotly_chart(fig_cocomo, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})

        if st.button("Save COCOMO sizing to project"):
            active["cocomo_mode"] = selected_mode
            active["kloc"] = float(input_kloc)
            db.save_complete_project(active)
            st.success("COCOMO parameters saved.")

    # -------------------------------------------------------------
    # TAB 2: FUNCTION POINTS (Albrecht FPA)
    # -------------------------------------------------------------
    with tab_fp:
        saved_fp = active.get("fp_components") or {
            "EI": {"low": 10, "average": 15, "high": 5},
            "EO": {"low": 8, "average": 12, "high": 4},
            "EQ": {"low": 10, "average": 15, "high": 4},
            "ILF": {"low": 4, "average": 8, "high": 3},
            "EIF": {"low": 2, "average": 4, "high": 2},
        }
        saved_gsc = active.get("gsc_ratings") or [3] * 14

        st.markdown("## Information domain counts")
        comp_inputs = {}
        for comp_key, weights in FP_COMPLEXITY_WEIGHTS.items():
            st.markdown(f"**{weights['name']}** (Low={weights['low']}, Avg={weights['average']}, High={weights['high']})")
            c_low, c_avg, c_high = st.columns(3)
            with c_low:
                cnt_low = st.number_input(f"{comp_key} low", min_value=0, value=int(saved_fp.get(comp_key, {}).get("low", 0)), key=f"fp_{comp_key}_low")
            with c_avg:
                cnt_avg = st.number_input(f"{comp_key} avg", min_value=0, value=int(saved_fp.get(comp_key, {}).get("average", 0)), key=f"fp_{comp_key}_avg")
            with c_high:
                cnt_high = st.number_input(f"{comp_key} high", min_value=0, value=int(saved_fp.get(comp_key, {}).get("high", 0)), key=f"fp_{comp_key}_high")
            comp_inputs[comp_key] = {"low": cnt_low, "average": cnt_avg, "high": cnt_high}

        with st.expander("General system characteristics (14 factors)"):
            gsc_cols = st.columns(2)
            gsc_ratings = []
            for idx, gsc_name in enumerate(GENERAL_SYSTEM_CHARACTERISTICS):
                col = gsc_cols[idx % 2]
                default_score = saved_gsc[idx] if idx < len(saved_gsc) else 3
                val = col.slider(f"{idx+1}. {gsc_name}", min_value=0, max_value=5, value=int(default_score), key=f"gsc_{idx}")
                gsc_ratings.append(val)

        fp_result = calculate_function_points(comp_inputs, gsc_ratings)

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            with st.container(border=True):
                st.metric("Unadjusted FP", f"{fp_result.ufp:.0f}")
        with f2:
            with st.container(border=True):
                st.metric("Total influence", f"{fp_result.tdi} / 70")
        with f3:
            with st.container(border=True):
                st.metric("VAF multiplier", f"{fp_result.vaf:.4f}")
        with f4:
            with st.container(border=True):
                st.metric("Adjusted FP", f"{fp_result.afp:.1f}")

        st.markdown("## Language conversion factors")
        df_lang = pd.DataFrame([
            {
                "Language": lang,
                "LOC / FP": factor,
                "Equivalent KLOC": round(kloc_val, 2),
                "Source lines": f"{kloc_val * 1000:,.0f}",
            }
            for lang, kloc_val in fp_result.kloc_by_language.items()
            for factor in [LANGUAGE_LOC_FACTORS[lang]]
        ])
        st.dataframe(df_lang, use_container_width=True, hide_index=True)

        col_apply1, col_apply2 = st.columns([2, 1])
        with col_apply1:
            target_lang = st.selectbox("Target language", options=list(LANGUAGE_LOC_FACTORS.keys()), index=0)
            target_kloc = fp_result.kloc_by_language.get(target_lang, 20.0)
        with col_apply2:
            st.write("")
            st.write("")
            if st.button("Apply FP sizing to project"):
                active["kloc"] = round(target_kloc, 2)
                active["fp_components"] = comp_inputs
                active["gsc_ratings"] = gsc_ratings
                db.save_complete_project(active)
                st.success(f"Updated project size to {target_kloc:.2f} KLOC.")
                st.rerun()

    # -------------------------------------------------------------
    # TAB 3: COSMIC FULL FUNCTION POINTS
    # -------------------------------------------------------------
    with tab_cosmic:
        st.caption("COSMIC FFP (ISO/IEC 19761) sizes processes by counting data movements: Entries (E), Exits (X), Reads (R), and Writes (W).")

        if "cosmic_processes" not in st.session_state:
            st.session_state.cosmic_processes = [
                {"process_id": "P-01", "name": "User registration and KYC", "entries": 4, "exits": 3, "reads": 2, "writes": 2},
                {"process_id": "P-02", "name": "Authentication and tokens", "entries": 2, "exits": 2, "reads": 2, "writes": 1},
                {"process_id": "P-03", "name": "Core transaction workflow", "entries": 5, "exits": 4, "reads": 4, "writes": 3},
                {"process_id": "P-04", "name": "Audit reporting and export", "entries": 2, "exits": 5, "reads": 4, "writes": 0},
            ]

        col_c_cfg1, col_c_cfg2 = st.columns(2)
        with col_c_cfg1:
            prod_hours = st.slider("Productivity (hours / CFP)", min_value=4.0, max_value=30.0, value=12.0, step=1.0)
        with col_c_cfg2:
            team_sz = int(active.get("team_size", 5))
            st.write(f"Active team size: **{team_sz} staff**")

        cosmic_res = calculate_cosmic_ffp(
            st.session_state.cosmic_processes,
            productivity_hours_per_cfp=prod_hours,
            team_size=team_sz,
        )

        cm1, cm2, cm3, cm4 = st.columns(4)
        with cm1:
            with st.container(border=True):
                st.metric("Total size", f"{cosmic_res.total_cfp} CFP")
        with cm2:
            with st.container(border=True):
                st.metric("Labor effort", f"{cosmic_res.total_effort_hours:,.0f} hours")
        with cm3:
            with st.container(border=True):
                st.metric("Person-months", f"{cosmic_res.total_effort_pm:.1f} PM")
        with cm4:
            with st.container(border=True):
                st.metric("Schedule", f"{cosmic_res.estimated_duration_months:.1f} months")

        st.markdown("## Functional processes")
        df_cosmic = pd.DataFrame([p.to_dict() for p in cosmic_res.processes]).rename(columns={
            "process_id": "ID",
            "name": "Process name",
            "entries": "Entries (E)",
            "exits": "Exits (X)",
            "reads": "Reads (R)",
            "writes": "Writes (W)",
            "cfp": "Total CFP",
        })
        st.dataframe(df_cosmic, use_container_width=True, hide_index=True)

        with st.expander("Add functional process"):
            with st.form("add_cosmic_form"):
                cp_id = st.text_input("Process ID", value=f"P-{len(st.session_state.cosmic_processes)+1:02d}")
                cp_name = st.text_input("Process name")
                ce1, ce2, ce3, ce4 = st.columns(4)
                with ce1:
                    val_e = st.number_input("Entries", min_value=0, value=2)
                with ce2:
                    val_x = st.number_input("Exits", min_value=0, value=2)
                with ce3:
                    val_r = st.number_input("Reads", min_value=0, value=1)
                with ce4:
                    val_w = st.number_input("Writes", min_value=0, value=1)

                if st.form_submit_button("Add process"):
                    if cp_name.strip():
                        st.session_state.cosmic_processes.append({
                            "process_id": cp_id,
                            "name": cp_name.strip(),
                            "entries": int(val_e),
                            "exits": int(val_x),
                            "reads": int(val_r),
                            "writes": int(val_w),
                        })
                        st.rerun()

    # -------------------------------------------------------------
    # TAB 4: BOTTOM-UP / THREE-POINT (PERT)
    # -------------------------------------------------------------
    with tab_pert:
        st.caption("PERT computes expected effort E = (O + 4M + P) / 6 and combined variance across decomposed WBS tasks.")

        if "pert_tasks" not in st.session_state:
            st.session_state.pert_tasks = [
                {"task_id": "WBS-01", "name": "Architecture specification", "category": "Architecture", "optimistic": 20.0, "most_likely": 35.0, "pessimistic": 60.0},
                {"task_id": "WBS-02", "name": "Frontend interface implementation", "category": "Frontend", "optimistic": 40.0, "most_likely": 65.0, "pessimistic": 110.0},
                {"task_id": "WBS-03", "name": "Core backend services and schema", "category": "Backend", "optimistic": 60.0, "most_likely": 95.0, "pessimistic": 150.0},
                {"task_id": "WBS-04", "name": "Security hardening and auth", "category": "Security", "optimistic": 15.0, "most_likely": 30.0, "pessimistic": 55.0},
                {"task_id": "WBS-05", "name": "Integration and test suites", "category": "QA", "optimistic": 25.0, "most_likely": 45.0, "pessimistic": 80.0},
            ]

        pert_res = calculate_pert(st.session_state.pert_tasks)

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            with st.container(border=True):
                st.metric("Expected effort", f"{pert_res.total_expected:.1f} hours")
        with p2:
            with st.container(border=True):
                st.metric("Standard deviation", f"±{pert_res.combined_sd:.2f} hrs")
        with p3:
            with st.container(border=True):
                st.metric("90% confidence range", f"{pert_res.confidence_90_range[0]:.0f}–{pert_res.confidence_90_range[1]:.0f} hrs")
        with p4:
            with st.container(border=True):
                st.metric("Decomposed tasks", f"{pert_res.total_tasks} tasks")

        st.markdown("## Decomposed tasks")
        df_pert = pd.DataFrame([t.to_dict() for t in pert_res.tasks]).rename(columns={
            "task_id": "WBS ID",
            "name": "Task name",
            "category": "Category",
            "optimistic": "Optimistic (O)",
            "most_likely": "Likely (M)",
            "pessimistic": "Pessimistic (P)",
            "expected": "Expected (E)",
            "standard_deviation": "SD",
        })
        st.dataframe(df_pert[["WBS ID", "Task name", "Category", "Optimistic (O)", "Likely (M)", "Pessimistic (P)", "Expected (E)", "SD"]], use_container_width=True, hide_index=True)

        with st.expander("Confidence intervals"):
            df_conf = pd.DataFrame([
                {"Level": "68% (±1.00σ)", "Lower (hours)": f"{pert_res.confidence_68_range[0]:.1f}", "Upper (hours)": f"{pert_res.confidence_68_range[1]:.1f}"},
                {"Level": "90% (±1.645σ)", "Lower (hours)": f"{pert_res.confidence_90_range[0]:.1f}", "Upper (hours)": f"{pert_res.confidence_90_range[1]:.1f}"},
                {"Level": "95% (±1.96σ)", "Lower (hours)": f"{pert_res.confidence_95_range[0]:.1f}", "Upper (hours)": f"{pert_res.confidence_95_range[1]:.1f}"},
            ])
            st.dataframe(df_conf, use_container_width=True, hide_index=True)

        with st.expander("Add WBS task"):
            with st.form("add_pert_form"):
                pt_id = st.text_input("Task ID", value=f"WBS-{len(st.session_state.pert_tasks)+1:02d}")
                pt_name = st.text_input("Task name")
                pt_cat = st.selectbox("Category", ["Architecture", "Backend", "Frontend", "Security", "QA", "DevOps"])
                co1, co2, co3 = st.columns(3)
                with co1:
                    po = st.number_input("Optimistic hours", min_value=1.0, value=10.0, step=2.0)
                with co2:
                    pm = st.number_input("Likely hours", min_value=1.0, value=20.0, step=2.0)
                with co3:
                    pp = st.number_input("Pessimistic hours", min_value=1.0, value=40.0, step=5.0)

                if st.form_submit_button("Add task"):
                    if po > pm or pm > pp:
                        st.error("Estimates must satisfy: Optimistic <= Likely <= Pessimistic")
                    elif pt_name.strip():
                        st.session_state.pert_tasks.append({
                            "task_id": pt_id,
                            "name": pt_name.strip(),
                            "category": pt_cat,
                            "optimistic": float(po),
                            "most_likely": float(pm),
                            "pessimistic": float(pp),
                        })
                        st.rerun()
