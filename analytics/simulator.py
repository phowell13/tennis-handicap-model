import random
from dataclasses import dataclass

@dataclass
class MatchConfig:
    best_of_sets: int = 3  # WTA
    tiebreak_at: int = 6   # standard 6-6 tiebreak

def simulate_set(p1_hold: float, p2_hold: float, cfg: MatchConfig) -> tuple[int, int]:
    g1 = g2 = 0
    server = 1  # 1 = player1 serves first in set

    while True:
        if server == 1:
            # player 1 serving
            if random.random() < p1_hold:
                g1 += 1
            else:
                g2 += 1
            server = 2
        else:
            # player 2 serving
            # player 1 wins return game with prob (1 - p2_hold)
            if random.random() < (1 - p2_hold):
                g1 += 1
            else:
                g2 += 1
            server = 1

        # normal set end
        if (g1 >= 6 or g2 >= 6) and abs(g1 - g2) >= 2 and (g1 >= cfg.tiebreak_at or g2 >= cfg.tiebreak_at):
            return g1, g2

        # tiebreak at 6-6
        if g1 == cfg.tiebreak_at and g2 == cfg.tiebreak_at:
            # approximate tiebreak: player 1 wins with probability equal to game share
            # game share ~ average of serve/return game win probs
            p1_game = 0.5 * p1_hold + 0.5 * (1 - p2_hold)
            if random.random() < p1_game:
                return g1 + 1, g2
            else:
                return g1, g2 + 1

def simulate_match(p1_hold: float, p2_hold: float, cfg: MatchConfig) -> tuple[int, int]:
    sets_to_win = cfg.best_of_sets // 2 + 1
    s1 = s2 = 0
    total_g1 = total_g2 = 0

    while s1 < sets_to_win and s2 < sets_to_win:
        g1, g2 = simulate_set(p1_hold, p2_hold, cfg)
        total_g1 += g1
        total_g2 += g2
        if g1 > g2:
            s1 += 1
        else:
            s2 += 1

    return total_g1, total_g2

def handicap_cover_prob_mc(p1_hold: float, p2_hold: float, line: float,
                           cfg: MatchConfig, n_sims: int = 50000) -> float:
    """
    line: handicap for player 1 (e.g. -6.5 means player 1 must win by > 6.5 games)
    Returns P(player 1 covers the handicap).
    """
    required_margin = -line  # convert -6.5 → +6.5

    wins = 0
    for _ in range(n_sims):
        g1, g2 = simulate_match(p1_hold, p2_hold, cfg)
        if (g1 - g2) > required_margin:
            wins += 1
    return wins / n_sims
