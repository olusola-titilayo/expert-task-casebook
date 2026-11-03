"""Non-conventional cash flow with two IRRs, decided by NPV and MIRR at the hurdle rate."""

FLOWS = [-100.0, 230.0, -132.0]


def npv(rate, flows=FLOWS):
    return sum(flow / (1 + rate) ** t for t, flow in enumerate(flows))


def solve():
    # Multiply NPV by (1+r)^2 to get a quadratic in x = 1+r: -100x^2 + 230x - 132 = 0.
    a, b, c = FLOWS
    root = (b * b - 4 * a * c) ** 0.5
    irrs = sorted(((-b + sign * root) / (2 * a)) - 1 for sign in (1, -1))
    hurdle = 0.12
    pv_out = sum(-f / (1 + hurdle) ** t for t, f in enumerate(FLOWS) if f < 0)
    fv_in = sum(f * (1 + hurdle) ** (len(FLOWS) - 1 - t) for t, f in enumerate(FLOWS) if f > 0)
    mirr = (fv_in / pv_out) ** (1 / (len(FLOWS) - 1)) - 1
    return {"irr_low": irrs[0], "irr_high": irrs[1], "npv_at_hurdle": npv(hurdle), "mirr": mirr}
