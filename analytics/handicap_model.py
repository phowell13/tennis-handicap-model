# analytics/handicap_model.py
from dataclasses import dataclass

@dataclass
class MatchParams:
    best_of_sets: int = 3
    avg_games_per_set: float = 10.5  # typical WTA clay

def expected_games_diff(p1: dict, p2: dict, params: MatchParams):
    # p1 and p2 have "hold"
    hold1, hold2 = p1["hold"], p2["hold"]

    # probability player 1 wins a random game (serve/return mix)
    # assume 50% of games each on serve
    p1_on_serve = hold1
    p2_on_serve = 1 - hold2
    p1_game = 0.5 * p1_on_serve + 0.5 * p2_on_serve

    p2_game = 1 - p1_game

    sets = (params.best_of_sets + 1) / 2  # crude expected sets
    total_games = params.avg_games_per_set * sets

    g1 = total_games * p1_game
    g2 = total_games * p2_game
    return g1, g2

