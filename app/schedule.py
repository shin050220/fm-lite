from datetime import date, timedelta
from typing import List, Tuple, Optional
import random

Match = Tuple[str, str]
Round = List[Match]
Schedule = List[Round]

def generate_round_robin(
    teams: List[str],
    double_round: bool = True,
    shuffle_teams: bool = True,
    seed: Optional[int] = 42,
    bye_token: str = "BYE",
) -> Schedule:
    """サークル法で総当たり日程を生成。奇数チームはBYE追加。"""
    if seed is not None:
        random.seed(seed)
    teams = teams[:]
    if shuffle_teams:
        random.shuffle(teams)
    if len(teams) % 2 == 1:
        teams.append(bye_token)

    n = len(teams); half = n // 2
    fixed, rot = teams[0], teams[1:]

    rounds: Schedule = []
    for r in range(n - 1):
        left = [fixed] + rot[:half - 1]
        right = rot[half - 1:][::-1]
        swap = (r % 2 == 1)
        matches: Round = []
        for a, b in zip(left, right):
            if bye_token in (a, b):
                continue
            matches.append((b, a) if swap else (a, b))
        rounds.append(matches)
        rot = [rot[-1]] + rot[:-1]

    if double_round:
        rounds += [[(b, a) for (a, b) in rnd] for rnd in rounds]
    return rounds

def assign_dates(schedule: Schedule, start_on: date, interval_days: int = 7):
    out = []
    for rnd_no, rnd in enumerate(schedule, start=1):
        d = start_on + timedelta(days=(rnd_no - 1) * interval_days)
        for home, away in rnd:
            out.append((rnd_no, d, home, away))
    return out
