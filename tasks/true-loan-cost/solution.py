"""True cost of a loan with an upfront fee: solve for the rate that equates cash received and repaid."""


def payment(principal, monthly_rate, months):
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def present_value(pay, monthly_rate, months):
    return sum(pay / (1 + monthly_rate) ** t for t in range(1, months + 1))


def solve():
    principal, nominal, fee, months = 10000.0, 0.12, 0.02, 12
    pay = payment(principal, nominal / 12, months)
    received = principal * (1 - fee)
    low, high = 0.0, 1.0
    for _ in range(200):
        mid = (low + high) / 2
        low, high = (mid, high) if present_value(pay, mid, months) > received else (low, mid)
    monthly = (low + high) / 2
    return {"payment": pay, "received": received, "monthly_rate": monthly,
            "apr": monthly * 12, "effective_annual": (1 + monthly) ** 12 - 1}
