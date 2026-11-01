"""Unit tests for Risk Management & Risk Exposure Engine (VTU 24CS51 Module 4)."""

import pytest
import math
from core.risk import analyze_risk_register, classify_severity


def test_risk_exposure_formula():
    """Verify RE = Probability * Impact and ranking logic."""
    risks = [
        {"id": "R1", "description": "Minor delay", "category": "Technical", "probability": 0.2, "impact_cost": 10000.0},
        {"id": "R2", "description": "Major breach", "category": "Security & Compliance", "probability": 0.5, "impact_cost": 100000.0},
        {"id": "R3", "description": "Scope creep", "category": "Requirements & Scope", "probability": 0.8, "impact_cost": 30000.0},
    ]

    summary = analyze_risk_register(risks)

    # RE(R1) = 0.2 * 10,000 = 2,000
    # RE(R2) = 0.5 * 100,000 = 50,000
    # RE(R3) = 0.8 * 30,000 = 24,000
    # Total = 76,000
    assert summary.total_risks == 3
    assert math.isclose(summary.total_exposure, 76000.0, rel_tol=1e-5)

    # Ranking: R2 (50k) > R3 (24k) > R1 (2k)
    assert summary.ranked_risks[0].id == "R2"
    assert summary.ranked_risks[0].rank == 1
    assert summary.ranked_risks[1].id == "R3"
    assert summary.ranked_risks[1].rank == 2
    assert summary.ranked_risks[2].id == "R1"
    assert summary.ranked_risks[2].rank == 3


def test_empty_risk_register():
    summary = analyze_risk_register([])
    assert summary.total_risks == 0
    assert summary.total_exposure == 0.0
    assert summary.ranked_risks == []


def test_risk_severity_classification():
    sev_crit = classify_severity(0.8, 90000, 100000)
    assert sev_crit in ["Critical", "High"]

    sev_low = classify_severity(0.1, 5000, 100000)
    assert sev_low == "Low"
