"""Value real operating cash flows plus a fixed nominal tax shield, keeping each at a consistent rate."""


def solve():
    nominal, inflation = 0.1235, 0.05
    real = (1 + nominal) / (1 + inflation) - 1
    operating = sum(100.0 / (1 + real) ** t for t in (1, 2, 3))
    shield = sum(30.0 / (1 + nominal) ** t for t in (1, 2, 3))
    return {"real_rate": real, "operating_pv": operating, "shield_pv": shield, "total_pv": operating + shield}
