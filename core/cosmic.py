"""COSMIC Full Function Points (FFP) Estimation Engine.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 4:
    Software Sizing & Functional Metrics, COSMIC Full Function Points (ISO/IEC 19761).

Core Concepts:
    A software system comprises functional processes. Each process moves data across
    the boundary or interfaces with persistent storage through 4 Data Movement types:
    - Entry (E)  : Moves data from a functional user across boundary into process.
    - Exit (X)   : Moves data from inside the process across boundary to functional user.
    - Read (R)   : Moves data from persistent storage into the functional process.
    - Write (W)  : Moves data from functional process into persistent storage.

Formulas:
    Process Size (CFP) = E + X + R + W
    Total Project Size (CFP) = sum(Process Size_i)
    Effort (Person-Hours) = Total CFP * Productivity (Hours/CFP)
    Effort (Person-Months) = Effort (Person-Hours) / 160
    Nominal Duration (Months) = Effort (Person-Months) / Team Size
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class FunctionalProcess:
    process_id: str
    name: str
    entries: int
    exits: int
    reads: int
    writes: int
    cfp: int = 0

    def calculate_cfp(self) -> int:
        self.cfp = int(self.entries + self.exits + self.reads + self.writes)
        return self.cfp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_id": self.process_id,
            "name": self.name,
            "entries": self.entries,
            "exits": self.exits,
            "reads": self.reads,
            "writes": self.writes,
            "cfp": self.cfp or self.calculate_cfp(),
        }


@dataclass
class CosmicResult:
    total_cfp: int
    total_entries: int
    total_exits: int
    total_reads: int
    total_writes: int
    productivity_hours_per_cfp: float
    total_effort_hours: float
    total_effort_pm: float
    estimated_duration_months: float
    processes: List[FunctionalProcess]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cfp": self.total_cfp,
            "total_entries": self.total_entries,
            "total_exits": self.total_exits,
            "total_reads": self.total_reads,
            "total_writes": self.total_writes,
            "productivity_hours_per_cfp": self.productivity_hours_per_cfp,
            "total_effort_hours": round(self.total_effort_hours, 1),
            "total_effort_pm": round(self.total_effort_pm, 2),
            "estimated_duration_months": round(self.estimated_duration_months, 2),
            "processes": [p.to_dict() for p in self.processes],
        }


def calculate_cosmic_ffp(
    processes_data: List[Dict[str, Any]],
    productivity_hours_per_cfp: float = 12.0,
    team_size: int = 5,
) -> CosmicResult:
    """Calculate COSMIC Full Function Points and project effort.

    Args:
        processes_data: List of dicts with keys: 'process_id', 'name', 'entries', 'exits', 'reads', 'writes'.
        productivity_hours_per_cfp: Productivity delivery rate in hours per CFP (> 0). Default 12.0.
        team_size: Number of concurrent developers (> 0). Default 5.

    Returns:
        CosmicResult with total CFP and labor forecasts.
    """
    if productivity_hours_per_cfp <= 0:
        raise ValueError(f"Productivity hours per CFP must be positive, got {productivity_hours_per_cfp}")
    if team_size <= 0:
        raise ValueError(f"Team size must be at least 1, got {team_size}")

    processes: List[FunctionalProcess] = []
    tot_e = 0
    tot_x = 0
    tot_r = 0
    tot_w = 0
    tot_cfp = 0

    for idx, p in enumerate(processes_data, start=1):
        pid = str(p.get("process_id", f"FP-{idx:02d}"))
        pname = str(p.get("name", f"Functional Process {idx}"))
        e = max(0, int(p.get("entries", 0)))
        x = max(0, int(p.get("exits", 0)))
        r = max(0, int(p.get("reads", 0)))
        w = max(0, int(p.get("writes", 0)))

        fp = FunctionalProcess(
            process_id=pid,
            name=pname,
            entries=e,
            exits=x,
            reads=r,
            writes=w,
        )
        fp_cfp = fp.calculate_cfp()

        tot_e += e
        tot_x += x
        tot_r += r
        tot_w += w
        tot_cfp += fp_cfp
        processes.append(fp)

    total_effort_hours = tot_cfp * productivity_hours_per_cfp
    total_effort_pm = total_effort_hours / 160.0  # Standard 160 working hours per person-month
    duration_months = total_effort_pm / team_size if team_size > 0 else 0.0

    return CosmicResult(
        total_cfp=tot_cfp,
        total_entries=tot_e,
        total_exits=tot_x,
        total_reads=tot_r,
        total_writes=tot_w,
        productivity_hours_per_cfp=productivity_hours_per_cfp,
        total_effort_hours=total_effort_hours,
        total_effort_pm=total_effort_pm,
        estimated_duration_months=duration_months,
        processes=processes,
    )
