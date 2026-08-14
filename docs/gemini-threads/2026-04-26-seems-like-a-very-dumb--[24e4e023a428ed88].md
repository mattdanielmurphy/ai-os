---
title: "seems like a very dumb and inaccurate way of finding what yo"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "ddf578cf-0f72-594a-b96c-7cfacc8239b2"
url: ""
---

# seems like a very dumb and inaccurate way of finding what yo

> [!NOTE]
> Archived Gemini Thread: [seems like a very dumb and inaccurate way of finding what yo]() | Date: 2026-08-13

## User

seems like a very dumb and inaccurate way of finding what you can get trivially through algebra...

---

## Gemini

It is definitely an approximation-heavy approach. Using the Trace function on a graphing calculator is essentially a visual "guess and check," which can feel imprecise compared to the elegance of algebra.


The reason this is often taught first in Pre-calculus is to build a conceptual bridge before introducing Logarithms. While tracing gives you a quick visual sense of the relationship between the light source distance ($x$) and the intensity ($y$), it’s nowhere near as precise as solving the equation directly.


To solve part (c) with algebra, you would set up the equation based on the function shown on the TI-84 screen ($Y_1 = 100(0.96)^x$):


$$30 = 100(0.096)^x$$


The Algebraic Route

* Isolate the base: Divide both sides by $100$.
$$0.3 = (0.96)^x$$

* Apply Logarithms: Take the log of both sides to bring down the exponent.
$$\log(0.3) = x \log(0.96)$$

* Solve for $x$:
$$x = \frac{\log(0.3)}{\log(0.96)}$$

* Calculate:
$$x \approx 29.49$$


The calculator's trace value of 29.26 (where $y \approx 30.29$) shows the inherent "clunkiness" of the manual method. The algebraic solution is not only faster once you know the laws of logarithms, but it also removes the "close as possible" guesswork required by the toggle keys.


Since you're on the "Laws of Logarithms" page of your Pre-calculus 12 module, the course is likely about to pivot to this exact realization—that algebra is the superior tool here.


Are you currently working through the change of base formula, or just getting started with basic log properties?

---

## User

half-life time d?
wtf?

---

## Gemini

I hear you—the phrasing on this slide is a bit of a mess. Calling it "half-life time $d$" is confusing because $d$ is already defined as distance, not time. In this specific context, they are asking you to find the "half-value distance."


Essentially, they want to know: At what distance ($d$) does the light intensity ($I$) drop to exactly half of its original value?


Since the starting intensity ($I_0$) is 100, you are looking for the distance where the intensity becomes 50.


Step 1: Solving for the "Half-Life" Distance
To find this using algebra (the "not-dumb" way), set $I = 50$:


$$50 = 100(0.96)^d$$



* Divide by 100: $0.5 = (0.96)^d$

* Log both sides: $\log(0.5) = d \log(0.96)$

* Isolate $d$: $d = \frac{\log(0.5)}{\log(0.96)}$

* Calculate: $d \approx 16.98$ meters.



Step 2: Rewriting the Equation (The Goal of Part B)
The slide wants you to rewrite the original equation using base $\frac{1}{2}$ (or $0.5$). The standard formula for exponential decay using half-life is:


$$I = I_0 \left( \frac{1}{2} \right)^{\frac{d}{h}}$$


Where $h$ is the half-life value you just calculated ($16.98$). So, your final rewritten equation for Example 3 should look like this:


$$I = 100 \left( \frac{1}{2} \right)^{\frac{d}{16.98}}$$


Why bother doing this?
While the original $(0.96)^d$ tells you the light drops by 4% every meter, the new version $(\frac{1}{2})^{\frac{d}{16.98}}$ tells you instantly that the light cuts in half every ~17 meters. It's just a different way of looking at the same decay.


Does that clear up what they meant by "Step 1" and "Step 2" in those solution boxes?

---

## User

cursive capital I looks a LOT like lowercase cursive d

---

## Gemini

You aren't wrong. In traditional cursive (like the Palmer Method), a capital I and a lowercase d both start with that same vertical loop and a rounded base. When they’re isolated on a math slide like this, the distinction basically disappears.


It’s a bizarre choice for a textbook to use $d$ for "distance" and then suddenly pivot to calling the solution "half-life time $d$." In any standard physics or math context:



* $d$ usually stands for distance.

* $t$ usually stands for time.

* $h$ or $T_{1/2}$ usually stands for half-life.


By calling the result "half-life time $d$," they are effectively saying "The distance ($d$) at which the half-life occurs." It’s linguistic gymnastics that makes the math harder to follow than it needs to be.


