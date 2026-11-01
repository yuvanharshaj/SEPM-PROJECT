"""Consolidated Project Report Generator (PDF & CSV).

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Modules 1-5:
    Consolidated decision-support synthesis uniting Process Selection, Cost & Effort Estimation,
    Risk Management, Economic Evaluation, and McCall Software Quality Assurance.
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
    writer.writerow(["--- PROJECT SETUP ---"])
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
    writer.writerow(["--- PROCESS MODEL ADVISOR (VTU MODULE 1) ---"])
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

    # 3. Effort Estimation (COCOMO & FP)
    cocomo = report_data.get("cocomo", {})
    fp = report_data.get("fp", {})
    writer.writerow(["--- EFFORT & SIZE ESTIMATION (VTU MODULE 3) ---"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["COCOMO Mode", cocomo.get("mode", "N/A")])
    writer.writerow(["Estimated KLOC", cocomo.get("kloc", "N/A")])
    writer.writerow(["Effort (Person-Months)", cocomo.get("effort_pm", "N/A")])
    writer.writerow(["Development Time (Months)", cocomo.get("duration_months", "N/A")])
    writer.writerow(["Average Staffing (Persons)", cocomo.get("avg_staff", "N/A")])
    writer.writerow(["Productivity (LOC/PM)", cocomo.get("productivity_loc_pm", "N/A")])
    writer.writerow(["Unadjusted Function Points (UFP)", fp.get("ufp", "N/A")])
    writer.writerow(["Value Adjustment Factor (VAF)", fp.get("vaf", "N/A")])
    writer.writerow(["Adjusted Function Points (AFP)", fp.get("afp", "N/A")])
    writer.writerow([])

    # 4. Risk Register
    risks = report_data.get("risks", {})
    writer.writerow(["--- RISK REGISTER & RMMM PLAN (VTU MODULE 4) ---"])
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

    # 5. Business Case
    biz = report_data.get("business_case", {})
    writer.writerow(["--- BUSINESS CASE & ECONOMIC FEASIBILITY (VTU MODULE 4) ---"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Initial Investment", biz.get("initial_investment", 0)])
    writer.writerow(["Discount Rate (%)", biz.get("discount_rate_pct", 0)])
    writer.writerow(["Net Present Value (NPV)", biz.get("npv", 0)])
    writer.writerow(["Simple ROI (%)", biz.get("roi_pct", 0)])
    writer.writerow(["Discounted ROI (%)", biz.get("discounted_roi_pct", 0)])
    writer.writerow(["Payback Period (Years)", biz.get("payback_period_years", "N/A")])
    writer.writerow(["Financial Viability", "VIABLE" if biz.get("is_financially_viable") else "UNVIABLE"])
    writer.writerow([])

    # 6. Quality Scorecard
    quality = report_data.get("quality", {})
    writer.writerow(["--- MCCALL QUALITY SCORECARD (VTU MODULE 5) ---"])
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

    # Custom styling
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0D47A1"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#546E7A"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1565C0"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#263238"),
    )
    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#37474F"),
        alignment=1,
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("ProcessCompass: Decision-Support Synthesis", title_style))
    elements.append(
        Paragraph(
            f"VTU 24CS51 Software Engineering & Project Management | Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
            subtitle_style,
        )
    )
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0D47A1"), spaceAfter=10))

    proj = report_data.get("project", {})

    # Section 1: Project Information
    elements.append(Paragraph("1. Project Specification & Environment", h2_style))
    proj_table_data = [
        [
            Paragraph("<b>Project Name:</b>", body_style),
            Paragraph(str(proj.get("name", "N/A")), body_style),
            Paragraph("<b>Target Budget:</b>", body_style),
            Paragraph(f"${float(proj.get('budget', 0)):,.2f}", body_style),
        ],
        [
            Paragraph("<b>Team Size:</b>", body_style),
            Paragraph(f"{proj.get('team_size', 0)} engineers", body_style),
            Paragraph("<b>Planned Duration:</b>", body_style),
            Paragraph(f"{proj.get('duration', 0)} months", body_style),
        ],
        [
            Paragraph("<b>Req Stability:</b>", body_style),
            Paragraph(str(proj.get("req_stability", "Medium")), body_style),
            Paragraph("<b>Customer Involvement:</b>", body_style),
            Paragraph(str(proj.get("customer_involvement", "Medium")), body_style),
        ],
        [
            Paragraph("<b>Risk Level:</b>", body_style),
            Paragraph(str(proj.get("risk_level", "Medium")), body_style),
            Paragraph("<b>Need for Early Delivery:</b>", body_style),
            Paragraph(str(proj.get("early_delivery", "Medium")), body_style),
        ],
    ]
    t_proj = Table(proj_table_data, colWidths=[100, 165, 110, 165])
    t_proj.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F4F8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CFD8DC")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_proj)
    elements.append(Spacer(1, 10))

    # Section 2: Process Model Advisor
    elements.append(Paragraph("2. Process Model Recommendation (VTU Module 1)", h2_style))
    advisor = report_data.get("advisor", {})
    ranked = advisor.get("ranked_models", [])

    model_rows = [["Rank", "Lifecycle Model", "Alignment %", "Suitability Rationale"]]
    for m in ranked[:5]:
        model_rows.append([
            str(m.get("rank")),
            m.get("model_name"),
            f"{m.get('percentage')}%",
            Paragraph(m.get("justification", "")[:130] + "...", body_style),
        ])
    t_models = Table(model_rows, colWidths=[35, 120, 75, 310])
    t_models.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FA")]),
    ]))
    elements.append(t_models)
    elements.append(Spacer(1, 10))

    # Section 3: Effort & Size Estimation (COCOMO & FP)
    elements.append(Paragraph("3. Effort & Size Estimation (VTU Module 3 - Boehm & Albrecht)", h2_style))
    cocomo = report_data.get("cocomo", {})
    fp = report_data.get("fp", {})

    est_data = [
        ["COCOMO Mode", str(cocomo.get("mode", "N/A")).title(), "Unadjusted FP (UFP)", f"{fp.get('ufp', 0):.1f}"],
        ["Project Size", f"{cocomo.get('kloc', 0):.2f} KLOC", "Value Adjustment (VAF)", f"{fp.get('vaf', 1.0):.4f}"],
        ["Effort (Person-Months)", f"{cocomo.get('effort_pm', 0):.2f} PM", "Adjusted FP (AFP)", f"{fp.get('afp', 0):.1f}"],
        ["Nominal Duration", f"{cocomo.get('duration_months', 0):.2f} Months", "Average Staff Size", f"{cocomo.get('avg_staff', 0):.2f} Staff"],
    ]
    t_est = Table(est_data, colWidths=[130, 135, 135, 140])
    t_est.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ECEFF1")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#ECEFF1")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CFD8DC")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    elements.append(t_est)
    elements.append(Spacer(1, 10))

    # Section 4: Risk Register
    elements.append(Paragraph("4. Risk Register & Exposure Analysis (VTU Module 4 - RMMM)", h2_style))
    risks = report_data.get("risks", {})
    ranked_risks = risks.get("ranked_risks", [])[:4]

    risk_rows = [["ID", "Category", "Prob (P)", "Impact ($)", "Exposure (RE)", "Mitigation Strategy"]]
    for r in ranked_risks:
        risk_rows.append([
            r.get("id"),
            r.get("category"),
            f"{r.get('probability'):.2f}",
            f"${r.get('impact_cost'):,.0f}",
            f"${r.get('exposure'):,.0f}",
            Paragraph(r.get("mitigation", "")[:90], body_style),
        ])
    if not ranked_risks:
        risk_rows.append(["-", "None recorded", "-", "-", "-", "No risks registered."])

    t_risks = Table(risk_rows, colWidths=[35, 105, 55, 65, 75, 205])
    t_risks.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#37474F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_risks)
    elements.append(Spacer(1, 10))

    # Section 5: Economic Feasibility
    elements.append(Paragraph("5. Economic Feasibility & Cost-Benefit (VTU Module 4)", h2_style))
    biz = report_data.get("business_case", {})
    biz_rows = [
        ["Initial Investment", f"${biz.get('initial_investment', 0):,.2f}", "Net Present Value (NPV)", f"${biz.get('npv', 0):,.2f}"],
        ["Discount Rate", f"{biz.get('discount_rate_pct', 0)}%", "Return on Investment (ROI)", f"{biz.get('roi_pct', 0):.2f}%"],
        ["Payback Period", f"{biz.get('payback_period_years', 'N/A')} yrs", "Financial Status", "VIABLE" if biz.get("is_financially_viable") else "UNVIABLE"],
    ]
    t_biz = Table(biz_rows, colWidths=[130, 135, 135, 140])
    t_biz.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#E8F5E9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8E6C9")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    elements.append(t_biz)
    elements.append(Spacer(1, 10))

    # Section 6: McCall Quality Scorecard
    elements.append(Paragraph("6. McCall Quality Scorecard (VTU Module 5 - SQA)", h2_style))
    quality = report_data.get("quality", {})
    mqi_score = quality.get("overall_index", 0.0)
    mqi_pct = quality.get("overall_percentage", 0.0)

    cats = quality.get("categories", {})
    q_rows = [["Quality Pillar", "Pillar Average (1-5)", "Compliance %", "Status"]]
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

    t_qual = Table(q_rows, colWidths=[180, 120, 100, 140])
    t_qual.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00695C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B2DFDB")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E0F2F1")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(t_qual)

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

