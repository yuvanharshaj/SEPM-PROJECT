"""Effort & Size Estimator UI (Basic COCOMO & Albrecht Function Points)."""

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
from ui.components import render_page_header
from db.database import DatabaseManager


def render_effort_estimator_page():
    render_page_header(
        title="Software Effort & Size Estimator",
        subtitle="Empirical cost estimation via Boehm's Basic COCOMO and Albrecht's Function Point Analysis (FPA).",
        module_tag="VTU 24CS51: Module 3 (Cost Estimation & Metrics)",
        co_tag="CO3: Apply Algorithmic Models to Predict Project Effort, Time & Size",
    )

    active = st.session_state.get("current_project")
    if not active:
        st.warning("Please select or initialize a project in 'Project Setup' first.")
        return

    db: DatabaseManager = st.session_state.db

    tab_cocomo, tab_fp = st.tabs(["📐 (a) Basic COCOMO Model", "🔢 (b) Function Point Analysis (FPA)"])

    # -------------------------------------------------------------
    # TAB A: BASIC COCOMO
    # -------------------------------------------------------------
    with tab_cocomo:
        st.markdown("### Boehm's Basic COCOMO Formulation")
        st.latex(r"Effort = a \cdot (\text{KLOC})^b \quad [\text{Person-Months}]")
        st.latex(r"Time = c \cdot (Effort)^d \quad [\text{Months}], \quad Staff = \frac{Effort}{Time} \quad [\text{Persons}]")

        col_in1, col_in2 = st.columns([1, 1])

        with col_in1:
            curr_mode = active.get("cocomo_mode", "organic")
            modes = ["organic", "semi-detached", "embedded"]
            selected_mode = st.selectbox(
                "Development Mode:",
                options=modes,
                index=modes.index(curr_mode) if curr_mode in modes else 0,
                format_func=lambda x: f"{x.title()} Mode — {COCOMO_COEFFICIENTS[x]['description']}",
            )

        with col_in2:
            curr_kloc = float(active.get("kloc", 25.0))
            input_kloc = st.number_input(
                "Estimated Codebase Size (KLOC - Thousands of LOC):",
                min_value=0.5,
                max_value=2000.0,
                value=curr_kloc,
                step=1.0,
                help="1 KLOC = 1,000 physical source lines of code",
            )

        # Coefficient card
        coeff = COCOMO_COEFFICIENTS[selected_mode]
        st.caption(
            f"**Active Empirical Constants ({selected_mode.title()}):** "
            f"a = {coeff['a']}, b = {coeff['b']}, c = {coeff['c']}, d = {coeff['d']}"
        )

        cocomo_res = calculate_cocomo(input_kloc, selected_mode)

        # Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Required Effort", f"{cocomo_res.effort_pm:.1f} PM", help="Person-Months of labor")
        with m2:
            st.metric("Development Schedule", f"{cocomo_res.duration_months:.1f} Months", help="Nominal calendar duration")
        with m3:
            st.metric("Recommended Staff", f"{cocomo_res.avg_staff:.1f} Engineers", help="Average concurrent team size")
        with m4:
            st.metric("Productivity", f"{cocomo_res.productivity_loc_pm:.0f} LOC/PM", help="Lines of code delivered per person-month")

        # Multi-mode sensitivity graph
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
            title="Effort Scaling Across COCOMO Modes",
        )
        fig_cocomo.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cocomo, use_container_width=True)

        if st.button("💾 Persist COCOMO Parameters to Active Project"):
            active["cocomo_mode"] = selected_mode
            active["kloc"] = float(input_kloc)
            db.save_complete_project(active)
            st.success("COCOMO sizing parameters saved!")

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
        st.caption("Count user-facing transactions and logical files across Low, Average, and High complexity:")

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

        # Compute FP
        fp_result = calculate_function_points(comp_inputs, gsc_ratings)

        # Display FP Results
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.metric("Unadjusted FP (UFP)", f"{fp_result.ufp:.0f}")
        with f2:
            st.metric("Total Influence (TDI)", f"{fp_result.tdi} / 70")
        with f3:
            st.metric("Adjustment Factor (VAF)", f"{fp_result.vaf:.4f}")
        with f4:
            st.metric("Adjusted FP (AFP)", f"{fp_result.afp:.1f}")

        st.markdown("---")
        st.markdown("#### 3. Language Gear Factors & Equivalent Sizing (FP ➡️ KLOC)")
        st.caption("Industry benchmark LOC/FP ratios for software sizing:")

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
