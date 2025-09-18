# app/api.py
import sqlite3
from typing import Optional, List, Dict
from fastapi import FastAPI, Query

DB_PATH = "football.db"
app = FastAPI(title="FM Lite API")


def get_con() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con


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
