# expert-task-casebook

![CI](https://github.com/olusola-titilayo/expert-task-casebook/actions/workflows/ci.yml/badge.svg)

Six finance and energy-economics tasks written the way expert AI-evaluation tasks are written: a realistic prompt,
a weighted rubric, a reference answer, and a plausible wrong answer that the rubric has to catch.

A good expert task isn't simply hard. It has one tempting wrong path and an answer that can be proved. So every
number here comes from running code, not from typing it in.

| Task | Where a weak answer goes wrong |
|---|---|
| [NPV timing convention](tasks/npv-timing/prompt.md) | The textbook formula is one reflex away, and it gives a clean-looking wrong number. |
| [Two IRRs on one project](tasks/irr-multiple-roots/prompt.md) | The prompt hands over a real root and a confident conclusion. |
| [Mixing real and nominal cash flows](tasks/real-vs-nominal/prompt.md) | Applying one discount rate to everything is the natural habit. |
| [Production sharing contract cash flow](tasks/psc-cost-recovery/prompt.md) | The cap only bites because costs are front-loaded. |
| [True cost of a loan with a fee](tasks/true-loan-cost/prompt.md) | The wrong answer feels sensible: 12 + 2. |
| [Bond price sensitivity](tasks/bond-duration/prompt.md) | There is a built-in check most answers miss: at a 6% yield, a 6% coupon bond prices at exactly 100. |

## What's in a task

```
tasks/npv-timing/
  prompt.md             what the model is asked
  rubric.json           weighted criteria, with penalties for known failure modes
  reference_answer.md   the expert answer
  trap_answer.md        a confident, plausible, wrong answer
  solution.py           computes the numbers behind the answer
  why_this_task.md      why this task separates strong answers from weak ones
```

## What the tests prove

- **Each rubric separates good from bad:** the reference answer passes and the trap answer fails. A rubric that
  passes everything is worthless, so this is checked directly.
- **The answer key is right.** Each `solution.py` is checked a second way: the IRRs give an NPV of zero, the loan
  amortises to exactly zero, duration and convexity match numerical derivatives of the price, and the PSC split adds
  back up to total revenue.
- **The written answers match the code.** The key figures from `solution.py` must appear in `reference_answer.md`.
- **Rubrics are well formed:** unique ids, at least one required criterion and one penalty, and penalties phrased as
  "Agent ...".

Rubrics use the format of [llm-rubric-scorer](https://github.com/olusola-titilayo/llm-rubric-scorer), and CI scores
every answer with that tool too, so the two repos are tested together:

```bash
node dist/src/cli.js tasks/npv-timing/rubric.json tasks/npv-timing/reference_answer.md
```

## Limits

The automatic checks are regular expressions, so they're a first pass and not a judgement of the reasoning. The
`description` of each criterion is written so a human can grade it properly. A model could also pass a regex by luck,
which is why real evaluation pairs checks like these with human review.

Scenarios and figures are invented for illustration and aren't investment advice.

## Run it

```bash
pip install pytest
pytest -q
```

## License

MIT
