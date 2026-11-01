"""Unit tests for COSMIC Full Function Points (FFP) Engine (VTU 24CS51 Module 4)."""

import pytest
import math
from core.cosmic import calculate_cosmic_ffp, FunctionalProcess


def test_cosmic_functional_process():
    """Verify single process CFP = E + X + R + W."""
    fp = FunctionalProcess(
        process_id="FP-01",
        name="User Authentication",
        entries=2,
        exits=2,
        reads=1,
        writes=1,
    )
    assert fp.calculate_cfp() == 6
    assert fp.cfp == 6


def test_cosmic_aggregate_calculation():
    """Verify multiple functional processes summation and effort conversion."""
    processes = [
        {"process_id": "P1", "name": "Patient Check-in", "entries": 3, "exits": 2, "reads": 1, "writes": 2}, # 8 CFP
        {"process_id": "P2", "name": "Vitals Stream", "entries": 1, "exits": 4, "reads": 2, "writes": 2},     # 9 CFP
        {"process_id": "P3", "name": "Telemetry Alert", "entries": 2, "exits": 1, "reads": 1, "writes": 1},    # 5 CFP
    ]
    # Total CFP = 8 + 9 + 5 = 22 CFP
    # Productivity = 10 hours/CFP -> 220 hours
    # Effort PM = 220 / 160 = 1.375 PM
    # Team size = 2 -> Duration = 1.375 / 2 = 0.6875 months
    res = calculate_cosmic_ffp(processes, productivity_hours_per_cfp=10.0, team_size=2)

    assert res.total_cfp == 22
    assert res.total_entries == 6
    assert res.total_exits == 7
    assert res.total_reads == 4
    assert res.total_writes == 5
    assert math.isclose(res.total_effort_hours, 220.0, rel_tol=1e-5)
    assert math.isclose(res.total_effort_pm, 1.375, rel_tol=1e-5)
    assert math.isclose(res.estimated_duration_months, 0.6875, rel_tol=1e-5)


def test_cosmic_validation():
    with pytest.raises(ValueError, match="Productivity hours per CFP must be positive"):
        calculate_cosmic_ffp([], productivity_hours_per_cfp=0.0)

    with pytest.raises(ValueError, match="Team size must be at least 1"):
        calculate_cosmic_ffp([], team_size=0)
