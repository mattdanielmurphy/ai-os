---
title: "9: why am I getting 5.4V?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "888bfafa-5421-5c3c-9c13-539f1346d6bb"
url: ""
---

# 9: why am I getting 5.4V?

> [!NOTE]
> Archived Gemini Thread: [9: why am I getting 5.4V?]() | Date: 2026-08-13

## User

9: why am I getting 5.4V?

---

## Gemini

It looks like you are running into a classic unit conversion or exponent oversight! You are finding the right base numbers ($2 + 4 = 6$, and $6 \times 9 = 54$), but you're missing the scale factors for Coulomb's constant and the charge prefix.


Here is how the math breaks down to show exactly where that $10^4$ factor comes from:


1. Identify the Formula and Givens
:
$$V_{\text{net}} = \frac{kQ_1}{r_1} + \frac{kQ2}{r_2} = k \left( \frac{Q_1}{r_1} + \frac{Q_2}{r_2} \right)$$



* Coulomb's Constant ($k$): $\approx 8.99 \times 10^9 \text{ N}\cdot\text{m}^2/\text{C}^2$ (usually rounded to $9.0 \times 10^9$)

* 

* 



2. Set Up the Calculation
Substitute the values into the parentheses first to find the combined value of $\frac{Q}{r}$:


$$\frac{1.0 \times 10^{-6}\text{ C}}{0.50\text{ m}} + \frac{4.0 \times 10^{-6}\text{ C}}{1.0\text{ m}}$$


$$\left(2.0 \times 10^{-6}\text{ C/m}\right) + \left(4.0 \times 10^{-6}\text{ C/m}\right) = 6.0 \times 10^{-6}\text{ C/m}$$



3. Multiply by Coulomb's Constant ($k$)
Now, bring the exponent from $k$ ($10^9$) into the mix:


$$V_{\text{net}} = (9.0 \times 10^9) \times (6.0 \times 10^{-6})$$


Multiply the coefficients and add the exponents ($9 + (-6) = 3$):


$$V_{\text{net}} = 54 \times 10^3\text{ V}$$


:
$$V_{\text{net}} = 5.4 \times 10^4\text{ V}$$


Double-check your steps to make sure you converted the microcoulombs ($\mu\text{C}$) to $\times 10^{-6}\text{ C}$ and included the full $10^9$ exponent for $k$.

---

## User

I don't get it, look at my calculator

---

## Gemini

Ah, the screenshot makes it completely clear what happened.


Take a close look at the fraction inside your parentheses:
You entered (1/.5 * 4/1) instead of (1/.5 + 4/1).


Because you multiplied the two fractions inside the parentheses instead of adding them, the math went like this:


$$\frac{1}{0.5} \times \frac{4}{1} = 2 \times 4 = 8$$


Then multiplying that by $9 \times 10^9$ and the $10^{-6}$ prefix gave you:
$$8 \times (9 \times 10^9) \times 10^{-6} = 72 \times 10^3 = 7.2 \times 10^4\text{ V}$$


If you swap that multiplication sign for an addition sign inside the parentheses, you will get the correct $5.4 \times 10^4\text{ V}$ ($54,000\text{ V}$).

---

## User

what's 36.0 MeV?

---

## Gemini

An MeV stands for Mega-electronvolt, which is a unit of energy commonly used in nuclear and particle physics.


To break down 36.0 MeV:



* The Unit: One electronvolt ($\text{eV}$) is the amount of kinetic energy gained by a single electron accelerating through an electric potential difference of one volt. The "Mega" prefix means one million ($10^6$).

* In Joules: In standard SI units, energy is measured in Joules ($\text{J}$). Because subatomic particles have tiny amounts of energy, we use MeV to avoid extremely small decimals:
$$1 \text{ eV} = 1.602 \times 10^{-19} \text{ J}$$
$$1 \text{ MeV} = 1.602 \times 10^{-13} \text{ J}$$


Multiplying this out for your specific value:
$$36.0 \text{ MeV} = 36.0 \times 10^6 \text{ eV} = 5.767 \times 10^{-12} \text{ Joules}$$


Context in Physics Problems
In high school or introductory university physics (like a mechanics or electromagnetism unit involving moving charges), a value like 36.0 MeV typically represents the kinetic energy ($KE$) of a fast-moving subatomic particle, such as a proton or an alpha particle, inside an accelerator or a magnetic field.


For example, if you are calculating the velocity ($v$) of a proton ($m = 1.67 \times 10^{-27} \text{ kg}$) with this much kinetic energy using the classical formula:
$$KE = \frac{1}{2}mv^2 \implies v = \sqrt{\frac{2KE}{m}}$$


Plugging in $5.76 \times 10^{-12} \text{ J}$ yields a velocity of approximately $8.31 \times 10^7 \text{ m/s}$ (about 28% the speed of light).

---

## User

for 16, dont you need to do trig to figure out distance between B and q2?

---

## Gemini

You actually don't need any trig for point B! .


:
*

*



* .


Since electric potential ($V$) is a scalar quantity, the total potential at B is just the direct sum of the potentials from each charge:
$$V_B = \frac{kQ_1}{r_1} + \frac{kQ_2}{r_2}$$


.


.


What about Point A?
You don't need trig for point A either!



* .

* .


.

---

## User

yeah but without the answer key we wouldnt know it's 0V

---

## Gemini

.


:


1. Find the total distance between $Q_2$ and $Q_1$
.
*

*


Using the Pythagorean theorem to find the total horizontal separation ($x_{\text{total}}$) along the bottom line:
$$x_{\text{total}}^2 = 66.1^2 - 26^2$$
$$x_{\text{total}}^2 = 4369.21 - 676 = 3693.21$$
$$x_{\text{total}} \approx 60.77\text{ cm}$$



2. Find the horizontal position of Point B
.


Let's find B's horizontal distance to $Q_1$ ($x_B$):
$$x_B^2 = 40^2 - 26^2$$
$$x_B^2 = 1600 - 676 = 924$$
$$x_B \approx 30.40\text{ cm}$$



3. Compare the segments
Now look at how that horizontal line is split:



* The total distance between the charges is $60.77\text{ cm}$.

* Point B sits $30.40\text{ cm}$ away from $Q_1$ horizontally.

* This leaves exactly $60.77 - 30.40 = 30.37\text{ cm}$ (or $30.40\text{ cm}$ factoring in rounding) from $Q_2$ to B horizontally.


. .

---

## User

for 5, if left side is positive and right side is negative, then right side is north, right?

---

## Gemini

.


Here is how you can verify it cleanly using the Right-Hand Rule for solenoids (coils):


1. Trace the Current Direction

* .

* Following the first loop on the left, the wire goes up and over the top, flowing downward across the front face of the core.


2. Apply the Right-Hand Rule

* Curl the fingers of your right hand in the direction of the current on the side facing you (downward).

* Extend your thumb out horizontally.


When your fingers curl down across the front of the cylinder, your right thumb points directly to the right. .

---

## User

answer for q7?

---

## Gemini

.


Here is how you figure it out step-by-step using the Right-Hand Rule for moving charges:


1. Identify your vectors

* .

* .

* .



2. Apply the Right-Hand Rule

* .

* .

* Look at where your four fingers are pointing. .


.

---

