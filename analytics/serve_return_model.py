import math

def hold_prob_from_points(p_srv: float) -> float:
    """
    Logistic mapping from service points won → hold%
    Calibrated for WTA.
    p_srv is a decimal (e.g. 0.62)
    """
    return 1 / (1 + math.exp(-12 * (p_srv - 0.61)))

def build_hold_return_profile(profile: dict) -> dict:
    p_srv = profile["srv_pts_won"]
    hold = hold_prob_from_points(p_srv)
    return { **profile, "hold": hold }

