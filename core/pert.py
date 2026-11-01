"""Bottom-Up & Three-Point (PERT) Estimation Engine.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 4:
    Project Estimation Techniques, Decomposition Techniques, Bottom-Up Estimating,
    Three-Point (PERT) Statistical Estimating (Beta Distribution).

Formulas:
    For each task i:
        Expected Effort (E_i)       : E_i = (O_i + 4*M_i + P_i) / 6
        Standard Deviation (SD_i)   : SD_i = (P_i - O_i) / 6
        Variance (V_i)              : V_i = SD_i^2

    For the aggregate project:
        Total Expected Effort       : E_total = sum(E_i)
        Combined Variance (V_total) : V_total = sum(V_i)
        Combined Standard Deviation : SD_total = sqrt(V_total)
        90% Confidence Interval     : E_total +/- (1.645 * SD_total)
        95% Confidence Interval     : E_total +/- (1.960 * SD_total)
        68% Confidence Interval     : E_total +/- (1.000 * SD_total)
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import math


@dataclass
class PertTask:
    task_id: str
    name: str
    category: str
    optimistic: float
    most_likely: float
    pessimistic: float
    expected: float = 0.0
    standard_deviation: float = 0.0
    variance: float = 0.0

    def compute(self) -> None:
        if self.optimistic < 0 or self.most_likely < 0 or self.pessimistic < 0:
            raise ValueError(f"Task '{self.name}' has negative estimate values.")
        if not (self.optimistic <= self.most_likely <= self.pessimistic):
            raise ValueError(
                f"Task '{self.name}': Values must satisfy Optimistic ({self.optimistic}) <= "
                f"Most Likely ({self.most_likely}) <= Pessimistic ({self.pessimistic})"
            )

        self.expected = (self.optimistic + (4.0 * self.most_likely) + self.pessimistic) / 6.0
        self.standard_deviation = (self.pessimistic - self.optimistic) / 6.0
        self.variance = self.standard_deviation ** 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "category": self.category,
            "optimistic": round(self.optimistic, 2),
            "most_likely": round(self.most_likely, 2),
            "pessimistic": round(self.pessimistic, 2),
            "expected": round(self.expected, 2),
            "standard_deviation": round(self.standard_deviation, 2),
            "variance": round(self.variance, 3),
        }


@dataclass
class PertResult:
    total_tasks: int
    total_expected: float
    combined_variance: float
    combined_sd: float
    confidence_90_range: Tuple[float, float]
    confidence_95_range: Tuple[float, float]
    confidence_68_range: Tuple[float, float]
    tasks: List[PertTask]
    category_breakdown: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tasks": self.total_tasks,
            "total_expected": round(self.total_expected, 2),
            "combined_variance": round(self.combined_variance, 3),
            "combined_sd": round(self.combined_sd, 2),
            "confidence_90_range": (round(self.confidence_90_range[0], 2), round(self.confidence_90_range[1], 2)),
            "confidence_95_range": (round(self.confidence_95_range[0], 2), round(self.confidence_95_range[1], 2)),
            "confidence_68_range": (round(self.confidence_68_range[0], 2), round(self.confidence_68_range[1], 2)),
            "category_breakdown": {k: round(v, 2) for k, v in self.category_breakdown.items()},
            "tasks": [t.to_dict() for t in self.tasks],
        }


def calculate_pert(tasks_data: List[Dict[str, Any]]) -> PertResult:
    """Calculate bottom-up PERT three-point effort and confidence intervals.

    Args:
        tasks_data: List of dicts with keys 'task_id', 'name', 'category', 'optimistic', 'most_likely', 'pessimistic'.

    Returns:
        PertResult containing expected totals, combined SD, and confidence ranges.
    """
    if not tasks_data:
        return PertResult(
            total_tasks=0,
            total_expected=0.0,
            combined_variance=0.0,
            combined_sd=0.0,
            confidence_90_range=(0.0, 0.0),
            confidence_95_range=(0.0, 0.0),
            confidence_68_range=(0.0, 0.0),
            tasks=[],
            category_breakdown={},
        )

    tasks: List[PertTask] = []
    total_e = 0.0
    total_v = 0.0
    cat_effort: Dict[str, float] = {}

    for idx, t in enumerate(tasks_data, start=1):
        task_id = str(t.get("task_id", f"T-{idx:02d}"))
        name = str(t.get("name", f"Task {idx}"))
        cat = str(t.get("category", "Development"))
        o = float(t.get("optimistic", 10.0))
        m = float(t.get("most_likely", 15.0))
        p = float(t.get("pessimistic", 25.0))

        item = PertTask(
            task_id=task_id,
            name=name,
            category=cat,
            optimistic=o,
            most_likely=m,
            pessimistic=p,
        )
        item.compute()

        total_e += item.expected
        total_v += item.variance
        cat_effort[cat] = cat_effort.get(cat, 0.0) + item.expected
        tasks.append(item)

    combined_sd = math.sqrt(total_v)

    # Confidence ranges (Z-scores)
    # 90%: Z = 1.645
    range_90 = (max(0.0, total_e - (1.645 * combined_sd)), total_e + (1.645 * combined_sd))
    # 95%: Z = 1.960
    range_95 = (max(0.0, total_e - (1.960 * combined_sd)), total_e + (1.960 * combined_sd))
    # 68%: Z = 1.000
    range_68 = (max(0.0, total_e - (1.000 * combined_sd)), total_e + (1.000 * combined_sd))

    return PertResult(
        total_tasks=len(tasks),
        total_expected=total_e,
        combined_variance=total_v,
        combined_sd=combined_sd,
        confidence_90_range=range_90,
        confidence_95_range=range_95,
        confidence_68_range=range_68,
        tasks=tasks,
        category_breakdown=cat_effort,
    )
