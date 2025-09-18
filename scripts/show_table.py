# scripts/show_table.py
import sqlite3

SEASON = 2025
DB_PATH = "football.db"


def main():
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.execute(
            """
        WITH played AS (
          SELECT * FROM fixtures
          WHERE season=? AND status='played'
        ),
        home AS (
          SELECT th.id AS team_id, th.name,
                 1 AS pld,
                 CASE WHEN f.home_goals > f.away_goals THEN 1 ELSE 0 END AS w,
                 CASE WHEN f.home_goals = f.away_goals THEN 1 ELSE 0 END AS d,
                 CASE WHEN f.home_goals < f.away_goals THEN 1 ELSE 0 END AS l,
                 f.home_goals AS gf, f.away_goals AS ga,
                 CASE WHEN f.home_goals > f.away_goals THEN 3
                      WHEN f.home_goals = f.away_goals THEN 1 ELSE 0 END AS pts
          FROM played f
          JOIN teams th ON th.id=f.home_team_id
        ),
        away AS (
          SELECT ta.id AS team_id, ta.name,
                 1 AS pld,
                 CASE WHEN f.away_goals > f.home_goals THEN 1 ELSE 0 END AS w,
                 CASE WHEN f.away_goals = f.home_goals THEN 1 ELSE 0 END AS d,
                 CASE WHEN f.away_goals < f.home_goals THEN 1 ELSE 0 END AS l,
                 f.away_goals AS gf, f.home_goals AS ga,
                 CASE WHEN f.away_goals > f.home_goals THEN 3
                      WHEN f.away_goals = f.home_goals THEN 1 ELSE 0 END AS pts
          FROM played f
          JOIN teams ta ON ta.id=f.away_team_id
        ),
        allrows AS (
          SELECT * FROM home
          UNION ALL
          SELECT * FROM away
        )
        SELECT name,
               SUM(pld) AS Pld,
               SUM(w) AS W,
               SUM(d) AS D,
               SUM(l) AS L,
               SUM(gf) AS GF,
               SUM(ga) AS GA,
               SUM(gf) - SUM(ga) AS GD,
               SUM(pts) AS Pts
        FROM allrows
        GROUP BY team_id
        ORDER BY Pts DESC, GD DESC, GF DESC, name ASC;
        """,
            (SEASON,),
        )
        print("Team                     Pld  W  D  L  GF  GA  GD  Pts")
        print("-" * 62)
        for name, pld, w, d, l, gf, ga, gd, pts in cur.fetchall():
            print(
                f"{name:22} {pld:>3} {w:>2} {d:>2} {l:>2} "
                f"{gf:>3} {ga:>3} {gd:>3} {pts:>4}"
            )
    finally:
        con.close()


if __name__ == "__main__":
    main()
