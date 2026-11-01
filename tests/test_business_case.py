"""Unit tests for Business Case, NPV, ROI, Payback, Scenario Risk & RADR (VTU 24CS51 Module 3)."""

import pytest
import math
from core.business_case import (
    evaluate_business_case,
    evaluate_scenario_risk,
    evaluate_radr,
)


def test_positive_business_case():
    """Verify NPV, ROI and payback on a profitable project."""
    initial = 100000.0
    benefits = [40000.0, 50000.0, 60000.0]
    costs = [10000.0, 10000.0, 10000.0]
    discount_rate = 10.0  # 10%

    res = evaluate_business_case(initial, benefits, costs, discount_rate)

    assert math.isclose(res.net_profit, 20000.0, rel_tol=1e-4)
    assert math.isclose(res.roi_pct, 20.0, rel_tol=1e-4)
    assert len(res.yearly_flows) == 4  # Year 0 + 3 years

    assert res.payback_period_years is not None
    assert math.isclose(res.payback_period_years, 2.6, rel_tol=1e-2)


def test_unviable_business_case():
    """Returns that fail to cover investment should flag project as unviable."""
    initial = 100000.0
    benefits = [10000.0, 10000.0]
    costs = 5000.0
    res = evaluate_business_case(initial, benefits, costs, discount_rate_pct=8.0)

    assert res.npv < 0
    assert not res.is_financially_viable
    assert res.payback_period_years is None


def test_validation_errors():
    with pytest.raises(ValueError, match="Initial investment must be positive"):
        evaluate_business_case(initial_investment=-1000.0, annual_benefits=[1000.0])

    with pytest.raises(ValueError, match="Must provide at least one year"):
        evaluate_business_case(initial_investment=1000.0, annual_benefits=[])


def test_scenario_risk_evaluation():
    """Verify Expected NPV (EMV) = sum(p_i * NPV_i) and variance."""
    initial = 80000.0
    benefits = [30000.0, 40000.0, 50000.0]
    costs = [5000.0, 5000.0, 5000.0]
    discount_rate = 10.0
    probs = (0.20, 0.60, 0.20)

    scenario_res = evaluate_scenario_risk(
        base_investment=initial,
        base_benefits=benefits,
        base_costs=costs,
        discount_rate_pct=discount_rate,
        probabilities=probs,
    )

    assert len(scenario_res.scenarios) == 3
    s_names = [s.name for s in scenario_res.scenarios]
    assert s_names == ["Optimistic", "Most Likely", "Pessimistic"]

    # Manual EMV check
    opt_npv = scenario_res.scenarios[0].npv
    likely_npv = scenario_res.scenarios[1].npv
    pess_npv = scenario_res.scenarios[2].npv

    expected_manual = (0.20 * opt_npv) + (0.60 * likely_npv) + (0.20 * pess_npv)
    assert math.isclose(scenario_res.expected_npv, expected_manual, rel_tol=1e-5)
    assert scenario_res.npv_standard_deviation >= 0.0
    assert scenario_res.npv_variance >= 0.0


def test_radr_evaluation():
    """Verify Risk-Adjusted Discount Rate increases hurdle rate and reduces NPV."""
    initial = 60000.0
    benefits = [30000.0, 35000.0, 40000.0]
    costs = [6000.0, 6000.0, 6000.0]
    base_rate = 10.0
    risk_premium = 4.0

    radr_res = evaluate_radr(
        initial_investment=initial,
        annual_benefits=benefits,
        annual_costs=costs,
        base_discount_rate_pct=base_rate,
        risk_premium_pct=risk_premium,
    )

    assert radr_res.base_discount_rate_pct == 10.0
    assert radr_res.risk_premium_pct == 4.0
    assert radr_res.adjusted_discount_rate_pct == 14.0
    # Higher discount rate implies lower NPV
    assert radr_res.adjusted_npv < radr_res.base_npv
    assert radr_res.npv_delta < 0
