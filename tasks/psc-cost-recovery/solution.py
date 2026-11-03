"""Production sharing contract: royalty, capped cost recovery with carry-forward, profit split."""


def solve():
    revenue = [100.0, 150.0, 120.0]
    capex = [180.0, 0.0, 0.0]
    opex = [20.0, 20.0, 20.0]
    royalty_rate, cost_cap, contractor_share = 0.10, 0.50, 0.40

    pool = 0.0
    years = []
    for gross, cap_cost, op_cost in zip(revenue, capex, opex):
        royalty = gross * royalty_rate
        net = gross - royalty
        pool += cap_cost + op_cost
        cost_oil = min(pool, net * cost_cap)
        pool -= cost_oil
        profit = net - cost_oil
        contractor = cost_oil + profit * contractor_share
        years.append({
            "royalty": royalty, "cost_oil": cost_oil, "profit_oil": profit, "unrecovered": pool,
            "contractor_cash": contractor - cap_cost - op_cost,
        })
    spent = sum(capex) + sum(opex)
    contractor_total = sum(y["contractor_cash"] for y in years)
    return {
        "years": years,
        "contractor_net": contractor_total,
        "government_take": sum(revenue) - spent - contractor_total,
        "unrecovered_end": pool,
    }
