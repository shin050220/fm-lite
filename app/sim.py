from dataclasses import dataclass
import math
import random
from typing import Tuple


@dataclass
class TeamStrength:
    attack: float  # 攻撃強度（平均0を想定）
    defense: float  # 守備強度（平均0を想定・値が高いほど強い）


def expected_goals(
    home: TeamStrength, away: TeamStrength, base: float = 1.25, home_adv: float = 0.12
) -> Tuple[float, float]:
    """
    期待得点λの設計：
    λ_home = base * exp( (A_home - D_away) + home_adv )
    λ_away = base * exp( (A_away - D_home) )
    """
    lam_h = base * math.exp((home.attack - away.defense) + home_adv)
    lam_a = base * math.exp((away.attack - home.defense))
    return lam_h, lam_a


def poisson_sample(lam: float, rng: random.Random) -> int:
    """
    追加依存を増やさず Knuth法でPoisson乱数を生成
    """
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def simulate_score(
    lam_h: float, lam_a: float, seed: int | None = None
) -> Tuple[int, int]:
    rng = random.Random(seed)
    return poisson_sample(lam_h, rng), poisson_sample(lam_a, rng)
