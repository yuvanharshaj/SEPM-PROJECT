"""SQLite Database Management Layer for ProcessCompass.

Provides persistence for Projects, Process Evaluations, Effort Estimates,
Risk Registers, Business Cases, and McCall Quality Scorecards.
Preloads benchmark sample projects on initial run.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


DEFAULT_DB_PATH = "process_compass.db"


class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Create database tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Projects Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                team_size INTEGER DEFAULT 5,
                duration INTEGER DEFAULT 6,
                budget REAL DEFAULT 50000.0,
                req_stability TEXT DEFAULT 'Medium',
                customer_involvement TEXT DEFAULT 'Medium',
                risk_level TEXT DEFAULT 'Medium',
                early_delivery TEXT DEFAULT 'Medium',
                team_experience TEXT DEFAULT 'Medium',
                cocomo_mode TEXT DEFAULT 'organic',
                kloc REAL DEFAULT 20.0,
                created_at TEXT,
                updated_at TEXT
            );
            """)

            # 2. Function Points Configurations Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fp_configs (
                project_id INTEGER PRIMARY KEY,
                components_json TEXT,
                gsc_ratings_json TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """)

            # 3. Risks Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                risk_code TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                probability REAL NOT NULL,
                impact_cost REAL NOT NULL,
                mitigation TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """)

            # 4. Business Cases Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_cases (
                project_id INTEGER PRIMARY KEY,
                initial_investment REAL NOT NULL,
                annual_benefits_json TEXT NOT NULL,
                annual_costs_json TEXT NOT NULL,
                discount_rate_pct REAL NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """)

            # 5. Quality Scorecard Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_scores (
                project_id INTEGER PRIMARY KEY,
                scores_json TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """)

            conn.commit()

        # Seed sample data if table is currently empty
        self.preload_samples_if_empty()

    def preload_samples_if_empty(self) -> None:
        """Seed benchmark projects from sample_data/samples.py if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cnt FROM projects;")
            count = cursor.fetchone()["cnt"]

            if count == 0:
                from sample_data.samples import SAMPLE_PROJECTS
                for sample in SAMPLE_PROJECTS:
                    self.save_complete_project(sample)

    def list_projects(self) -> List[Dict[str, Any]]:
        """Return list of basic project summaries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, team_size, duration, budget, updated_at FROM projects ORDER BY id ASC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Fetch full project details including risks, FP, business case, and quality scores."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?;", (project_id,))
            proj_row = cursor.fetchone()
            if not proj_row:
                return None

            proj = dict(proj_row)

            # FP config
            cursor.execute("SELECT components_json, gsc_ratings_json FROM fp_configs WHERE project_id = ?;", (project_id,))
            fp_row = cursor.fetchone()
            if fp_row:
                proj["fp_components"] = json.loads(fp_row["components_json"])
                proj["gsc_ratings"] = json.loads(fp_row["gsc_ratings_json"])
            else:
                proj["fp_components"] = None
                proj["gsc_ratings"] = None

            # Risks
            cursor.execute("SELECT risk_code AS id, category, description, probability, impact_cost, mitigation FROM risks WHERE project_id = ? ORDER BY id ASC;", (project_id,))
            proj["risks"] = [dict(r) for r in cursor.fetchall()]

            # Business Case
            cursor.execute("SELECT initial_investment, annual_benefits_json, annual_costs_json, discount_rate_pct FROM business_cases WHERE project_id = ?;", (project_id,))
            biz_row = cursor.fetchone()
            if biz_row:
                proj["business_case"] = {
                    "initial_investment": biz_row["initial_investment"],
                    "annual_benefits": json.loads(biz_row["annual_benefits_json"]),
                    "annual_costs": json.loads(biz_row["annual_costs_json"]),
                    "discount_rate_pct": biz_row["discount_rate_pct"],
                }
            else:
                proj["business_case"] = None

            # Quality Scores
            cursor.execute("SELECT scores_json FROM quality_scores WHERE project_id = ?;", (project_id,))
            q_row = cursor.fetchone()
            if q_row:
                proj["quality_scores"] = json.loads(q_row["scores_json"])
            else:
                proj["quality_scores"] = None

            return proj

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM projects WHERE name = ?;", (name,))
            row = cursor.fetchone()
            if row:
                return self.get_project_by_id(row["id"])
            return None

    def save_complete_project(self, data: Dict[str, Any]) -> int:
        """Insert or update a comprehensive project bundle."""
        now_str = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()

            name = data["name"].strip()
            # Check if project exists by name or id
            p_id = data.get("id")
            if not p_id:
                cursor.execute("SELECT id FROM projects WHERE name = ?;", (name,))
                existing = cursor.fetchone()
                if existing:
                    p_id = existing["id"]

            if p_id:
                cursor.execute("""
                UPDATE projects SET
                    name = ?, description = ?, team_size = ?, duration = ?, budget = ?,
                    req_stability = ?, customer_involvement = ?, risk_level = ?,
                    early_delivery = ?, team_experience = ?, cocomo_mode = ?, kloc = ?,
                    updated_at = ?
                WHERE id = ?;
                """, (
                    name,
                    data.get("description", ""),
                    int(data.get("team_size", 5)),
                    int(data.get("duration", 6)),
                    float(data.get("budget", 50000.0)),
                    data.get("req_stability", "Medium"),
                    data.get("customer_involvement", "Medium"),
                    data.get("risk_level", "Medium"),
                    data.get("early_delivery", "Medium"),
                    data.get("team_experience", "Medium"),
                    data.get("cocomo_mode", "organic"),
                    float(data.get("kloc", 20.0)),
                    now_str,
                    p_id,
                ))
            else:
                cursor.execute("""
                INSERT INTO projects (
                    name, description, team_size, duration, budget,
                    req_stability, customer_involvement, risk_level,
                    early_delivery, team_experience, cocomo_mode, kloc,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    name,
                    data.get("description", ""),
                    int(data.get("team_size", 5)),
                    int(data.get("duration", 6)),
                    float(data.get("budget", 50000.0)),
                    data.get("req_stability", "Medium"),
                    data.get("customer_involvement", "Medium"),
                    data.get("risk_level", "Medium"),
                    data.get("early_delivery", "Medium"),
                    data.get("team_experience", "Medium"),
                    data.get("cocomo_mode", "organic"),
                    float(data.get("kloc", 20.0)),
                    now_str,
                    now_str,
                ))
                p_id = cursor.lastrowid

            # Save FP configs if present
            if "fp_components" in data and data["fp_components"]:
                cursor.execute("""
                INSERT INTO fp_configs (project_id, components_json, gsc_ratings_json)
                VALUES (?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    components_json = excluded.components_json,
                    gsc_ratings_json = excluded.gsc_ratings_json;
                """, (
                    p_id,
                    json.dumps(data["fp_components"]),
                    json.dumps(data.get("gsc_ratings", [3] * 14)),
                ))

            # Save Risks
            if "risks" in data and isinstance(data["risks"], list):
                cursor.execute("DELETE FROM risks WHERE project_id = ?;", (p_id,))
                for idx, r in enumerate(data["risks"], start=1):
                    rcode = r.get("id") or f"R-{idx:02d}"
                    cursor.execute("""
                    INSERT INTO risks (project_id, risk_code, category, description, probability, impact_cost, mitigation)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    """, (
                        p_id,
                        rcode,
                        r.get("category", "Technical"),
                        r.get("description", f"Risk {idx}"),
                        float(r.get("probability", 0.3)),
                        float(r.get("impact_cost", 10000.0)),
                        r.get("mitigation", "Monitor"),
                    ))

            # Save Business Case
            if "business_case" in data and data["business_case"]:
                bc = data["business_case"]
                cursor.execute("""
                INSERT INTO business_cases (project_id, initial_investment, annual_benefits_json, annual_costs_json, discount_rate_pct)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    initial_investment = excluded.initial_investment,
                    annual_benefits_json = excluded.annual_benefits_json,
                    annual_costs_json = excluded.annual_costs_json,
                    discount_rate_pct = excluded.discount_rate_pct;
                """, (
                    p_id,
                    float(bc.get("initial_investment", data.get("budget", 50000.0))),
                    json.dumps(bc.get("annual_benefits", [20000.0, 30000.0, 40000.0])),
                    json.dumps(bc.get("annual_costs", [5000.0, 5000.0, 5000.0])),
                    float(bc.get("discount_rate_pct", 10.0)),
                ))

            # Save Quality Scores
            if "quality_scores" in data and data["quality_scores"]:
                cursor.execute("""
                INSERT INTO quality_scores (project_id, scores_json)
                VALUES (?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    scores_json = excluded.scores_json;
                """, (
                    p_id,
                    json.dumps(data["quality_scores"]),
                ))

            conn.commit()
            return p_id

    def delete_project(self, project_id: int) -> bool:
        """Delete project and associated cascade tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?;", (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    def reset_to_defaults(self) -> None:
        """Clear database and reload the 3 reference sample projects."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects;")
            conn.commit()
        from sample_data.samples import SAMPLE_PROJECTS
        for sample in SAMPLE_PROJECTS:
            self.save_complete_project(sample)

