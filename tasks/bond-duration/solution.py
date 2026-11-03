"""Bond price sensitivity: duration estimate, convexity correction and exact repricing."""


def price(y, coupon=6.0, face=100.0, n=5):
    return sum(coupon / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n


def solve(y=0.05, shift=0.01, coupon=6.0, face=100.0, n=5):
    flows = [coupon] * (n - 1) + [coupon + face]
    p = price(y, coupon, face, n)
    macaulay = sum(t * f / (1 + y) ** t for t, f in enumerate(flows, 1)) / p
    modified = macaulay / (1 + y)
    convexity = sum(t * (t + 1) * f / (1 + y) ** (t + 2) for t, f in enumerate(flows, 1)) / p
    duration_only = -modified * shift
    with_convexity = duration_only + 0.5 * convexity * shift ** 2
    exact = price(y + shift, coupon, face, n) / p - 1
    return {"price": p, "macaulay": macaulay, "modified": modified, "convexity": convexity,
            "duration_only": duration_only, "with_convexity": with_convexity, "exact": exact}