If you’re writing this down in your own notes to keep it sane, I’d suggest labeling that value as $h = 16.98$. It makes the final formula—$I = 100(0.5)^{d/h}$—actually look like a formula instead of a pile of the same letter.


Does the next slide finally move on to a different variable, or are they sticking with $d$ for everything?

---

## User

forget all previous context. show me a way to write my d and I more distinctly

---

## Gemini

To keep your variables from looking like a repetitive loop of ink, the best strategy is to lean into the structural differences between print and cursive, or adopt specific "math-style" script conventions.


Here are a few ways to separate them visually:


1. The "Hook & Bar" Method (Most Distinct)

* Capital I: Use a block serif style even if the rest of your math is in script.

* Draw a vertical bar with a clear horizontal top and bottom cross-stroke ($\text{I}$).

* This is the standard in most textbooks to prevent confusion with $1$, $l$, or $J$.




* Lowercase d: Stick to a standard print d with a straight vertical "ascender" (the tall stick). Avoid the cursive loop that curls back to the left, which is what makes it look like a capital $I$.


2. The Loop Distinction (Cursive Style)
If you prefer writing in cursive, you have to exaggerate the entry and exit strokes:



* For $I$ (Intensity): Start with a wide, horizontal loop that moves from left to right before dropping down. The "head" of the $I$ should be significantly wider than the body.

* For $d$ (Distance): Start with the oval base first (like a lowercase $a$), then bring the stroke straight up and back down. If you must loop the top, keep the loop extremely narrow and tight to the stem.


3. Using Alternate Notation
In physics and advanced math, when letters get crowded, we often switch symbols to avoid this exact headache:



* Use $\ell$ for length/distance: A script $\ell$ (like a lowercase $L$) is very common for distance/length and won't be confused with an $I$ or a $d$.

* Use $x$ for distance: In almost all coordinate geometry, $x$ is the universal symbol for horizontal distance.


Summary Comparison




















VariableRecommended LookWhy?$I$ (Intensity)$\text{I}$ (with serifs)Crossbars at the top/bottom kill any ambiguity.$d$ (Distance)$\text{d}$ (print-style)A straight vertical stick cannot be mistaken for a loop.
Pro Tip: If you are stuck using the variables provided on the slide, try writing your $I$ slightly larger than your $d$. Since $I$ represents a total value (Intensity) and $d$ is a unit of measurement (distance), the size difference helps your brain categorize them at a glance.


Does the straight-stick d feel comfortable for your writing speed, or do you prefer keeping the flow of cursive?

---

## User

as an aside, presumably batteries don't actually work like this?

---

## Gemini

You're right to be skeptical. In the real world, battery discharge is rarely a perfectly smooth exponential curve like the one in Example 4.


The math problem assumes a constant 15% loss per hour, but actual battery chemistry is much more erratic.


Why the Math Model Lies

* The "Voltage Drop" Cliff: Most modern lithium-ion batteries (like in your laptop or phone) maintain a relatively steady voltage for a long time and then plummet once they hit a certain threshold. It’s less of a gentle slide and more of a walk off a cliff at the end.

* Linear vs. Exponential: Under a constant load (like a laptop running a specific program), a battery often drains linearly (e.g., 10% every hour) rather than exponentially. Exponential decay implies that as the battery gets lower, it drains slower, which isn't usually how hardware behaves.

* The "Idle" Factor: A battery sitting on a shelf does experience exponential "self-discharge," but it's usually around 1-2% per month, not 15% per hour.


Why do textbooks use this example?
Textbooks love the battery example because "percent loss" is the easiest way to teach Exponential Decay without using scary physics terms. It’s a "mathematical fiction" used to practice the formula:


$$P = 100(0.85)^h$$


If you want to solve (b) and (c) for this "fake" battery:

* For (b): You're looking for the "half-life" of this battery charge.
$$50 = 100(0.85)^h \implies 0.5 = 0.85^h$$
$$h = \frac{\log(0.5)}{\log(0.85)} \approx 4.27 \text{ hours.}$$

* For (c): Use that value to rewrite the base as $0.5$:
$$P = 100(0.5)^{\frac{h}{4.27}}$$


In short: the math is solid, but the physics is a bit of a stretch. If your laptop actually lost 15% of its charge every hour just sitting there, you'd probably be looking for a replacement battery!


Are you finding that the questions in this module are mostly these types of "real-world" word problems?

---

## User

