"""Unit tests for SQLite Database Layer and Sample Preloading."""

import os
import pytest
from db.database import DatabaseManager


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_compass.db"
    mgr = DatabaseManager(db_path=str(db_file))
    return mgr


def test_db_initialization_and_preloading(temp_db):
    """Database initializes with 3 benchmark sample projects."""
    projects = temp_db.list_projects()
    assert len(projects) == 3
    names = {p["name"] for p in projects}
    assert "College ERP System" in names
    assert "Mobile Banking App" in names
    assert "Embedded IoT Medical Device" in names


def test_db_get_project_details(temp_db):
    """Fetching complete project extracts FP, risks, business case, and quality scores."""
    proj = temp_db.get_project_by_name("College ERP System")
    assert proj is not None
    assert proj["team_size"] == 14
    assert len(proj["risks"]) == 4
    assert proj["fp_components"] is not None
    assert proj["business_case"]["initial_investment"] == 7000000.0
    assert "Correctness" in proj["quality_scores"]


def test_db_save_and_update(temp_db):
    """Saving new project inserts row; saving existing name updates."""
    new_proj = {
        "name": "Autonomous Drone Navigator",
        "description": "Embedded flight controller for quadcopters",
        "team_size": 4,
        "duration": 6,
        "budget": 35000.0,
        "req_stability": "High",
        "customer_involvement": "Low",
        "risk_level": "High",
        "early_delivery": "Low",
        "team_experience": "High",
        "cocomo_mode": "embedded",
        "kloc": 15.0,
        "risks": [
            {"id": "R-01", "category": "Technical", "description": "IMU drift", "probability": 0.4, "impact_cost": 5000.0}
        ],
    }
    pid = temp_db.save_complete_project(new_proj)
    assert pid is not None

    fetched = temp_db.get_project_by_id(pid)
    assert fetched["name"] == "Autonomous Drone Navigator"
    assert len(fetched["risks"]) == 1

    # Update team size
    new_proj["id"] = pid
    new_proj["team_size"] = 5
    temp_db.save_complete_project(new_proj)

    updated = temp_db.get_project_by_id(pid)
    assert updated["team_size"] == 5


def test_db_delete(temp_db):
    proj = temp_db.get_project_by_name("College ERP System")
    pid = proj["id"]
    deleted = temp_db.delete_project(pid)
    assert deleted is True

    assert temp_db.get_project_by_id(pid) is None

