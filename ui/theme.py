"""Design System, Global Theme, CSS Variables, and Plotly Styling for ProcessCompass.

Provides:
- Complete CSS Design System with Google Fonts, CSS variables, and light/dark theme compliance.
- Elevated KPI metric card components with count-up entrance animations and hover lifts.
- Standardized Plotly chart theming with animated transitions and accessible palettes.
- Academic chips, empty states, and polished widget overrides.
"""

from typing import Optional, Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px

# ProcessCompass Design Tokens
PRIMARY_COLOR = "#2563EB"       # Deep Cobalt
PRIMARY_DARK = "#1E40AF"        # Dark Cobalt
ACCENT_COLOR = "#0D9488"        # Teal / Emerald Accent
ACCENT_LIGHT = "#F0FDFA"
WARNING_COLOR = "#F59E0B"       # Warm Amber
DANGER_COLOR = "#EF4444"        # Crimson Red
SUCCESS_COLOR = "#10B981"       # Emerald Green

CHART_PALETTE = [
    "#2563EB",  # Cobalt Blue
    "#0D9488",  # Deep Teal
    "#F59E0B",  # Amber
    "#8B5CF6",  # Violet
    "#EC4899",  # Rose Pink
    "#10B981",  # Emerald Green
    "#6366F1",  # Indigo
    "#14B8A6",  # Cyan
]

