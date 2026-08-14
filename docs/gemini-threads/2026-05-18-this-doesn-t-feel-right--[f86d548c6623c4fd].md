---
title: "this doesn't feel right, is it right?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "84755ceb-8215-5254-9fc9-d5389d33bd4b"
url: ""
---

# this doesn't feel right, is it right?

> [!NOTE]
> Archived Gemini Thread: [this doesn't feel right, is it right?]() | Date: 2026-08-13

## User

this doesn't feel right, is it right?

---

## Gemini

The math itself is actually spot on, but I think I see why your gut is telling you something is "off." You've correctly identified a tricky significant figure rule, but you’ve also typed a few of your formulas upside down in the report, which makes the steps look mathematically impossible as written.


1. The Significant Figures (The "Right" Part)
Your note about the denominator is 100% correct. This is a classic case of subtractive cancellation.



* The Math: $$0.111 - 0.020 = 0.091$$

* The Rule: When subtracting, you go by decimal places. Since both values have 3 decimal places, the result ($0.091$) keeps 3 decimal places.

* The Catch: Even though it has 3 decimal places, it only has two significant figures (the 9 and the 1).

* The Result: When you divide $48.9$ (3 sig figs) by $0.091$ (2 sig figs), your final answer is restricted to the lower count. Rounding $537.36$ to $5.4 \times 10^2$ is exactly what you should do.



2. The "Flipped" Formulas (The "Off" Part)
While your final numbers ($5.4 \times 10^2$ and $9.0 \times 10^9$) are correct, the formulas you wrote to get there are visually inverted in a few places:



* 
The Slope Formula: In your text, you wrote $slope = \frac{\Delta (1/r^2)}{\Delta F_E}$. That would be $\frac{0.091}{48.9}$, which equals roughly $0.00186$. To get your result of $537.36$, the formula must be:
$$\text{slope} = \frac{\Delta F_E}{\Delta (1/r^2)}$$




* 
The Coulomb's Constant Formula: In the "Determining Coulomb’s Constant" section, you wrote $k = \frac{Q_1 Q_2}{\text{slope}}$. If you actually divide $6.0 \times 10^{-12}$ by $0.054$, you get a tiny number ($1.1 \times 10^{-10}$). To get the correct value for $k$, the formula should be:
$$k = \frac{\text{slope}}{Q_1 Q_2}$$




* 
The Balloon Trigonometry: In the "Ace" section, you wrote $\tan \theta = \frac{mg}{F_E}$. If $\theta$ is the angle from the vertical, it should be:
$$\tan \theta = \frac{F_E}{mg}$$





The Verdict: Your physics intuition is doing the heavy lifting correctly in your head (which is why your final answers match the theoretical values), but your fingers are flipping the fractions on the page. Fix those three ratios, and the report will be technically perfect.


Do you want me to help you re-verify the free-body diagram for those balloons to make sure the $\tan \theta$ derivation is airtight?

---

