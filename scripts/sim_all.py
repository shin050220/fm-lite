# scripts/sim_all.py
import sqlite3
from app.db import connect, apply_schema, ensure_fixture_goal_columns
from app.sim import TeamStrength, expected_goals, simulate_score

SEASON = 2025
DB_PATH = "football.db"
SEED_BASE = 54321


def fetch_team_strengths(con: sqlite3.Connection) -> dict[int, TeamStrength]:
    rows = con.execute("SELECT id, rating_attack, rating_defense FROM teams").fetchall()
    return {
        tid: TeamStrength(attack=att or 0.0, defense=defn or 0.0)
        for (tid, att, defn) in rows
    }


def main():
    con = connect(DB_PATH)
    try:
        apply_schema(con)
        ensure_fixture_goal_columns(con)
        strengths = fetch_team_strengths(con)

        rows = con.execute(
            """
            SELECT id, round_no, home_team_id, away_team_id
            FROM fixtures
            WHERE season=? AND status='scheduled'
            ORDER BY round_no, id
        """,
            (SEASON,),
        ).fetchall()

        if not rows:
            print("No scheduled fixtures. Nothing to simulate.")
            return

        updates = []
        for i, (fix_id, rnd, home_id, away_id) in enumerate(rows, start=1):
            lam_h, lam_a = expected_goals(strengths[home_id], strengths[away_id])
            hg, ag = simulate_score(lam_h, lam_a, seed=SEED_BASE + i)
            print(f"[R{rnd}] fixture#{fix_id} {home_id} vs {away_id} -> {hg}-{ag}")
            updates.append((hg, ag, "played", fix_id))

        with con:
            con.executemany(
                "UPDATE fixtures SET home_goals=?, away_goals=?, status=? WHERE id=?",
                updates,
            )
        print(f"Saved {len(updates)} results.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
