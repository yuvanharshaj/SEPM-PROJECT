"""Consolidated Project Report Generator (PDF & CSV).

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Modules 1-5:
    Consolidated decision-support synthesis uniting Process Selection (M1),
    Agile Sprint Planning (M2), Project Evaluation & Business Case (M3),
    Effort Estimation (COCOMO, FPA, COSMIC, PERT) & Risk Management (M4),
    and McCall Software Quality Assurance (M5).
"""

import io
import csv
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)


def generate_consolidated_csv(report_data: Dict[str, Any]) -> str:
    """Generate a clean consolidated CSV representation of the project analysis."""
    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Project Overview
    proj = report_data.get("project", {})
    writer.writerow(["# ProcessCompass Project Evaluation Summary"])
    writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["Syllabus Mapping", "VTU 24CS51 Software Engineering & Project Management"])
    writer.writerow([])
    writer.writerow(["--- 1. PROJECT SETUP & CONSTRAINTS (VTU MODULE 3) ---"])
    writer.writerow(["Project Name", proj.get("name", "N/A")])
    writer.writerow(["Description", proj.get("description", "N/A")])
    writer.writerow(["Team Size (Persons)", proj.get("team_size", 0)])
    writer.writerow(["Duration (Months)", proj.get("duration", 0)])
    writer.writerow(["Budget (USD / INR)", proj.get("budget", 0)])
    writer.writerow(["Requirement Stability", proj.get("req_stability", "Medium")])
    writer.writerow(["Customer Involvement", proj.get("customer_involvement", "Medium")])
    writer.writerow(["Risk Level", proj.get("risk_level", "Medium")])
    writer.writerow(["Need for Early Delivery", proj.get("early_delivery", "Medium")])
    writer.writerow(["Team Experience", proj.get("team_experience", "Medium")])
    writer.writerow([])

    # 2. Process Model Advisor
    advisor = report_data.get("advisor", {})
    writer.writerow(["--- 2. PROCESS MODEL ADVISOR (VTU MODULE 1) ---"])
    writer.writerow(["Rank", "Model Name", "Score", "Percentage (%)", "Suitability"])
    ranked = advisor.get("ranked_models", [])
    for m in ranked:
        writer.writerow([
            m.get("rank"),
            m.get("model_name"),
            m.get("score"),
            f"{m.get('percentage')}%",
            "Top Recommendation" if m.get("rank") == 1 else "Alternative",
        ])
    writer.writerow([])

    # 3. Agile Lab
    agile = report_data.get("agile", {})
    writer.writerow(["--- 3. AGILE LAB & SPRINT RELEASE PLAN (VTU MODULE 2) ---"])
    writer.writerow(["Backlog Story Points", agile.get("total_story_points", "N/A")])
    writer.writerow(["Team Velocity (Points/Sprint)", agile.get("team_velocity", "N/A")])
    writer.writerow(["Sprint Length (Weeks)", agile.get("sprint_length_weeks", "N/A")])
    writer.writerow(["Sprints Needed", agile.get("sprints_needed", "N/A")])
    writer.writerow(["Total Calendar Days", agile.get("total_calendar_days", "N/A")])
    writer.writerow(["Projected Release Date", agile.get("finish_date", "N/A")])
    writer.writerow([])

    # 4. Effort Estimation (COCOMO, FP, COSMIC, PERT)
    cocomo = report_data.get("cocomo", {})
    fp = report_data.get("fp", {})
    cosmic = report_data.get("cosmic", {})
    pert = report_data.get("pert", {})
    writer.writerow(["--- 4. EFFORT ESTIMATION & SIZING (VTU MODULE 4 & 5) ---"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["COCOMO Mode", cocomo.get("mode", "N/A")])
    writer.writerow(["Estimated KLOC", cocomo.get("kloc", "N/A")])
    writer.writerow(["COCOMO Effort (Person-Months)", cocomo.get("effort_pm", "N/A")])
    writer.writerow(["Nominal Duration (Months)", cocomo.get("duration_months", "N/A")])
    writer.writerow(["Average Staffing (Persons)", cocomo.get("avg_staff", "N/A")])
    writer.writerow(["Unadjusted Function Points (UFP)", fp.get("ufp", "N/A")])
    writer.writerow(["Adjusted Function Points (AFP)", fp.get("afp", "N/A")])
    if cosmic:
        writer.writerow(["COSMIC Function Points (CFP)", cosmic.get("total_cfp", "N/A")])
        writer.writerow(["COSMIC Effort (Hours)", cosmic.get("total_effort_hours", "N/A")])
        writer.writerow(["COSMIC Effort (Person-Months)", cosmic.get("total_effort_pm", "N/A")])
    if pert:
        writer.writerow(["PERT Expected Effort (Hours)", pert.get("total_expected", "N/A")])
        writer.writerow(["PERT Combined Std Dev (Hours)", pert.get("combined_sd", "N/A")])
        writer.writerow(["PERT 90% Range (Hours)", f"{pert.get('confidence_90_range', ('N/A', 'N/A'))}"])
    writer.writerow([])

    # 5. Risk Register
    risks = report_data.get("risks", {})
    writer.writerow(["--- 5. RISK REGISTER & RMMM PLAN (VTU MODULE 4) ---"])
    writer.writerow(["Total Risks", risks.get("total_risks", 0)])
    writer.writerow(["Total Risk Exposure (Cost)", risks.get("total_exposure", 0.0)])
    writer.writerow(["Risk ID", "Category", "Description", "Probability", "Impact Cost", "Exposure", "Severity", "Mitigation"])
    for r in risks.get("ranked_risks", []):
        writer.writerow([
            r.get("id"),
            r.get("category"),
            r.get("description"),
            r.get("probability"),
            r.get("impact_cost"),
            r.get("exposure"),
            r.get("severity_level"),
            r.get("mitigation"),
        ])
    writer.writerow([])

    # 6. Business Case & Scenario Risk
    biz = report_data.get("business_case", {})
    scenario = report_data.get("scenario", {})
    radr = report_data.get("radr", {})
    writer.writerow(["--- 6. BUSINESS CASE & ECONOMIC FEASIBILITY (VTU MODULE 3) ---"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Initial Investment", biz.get("initial_investment", 0)])
    writer.writerow(["Discount Rate (%)", biz.get("discount_rate_pct", 0)])
    writer.writerow(["Net Present Value (NPV)", biz.get("npv", 0)])
    writer.writerow(["Simple ROI (%)", biz.get("roi_pct", 0)])
    writer.writerow(["Payback Period (Years)", biz.get("payback_period_years", "N/A")])
    writer.writerow(["Financial Viability", "VIABLE" if biz.get("is_financially_viable") else "UNVIABLE"])
    if scenario:
        writer.writerow(["Expected NPV (EMV)", scenario.get("expected_npv", "N/A")])
        writer.writerow(["Expected ROI (%)", scenario.get("expected_roi_pct", "N/A")])
        writer.writerow(["NPV Standard Deviation", scenario.get("npv_standard_deviation", "N/A")])
    if radr:
        writer.writerow(["RADR Adjusted Rate (%)", radr.get("adjusted_discount_rate_pct", "N/A")])
        writer.writerow(["Risk-Adjusted NPV", radr.get("adjusted_npv", "N/A")])
    writer.writerow([])

    # 7. Quality Scorecard
    quality = report_data.get("quality", {})
    writer.writerow(["--- 7. MCCALL QUALITY SCORECARD (VTU MODULE 5) ---"])
    writer.writerow(["Overall McCall Quality Index", f"{quality.get('overall_index', 0)} / 5.0"])
    writer.writerow(["Overall Compliance (%)", f"{quality.get('overall_percentage', 0)}%"])
    writer.writerow(["Factor", "Category", "Rating (1-5)"])
    for cat_name, c_data in quality.get("categories", {}).items():
        for factor, score in c_data.get("factors", {}).items():
            writer.writerow([factor, cat_name, score])

    return output.getvalue()


def generate_consolidated_pdf(report_data: Dict[str, Any]) -> bytes:
    """Generate a publication-grade, styled PDF summary using ReportLab."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0D47A1"),
        spaceAfter=3,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#546E7A"),
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1565C0"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#263238"),
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("ProcessCompass: Executive Decision-Support Synthesis", title_style))
    elements.append(
        Paragraph(
            f"VTU 24CS51 Software Engineering & Project Management &bull; Author: YUVAN HARSHAJ &bull; Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
            subtitle_style,
        )
    )
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0D47A1"), spaceAfter=8))

    proj = report_data.get("project", {})

    # 1. Project Profile (M3)
    elements.append(Paragraph("1. Project Specification & Scope Constraints (VTU Module 3 - CO3)", h2_style))
    proj_table_data = [
        [
            Paragraph("<b>Project:</b>", body_style),
            Paragraph(str(proj.get("name", "N/A")), body_style),
            Paragraph("<b>Budget:</b>", body_style),
            Paragraph(f"${float(proj.get('budget', 0)):,.0f}", body_style),
        ],
        [
            Paragraph("<b>Team Size:</b>", body_style),
            Paragraph(f"{proj.get('team_size', 0)} Engineers", body_style),
            Paragraph("<b>Duration:</b>", body_style),
            Paragraph(f"{proj.get('duration', 0)} Months", body_style),
        ],
        [
            Paragraph("<b>Req Stability:</b>", body_style),
            Paragraph(str(proj.get("req_stability", "Medium")), body_style),
            Paragraph("<b>Customer Involv.:</b>", body_style),
            Paragraph(str(proj.get("customer_involvement", "Medium")), body_style),
        ],
    ]
    t_proj = Table(proj_table_data, colWidths=[90, 180, 90, 180])
    t_proj.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CFD8DC")),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_proj)

    # 2. Process Model Advisor (M1)
    elements.append(Paragraph("2. Process Model Recommendation (VTU Module 1 - CO1)", h2_style))
    advisor = report_data.get("advisor", {})
    ranked = advisor.get("ranked_models", [])

    model_rows = [["Rank", "Lifecycle Model", "Match %", "Suitability Rationale"]]
    for m in ranked[:4]:
        model_rows.append([
            str(m.get("rank")),
            m.get("model_name"),
            f"{m.get('percentage')}%",
            Paragraph(m.get("justification", "")[:120] + "...", body_style),
        ])
    t_models = Table(model_rows, colWidths=[35, 120, 65, 320])
    t_models.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    elements.append(t_models)

    # 3. Agile Lab & Sprint Release (M2)
    agile = report_data.get("agile", {})
    elements.append(Paragraph("3. Agile Lab & Sprint Release Schedule (VTU Module 2 - CO2)", h2_style))
    agile_rows = [
        ["Backlog Story Points", f"{agile.get('total_story_points', 0)} pts", "Sprints Needed", f"{agile.get('sprints_needed', 0)} Sprints"],
        ["Team Velocity", f"{agile.get('team_velocity', 0)} pts / sprint", "Projected Release", str(agile.get("finish_date", "N/A"))],
    ]
    t_agile = Table(agile_rows, colWidths=[135, 135, 135, 135])
    t_agile.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDE7F6")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EDE7F6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1C4E9")),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    elements.append(t_agile)

    # 4. Effort Estimation (M4 & M5)
    elements.append(Paragraph("4. Effort Estimation (VTU Module 4 & 5 - CO4)", h2_style))
    cocomo = report_data.get("cocomo", {})
    fp = report_data.get("fp", {})
    cosmic = report_data.get("cosmic", {})
    pert = report_data.get("pert", {})

    est_data = [
        ["COCOMO Mode & Size", f"{str(cocomo.get('mode', 'N/A')).title()} ({cocomo.get('kloc', 0):.1f} KLOC)", "COCOMO Effort / Time", f"{cocomo.get('effort_pm', 0):.1f} PM / {cocomo.get('duration_months', 0):.1f} Mos"],
        ["Function Points (UFP / AFP)", f"{fp.get('ufp', 0):.0f} UFP / {fp.get('afp', 0):.1f} AFP", "COSMIC Size & Effort", f"{cosmic.get('total_cfp', 0)} CFP ({cosmic.get('total_effort_pm', 0):.1f} PM)"],
        ["PERT Expected Effort", f"{pert.get('total_expected', 0):.1f} Hours", "PERT 90% Confidence", f"{pert.get('confidence_90_range', (0,0))[0]:.0f} – {pert.get('confidence_90_range', (0,0))[1]:.0f} Hrs"],
    ]
    t_est = Table(est_data, colWidths=[140, 130, 140, 130])
    t_est.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ECEFF1")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#ECEFF1")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CFD8DC")),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    elements.append(t_est)

    # 5. Risk Register (M4)
    elements.append(Paragraph("5. Risk Register & Prioritization (VTU Module 4 - CO4)", h2_style))
    risks = report_data.get("risks", {})
    ranked_risks = risks.get("ranked_risks", [])[:3]

    risk_rows = [["ID", "Category", "P", "Impact ($)", "Exposure ($)", "Mitigation Plan"]]
    for r in ranked_risks:
        risk_rows.append([
            r.get("id"),
            r.get("category"),
            f"{r.get('probability'):.2f}",
            f"${r.get('impact_cost'):,.0f}",
            f"${r.get('exposure'):,.0f}",
            Paragraph(r.get("mitigation", "")[:80], body_style),
        ])
    if not ranked_risks:
        risk_rows.append(["-", "No risks logged", "-", "-", "-", "-"])

    t_risks = Table(risk_rows, colWidths=[35, 110, 35, 60, 70, 230])
    t_risks.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#37474F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_risks)

    # 6. Business Case, Scenario Risk & RADR (M3)
    elements.append(Paragraph("6. Business Case & Scenario Risk Evaluation (VTU Module 3 - CO3)", h2_style))
    biz = report_data.get("business_case", {})
    scenario = report_data.get("scenario", {})
    radr = report_data.get("radr", {})

    biz_rows = [
        ["Net Present Value (NPV)", f"${biz.get('npv', 0):,.2f}", "Expected NPV (EMV)", f"${scenario.get('expected_npv', 0):,.2f}"],
        ["Simple ROI / Payback", f"{biz.get('roi_pct', 0):.1f}% / {biz.get('payback_period_years', 'N/A')} yrs", "NPV Standard Deviation", f"±${scenario.get('npv_standard_deviation', 0):,.2f}"],
        ["Base Hurdle Rate", f"{biz.get('discount_rate_pct', 0)}%", "RADR Adjusted Rate & NPV", f"{radr.get('adjusted_discount_rate_pct', 0):.1f}% (${radr.get('adjusted_npv', 0):,.0f})"],
    ]
    t_biz = Table(biz_rows, colWidths=[140, 130, 140, 130])
    t_biz.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#E8F5E9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8E6C9")),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    elements.append(t_biz)

    # 7. Quality Scorecard (M5)
    elements.append(Paragraph("7. McCall's Software Quality Scorecard (VTU Module 5 - CO5)", h2_style))
    quality = report_data.get("quality", {})
    mqi_score = quality.get("overall_index", 0.0)
    mqi_pct = quality.get("overall_percentage", 0.0)

    cats = quality.get("categories", {})
    q_rows = [["Quality Pillar", "Pillar Average (1-5)", "Compliance %", "Audit Status"]]
    for c_name, c_info in cats.items():
        q_rows.append([
            c_name,
            f"{c_info.get('average_score', 0):.2f} / 5.0",
            f"{c_info.get('percentage', 0):.1f}%",
            "Strong" if c_info.get('average_score', 0) >= 4.0 else ("Adequate" if c_info.get('average_score', 0) >= 3.0 else "Needs Work"),
        ])
    q_rows.append([
        "OVERALL MCCALL QUALITY INDEX",
        f"{mqi_score:.2f} / 5.0",
        f"{mqi_pct:.1f}%",
        quality.get("sqa_verdict", "N/A")[:30],
    ])

    t_qual = Table(q_rows, colWidths=[180, 110, 100, 150])
    t_qual.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00695C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B2DFDB")),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E0F2F1")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(t_qual)

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
