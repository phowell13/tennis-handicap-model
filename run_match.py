from analytics.player_stats import load_raw, build_player_surface_stats, get_player_profile
from analytics.serve_return_model import build_hold_return_profile
from analytics.handicap_model import MatchParams, expected_games_diff, handicap_cover_prob
from betting.betfair_market import HandicapMarket, edge

def main():
    df = load_raw()
    agg = build_player_surface_stats(df)

    sab = build_hold_return_profile(get_player_profile(agg, "Sabalenka A.", "clay"))
    osa = build_hold_return_profile(get_player_profile(agg, "Osaka N.", "clay"))

    params = MatchParams()
    g1, g2 = expected_games_diff(sab, osa, params)
    diff = g1 - g2
    print(f"Expected games: Sabalenka {g1:.2f} – Osaka {g2:.2f} (diff {diff:.2f})")

    markets = [
        HandicapMarket(line=-6.5, price_a=5.0,  price_b=1.25),
        HandicapMarket(line=-5.5, price_a=2.70, price_b=1.60),
        HandicapMarket(line=-4.5, price_a=1.97, price_b=2.02),
        HandicapMarket(line=-3.5, price_a=1.58, price_b=3.05),
        HandicapMarket(line=-2.5, price_a=1.46, price_b=4.40),
        HandicapMarket(line=-1.5, price_a=1.38, price_b=5.40),
    ]

    for m in markets:
        p_cover = handicap_cover_prob(diff, m.line)
        e = edge(p_cover, m.price_a)
        print(
            f"Sabalenka {m.line:+.1f}: model p={p_cover:.3f}, "
            f"fair={1/p_cover:.2f}, market={m.price_a:.2f}, edge={e*100:.1f}%"
        )

if __name__ == "__main__":
    main()
