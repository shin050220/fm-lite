# scripts/sim_round.py
import sys
import sqlite3
from app.db import (
    connect,
    apply_schema,
    ensure_fixture_goal_columns,
)  # ← ensure_schema ではなく apply_schema
from app.sim import TeamStrength, expected_goals, simulate_score

SEASON = 2025
ROUND = int(sys.argv[1]) if len(sys.argv) > 1 else 1  # ← ここを引数対応に
SEED_BASE = 12345
DB_PATH = "football.db"


def fetch_team_strengths(con: sqlite3.Connection) -> dict[int, TeamStrength]:
    rows = con.execute("SELECT id, rating_attack, rating_defense FROM teams").fetchall()
    return {
        tid: TeamStrength(attack=att or 0.0, defense=defn or 0.0)
        for (tid, att, defn) in rows
    }


def main():
    con = connect(DB_PATH)
    try:
        apply_schema(con)  # ← ここも ensure_schema ではなく apply_schema
        ensure_fixture_goal_columns(con)

        strengths = fetch_team_strengths(con)
        rows = con.execute(
            """
            SELECT id, home_team_id, away_team_id
            FROM fixtures
            WHERE season=? AND round_no=? AND status='scheduled'
            ORDER BY id
        """,
            (SEASON, ROUND),
        ).fetchall()

        if not rows:
            print(f"No scheduled fixtures for season={SEASON}, round={ROUND}.")
            return

        updates = []
        for i, (fix_id, home_id, away_id) in enumerate(rows, start=1):
            lam_h, lam_a = expected_goals(strengths[home_id], strengths[away_id])
            hg, ag = simulate_score(lam_h, lam_a, seed=SEED_BASE + i)
            print(
                f"[R{ROUND}] fixture#{fix_id} {home_id} vs {away_id} -> "
                f"{hg}-{ag} (λ={lam_h:.2f}/{lam_a:.2f})"
            )
            updates.append((hg, ag, "played", fix_id))

        with con:
            con.executemany(
                "UPDATE fixtures SET home_goals=?, away_goals=?, status=? WHERE id=?",
                updates,
            )
        print("Saved results.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
