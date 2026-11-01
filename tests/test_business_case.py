"""Unit tests for Business Case, NPV, ROI & Payback Engine (VTU 24CS51 Module 4)."""

import pytest
import math
from core.business_case import evaluate_business_case


def test_positive_business_case():
    """Verify NPV, ROI and payback on a profitable project."""
    initial = 100000.0
    benefits = [40000.0, 50000.0, 60000.0]
    costs = [10000.0, 10000.0, 10000.0]
    discount_rate = 10.0  # 10%

    # NCF_1 = 30,000, NCF_2 = 40,000, NCF_3 = 50,000
    # Total profit = (30k + 40k + 50k) - 100k = 20,000
    # ROI = (20,000 / 100,000) * 100 = 20.0%
    # DCF_1 = 30000 / 1.1^1 = 27,272.73
    # DCF_2 = 40000 / 1.1^2 = 33,057.85
    # DCF_3 = 50000 / 1.1^3 = 37,565.74
    # NPV = (27272.73 + 33057.85 + 37565.74) - 100000 = -2,103.68 (slightly negative at 10%)
    res = evaluate_business_case(initial, benefits, costs, discount_rate)

    assert math.isclose(res.net_profit, 20000.0, rel_tol=1e-4)
    assert math.isclose(res.roi_pct, 20.0, rel_tol=1e-4)
    assert len(res.yearly_flows) == 4  # Year 0 + 3 years

    # Undiscounted Payback:
    # End yr 1: 30k (deficit 70k)
    # End yr 2: 70k (deficit 30k)
    # End yr 3: 120k (surplus 20k)
    # Payback = 2 + 30/50 = 2.6 years
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
    assert res.payback_period_years is None  # Never pays back within project span


def test_validation_errors():
    with pytest.raises(ValueError, match="Initial investment must be positive"):
        evaluate_business_case(initial_investment=-1000.0, annual_benefits=[1000.0])

    with pytest.raises(ValueError, match="Must provide at least one year"):
        evaluate_business_case(initial_investment=1000.0, annual_benefits=[])

