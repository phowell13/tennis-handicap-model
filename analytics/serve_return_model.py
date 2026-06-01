# analytics/serve_return_model.py
def hold_prob_from_points(p_srv: float, p_ret: float) -> float:
    """
    Very rough mapping: higher p_srv → higher hold.
    You can later replace this with a proper game-level model.
    """
    # baseline around 0.62 → ~0.75 hold
    base_pts = 0.62
    base_hold = 0.75
    slope = 1.2  # tweakable

    delta = p_srv - base_pts
    hold = base_hold + slope * delta
    return max(0.40, min(0.95, hold))

def build_hold_return_profile(profile: dict) -> dict:
    p_srv = profile["srv_pts_won"]
    p_ret = profile["ret_pts_won"]
    hold = hold_prob_from_points(p_srv, p_ret)
    # approximate return games won as 1 - opponent hold later
    return {**profile, "hold": hold}

