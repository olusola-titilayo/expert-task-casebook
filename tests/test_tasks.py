"""Checks each rubric against its answers, and each answer key against an independent calculation."""
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent / "tasks"
TASKS = sorted(p.name for p in ROOT.iterdir() if p.is_dir())


def load(task):
    spec = importlib.util.spec_from_file_location(f"solution_{task.replace('-', '_')}", ROOT / task / "solution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rubric(task):
    return json.loads((ROOT / task / "rubric.json").read_text())


def met(check, text):
    if check["kind"] == "includes":
        return check["text"].lower() in text.lower()
    if check["kind"] == "regex":
        return re.search(check["pattern"], text, re.I if "i" in check.get("flags", "") else 0) is not None
    if check["kind"] == "allOf":
        return all(met(c, text) for c in check["checks"])
    raise AssertionError(f"unsupported check {check['kind']}")


def score(task, answer):
    """Same rules as llm-rubric-scorer: penalties subtract, required criteria must be met."""
    r = rubric(task)
    text = (ROOT / task / answer).read_text()
    total = maximum = 0
    required_ok = True
    for c in r["criteria"]:
        hit = met(c["check"], text)
        if c["weight"] > 0:
            maximum += c["weight"]
            total += c["weight"] if hit else 0
        elif hit:
            total += c["weight"]
        if c.get("required") and not hit:
            required_ok = False
    normalized = max(0, total) / maximum
    return required_ok and normalized >= r["passThreshold"], normalized


def test_six_tasks():
    assert len(TASKS) == 6


@pytest.mark.parametrize("task", TASKS)
def test_reference_answer_earns_full_marks(task):
    passed, normalized = score(task, "reference_answer.md")
    assert passed
    assert normalized == pytest.approx(1.0), "the reference should meet every positive criterion and no penalty"


@pytest.mark.parametrize("task", TASKS)
def test_trap_answer_fails_clearly(task):
    passed, normalized = score(task, "trap_answer.md")
    assert not passed
    assert normalized < 0.3, "a wrong answer shouldn't earn most of the marks"


@pytest.mark.parametrize("task", TASKS)
def test_trap_answer_triggers_a_penalty(task):
    text = (ROOT / task / "trap_answer.md").read_text()
    assert any(c["weight"] < 0 and met(c["check"], text) for c in rubric(task)["criteria"])


@pytest.mark.parametrize("task", TASKS)
def test_rubric_is_well_formed(task):
    r = rubric(task)
    ids = [c["id"] for c in r["criteria"]]
    assert len(ids) == len(set(ids))
    assert any(c.get("required") for c in r["criteria"])
    penalties = [c for c in r["criteria"] if c["weight"] < 0]
    assert penalties
    assert all(c["description"].startswith("Agent ") for c in penalties)
    assert not any(c.get("required") and c["weight"] < 0 for c in r["criteria"])
    assert all(c["weight"] != 0 for c in r["criteria"])


KEY_FIGURES = {
    "npv-timing": lambda s: [f"{s['mid_year_npv']:.2f}", f"{s['year_end_npv']:.2f}", f"{s['understatement']:.2f}"],
    "irr-multiple-roots": lambda s: ["10%", "20%", f"{s['npv_at_hurdle']:.2f}", f"{s['mirr']:.2%}"],
    "real-vs-nominal": lambda s: [f"{s['total_pv']:.2f}", f"{s['operating_pv']:.2f}", f"{s['shield_pv']:.2f}"],
    "psc-cost-recovery": lambda s: [f"{-s['contractor_net']:.1f}", f"{s['government_take']:.1f}",
                                    f"{s['unrecovered_end']:.1f}", *[f"{y['cost_oil']:.1f}" for y in s["years"]]],
    "true-loan-cost": lambda s: [f"{s['payment']:.2f}", f"{s['apr']:.2%}", f"{s['effective_annual']:.2%}"],
    "bond-duration": lambda s: [f"{s['price']:.2f}", f"{s['macaulay']:.3f}", f"{s['modified']:.3f}",
                                f"{s['convexity']:.2f}", f"{-s['exact']:.2%}", f"{-s['with_convexity']:.2%}"],
}


@pytest.mark.parametrize("task", TASKS)
def test_reference_answer_quotes_the_computed_figures(task):
    reference = (ROOT / task / "reference_answer.md").read_text()
    for figure in KEY_FIGURES[task](load(task).solve()):
        assert figure in reference, f"{figure} is computed by solution.py but missing from the answer"


# Independent checks: each confirms an answer by a different route from solution.py.

def test_npv_mid_year_equals_annuity_shifted_half_a_year():
    s = load("npv-timing").solve()
    annuity = 400 * (1 - 1.1 ** -4) / 0.1
    assert s["year_end_npv"] == pytest.approx(annuity - 1000)
    assert s["mid_year_npv"] == pytest.approx(annuity * 1.1 ** 0.5 - 1000)


def test_both_irrs_really_zero_the_npv_and_the_sign_pattern_holds():
    mod = load("irr-multiple-roots")
    s = mod.solve()
    assert mod.npv(s["irr_low"]) == pytest.approx(0, abs=1e-9)
    assert mod.npv(s["irr_high"]) == pytest.approx(0, abs=1e-9)
    assert mod.npv(0.05) < 0 < mod.npv(0.15)
    assert mod.npv(0.30) < 0
    assert s["npv_at_hurdle"] > 0 and s["mirr"] > 0.12


def test_real_method_equals_nominal_method():
    s = load("real-vs-nominal").solve()
    nominal_way = sum(100 * 1.05 ** t / 1.1235 ** t for t in (1, 2, 3))
    assert s["operating_pv"] == pytest.approx(nominal_way)


def test_psc_money_is_conserved():
    s = load("psc-cost-recovery").solve()
    revenue, spent = [100, 150, 120], 240
    for gross, y in zip(revenue, s["years"]):
        assert y["royalty"] + y["cost_oil"] + y["profit_oil"] == pytest.approx(gross)
    recovered = sum(y["cost_oil"] for y in s["years"])
    assert recovered + s["unrecovered_end"] == pytest.approx(spent)
    assert s["contractor_net"] + s["government_take"] == pytest.approx(sum(revenue) - spent)
    contractor = recovered + 0.4 * sum(y["profit_oil"] for y in s["years"]) - spent
    assert s["contractor_net"] == pytest.approx(contractor)


def test_loan_amortises_to_zero_and_the_rate_prices_the_net_proceeds():
    mod = load("true-loan-cost")
    s = mod.solve()
    balance = 10000.0
    for _ in range(12):
        balance = balance * 1.01 - s["payment"]
    assert balance == pytest.approx(0, abs=1e-6)
    assert mod.present_value(s["payment"], s["monthly_rate"], 12) == pytest.approx(9800)


def test_bond_sensitivities_match_numerical_derivatives():
    mod = load("bond-duration")
    s = mod.solve()
    h = 1e-4
    p, up, down = mod.price(0.05), mod.price(0.05 + h), mod.price(0.05 - h)
    assert s["modified"] == pytest.approx(-(up - down) / (2 * h) / p, rel=1e-5)
    assert s["convexity"] == pytest.approx((up - 2 * p + down) / h ** 2 / p, rel=1e-4)
    assert mod.price(0.06) == pytest.approx(100)
    assert abs(s["with_convexity"] - s["exact"]) < abs(s["duration_only"] - s["exact"])
