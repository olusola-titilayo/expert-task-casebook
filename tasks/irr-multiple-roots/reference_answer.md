**No. The project should be accepted, though only just: NPV at 12% is +$0.13.**

The cash flow changes sign twice (minus, plus, minus), so it can have more than one IRR. It has two:

-100 + 230/(1+r) - 132/(1+r)^2 = 0 gives **r = 10% and r = 20%**.

NPV is negative below 10%, positive between 10% and 20%, and negative above 20%. The spreadsheet found one root and stopped. The usual "IRR above the hurdle" rule doesn't work here, because neither root is a meaningful rate of return.

At the 12% hurdle, NPV = -100 + 230/1.12 - 132/1.12^2 = **+$0.13**.

A cross-check: MIRR at 12% is 12.03%, just above the hurdle, which agrees with the small positive NPV.

The value created is tiny compared with $100 invested and $132 of clean-up exposure. A small rise in clean-up cost removes it, so this deserves a sensitivity check before approval.
