import math

def hold_prob_from_points(p_srv: float) -> float:
    """
    Logistic mapping from service points won → hold%
    Calibrated for WTA.
    """
    # logistic curve centered at 0.61 SPW
    return 1 / (1 + math.exp(-12 * (p_srv - 0.61)))

