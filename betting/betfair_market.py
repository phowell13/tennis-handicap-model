# betting/betfair_market.py
from dataclasses import dataclass

@dataclass
class HandicapMarket:
    line: float   # Sabalenka -X.5
    price_a: float  # Sabalenka -X.5
    price_b: float  # Osaka +X.5

    @property
    def implied_prob_a(self):
        return 1.0 / self.price_a

    @property
    def implied_prob_b(self):
        return 1.0 / self.price_b

def edge(model_p: float, market_price: float) -> float:
    fair_price = 1.0 / model_p
    return (market_price / fair_price) - 1.0