what's the equation for b)
I got (81*log.6)/log.5

---

## Gemini

Actually, you are remarkably close, but it looks like you might have hit a small "logic snag" with the decimals.


The half-life is 8.1 days, not 81. Also, if you are looking for 6%, the decimal is $0.06$, not $.6$.


Here is the algebraic breakdown to see where those numbers land:


The Setup
Using the standard half-life formula:
$$A = A_0 \left( \frac{1}{2} \right)^{\frac{t}{h}}$$



* $A$ (Final amount): 6

* $A_0$ (Initial amount): 100

* $h$ (Half-life): 8.1


$$6 = 100(0.5)^{\frac{t}{8.1}}$$


The Algebra

* Isolate the base: $0.06 = (0.5)^{\frac{t}{8.1}}$

* Log both sides: $\log(0.06) = \frac{t}{8.1} \log(0.5)$

* Multiply by 8.1: $8.1 \log(0.06) = t \log(0.5)$

* Solve for $t$:
$$t = \frac{8.1 \times \log(0.06)}{\log(0.5)}$$


The Calculation
If you plug that into a calculator:
$$t \approx \frac{8.1 \times (-1.2218)}{-0.3010} \approx 32.87$$


Rounded to the nearest day (as the Answer on your slide suggests), you get 33 days.


Wait, what about my version?
If you use your original setup $(\frac{81 \times \log(0.6)}{\log(0.5)})$, you'd get about 59.7. The 8.1 vs 81 is likely just a typo, but the $0.6$ vs $0.06$ is a common trap—$0.6$ would actually represent 60% remaining!


Does the 8.1 vs 81 mix-up happen often with this module's font, or was that just a quick mental skip?

---

## User

give me a hint about how to solve this one

---

## Gemini

For Example 6, the wording is the trickiest part.


The prompt says: "20%... decays in 7 days."


The Critical Hint
Before you touch any logs, you need to determine your "remaining amount" ($A$).



* If 20% has decayed, what percentage is left?

* (Hint: It’s not 20).


The Setup
Once you have that remaining percentage (let's call it $y$), use the half-life formula:


$$y = 100(0.5)^{\frac{t}{h}}$$



* Plug in 7 for your time ($t$).

* Plug in your remaining percentage for $y$.

* Your goal is to solve for $h$ (the half-life), which is currently stuck in the exponent.


Algebraic tip: Since you are solving for a variable in the denominator of an exponent, you’ll likely end up with a step where you have to multiply both sides by $h$ to get it out of the fraction after taking the logs.


Does that help you get the initial equation on paper, or do you want to check the "remaining amount" logic first?

---

## User

(7log.8)/log.5?

---

## Gemini

Spot on. That is the exact algebraic setup for finding the half-life.


By using $0.8$ (the 80% remaining), you've successfully bypassed the "20% decay" trap. Here is how that looks in the final steps:


$$h = \frac{7 \log(0.5)}{\log(0.8)}$$


Wait—check your division order! To isolate $h$ from the exponent $\frac{7}{h}$, the algebra actually flips the logs compared to your previous "finding time" calculation:



* $0.8 = (0.5)^{7/h}$

* $\log(0.8) = \frac{7}{h} \log(0.5)$

* $h \log(0.8) = 7 \log(0.5)$

* $h = \frac{7 \log(0.5)}{\log(0.8)}$


Quick Calculation

* $\log(0.5) \approx -0.301$

* $\log(0.8) \approx -0.097$

* $h \approx \frac{7(-0.301)}{-0.097} \approx \mathbf{21.7}$


If you punch in your version $(7 \log(0.8)) / \log(0.5)$, you’ll get $2.25$.


The "Sniff Test": If it takes 7 days just to lose 20%, the half-life (losing 50%) must be longer than 7 days. 21.7 days passes the test; 2.25 days doesn't.


Does the Answer button on the slide match that 21.7?

---

## User

h/7 = (log.5)/log.8 right?

---

## Gemini

Exactly. You’ve successfully flipped the fraction and the logs to isolate $h$ properly.


$$h = \frac{7 \log(0.5)}{\log(0.8)}$$


Since $h$ was in the denominator of the exponent ($7/h$), your algebraic move to flip both sides of the equation is the cleanest way to solve it.


If you punch that into your calculator, you should get:



* $7 \times (-0.30103) \approx -2.107$

* $-2.107 / -0.0969 \approx \mathbf{21.74}$


So the half-life is approximately 21.7 days.


Does the Solution on your screen confirm that, or does it round it to a whole number?

---

