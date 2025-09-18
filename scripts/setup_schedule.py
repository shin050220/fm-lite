from datetime import date
import csv
from app.db import connect, apply_schema
from app.schedule import generate_round_robin, assign_dates

SEASON = 2025
START_ON = date(2025, 9, 20)
INTERVAL_DAYS = 7
DB_PATH = "football.db"


def load_teams_csv(path="data/teams.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return [row["name"] for row in csv.DictReader(f)]


def main():
    teams = load_teams_csv()

    con = connect(DB_PATH)
    try:
        apply_schema(con)
        with con:
            con.executemany(
                "INSERT OR IGNORE INTO teams(name) VALUES(?)", [(t,) for t in teams]
            )

        schedule = generate_round_robin(
            teams, double_round=True, shuffle_teams=True, seed=123
        )
        fixtures = assign_dates(
            schedule, start_on=START_ON, interval_days=INTERVAL_DAYS
        )

        # name→id
        cur = con.execute("SELECT id, name FROM teams")
        name_id = {n: i for i, n in cur.fetchall()}

        rows = [
            (SEASON, rnd, d.isoformat(), name_id[h], name_id[a])
            for rnd, d, h, a in fixtures
        ]

        sql = (
            "INSERT OR IGNORE INTO fixtures("
            "season, round_no, match_date, home_team_id, away_team_id"
            ") VALUES (?, ?, ?, ?, ?)"
        )
        with con:
            con.executemany(sql, rows)

        # 動作確認
        for row in con.execute(
            """
            SELECT round_no, match_date, th.name, ta.name
            FROM fixtures f
            JOIN teams th ON th.id=f.home_team_id
            JOIN teams ta ON ta.id=f.away_team_id
            WHERE season=? ORDER BY round_no, f.id LIMIT 10
            """,
            (SEASON,),
        ):
            print(row)
    finally:
        con.close()


if __name__ == "__main__":
    main()
