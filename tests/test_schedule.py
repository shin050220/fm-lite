from app.schedule import generate_round_robin

def test_round_count_even_teams():
    teams = [f"T{i}" for i in range(6)]
    sched = generate_round_robin(teams, double_round=True, shuffle_teams=False, seed=None)
    # 6チーム → 1回戦で5節、2回戦で10節
    assert len(sched) == 10
    # 各節、3試合（重複なし）
    for rnd in sched:
        assert len(rnd) == 3
        assert len(set(rnd)) == len(rnd)
