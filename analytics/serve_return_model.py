def hold_prob_from_points(p_srv: float) -> float:
    base_pts = 0.62
    base_hold = 0.75
    slope = 1.2
    delta = p_srv - base_pts
    hold = base_hold + slope * delta
    return max(0.40, min(0.95, hold))

def build_hold_return_profile(profile: dict) -> dict:
    p_srv = profile["srv_pts_won"]
    hold = hold_prob_from_points(p_srv)
    return {**profile, "hold": hold}
