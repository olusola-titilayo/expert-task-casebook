"""NPV of a level cash flow, with year-end and mid-year timing."""


def solve():
    rate, invest, flow, years = 0.10, 1000.0, 400.0, 4
    year_end = -invest + sum(flow / (1 + rate) ** t for t in range(1, years + 1))
    mid_year = -invest + sum(flow / (1 + rate) ** (t - 0.5) for t in range(1, years + 1))
    return {"year_end_npv": year_end, "mid_year_npv": mid_year, "understatement": mid_year - year_end}
