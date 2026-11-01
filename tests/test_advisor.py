"""Unit tests for Process Model Advisor Engine (VTU 24CS51 Module 1)."""

import pytest
from core.advisor import evaluate_models, MODELS


def test_advisor_agile_profile():
    """Volatile requirements, high customer involvement, need for early delivery should favor Scrum or XP."""
    profile = {
        "req_stability": "Low",
        "team_size": "Small",
        "duration": "Short",
        "risk_level": "Medium",
        "customer_involvement": "High",
        "early_delivery": "High",
        "team_experience": "High",
    }
    result = evaluate_models(profile)

    assert result.top_model.model_name in ["Scrum", "XP"]
    assert result.top_model.percentage > 70.0
    # Waterfall should be penalised for low requirement stability and high early delivery need
    waterfall_model = next(m for m in result.ranked_models if m.model_name == "Waterfall")
    assert waterfall_model.score < result.top_model.score
    assert len(result.ranked_models) == len(MODELS)


def test_advisor_waterfall_profile():
    """Fixed requirements, low risk, low customer involvement should favor Waterfall."""
    profile = {
        "req_stability": "High",
        "team_size": "Medium",
        "duration": "Medium",
        "risk_level": "Low",
        "customer_involvement": "Low",
        "early_delivery": "Low",
        "team_experience": "High",
    }
    result = evaluate_models(profile)

    assert result.top_model.model_name == "Waterfall"
    assert result.top_model.rank == 1
    assert "Waterfall" in result.executive_summary


def test_advisor_spiral_profile():
    """High risk, complex, large team, long duration should favor Spiral / Unified Process."""
    profile = {
        "req_stability": "Medium",
        "team_size": "Large",
        "duration": "Long",
        "risk_level": "High",
        "customer_involvement": "High",
        "early_delivery": "Low",
        "team_experience": "High",
    }
    result = evaluate_models(profile)

    assert result.top_model.model_name in ["Evolutionary/Spiral", "Unified Process"]


def test_custom_weights_effect():
    """Tuning weights alters scoring."""
    profile = {
        "req_stability": "Medium",
        "team_size": "Small",
        "duration": "Short",
        "risk_level": "Medium",
        "customer_involvement": "Medium",
        "early_delivery": "Medium",
        "team_experience": "Medium",
    }
    res_default = evaluate_models(profile)
    # Exaggerate early delivery weight massively
    res_skewed = evaluate_models(profile, custom_weights={"early_delivery": 10.0})

    assert res_skewed.top_model.score > res_default.top_model.score