THEME_CSS = """
<style>
/* 1. Google Fonts Import */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* 2. Global CSS Variables */
:root {
    --pc-font-sans: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --pc-font-mono: 'JetBrains Mono', monospace;
    --pc-bg: #F8FAFC;
    --pc-card-bg: #FFFFFF;
    --pc-card-subtle: #F1F5F9;
    --pc-border: #E2E8F0;
    --pc-border-focus: #3B82F6;
    --pc-text-main: #0F172A;
    --pc-text-muted: #64748B;
    --pc-text-subtle: #94A3B8;
    --pc-primary: #2563EB;
    --pc-primary-dark: #1E40AF;
    --pc-primary-subtle: #EFF6FF;
    --pc-accent: #0D9488;
    --pc-accent-subtle: #F0FDFA;
    --pc-shadow-sm: 0 1px 2px 0 rgba(15, 23, 42, 0.05);
    --pc-shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
    --pc-shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.05);
    --pc-radius-sm: 8px;
    --pc-radius-md: 12px;
    --pc-radius-lg: 16px;
    --pc-transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1);
}

/* Dark Mode Overrides */
[data-theme="dark"],
.stApp[data-theme="dark"] {
    --pc-bg: #0B0F19;
    --pc-card-bg: #151E2E;
    --pc-card-subtle: #1E293B;
    --pc-border: #334155;
    --pc-border-focus: #60A5FA;
    --pc-text-main: #F8FAFC;
    --pc-text-muted: #94A3B8;
    --pc-text-subtle: #64748B;
    --pc-primary-subtle: rgba(37, 99, 235, 0.15);
    --pc-accent-subtle: rgba(13, 148, 136, 0.15);
    --pc-shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.4);
    --pc-shadow-md: 0 4px 8px -1px rgba(0, 0, 0, 0.45);
    --pc-shadow-lg: 0 12px 20px -3px rgba(0, 0, 0, 0.5);
}

/* 3. Base Typography & Container */
html, body, [class*="css"], .stApp {
    font-family: var(--pc-font-sans);
    color: var(--pc-text-main);
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1350px !important;
}

/* 4. Page Entrance Animations */
@keyframes pcFadeUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (prefers-reduced-motion: no-preference) {
    .stApp > div:first-child {
        animation: pcFadeUp 320ms cubic-bezier(0.16, 1, 0.3, 1);
    }
    .pc-kpi-card {
        animation: pcFadeUp 280ms cubic-bezier(0.16, 1, 0.3, 1);
    }
}

/* 5. Custom Elevated KPI Cards */
.pc-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.pc-kpi-card {
    background: var(--pc-card-bg);
    border: 1px solid var(--pc-border);
    border-radius: var(--pc-radius-md);
    padding: 16px 20px;
    box-shadow: var(--pc-shadow-sm);
    transition: var(--pc-transition);
    position: relative;
    overflow: hidden;
}

.pc-kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--pc-shadow-md);
    border-color: rgba(37, 99, 235, 0.3);
}

.pc-kpi-accent-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--pc-primary);
}

.pc-kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.pc-kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--pc-text-muted);
}

.pc-kpi-icon {
    font-size: 1.1rem;
    opacity: 0.85;
}

.pc-kpi-value {
    font-family: var(--pc-font-sans);
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--pc-text-main);
    line-height: 1.2;
    margin-bottom: 4px;
}

.pc-kpi-footer {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.8rem;
    color: var(--pc-text-muted);
}

.pc-kpi-delta {
    display: inline-flex;
    align-items: center;
    padding: 2px 7px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
}

.pc-kpi-delta-up {
    background-color: rgba(16, 185, 129, 0.12);
    color: #059669;
}

.pc-kpi-delta-down {
    background-color: rgba(239, 68, 68, 0.12);
    color: #DC2626;
}

.pc-kpi-delta-neutral {
    background-color: rgba(100, 116, 139, 0.12);
    color: #475569;
}

/* 6. Standard Elevated Card */
.pc-card {
    background: var(--pc-card-bg);
    border: 1px solid var(--pc-border);
    border-radius: var(--pc-radius-md);
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: var(--pc-shadow-sm);
    transition: var(--pc-transition);
}

.pc-card:hover {
    box-shadow: var(--pc-shadow-md);
}

/* 7. Academic Syllabus Badge */
.pc-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--pc-primary-subtle);
    color: var(--pc-primary-dark);
    font-weight: 700;
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 9999px;
    border: 1px solid rgba(37, 99, 235, 0.2);
    margin-bottom: 8px;
    letter-spacing: 0.02em;
}

/* 8. Streamlit Tabs Modernization */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: var(--pc-card-subtle);
    padding: 6px;
    border-radius: var(--pc-radius-md);
    border: 1px solid var(--pc-border);
    margin-bottom: 1.5rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--pc-radius-sm) !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: var(--pc-text-muted) !important;
    border: none !important;
    background-color: transparent !important;
    transition: var(--pc-transition) !important;
}

.stTabs [aria-selected="true"] {
    background-color: var(--pc-card-bg) !important;
    color: var(--pc-primary) !important;
    box-shadow: var(--pc-shadow-sm) !important;
    font-weight: 700 !important;
}

/* 9. Buttons Polishing */
.stButton > button {
    border-radius: var(--pc-radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 18px !important;
    transition: var(--pc-transition) !important;
    border: 1px solid var(--pc-border) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: var(--pc-shadow-sm) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB, #1E40AF) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1D4ED8, #1E3A8A) !important;
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.35) !important;
}

/* 10. Form Controls (Inputs, Selectboxes, Sliders) */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: var(--pc-radius-sm) !important;
    border-color: var(--pc-border) !important;
    font-size: 0.9rem !important;
    transition: var(--pc-transition) !important;
}

div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within {
    border-color: var(--pc-primary) !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15) !important;
}

/* 11. Expanders / Accordions */
.streamlit-expanderHeader {
    border-radius: var(--pc-radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    background-color: var(--pc-card-subtle) !important;
    border: 1px solid var(--pc-border) !important;
    color: var(--pc-text-main) !important;
}

/* 12. Alert / Callout Boxes */
div[data-testid="stAlert"] {
    border-radius: var(--pc-radius-sm) !important;
    border: 1px solid var(--pc-border) !important;
    border-left-width: 4px !important;
    box-shadow: var(--pc-shadow-sm) !important;
    padding: 12px 16px !important;
}

/* 13. DataFrames & Tables */
div[data-testid="stDataFrame"] {
    border-radius: var(--pc-radius-sm);
    border: 1px solid var(--pc-border);
    overflow: hidden;
}

/* 14. Empty State */
.pc-empty-state {
    text-align: center;
    padding: 40px 24px;
    background: var(--pc-card-bg);
    border: 2px dashed var(--pc-border);
    border-radius: var(--pc-radius-md);
    margin: 20px 0;
}

.pc-empty-icon {
    font-size: 2.8rem;
    margin-bottom: 12px;
    opacity: 0.8;
}

.pc-empty-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--pc-text-main);
    margin-bottom: 6px;
}

.pc-empty-desc {
    font-size: 0.88rem;
    color: var(--pc-text-muted);
    max-width: 460px;
    margin: 0 auto 16px auto;
    line-height: 1.5;
}
</style>
"""


