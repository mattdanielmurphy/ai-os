---
title: "I know I'm not using the math they intended but I thought it"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "6f1e9014-8c01-5743-aa20-be797b378a6b"
url: ""
---

# I know I'm not using the math they intended but I thought it

> [!NOTE]
> Archived Gemini Thread: [I know I'm not using the math they intended but I thought it]() | Date: 2026-08-13

## User

I know I'm not using the math they intended but I thought it should be as simple as 1.5*190/2, because if it takes 4 mins to full rotate, then it's 2 mins to reach the top.
But I guess the problem with my approach is I'm treating it like it's linear when it's circular.

---

## Gemini

Exactly. Your intuition that the movement isn't linear is spot on. If you were climbing a vertical ladder at a constant speed, your logic would work perfectly, but on a Ferris wheel, your vertical speed changes depending on where you are on the circle.


When you are at the "3 o'clock" or "9 o'clock" positions, you are moving almost entirely vertically (maximum vertical speed). When you are at the very top or bottom, you are moving horizontally, so your height barely changes for a moment.


To solve this, we use a trigonometric (sinusoidal) function.


1. Identify the Components

* Radius ($r$): The diameter is $190\text{ m}$, so the radius is $95\text{ m}$.

* Midline ($d$): This is the center of the wheel. Since the bottom is at $5\text{ m}$ and the radius is $95\text{ m}$, the center is at $5 + 95 = 100\text{ m}$.

* Amplitude ($a$): This is the radius, $95\text{ m}$.

* Period ($P$): $4\text{ minutes}$.

* Frequency ($b$): Calculated as $\frac{2\pi}{P} = \frac{2\pi}{4} = \frac{\pi}{2}$.


2. Set up the Equation
Since you start at the bottom (the minimum point), a negative cosine graph is the easiest way to model this:


$$h(t) = -a \cos(b \cdot t) + d$$


Plugging in our values:
$$h(t) = -95 \cos\left(\frac{\pi}{2} t\right) + 100$$


3. Solve for 1.5 Minutes
Substitute $t = 1.5$ into the equation:
$$h(1.5) = -95 \cos\left(\frac{\pi}{2} \cdot 1.5\right) + 100$$
$$h(1.5) = -95 \cos(0.75\pi) + 100$$


Using the unit circle or a calculator (in radians):



* $\cos(0.75\pi) = \cos(135^\circ) \approx -0.7071$


$$h(1.5) = -95(-0.7071) + 100$$
$$h(1.5) = 67.1745 + 100$$
$$h(1.5) \approx 167.17\text{ m}$$



Looking at your options, the height after 1.5 minutes is 167.18 m.


Does the transition from the linear "climb" logic to the cosine wave make sense in terms of why you're higher up than expected?

---

## User

how to answer this?

---

## Gemini

To find the period of a trigonometric function, you only need to focus on the coefficient of the variable inside the sine or cosine function.


The general form of the function is $z = a \sin(b(m - h)) + k$, where the period ($P$) is calculated using the formula:
$$P = \frac{2\pi}{|b|}$$


1. Identify the value of $b$
Looking at your function:
$$z = -4 \sin \left( 3\pi \frac{(m - 4)}{8} \right) + 3$$


We can rewrite the inside part to see the $b$ value more clearly:
$$z = -4 \sin \left( \frac{3\pi}{8} (m - 4) \right) + 3$$


So, $b = \frac{3\pi}{8}$.


2. Calculate the Period
Now, plug that value into the period formula:
$$P = \frac{2\pi}{\frac{3\pi}{8}}$$


To divide by a fraction, you multiply by its reciprocal:
$$P = 2\pi \cdot \frac{8}{3\pi}$$


3. Simplify
The $\pi$ units cancel out:
$$P = 2 \cdot \frac{8}{3}$$
$$P = \frac{16}{3}$$



Looking at the options on your screen, the correct choice is $\frac{16}{3}$.

---

## User

help me out here

---

## Gemini

This problem follows the same sinusoidal pattern as the Ferris wheel. Since you start at high tide (the maximum height), using a cosine function is the most efficient path.


1. Identify the Components

* Amplitude ($a$): Half the distance between high and low tide.
$$(13.4 - 2.6) / 2 = 5.4\text{ ft}$$

* Midline ($d$): The average depth.
$$(13.4 + 2.6) / 2 = 8\text{ ft}$$

* Period ($P$): The time for a full cycle. You're given the time from high to low (half a cycle) is $6.2\text{ hours}$, so a full cycle is:
$$6.2 \times 2 = 12.4\text{ hours}$$

* Frequency ($b$): $$2\pi / 12.4 \approx 0.5067$$


2. Set up the Equation
Let $t = 0$ be 6:30 AM. Since we start at the maximum:
$$h(t) = 5.4 \cos(0.5067t) + 8$$


3. Solve for $h(t) = 8$
The question asks when the tide is 8 feet high for the first time after 6:30 AM.
$$8 = 5.4 \cos(0.5067t) + 8$$
$$0 = 5.4 \cos(0.5067t)$$
$$0 = \cos(0.5067t)$$


The cosine function equals zero at $\pi/2$ (or $90^\circ$):
$$0.5067t = \frac{\pi}{2}$$
$$t = \frac{\pi}{2 \times 0.5067}$$
$$t = 3.1\text{ hours}$$


4. Convert to Clock Time

* 3.1 hours after 6:30 AM.

* $0.1\text{ hours} = 6\text{ minutes}$.

* $3\text{ hours and } 6\text{ minutes}$ after 6:30 AM is 9:36 AM.


The correct choice is 9:36 am.

---

## User

correct answer here? walk me through it

---

## Gemini

This follows the same logic as the last period problem, just with slightly different numbers. You’re looking for the horizontal length of one full wave.


1. Identify the $b$ value
In the function $y = -2 \sin \left( 2\pi \frac{(t - 6)}{3} \right) + 8$, the $b$ value is the coefficient attached to the $(t - 6)$ part.


We can rewrite the inner portion to make it clearer:
$$2\pi \frac{(t - 6)}{3} = \frac{2\pi}{3}(t - 6)$$


So, $b = \frac{2\pi}{3}$.


2. Use the Period Formula
The period ($P$) is always $2\pi$ divided by the absolute value of $b$:
$$P = \frac{2\pi}{|b|}$$
$$P = \frac{2\pi}{\frac{2\pi}{3}}$$


3. Simplify
To divide by a fraction, multiply by its reciprocal:
$$P = 2\pi \cdot \frac{3}{2\pi}$$


The $2\pi$ on top and bottom cancel each other out completely:
$$P = 3$$



The period of the function is 3. Looking at your screen, you should select the third option down.

---

## User

[2026-05-14 13:28 MDT-6] period makes no sense to me... 2pi/pi = 2, no?

---

## Gemini

In SCR-20260514-masa.jpg, there is a slight disconnect between the formula shown and the final result for the period.


You're right that $\frac{2\pi}{\pi} = 2$, but the value of $b$ for this function is actually 2, not $\pi$.


The Breakdown
For a sinusoidal function in the form $y = a \sin(b(x - h)) + k$:



* Identifying $b$: In the factored version of the equation shown in SCR-20260514-masa.jpg, $y = -3 \sin 2(x + \frac{\pi}{6}) - 4$, the coefficient $b$ is the number sitting right outside the parentheses for $x$. Here, $b = 2$.

* Calculating Period: The formula for the period is $P = \frac{2\pi}{|b|}$.

* The Math:
$$P = \frac{2\pi}{2} = \pi$$






Why the confusion?
Looking closely at the red handwritten notes in SCR-20260514-masa.jpg, the person who solved this wrote:
$$\frac{2\pi}{\pi} = \pi$$
This is a mathematical error in their notation. They likely confused the target answer ($\pi$) with the variable they were supposed to divide by ($b=2$). If they had plugged in the correct $b$ value, the work would read:
$$\frac{2\pi}{2} = \pi$$


So, your logic on the division is spot on, but the "b" value was mislabeled in the step-by-step scratchpad of the image.

---

## User

Created Gemini Canvas titled

---

## Gemini
## Gemini — 2026-05-14 19:28

---

## User

[2026-05-14 13:29 MDT-6] find any other errors

---

## Gemini

There is a significant contradiction in the handwritten work for Question 17b.



* .

* . The correct phase shift is 0.

* .

* However, the final large graph plotted at the bottom of page 10 is actually correct for the given function. It ignores the written phase shift and correctly places the peaks at $0$, $\frac{\pi}{2}$, and $\pi$, which properly reflects a phase shift of 0.


Aside from this discrepancy and the notation error you already spotted in Question 13, the calculations and final answers throughout the rest of the document are mathematically sound.

---

## User

[2026-05-14 13:44 MDT-6] how do you determine the period?
I figured I'd try (in orange) seeing where the peaks line up at easy-to-determine intervals, like halfway between the pis.
So there's 3 periods, stretching from -pi/2 to 3pi/2.
So I figure, you do 3periods/[(3pi/2)-(-pi/2)]
and that eventually simplifies to 3/2pi.
But that's recipricol to the actual period given in the answer key.

---

## Gemini

You've actually done all the hard work correctly; you just flipped the final fraction!


The period is defined as the horizontal length of one single cycle. When you calculate it from a graph, the formula is:


$$\text{Period} = \frac{\text{Total Distance}}{\text{Number of Cycles}}$$


Your Calculation
Looking at your orange markings in image_76619a.jpg:



* Total Distance: You measured from $-\frac{\pi}{2}$ to $\frac{3\pi}{2}$.
$$\text{Distance} = \frac{3\pi}{2} - (-\frac{\pi}{2}) = \frac{4\pi}{2} = 2\pi$$

* Number of Cycles: You correctly identified 3 full periods within that span.

* The Result: $$\text{Period} = \frac{2\pi}{3}$$


In your notes, you calculated $\frac{3 \text{ periods}}{2\pi}$, which gives you the frequency (cycles per unit distance), rather than the period (distance per cycle).


Verifying with the Equation
If you look at the function provided for that specific question ($y = \sin(3x)$ or similar, where $b=3$):
$$\text{Period} = \frac{2\pi}{|b|} = \frac{2\pi}{3}$$


It matches your visual observation perfectly once the fraction is right-side up. Whenever you're in doubt, just remember: Period is a distance, so the distance measurement ($2\pi$) needs to be on top.

---

## User

[2026-05-14 13:49 MDT-6] how do you get P=2pi from the equation?

---

## Gemini

To get the period from an equation, you look at the coefficient of $x$, which is usually labeled as $b$.


The standard period for a basic sine or cosine function is $2\pi$. The $b$ value tells you how many cycles fit into that $2\pi$ space. Therefore, to find the length of just one cycle (the period), you divide the standard $2\pi$ by that $b$ value.


The Formula
$$P = \frac{2\pi}{|b|}$$


Applying it to your example
In the function from the top of the page in image_760400.jpg:
$$y = \sin(x)$$



* Identify $b$: Since there is no visible number in front of the $x$, the coefficient is an invisible 1. So, $b = 1$.

* Calculate:
$$P = \frac{2\pi}{1} = 2\pi$$


Why does this work?
Think of $b$ as a "speed" multiplier.



* If $b=2$, the graph is moving twice as fast, so it finishes a cycle in half the time ($\frac{2\pi}{2} = \pi$).

* If $b=1$, it moves at the standard speed, finishing exactly at $2\pi$.


In the graph you marked up earlier where $b=3$, the "speed" was tripled, which is why the cycles were crushed together, resulting in a shorter period of $\frac{2\pi}{3}$.

---

## User

[2026-05-14 13:52 MDT-6] for the units at the bottom: -pi/3, pi/6, etc....
is it realistic that one could just write those straight up without any other calculation shown?

---

## Gemini

It is definitely realistic, though it usually depends on how comfortable you are with the unit circle and common fractions of $\pi$.


Most people who write those values directly are likely using one of these three mental shortcuts:


1. The "Grid Unit" Method
Once you find the period and the phase shift, you can determine the distance between your "critical points" (the peaks, valleys, and intercepts).



* A cycle is always split into four equal parts.

* If your period is $\pi$, each major movement happens every $\frac{\pi}{4}$ units.

* If you know your starting point (the phase shift), you just add that "grid unit" repeatedly. If the math is simple (like $\frac{\pi}{4} + \frac{\pi}{4}$), many students just do that in their head and write the results on the axis.


2. Converting to a Common Denominator
This is the "pro" way to do it without showing formal work. If your phase shift involves sixths (like $\frac{\pi}{6}$) and your period involves halves or quarters, you mentally convert everything to have a denominator of 6 or 12.



* You think of $\frac{\pi}{2}$ as $\frac{3\pi}{6}$.

* Counting along the axis becomes as simple as saying "one-sixth, two-sixths, three-sixths..." and simplifying as you write them down.


3. Visual Estimation (Least Accurate)
On some assignments, if the grid is already provided, you can simply look at the existing tick marks. If there are three boxes between $0$ and $\frac{\pi}{2}$, then each box must be $\frac{\pi}{6}$. You can then just "label as you go" based on the physical spacing.


Should you show work?
For your current coursework, if you can see the relationship (like recognizing that $\frac{\pi}{6}$ is just one-third of the way to $\frac{\pi}{2}$), writing them "straight up" is standard. However, if the fractions get messy—like adding $\frac{\pi}{7}$ to $\frac{2\pi}{3}$—showing a quick common denominator calculation on the side prevents easy-to-avoid arithmetic errors.

---

