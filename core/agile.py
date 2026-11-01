"""Agile Frameworks Comparison, Sprint Planning & Cost of Change Engine.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 2:
    Agile Development: What is Agility? What is an Agile Process?
    Agility Principles, The Cost of Change, Extreme Programming (XP),
    Other Agile Process Models: Adaptive Software Development (ASD), Scrum,
    Dynamic Systems Development Method (DSDM), Crystal, Feature Driven
    Development (FDD), Lean/Kanban.
Course Outcome:
    CO2: Interpret Agile Principles and Formulate Agile Project Iterations.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
import math
from datetime import date, timedelta


AGILE_FRAMEWORKS: List[Dict[str, Any]] = [
    {
        "name": "Scrum",
        "focus": "Iterative delivery, self-organizing teams & empiricism (Inspect-Adapt)",
        "team_size": "Small (3–9 developers + PO + SM)",
        "iteration_style": "Time-boxed Sprints (1–4 weeks)",
        "key_practices": "Sprint Planning, Daily Scrum, Sprint Review, Retrospective, Product Backlog refinement",
        "best_fit": "Evolving product requirements, cross-functional product development with active customer feedback",
    },
    {
        "name": "Extreme Programming (XP)",
        "focus": "Engineering discipline, code quality, test-driven agility",
        "team_size": "Small (2–10 developers)",
        "iteration_style": "Short releases (1–2 weeks)",
        "key_practices": "Pair Programming, Test-Driven Development (TDD), Continuous Integration (CI), Refactoring, On-site Customer",
        "best_fit": "High technical risk, rapidly changing requirements, systems demanding exceptional automated test coverage",
    },
    {
        "name": "Kanban",
        "focus": "Continuous workflow optimization, cycle time reduction & eliminating bottlenecks",
        "team_size": "Any size (ideal for service & maintenance teams)",
        "iteration_style": "Continuous flow (cadence decoupled from release)",
        "key_practices": "Visualizing workflow (Kanban Board), Limiting Work in Progress (WIP), Managing flow, Explicit policies",
        "best_fit": "Support teams, maintenance operations, continuous delivery environments with high incoming request variability",
    },
    {
        "name": "Feature-Driven Development (FDD)",
        "focus": "Client-valued feature chunks & object-oriented domain modeling",
        "team_size": "Medium to Large (multi-team scaling)",
        "iteration_style": "Short feature milestones (typically 2 weeks per feature set)",
        "key_practices": "Domain Object Modeling, Developing by Feature, Individual Class Ownership, Feature Teams, Regular Builds",
        "best_fit": "Enterprise object-oriented development with domain architectures and larger engineering organizations",
    },
    {
        "name": "Dynamic Systems Development Method (DSDM)",
        "focus": "Business governance, on-time budget delivery & strategic value",
        "team_size": "Small to Medium (cross-functional)",
        "iteration_style": "Strict timeboxes (Exploration, Engineering cycles)",
        "key_practices": "MoSCoW Prioritization (Must/Should/Could/Won't have), Timeboxing, Prototyping, Empowered Teams",
        "best_fit": "Corporate environments requiring strict delivery deadlines, fixed budgets, and regulatory milestone reporting",
    },
    {
        "name": "Adaptive Software Development (ASD)",
        "focus": "Complex Adaptive Systems (CAS), speculation vs predictability",
        "team_size": "Small to Medium",
        "iteration_style": "Time-boxed cycles (Speculate -> Collaborate -> Learn)",
        "key_practices": "Mission-driven planning, Component-based focus, Concurrent collaboration, Quality via customer feedback",
        "best_fit": "High-uncertainty innovation projects where requirements cannot be predicted in advance",
    },
    {
        "name": "Crystal",
        "focus": "People, communication, interaction & project criticality (Cockburn)",
        "team_size": "Color-coded: Clear (<=6), Yellow (<=20), Orange (<=40), Red (<=80)",
        "iteration_style": "Iterative (cycles from 1 to 3 months depending on color)",
        "key_practices": "Frequent delivery, Reflective improvement, Osmotic communication, Personal safety, Focus",
        "best_fit": "Tailored to team size and system criticality (Comfort, Discretionary Money, Essential Money, Life)",
    },
]


@dataclass
class SprintPlanResult:
    total_story_points: float
    team_velocity: float
    sprint_length_weeks: int
    sprints_needed: int
    total_weeks: int
    total_calendar_days: int
    start_date: str
    finish_date: str
    burndown_schedule: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_story_points": self.total_story_points,
            "team_velocity": self.team_velocity,
            "sprint_length_weeks": self.sprint_length_weeks,
            "sprints_needed": self.sprints_needed,
            "total_weeks": self.total_weeks,
            "total_calendar_days": self.total_calendar_days,
            "start_date": self.start_date,
            "finish_date": self.finish_date,
            "burndown_schedule": self.burndown_schedule,
        }


def calculate_sprint_plan(
    backlog_points: float,
    velocity_per_sprint: float,
    sprint_length_weeks: int = 2,
    start_date: date | None = None,
) -> SprintPlanResult:
    """Calculate sprint capacity, schedule duration, and burn-down curve.

    Args:
        backlog_points: Total estimated story points in product backlog (> 0).
        velocity_per_sprint: Expected or historical story points delivered per sprint (> 0).
        sprint_length_weeks: Duration of single sprint in weeks (1, 2, 3, or 4).
        start_date: Project sprint 1 kickoff date. Defaults to date.today().

    Returns:
        SprintPlanResult with milestone dates and burndown trajectory.
    """
    if backlog_points <= 0:
        raise ValueError(f"Backlog points must be positive, got {backlog_points}")
    if velocity_per_sprint <= 0:
        raise ValueError(f"Team velocity must be positive, got {velocity_per_sprint}")
    if sprint_length_weeks not in [1, 2, 3, 4]:
        raise ValueError(f"Sprint length should typically be 1, 2, 3, or 4 weeks, got {sprint_length_weeks}")

    if start_date is None:
        start_date = date.today()

    sprints_needed = math.ceil(backlog_points / velocity_per_sprint)
    total_weeks = sprints_needed * sprint_length_weeks
    total_days = total_weeks * 7
    finish_date = start_date + timedelta(days=total_days)

    # Burndown Schedule: Sprint 0 (initial backlog) down to Sprint N
    schedule: List[Dict[str, Any]] = []
    # Ideal step decrement
    ideal_step = backlog_points / sprints_needed if sprints_needed > 0 else 0.0

    current_date = start_date
    for s_idx in range(sprints_needed + 1):
        ideal_remaining = max(0.0, backlog_points - (s_idx * ideal_step))
        projected_remaining = max(0.0, backlog_points - (s_idx * velocity_per_sprint))

        schedule.append({
            "sprint": f"Sprint {s_idx}" if s_idx > 0 else "Baseline (Sprint 0)",
            "sprint_number": s_idx,
            "date": current_date.isoformat(),
            "ideal_remaining_points": round(ideal_remaining, 1),
            "projected_remaining_points": round(projected_remaining, 1),
            "points_burned": round(min(backlog_points, s_idx * velocity_per_sprint), 1),
        })

        if s_idx > 0:
            current_date += timedelta(days=sprint_length_weeks * 7)

    return SprintPlanResult(
        total_story_points=float(backlog_points),
        team_velocity=float(velocity_per_sprint),
        sprint_length_weeks=sprint_length_weeks,
        sprints_needed=sprints_needed,
        total_weeks=total_weeks,
        total_calendar_days=total_days,
        start_date=start_date.isoformat(),
        finish_date=finish_date.isoformat(),
        burndown_schedule=schedule,
    )


def generate_cost_of_change_data() -> List[Dict[str, Any]]:
    """Generate comparative data for Traditional vs Agile Cost of Change curves.

    Syllabus Reference:
        VTU 24CS51 Module 2: The Cost of Change Curve (Boehm vs Beck).
        Traditional curve rises exponentially through phases (Requirements -> Design -> Code -> Test -> Post-Release).
        Agile curve flattens cost of change through automated testing, continuous integration, and refactoring.
    """
    phases = [
        {"phase": "Requirements", "seq": 1, "traditional_multiplier": 1.0, "agile_multiplier": 1.0},
        {"phase": "Architecture & Design", "seq": 2, "traditional_multiplier": 3.5, "agile_multiplier": 1.3},
        {"phase": "Implementation / Coding", "seq": 3, "traditional_multiplier": 10.0, "agile_multiplier": 1.8},
        {"phase": "System Testing", "seq": 4, "traditional_multiplier": 40.0, "agile_multiplier": 2.5},
        {"phase": "Post-Release Production", "seq": 5, "traditional_multiplier": 100.0, "agile_multiplier": 3.8},
    ]

    result = []
    for p in phases:
        result.append({
            "Lifecycle Phase": p["phase"],
            "Sequence": p["seq"],
            "Traditional (Exponential)": p["traditional_multiplier"],
            "Agile (Flattened Curve)": p["agile_multiplier"],
            "Ratio (Traditional / Agile)": round(p["traditional_multiplier"] / p["agile_multiplier"], 1),
        })
    return result
