import sqlite3
from pathlib import Path

def connect(db_path: str = "football.db") -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def apply_schema(con: sqlite3.Connection, schema_path: str = "sql/schema.sql") -> None:
    sql = Path(schema_path).read_text(encoding="utf-8")
    con.executescript(sql)
