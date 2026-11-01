"""Unit tests for McCall's Quality Scorecard Engine (VTU 24CS51 Module 5)."""

import pytest
import math
from core.quality import evaluate_quality_scorecard, MCCALL_TAXONOMY, ALL_FACTORS


def test_mccall_factor_structure():
    """Ensure exactly 11 factors distributed across 3 pillars."""
    assert len(ALL_FACTORS) == 11
    assert "Product Operation" in MCCALL_TAXONOMY
    assert "Product Revision" in MCCALL_TAXONOMY
    assert "Product Transition" in MCCALL_TAXONOMY


def test_quality_evaluation_calculation():
    """Scorecard computes correct category averages and overall index."""
    # Score everything as 4.0
    ratings = {f: 4.0 for f in ALL_FACTORS}
    res = evaluate_quality_scorecard(ratings)

    assert math.isclose(res.overall_index, 4.0, rel_tol=1e-5)
    assert math.isclose(res.overall_percentage, 80.0, rel_tol=1e-5)
    assert res.categories["Product Operation"].average_score == 4.0
    assert res.categories["Product Revision"].average_score == 4.0
    assert res.categories["Product Transition"].average_score == 4.0


def test_quality_clamping_and_verdicts():
    # Out of range scores should be clamped to [1.0, 5.0]
    ratings = {f: 10.0 for f in ALL_FACTORS}
    res = evaluate_quality_scorecard(ratings)
    assert math.isclose(res.overall_index, 5.0, rel_tol=1e-5)
    assert "Grade A" in res.sqa_verdict

    ratings_low = {f: 0.5 for f in ALL_FACTORS}
    res_low = evaluate_quality_scorecard(ratings_low)
    assert math.isclose(res_low.overall_index, 1.0, rel_tol=1e-5)
    assert "Grade C" in res_low.sqa_verdict

