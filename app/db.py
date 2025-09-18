import sqlite3
from pathlib import Path


def connect(db_path: str = "football.db") -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def apply_schema(con: sqlite3.Connection, schema_path: str = "sql/schema.sql") -> None:
    sql = Path(schema_path).read_text(encoding="utf-8")
    con.executescript(sql)


def ensure_fixture_goal_columns(con: sqlite3.Connection) -> None:
    # 既存カラムを確認
    cols = {row[1] for row in con.execute("PRAGMA table_info(fixtures)")}
    to_add = []
    if "home_goals" not in cols:
        to_add.append(("home_goals", "INTEGER"))
    if "away_goals" not in cols:
        to_add.append(("away_goals", "INTEGER"))
    if to_add:
        for name, typ in to_add:
            con.execute(f"ALTER TABLE fixtures ADD COLUMN {name} {typ}")
    con.commit()
