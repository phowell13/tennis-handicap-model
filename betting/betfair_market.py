from dataclasses import dataclass

@dataclass
class HandicapMarket:
    line: float
    price_a: float
    price_b: float

    @property
    def implied_prob_a(self):
        return 1.0 / self.price_a

    @property
    def implied_prob_b(self):
        return 1.0 / self.price_b

def edge(model_p: float, market_price: float) -> float:
    fair_price = 1.0 / model_p
    return (market_price / fair_price) - 1.0
