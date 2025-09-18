PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL UNIQUE,
  short_name    TEXT,
  rating_attack REAL DEFAULT 0.0,
  rating_defense REAL DEFAULT 0.0,
  budget        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fixtures (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  season        INTEGER NOT NULL,
  round_no      INTEGER NOT NULL,
  match_date    TEXT NOT NULL,      -- ISO 'YYYY-MM-DD'
  home_team_id  INTEGER NOT NULL,
  away_team_id  INTEGER NOT NULL,
  status        TEXT NOT NULL DEFAULT 'scheduled',  -- scheduled / played / postponed
  UNIQUE(season, round_no, home_team_id, away_team_id),
  FOREIGN KEY(home_team_id) REFERENCES teams(id) ON DELETE CASCADE,
  FOREIGN KEY(away_team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fixtures_date ON fixtures(match_date);
CREATE INDEX IF NOT EXISTS idx_fixtures_round ON fixtures(season, round_no);
