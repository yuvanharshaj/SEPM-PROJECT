"""Minimal, accessible design system and chart theming for ProcessCompass."""

import streamlit as st
import plotly.graph_objects as go

# Minimal CSS under 150 lines focusing on typography, layout capping, and responsiveness
MINIMAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.5;
}

h1 {
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    letter-spacing: -0.01em !important;
    margin: 0 0 0.25rem 0 !important;
}

h2 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    line-height: 1.35 !important;
    margin: 1.25rem 0 0.5rem 0 !important;
}

h3 {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    margin: 1rem 0 0.35rem 0 !important;
}

p, span, label, div {
    font-size: 1rem;
}

.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 0.875rem !important;
    color: #64748b !important;
    line-height: 1.4 !important;
}

.block-container {
    max-width: 1200px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-top: 1rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: max(1.25rem, env(safe-area-inset-left)) !important;
    padding-right: max(1.25rem, env(safe-area-inset-right)) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stMetric"],
div[data-testid="stExpander"],
div[data-baseweb="tab-list"],
.stButton > button,
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 8px !important;
}

.stButton > button {
    min-height: 44px !important;
    font-weight: 500 !important;
    transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease !important;
}

[data-testid="stMetric"] {
    padding: 0.75rem 1rem !important;
}

[data-testid="stMetricLabel"] p {
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    color: #64748b !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
}

/* Page Header Row */
.pc-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.pc-header-left {
    flex: 1 1 auto;
}

.pc-header-right {
    flex: 0 0 auto;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 0.75rem !important;
        padding-left: 0.875rem !important;
        padding-right: 0.875rem !important;
    }
    h1 {
        font-size: 1.5rem !important;
    }
    h2 {
        font-size: 1.15rem !important;
    }
    .pc-header-row {
        flex-direction: column;
        align-items: stretch;
    }
    .pc-header-right {
        margin-top: 0.5rem;
    }
}

@media (prefers-reduced-motion: reduce) {
    * {
        transition: none !important;
        animation: none !important;
    }
}
</style>
"""


def inject_theme():
    """Inject minimal stylesheet."""
    st.markdown(MINIMAL_CSS, unsafe_allow_html=True)


def apply_plotly_theme(fig: go.Figure, height: int = 340) -> go.Figure:
    """Apply minimal, restrained Plotly theme."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        font=dict(family="'Inter', -apple-system, sans-serif", size=12, color="#0f172a"),
        colorway=["#1d4ed8", "#475569", "#64748b", "#94a3b8", "#cbd5e1"],
        margin=dict(l=40, r=24, t=20, b=40),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148, 163, 184, 0.2)",
        zeroline=False,
        linecolor="rgba(148, 163, 184, 0.3)",
        tickfont=dict(size=11),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148, 163, 184, 0.2)",
        zeroline=False,
        linecolor="rgba(148, 163, 184, 0.3)",
        tickfont=dict(size=11),
    )
    return fig
