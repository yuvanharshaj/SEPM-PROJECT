"""Unit tests for Agile Lab Engine (VTU 24CS51 Module 2)."""

import pytest
import math
from datetime import date
from core.agile import (
    calculate_sprint_plan,
    generate_cost_of_change_data,
    AGILE_FRAMEWORKS,
)


def test_agile_frameworks_coverage():
    """Verify all 7 syllabus agile frameworks are documented with required criteria."""
    assert len(AGILE_FRAMEWORKS) == 7
    names = {f["name"] for f in AGILE_FRAMEWORKS}
    expected = {"Scrum", "Extreme Programming (XP)", "Kanban", "Feature-Driven Development (FDD)",
                "Dynamic Systems Development Method (DSDM)", "Adaptive Software Development (ASD)", "Crystal"}
    assert names == expected

    for f in AGILE_FRAMEWORKS:
        assert "focus" in f
        assert "team_size" in f
        assert "iteration_style" in f
        assert "key_practices" in f
        assert "best_fit" in f


def test_sprint_planner_calculation():
    """Verify sprint counts, duration, and burndown data points."""
    # 125 story points / 25 velocity = exactly 5 sprints
    # 2 weeks/sprint -> 10 weeks -> 70 calendar days
    start = date(2026, 11, 2)
    plan = calculate_sprint_plan(
        backlog_points=125.0,
        velocity_per_sprint=25.0,
        sprint_length_weeks=2,
        start_date=start,
    )

    assert plan.sprints_needed == 5
    assert plan.total_weeks == 10
    assert plan.total_calendar_days == 70
    assert plan.start_date == "2026-11-02"
    assert len(plan.burndown_schedule) == 6  # Sprint 0 + 5 sprints

    # Baseline
    assert plan.burndown_schedule[0]["ideal_remaining_points"] == 125.0
    # Final sprint
    assert plan.burndown_schedule[5]["ideal_remaining_points"] == 0.0
    assert plan.burndown_schedule[5]["projected_remaining_points"] == 0.0


def test_sprint_planner_fractional():
    """Non-integer sprint ratio should round up (ceiling)."""
    # 100 points / 30 velocity = 3.33 -> 4 sprints needed
    plan = calculate_sprint_plan(
        backlog_points=100.0,
        velocity_per_sprint=30.0,
        sprint_length_weeks=1,
    )
    assert plan.sprints_needed == 4
    assert plan.total_weeks == 4


def test_sprint_planner_invalid_inputs():
    with pytest.raises(ValueError, match="Backlog points must be positive"):
        calculate_sprint_plan(backlog_points=0.0, velocity_per_sprint=20.0)

    with pytest.raises(ValueError, match="Team velocity must be positive"):
        calculate_sprint_plan(backlog_points=50.0, velocity_per_sprint=0.0)

    with pytest.raises(ValueError, match="Sprint length should typically be 1, 2, 3, or 4"):
        calculate_sprint_plan(backlog_points=50.0, velocity_per_sprint=10.0, sprint_length_weeks=6)


def test_cost_of_change_curves():
    """Verify Traditional exponential vs Agile flattened cost of change curves."""
    curves = generate_cost_of_change_data()
    assert len(curves) == 5

    # Requirements phase ratio should be 1.0
    assert curves[0]["Traditional (Exponential)"] == 1.0
    assert curves[0]["Agile (Flattened Curve)"] == 1.0

    # Post-release production phase
    last = curves[-1]
    assert last["Lifecycle Phase"] == "Post-Release Production"
    assert last["Traditional (Exponential)"] == 100.0
    assert last["Agile (Flattened Curve)"] < 10.0
    assert last["Traditional (Exponential)"] > last["Agile (Flattened Curve)"]
