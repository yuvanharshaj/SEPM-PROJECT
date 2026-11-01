"""Unit tests for Bottom-Up & Three-Point (PERT) Estimation Engine (VTU 24CS51 Module 4)."""

import pytest
import math
from core.pert import calculate_pert, PertTask


def test_pert_single_task():
    """Verify E = (O + 4M + P)/6 and SD = (P - O)/6."""
    task = PertTask(
        task_id="T-01",
        name="Database Schema Migration",
        category="Architecture",
        optimistic=6.0,
        most_likely=12.0,
        pessimistic=24.0,
    )
    task.compute()

    # E = (6 + 4*12 + 24) / 6 = (6 + 48 + 24) / 6 = 78 / 6 = 13.0
    # SD = (24 - 6) / 6 = 18 / 6 = 3.0
    # V = 3.0^2 = 9.0
    assert math.isclose(task.expected, 13.0, rel_tol=1e-5)
    assert math.isclose(task.standard_deviation, 3.0, rel_tol=1e-5)
    assert math.isclose(task.variance, 9.0, rel_tol=1e-5)


def test_pert_aggregate_project():
    """Verify combined expected effort, summed variance, and 90% confidence range."""
    # Task 1: O=4, M=10, P=16 -> E = (4+40+16)/6 = 10.0, SD = (16-4)/6 = 2.0, V = 4.0
    # Task 2: O=8, M=12, P=28 -> E = (8+48+28)/6 = 14.0, SD = (28-8)/6 = 3.3333, V = 11.1111
    # Total E = 24.0
    # Total V = 4.0 + 11.1111 = 15.1111
    # Combined SD = sqrt(15.1111) = 3.8873
    # 90% interval = [24.0 - 1.645*3.8873, 24.0 + 1.645*3.8873] = [17.61, 30.39]
    tasks = [
        {"task_id": "T1", "name": "Task 1", "category": "Backend", "optimistic": 4.0, "most_likely": 10.0, "pessimistic": 16.0},
        {"task_id": "T2", "name": "Task 2", "category": "Frontend", "optimistic": 8.0, "most_likely": 12.0, "pessimistic": 28.0},
    ]

    res = calculate_pert(tasks)

    assert math.isclose(res.total_expected, 24.0, rel_tol=1e-4)
    expected_v = 4.0 + ((20.0 / 6.0) ** 2)
    assert math.isclose(res.combined_variance, expected_v, rel_tol=1e-4)
    expected_sd = math.sqrt(expected_v)
    assert math.isclose(res.combined_sd, expected_sd, rel_tol=1e-4)

    expected_low = 24.0 - (1.645 * expected_sd)
    expected_high = 24.0 + (1.645 * expected_sd)
    assert math.isclose(res.confidence_90_range[0], expected_low, rel_tol=1e-3)
    assert math.isclose(res.confidence_90_range[1], expected_high, rel_tol=1e-3)


def test_pert_invalid_order_raises():
    with pytest.raises(ValueError, match="must satisfy Optimistic"):
        task = PertTask(
            task_id="T-Err",
            name="Broken Task",
            category="Test",
            optimistic=20.0,
            most_likely=10.0,
            pessimistic=30.0,
        )
        task.compute()


def test_pert_empty_list():
    res = calculate_pert([])
    assert res.total_tasks == 0
    assert res.total_expected == 0.0
    assert res.combined_sd == 0.0
