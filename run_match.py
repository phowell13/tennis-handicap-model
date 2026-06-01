from analytics.player_stats import load_raw, build_player_surface_stats, get_player_profile
from analytics.serve_return_model import build_hold_return_profile
from analytics.simulator import MatchConfig, handicap_cover_prob_mc
from betting.betfair_market import HandicapMarket, edge

def main():
    df = load_raw()
    agg = build_player_surface_stats(df)

    # Use actual names from your dataset and surface you want
    sab = build_hold_return_profile(get_player_profile(agg, "Naef C.", "clay"))
    osa = build_hold_return_profile(get_player_profile(agg, "Inglis M.", "clay"))

    cfg = MatchConfig()

    print(f"Sabalenka hold={sab['hold']:.3f}, Osaka hold={osa['hold']:.3f}")

    markets = [
        HandicapMarket(line=-6.5, price_a=5.0,  price_b=1.25),
        HandicapMarket(line=-5.5, price_a=2.70, price_b=1.60),
        HandicapMarket(line=-4.5, price_a=1.97, price_b=2.02),
        HandicapMarket(line=-3.5, price_a=1.58, price_b=3.05),
        HandicapMarket(line=-2.5, price_a=1.46, price_b=4.40),
        HandicapMarket(line=-1.5, price_a=1.38, price_b=5.40),
    ]

    for m in markets:
        print("DEBUG line =", m.line)
        p_cover = handicap_cover_prob_mc(sab["hold"], osa["hold"], m.line, cfg, n_sims=50000)
        e = edge(p_cover, m.price_a)
        print(
            f"Sabalenka {m.line:+.1f}: model p={p_cover:.3f}, "
            f"fair={1/p_cover:.2f}, market={m.price_a:.2f}, edge={e*100:.1f}%"
        )

if __name__ == "__main__":
    main()
