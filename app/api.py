# app/api.py
from fastapi.staticfiles import StaticFiles
import sqlite3
from typing import Optional, List, Dict
from fastapi import FastAPI, Query
from app.db import connect
from fastapi import HTTPException
from app.db import ensure_event_schema

DB_PATH = "football.db"
app = FastAPI(title="FM Lite API")


def get_con() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

@app.on_event("startup")
def _startup() -> None:
    con = get_con()
    try:
        ensure_event_schema(con)
    finally:
        con.close()

@app.get("/health")
def health() -> Dict[str, bool]:
    return {"ok": True}


@app.get("/fixtures")
def fixtures(
    season: int = Query(2025, ge=1900, le=3000),
    round: Optional[int] = Query(None, ge=1),
    status: Optional[str] = Query(None),
) -> List[Dict]:
    con = get_con()
    try:
        sql = (
            "SELECT f.id, f.season, f.round_no, f.match_date, "
            "th.name AS home, ta.name AS away, "
            "f.home_goals, f.away_goals, f.status "
            "FROM fixtures f "
            "JOIN teams th ON th.id=f.home_team_id "
            "JOIN teams ta ON ta.id=f.away_team_id "
            "WHERE f.season=?"
        )
        params = [season]
        if round is not None:
            sql += " AND f.round_no=?"
            params.append(round)
        if status is not None:
            sql += " AND f.status=?"
            params.append(status)
        sql += " ORDER BY f.round_no, f.id"
        rows = [dict(r) for r in con.execute(sql, params)]
        return rows
    finally:
        con.close()


@app.get("/table")
def table(season: int = Query(2025, ge=1900, le=3000)) -> List[Dict]:
    con = get_con()
    try:
        cur = con.execute(
            """
            WITH played AS (
              SELECT * FROM fixtures
              WHERE season=? AND status='played'
            ),
            home AS (
              SELECT th.id AS team_id, th.name, 1 AS pld,
                     CASE WHEN f.home_goals > f.away_goals THEN 1 ELSE 0 END AS w,
                     CASE WHEN f.home_goals = f.away_goals THEN 1 ELSE 0 END AS d,
                     CASE WHEN f.home_goals < f.away_goals THEN 1 ELSE 0 END AS l,
                     f.home_goals AS gf, f.away_goals AS ga,
                     CASE WHEN f.home_goals > f.away_goals THEN 3
                          WHEN f.home_goals = f.away_goals THEN 1 ELSE 0 END AS pts
              FROM played f JOIN teams th ON th.id=f.home_team_id
            ),
            away AS (
              SELECT ta.id AS team_id, ta.name, 1 AS pld,
                     CASE WHEN f.away_goals > f.home_goals THEN 1 ELSE 0 END AS w,
                     CASE WHEN f.away_goals = f.home_goals THEN 1 ELSE 0 END AS d,
                     CASE WHEN f.away_goals < f.home_goals THEN 1 ELSE 0 END AS l,
                     f.away_goals AS gf, f.home_goals AS ga,
                     CASE WHEN f.away_goals > f.home_goals THEN 3
                          WHEN f.away_goals = f.home_goals THEN 1 ELSE 0 END AS pts
              FROM played f JOIN teams ta ON ta.id=f.away_team_id
            ),
            allrows AS (
              SELECT * FROM home
              UNION ALL
              SELECT * FROM away
            )
            SELECT name AS team, SUM(pld) AS Pld, SUM(w) AS W, SUM(d) AS D,
                   SUM(l) AS L, SUM(gf) AS GF, SUM(ga) AS GA,
                   SUM(gf) - SUM(ga) AS GD, SUM(pts) AS Pts
            FROM allrows
            GROUP BY team_id
            ORDER BY Pts DESC, GD DESC, GF DESC, team ASC;
            """,
            (season,),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        con.close()

@app.get("/match/{fixture_id}")
def match_detail(fixture_id: int):
    con = get_con()
    try:
        fx = con.execute(
            """
            SELECT f.id, f.season, f.round_no, f.match_date,
                   th.name AS home, ta.name AS away,
                   f.home_goals, f.away_goals, f.status
            FROM fixtures f
            JOIN teams th ON th.id=f.home_team_id
            JOIN teams ta ON ta.id=f.away_team_id
            WHERE f.id=?
            """,
            (fixture_id,),
        ).fetchone()
        if fx is None:
            raise HTTPException(status_code=404, detail="Fixture not found")

        events = [
            dict(r)
            for r in con.execute(
                """
                SELECT minute, team_side, type, player, assist, description
                FROM match_events
                WHERE fixture_id=?
                ORDER BY minute, id
                """,
                (fixture_id,),
            ).fetchall()
        ]
        return {"fixture": dict(fx), "events": events}
    finally:
        con.close()

app.mount("/app", StaticFiles(directory="static", html=True), name="app")