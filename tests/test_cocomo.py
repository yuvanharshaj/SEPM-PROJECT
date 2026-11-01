"""Unit tests for Basic COCOMO Estimation Engine (VTU 24CS51 Module 3)."""

import pytest
import math
from core.cocomo import calculate_cocomo, COCOMO_COEFFICIENTS


def test_cocomo_organic_calculation():
    """Verify Organic mode against theoretical formula E = 2.4 * KLOC^1.05, T = 2.5 * E^0.38."""
    kloc = 10.0
    result = calculate_cocomo(kloc=kloc, mode="organic")

    expected_effort = 2.4 * (10.0 ** 1.05)
    expected_duration = 2.5 * (expected_effort ** 0.38)
    expected_staff = expected_effort / expected_duration
    expected_productivity = (10.0 * 1000.0) / expected_effort

    assert math.isclose(result.effort_pm, expected_effort, rel_tol=1e-5)
    assert math.isclose(result.duration_months, expected_duration, rel_tol=1e-5)
    assert math.isclose(result.avg_staff, expected_staff, rel_tol=1e-5)
    assert math.isclose(result.productivity_loc_pm, expected_productivity, rel_tol=1e-5)
    assert result.mode == "organic"


def test_cocomo_semidetached_calculation():
    """Verify Semi-detached mode against formula E = 3.0 * KLOC^1.12, T = 2.5 * E^0.35."""
    kloc = 32.0
    result = calculate_cocomo(kloc=kloc, mode="semi-detached")

    expected_effort = 3.0 * (32.0 ** 1.12)
    expected_duration = 2.5 * (expected_effort ** 0.35)

    assert math.isclose(result.effort_pm, expected_effort, rel_tol=1e-5)
    assert math.isclose(result.duration_months, expected_duration, rel_tol=1e-5)
    assert result.avg_staff > 0


def test_cocomo_embedded_calculation():
    """Verify Embedded mode against formula E = 3.6 * KLOC^1.20, T = 2.5 * E^0.32."""
    kloc = 50.0
    result = calculate_cocomo(kloc=kloc, mode="embedded")

    expected_effort = 3.6 * (50.0 ** 1.20)
    expected_duration = 2.5 * (expected_effort ** 0.32)

    assert math.isclose(result.effort_pm, expected_effort, rel_tol=1e-5)
    assert math.isclose(result.duration_months, expected_duration, rel_tol=1e-5)
    assert result.a == 3.6
    assert result.b == 1.20


def test_cocomo_invalid_mode_raises():
    with pytest.raises(ValueError, match="Invalid COCOMO mode"):
        calculate_cocomo(kloc=20.0, mode="super-complex")  # type: ignore


def test_cocomo_invalid_kloc_raises():
    with pytest.raises(ValueError, match="KLOC must be strictly greater than 0"):
        calculate_cocomo(kloc=0.0, mode="organic")

    with pytest.raises(ValueError, match="KLOC must be strictly greater than 0"):
        calculate_cocomo(kloc=-5.0, mode="organic")


def test_cocomo_to_dict():
    result = calculate_cocomo(kloc=15.0, mode="organic")
    d = result.to_dict()
    assert d["mode"] == "organic"
    assert "effort_pm" in d
    assert "duration_months" in d
    assert "avg_staff" in d
