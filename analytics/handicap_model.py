from dataclasses import dataclass
import math

@dataclass
class MatchParams:
    best_of_sets: int = 3
    avg_games_per_set: float = 10.5

def expected_games_diff(p1: dict, p2: dict, params: MatchParams):
    hold1, hold2 = p1["hold"], p2["hold"]

    p1_game = 0.5 * hold1 + 0.5 * (1 - hold2)
    p2_game = 1 - p1_game

    sets = (params.best_of_sets + 1) / 2
    total_games = params.avg_games_per_set * sets

    g1 = total_games * p1_game
    g2 = total_games * p2_game
    return g1, g2

def handicap_cover_prob(game_diff_mean: float, line: float, sd: float = 3.5) -> float:
    z = (line - game_diff_mean) / sd
    phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    return 1 - phi