def inject_theme():
    """Inject full CSS design tokens and component styling into Streamlit."""
    import streamlit as st
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, module_tag: str, co_tag: str):
    """Render standardized sticky-style modern page header with academic chip."""
    import streamlit as st
    st.markdown(
        f"""
        <div style="margin-bottom: 22px;">
            <div class="pc-badge">
                <span>📚 {module_tag}</span>
                <span>&bull;</span>
                <span>🎯 {co_tag}</span>
            </div>
            <h1 style="margin: 0; padding-top: 2px; font-size: 2.15rem; font-weight: 800; letter-spacing: -0.025em; color: var(--pc-text-main);">
                {title}
            </h1>
            <p style="margin: 6px 0 0 0; color: var(--pc-text-muted); font-size: 1.02rem; line-height: 1.45;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    subtitle: Optional[str] = None,
    delta: Optional[str] = None,
    delta_type: str = "neutral",  # "up", "down", "neutral"
    icon: Optional[str] = None,
    accent_color: str = "#2563EB",
) -> str:
    """Generate HTML for an elevated, animated KPI metric card."""
    delta_html = ""
    if delta:
        delta_class = "pc-kpi-delta-neutral"
        arrow = ""
        if delta_type == "up":
            delta_class = "pc-kpi-delta-up"
            arrow = "↑ "
        elif delta_type == "down":
            delta_class = "pc-kpi-delta-down"
            arrow = "↓ "
        delta_html = f'<span class="pc-kpi-delta {delta_class}">{arrow}{delta}</span>'

    icon_html = f'<span class="pc-kpi-icon">{icon}</span>' if icon else ""
    footer_sub = f'<span>{subtitle}</span>' if subtitle else ""

    html = f"""
    <div class="pc-kpi-card">
        <div class="pc-kpi-accent-bar" style="background: {accent_color};"></div>
        <div class="pc-kpi-header">
            <span class="pc-kpi-label">{label}</span>
            {icon_html}
        </div>
        <div class="pc-kpi-value">{value}</div>
        <div class="pc-kpi-footer">
            {delta_html}
            {footer_sub}
        </div>
    </div>
    """
    return html


def render_empty_state_html(icon: str, title: str, description: str) -> str:
    """Generate HTML for an empty-state card."""
    return f"""
    <div class="pc-empty-state">
        <div class="pc-empty-icon">{icon}</div>
        <div class="pc-empty-title">{title}</div>
        <div class="pc-empty-desc">{description}</div>
    </div>
    """


def apply_plotly_theme(
    fig: go.Figure,
    title: Optional[str] = None,
    height: int = 400,
    show_legend: bool = True,
    is_dark: bool = False,
) -> go.Figure:
    """Apply unified, professional dashboard theme to any Plotly chart.

    Features:
    - Transparent plot and canvas backgrounds so it dynamically blends into light or dark mode.
    - Subtle slate gridlines, custom hoverlabel styling, clean typefaces.
    - Smooth 400ms loading transitions.
    """
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    grid_color = "rgba(148, 163, 184, 0.18)"
    hover_bg = "#1E293B" if not is_dark else "#0F172A"
    hover_font = "#F8FAFC"

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else None,
            font=dict(family="'Plus Jakarta Sans', 'Inter', sans-serif", size=15, color=text_color),
            x=0.01,
            xanchor="left",
            y=0.96,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        font=dict(family="'Plus Jakarta Sans', 'Inter', sans-serif", size=12, color=text_color),
        colorway=CHART_PALETTE,
        margin=dict(l=45, r=35, t=50 if title else 25, b=45),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=text_color),
        ),
        hoverlabel=dict(
            bgcolor=hover_bg,
            font_size=12,
            font_family="'Plus Jakarta Sans', 'Inter', sans-serif",
            font_color=hover_font,
            bordercolor="rgba(0,0,0,0)",
        ),
        transition=dict(duration=400, easing="cubic-in-out"),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        linecolor=grid_color,
        tickfont=dict(size=11, color=text_color),
        title_font=dict(size=12, color=text_color),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        linecolor=grid_color,
        tickfont=dict(size=11, color=text_color),
        title_font=dict(size=12, color=text_color),
    )

    return fig

