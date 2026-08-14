---
title: "Only answer the questions that I explicitly type out or that"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "e601487f-be05-53a5-98cb-a1da78f3e4ee"
url: ""
---

# Only answer the questions that I explicitly type out or that

> [!NOTE]
> Archived Gemini Thread: [Only answer the questions that I explicitly type out or that]() | Date: 2026-08-13

## User

Only answer the questions that I explicitly type out or that are actively visible on my shared screen. If you cannot see the text or options for a specific question number, do not guess, infer, or generate a placeholder. Instead, simply state that you are waiting for the question context.

When answering, write the question number, the full question, its listed options, and your selected answer with the option number.

You must also show the work used to solve each question. Show only minimal algebraic or computational steps, just enough to match what a student would be expected to write on a test.

Do not explain anything unless absolutely necessary. Do not add commentary, teaching, justification, or extra notes beyond the minimal work and final answer.

Use this response format:

## Question 5
**Question:** Is the derivative of a constant always zero?

**Options:**
1. true
2. false

**Work:**
\( \frac{d}{dx}(c)=0 \)

**Correct Answer:** true (1st choice)

---

## Gemini

Item 1
Question: $$\lim_{x \to -4} \frac{6}{x + 4} =$$


Options:



* Does not exist

* $-\infty$

* $0$

* $\infty$


Work:
As $x \to -4^+$, $\frac{6}{x+4} \to \frac{6}{0^+} = \infty$
As $x \to -4^-$, $\frac{6}{x+4} \to \frac{6}{0^-} = -\infty$
Since the one-sided limits do not match, the limit does not exist.


Correct Answer: Does not exist (1st choice)

---

## User

double check this one again

---

## Gemini

Item 2
Question: $$\lim_{x \to 3} f(x) =$$


Options:



* 0

* $\infty$

* Does not exist

* $-\infty$


Work:
$\lim_{x \to 3^-} f(x) = -\infty$
$\lim_{x \to 3^+} f(x) = -\infty$


Correct Answer: $-\infty$ (4th choice)

---

## User

you have it

---

## Gemini

Item 6
Question: At $x = -2$ the function $y = \frac{5}{x + 2}$ is differentiable but not continuous.


Options:



* true

* false


Work:
At $x = -2$, the denominator is $0$, so the function is undefined.
Since it is undefined, it is neither continuous nor differentiable.
A function cannot be differentiable if it is not continuous.


Correct Answer: false (2nd choice)

---

## User

next
when you write this question in text form, put an asterisk explaining that there's accompanying images that aren't going to be seen in text form

---

## Gemini

Item 8
Question: Which of the following pairs of graphs could represent the graph of a function and the graph of its derivative?*
(Note: There are accompanying images for this question that are not seen in this text format.)


Options:



* III only

* I and III

* I only

* II only

* II and III


Work:



* Graph I: $f(x)$ models exponential growth (e.g., $e^x$). Its derivative $f'(x)$ would also be an exponential growth curve of the same shape. The graphs match this relationship. Valid.

* Graph II: $f(x)$ is a downward-opening parabola (degree 2 polynomial). Its derivative $f'(x)$ must be a straight line (degree 1). The provided $f'$ graph is another parabola, which is impossible. Invalid.

* Graph III: $f(x)$ increases, reaches a maximum, and then decreases. Therefore, $f'(x)$ must start positive, cross the x-axis (equal 0) at the maximum, and then become negative. The $f'$ graph accurately reflects this behavior (e.g., $f(x) = \sin x$ and $f'(x) = \cos x$). Valid.


Correct Answer: I and III (2nd choice)

---

## User

next, again, mark this one as incomplete in text form

---

## Gemini

Item 18
Question: If a Left Sum underapproximates the value of $\int_{0}^{a} f(x) dx$, where $a > 0$, and a Middle Sum overapproximates the value of $\int_{0}^{a} f(x) dx$, which of the following could be a graph of $y = f(x)$?*
(Note: This question relies on accompanying images that are incomplete in text form.)


Options:



* Graph of a ray rising at a constant rate

* Graph of a curve rising at an increasing rate

* Graph of a curve falling steeply

* Graph of a ray decreasing at a constant rate

* Graph of a curve increasing at a decreasing rate

* Graph of a curve decreasing at an increasing rate


Work:
Left sum underapproximates $\implies f(x)$ is increasing.
Middle sum overapproximates $\implies f(x)$ is concave down.
The function must be increasing and concave down (increasing at a decreasing rate).


Correct Answer: Graph of a curve increasing at a decreasing rate (5th choice)

---

## User

next

---

## Gemini

Item 26
Question: Consider the differential equation $\frac{1}{8x^3} \frac{dy}{dx} = \sqrt{x^4 + 9}$ with initial condition $(0, 1)$. First solve this to find $y(x)$, and then use it to answer this question: What is $y(2)$?


Options:



* None of these options

* $\frac{7}{3}$

* $\frac{5}{3}$

* $\frac{9}{3}$


Work:
$\frac{dy}{dx} = 8x^3\sqrt{x^4+9}$
$y = \int 8x^3\sqrt{x^4+9} , dx$
Let $u = x^4 + 9 \implies du = 4x^2 , dx \implies 2,du = 8x^3 , dx$
$y = \int 2\sqrt{u} , du = \frac{4}{3}u^{3/2} + C = \frac{4}{3}(x^4+9)^{3/2} + C$
Substitute $(0,1)$:
$1 = \frac{4}{3}(0+9)^{3/2} + C \implies 1 = \frac{4}{3}(27) + C \implies 1 = 36 + C \implies C = -35$
$y(x) = \frac{4}{3}(x^4+9)^{3/2} - 35$
Find $y(2)$:
$y(2) = \frac{4}{3}(2^4+9)^{3/2} - 35 = \frac{4}{3}(25)^{3/2} - 35 = \frac{4}{3}(125) - 35 = \frac{500}{3} - \frac{105}{3} = \frac{395}{3}$


Correct Answer: None of these options (1st choice)

---

## User

[2026-06-18 13:04 MDT-6] now collate all responses into one please
Make sure you keep the asterisk notes for the questions reliant on images that aren't present in the text versions (add such a note for q2)

---

## Gemini

Item 1
Question: $$\lim_{x \to -4} \frac{6}{x + 4} =$$


Options:



* Does not exist

* $-\infty$

* $0$

* $\infty$


Work:
As $x \to -4^+$, $\frac{6}{x+4} \to \frac{6}{0^+} = \infty$
As $x \to -4^-$, $\frac{6}{x+4} \to \frac{6}{0^-} = -\infty$
Since the one-sided limits do not match, the limit does not exist.


Correct Answer: Does not exist (1st choice)



Item 2
Question: $$\lim_{x \to 3} f(x) =$$*
(Note: There are accompanying images for this question that are not seen in this text format.)


Options:



* 0

* $\infty$

* Does not exist

* $-\infty$


Work:
$\lim_{x \to 3^-} f(x) = -\infty$
$\lim_{x \to 3^+} f(x) = -\infty$


Correct Answer: $-\infty$ (4th choice)



Item 3
Question: True or False: $\lim_{x \to -1} \frac{x^2 + 4x - 1}{x - 6} = \frac{4}{7}$


Options:



* True

* False


Work:
$\lim_{x \to -1} \frac{x^2 + 4x - 1}{x - 6} = \frac{(-1)^2 + 4(-1) - 1}{-1 - 6} = \frac{1 - 4 - 1}{-7} = \frac{-4}{-7} = \frac{4}{7}$


Correct Answer: True (1st choice)



Item 4
Question: What is the $\lim_{x \to 2} \frac{x^2 - 4}{x - 2}$?


Options:



* 0

* -2

* Does not exist (DNE)

* 2

* 4


Work:
$\lim_{x \to 2} \frac{x^2 - 4}{x - 2} = \lim_{x \to 2} \frac{(x - 2)(x + 2)}{x - 2} = \lim_{x \to 2} (x + 2) = 2 + 2 = 4$


Correct Answer: 4 (5th choice)



Item 5
Question: The graph of a function $f$ is shown in the diagram. Which of the statements below must be false?


Options:



* $f(a)$ exists.

* $f(x)$ is defined for $x = a$.

* $f$ is not continuous at $x = a$.

* $\lim_{x \to a} f(x)$ exists.

* All statements above are true.


Work:



* $f(a)$ is defined by the solid dot below the hole.

* $\lim_{x \to a} f(x)$ exists because the left and right paths meet at the hole.

* $f$ is not continuous at $x = a$ because $\lim_{x \to a} f(x) \neq f(a)$.

* Since all four individual statements are true, none of them are false.


Correct Answer: All statements above are true. (5th choice)



Item 6
Question: At $x = -2$ the function $y = \frac{5}{x + 2}$ is differentiable but not continuous.


Options:



* true

* false


Work:
At $x = -2$, the denominator is $0$, so the function is undefined.
Since it is undefined, it is neither continuous nor differentiable.
A function cannot be differentiable if it is not continuous.


Correct Answer: false (2nd choice)



Item 7
Question: Find $f'(x)$, if $f(x) = 7x^5 \sec^{-1}x$


Options:



* $35x^4 \sec^{-1}x - 7x^5 \frac{1}{|x|\sqrt{x^2-1}}$

* $35x^4 \sec^{-1}x - 7x^5 \sec^{-2}x$

* $35x^4 \sec^{-1}x - 7x^5 \frac{1}{1+x^2}$

* $35x^4 \sec^{-1}x + 7x^5 \frac{1}{|x|\sqrt{x^2-1}}$


Work:
Using the product rule $f'(x) = u'v + uv'$:
$u = 7x^5 \implies u' = 35x^4$
$v = \sec^{-1}x \implies v' = \frac{1}{|x|\sqrt{x^2-1}}$
$f'(x) = 35x^4 \sec^{-1}x + 7x^5 \left(\frac{1}{|x|\sqrt{x^2-1}}\right)$


Correct Answer: $35x^4 \sec^{-1}x + 7x^5 \frac{1}{|x|\sqrt{x^2-1}}$ (4th choice)



Item 8
Question: Which of the following pairs of graphs could represent the graph of a function and the graph of its derivative?*
(Note: There are accompanying images for this question that are not seen in this text format.)


Options:



* III only

* I and III

* I only

* II only

* II and III


Work:



* Graph I: $f(x)$ models exponential growth (e.g., $e^x$). Its derivative $f'(x)$ would also be an exponential growth curve of the same shape. The graphs match this relationship. Valid.

* Graph II: $f(x)$ is a downward-opening parabola (degree 2 polynomial). Its derivative $f'(x)$ must be a straight line (degree 1). The provided $f'$ graph is another parabola, which is impossible. Invalid.

* Graph III: $f(x)$ increases, reaches a maximum, and then decreases. Therefore, $f'(x)$ must start positive, cross the x-axis (equal 0) at the maximum, and then become negative. The $f'$ graph accurately reflects this behavior (e.g., $f(x) = \sin x$ and $f'(x) = \cos x$). Valid.


Correct Answer: I and III (2nd choice)



Item 9
Question: Find $f'(-3)$, if $f(x) = (-3x^2 - 9x)(-x^2 + 8)$ (Answer accurate to the nearest integer.)


Options:
(Note: This is a short-answer question with an input box instead of listed options.)


Work:
Using the product rule $f'(x) = u'v + uv'$:
$u = -3x^2 - 9x \implies u' = -6x - 9$
$v = -x^2 + 8 \implies v' = -2x$
$f'(-3) = u'(-3)v(-3) + u(-3)v'(-3)$
$u(-3) = -3(-3)^2 - 9(-3) = -27 + 27 = 0$
$u'(-3) = -6(-3) - 9 = 18 - 9 = 9$
$v(-3) = -(-3)^2 + 8 = -9 + 8 = -1$
$f'(-3) = (9)(-1) + (0)v'(-3) = -9$


Correct Answer: -9



Item 10
Question: The derivative of $y = (3x)^{x+5}$ with respect to $x$ is $3(x+5)(3x)^{x+4}$.


Options:



* false

* true


Work:
Let $y = (3x)^{x+5}$
$\ln y = (x+5)\ln(3x)$
$\frac{1}{y}y' = (1)\ln(3x) + (x+5)\cdot\frac{3}{3x}$
$y' = (3x)^{x+5}\left[\ln(3x) + \frac{x+5}{x}\right]$
This does not match $3(x+5)(3x)^{x+4}$ (which incorrectly applies the power rule).


Correct Answer: false (1st choice)



Item 11
Question: Solve this problem algebraically, using your knowledge of derivatives. Do not solve by graphing. What is the absolute maximum of the function $f(x) = \frac{2}{x-9}$ on the domain $[1, 7]$?


Options:



* $1/2$

* $-1$

* $-1/4$

* No absolute Maximum on the given domain.


Work:
$f'(x) = \frac{-2}{(x-9)^2}$
Since $f'(x) \neq 0$ anywhere and is defined on $[1,7]$, check the endpoints:
$f(1) = \frac{2}{1-9} = -\frac{1}{4}$
$f(7) = \frac{2}{7-9} = -1$
Comparing values, $-\frac{1}{4} > -1$.


Correct Answer: $-1/4$ (3th choice)



Item 12
Question: If the distance of an object is given by $d(t) = 3t^3 - 6t$, then at $t = 2$, the object’s velocity is


Options:



* cannot be determined.

* increasing.

* decreasing.

* constant.


Work:
$v(t) = d'(t) = 9t^2 - 6$
$a(t) = v'(t) = 18t$
$a(2) = 18(2) = 36$
Since $a(2) > 0$, the velocity is increasing.


Correct Answer: increasing. (2nd choice)



Item 13
Question: Given the derivative of a continuous function, $f'(x) = \frac{x^2 + 9x + 20}{x - 8}$, if each of the critical points and key values of the function were ADDED together, their SUM total would be:


Options:



* $-9$

* $0$

* $-1$

* $8$


Work:
Critical points/key values occur where $f'(x) = 0$ or $f'(x)$ is undefined.
Numerator equals 0:
$x^2 + 9x + 20 = 0 \implies (x + 4)(x + 5) = 0 \implies x = -4, x = -5$
Denominator equals 0:
$x - 8 = 0 \implies x = 8$
Sum of all critical points and key values:
$(-4) + (-5) + 8 = -1$


Correct Answer: $-1$ (3rd choice)



Item 14
Question: If $f'(x) < 0$ and $f''(x) < 0$, then which of the following is true?


Options:



* $f(x)$ is increasing and concave down

* $f(x)$ is increasing and concave up

* $f(x)$ is decreasing and concave up

* $f(x)$ is decreasing and concave down


Work:
$f'(x) < 0 \implies f(x)$ is decreasing.
$f''(x) < 0 \implies f(x)$ is concave down.


Correct Answer: $f(x)$ is decreasing and concave down (4th choice)



Item 15
Question: For the equation $y = x^3 - 4x$ determine the roots (or zeros) of the equation.


Options:



* 0, 2

* -2

* -2, 0, 2

* 0

* 2


Work:
$x^3 - 4x = 0$
$x(x^2 - 4) = 0$
$x(x - 2)(x + 2) = 0$
$x = 0, 2, -2$


Correct Answer: -2, 0, 2 (3rd choice)



Item 16
Question: If $\int_{0}^{2} f(x) dx = 5$ and $\int_{0}^{7} f(x) dx = 8$, then $\int_{2}^{7} f(x) dx =$ ___ ? (Answer accurate to nearest integer.)


Options:
(Note: This is a short-answer question with an input box instead of listed options.)


Work:
$\int_{0}^{7} f(x) dx = \int_{0}^{2} f(x) dx + \int_{2}^{7} f(x) dx$
$8 = 5 + \int_{2}^{7} f(x) dx$
$\int_{2}^{7} f(x) dx = 8 - 5 = 3$


Correct Answer: 3



Item 17
Question: If $\int_{-2}^{5} f(x) dx = 1$ and $\int_{-2}^{5} g(x) dx = -4$, then $\int_{-2}^{5} [2f(x) - 4g(x)] dx = 16$.


Options:



* false

* true


Work:
$\int_{-2}^{5} [2f(x) - 4g(x)] dx = 2\int_{-2}^{5} f(x) dx - 4\int_{-2}^{5} g(x) dx$
$= 2(1) - 4(-4) = 2 + 16 = 18$
Since $18 \neq 16$, the statement is false.


Correct Answer: false (1st choice)



Item 18
Question: If a Left Sum underapproximates the value of $\int_{0}^{a} f(x) dx$, where $a > 0$, and a Middle Sum overapproximates the value of $\int_{0}^{a} f(x) dx$, which of the following could be a graph of $y = f(x)$?*
(Note: This question relies on accompanying images that are incomplete in text form.)


Options:



* Graph of a ray rising at a constant rate

* Graph of a curve rising at an increasing rate

* Graph of a curve falling steeply

* Graph of a ray decreasing at a constant rate

* Graph of a curve increasing at a decreasing rate

* Graph of a curve decreasing at an increasing rate


Work:
Left sum underapproximates $\implies f(x)$ is increasing.
Middle sum overapproximates $\implies f(x)$ is concave down.
The function must be increasing and concave down (increasing at a decreasing rate).


Correct Answer: Graph of a curve increasing at a decreasing rate (5th choice)



Item 19
Question: $$\int \sin^4 x \cos x , dx =$$


Options:



* $\frac{\sin^4 x}{3} + C$

* $\frac{\sin^5 x}{5} + C$

* $\cos^5 x \sin^3 x + C$

* $\frac{\cos^5 x}{5} + C$


Work:
Let $u = \sin x \implies du = \cos x , dx$
$$\int u^4 , du = \frac{u^5}{5} + C = \frac{\sin^5 x}{5} + C$$


Correct Answer: $\frac{\sin^5 x}{5} + C$ (2nd choice)



Item 20
Question: $$\int (\sin^3 x \cos x) , dx =$$


Options:



* $-\frac{\cos^4 x \sin^2 x}{8} + C$

* $-\frac{\cos^4 x}{4} + C$

* $\frac{\sin^3 x}{3} + C$

* $\frac{\sin^4 x}{4} + C$


Work:
Let $u = \sin x \implies du = \cos x , dx$
$$\int u^3 , du = \frac{u^4}{4} + C = \frac{\sin^4 x}{4} + C$$


Correct Answer: $\frac{\sin^4 x}{4} + C$ (4th choice)



Item 21
Question: $$\int_{0}^{1} x\sqrt{25 + x^2} , dx = \int_{0}^{1} \frac{\sqrt{u}}{2} , du$$, after doing the substitution given by $u = 25 + x^2$.


Options:



* false

* true


Work:
Given $u = 25 + x^2 \implies du = 2x , dx \implies x , dx = \frac{1}{2} , du$.
When changing variables, the limits of integration must also change:
Lower limit: $x = 0 \implies u = 25 + (0)^2 = 25$
Upper limit: $x = 1 \implies u = 25 + (1)^2 = 26$
The transformed integral should be $$\int_{25}^{26} \frac{\sqrt{u}}{2} , du$$, not $$\int_{0}^{1} \frac{\sqrt{u}}{2} , du$$.


Correct Answer: false (1st choice)



Item 22
Question: What is the area between the curve $y = x^6$ and the x-axis on the interval from $[0, 2]$?


Options:



* $\frac{64\pi}{7}$

* $\frac{64}{7}$

* $\frac{128}{7}$

* $\frac{128\pi}{7}$


Work:
$$\text{Area} = \int_{0}^{2} x^6 , dx = \left[ \frac{x^7}{7} \right]_{0}^{2} = \frac{2^7}{7} - \frac{0^7}{7} = \frac{128}{7}$$


Correct Answer: $\frac{128}{7}$ (3rd choice)



Item 23
Question: The area under the curve $y = x^3 + 1$ from $x = 0 to x = 2$ is 8.


Options:



* false

* true


Work:
$$\text{Area} = \int_{0}^{2} (x^3 + 1) , dx = \left[ \frac{x^4}{4} + x \right]_{0}^{2}$$
$$= \left( \frac{2^4}{4} + 2 \right) - \left( \frac{0^4}{4} + 0 \right) = (4 + 2) - 0 = 6$$
Since $6 \neq 8$, the statement is false.


Correct Answer: false (1st choice)



Item 24
Question: If $\frac{1}{2x-3} \frac{dy}{dx} = 1$, and the function goes through the point $(1, 2)$, then $y = x^2 - 3x - 2$.


Options:



* true

* false


Work:
$\frac{dy}{dx} = 2x - 3$
$y = \int (2x - 3) , dx = x^2 - 3x + C$
Substitute $(1,2)$:
$2 = (1)^2 - 3(1) + C$
$2 = 1 - 3 + C \implies 2 = -2 + C \implies C = 4$
$y = x^2 - 3x + 4$
Since $x^2 - 3x + 4 \neq x^2 - 3x - 2$, the statement is false.


Correct Answer: false (2nd choice)



Item 25
Question: The function $y = C e^{3t} - e^2$ solves the differential equation $y'' - 4y' = -3y - 3e^2$.


Options:



* false

* true


Work:
$y = Ce^{3t} - e^2$
$y' = 3Ce^{3t}$
$y'' = 9Ce^{3t}$


Substitute into the left-hand side (LHS):
$\text{LHS} = 9Ce^{3t} - 4(3Ce^{3t}) = -3Ce^{3t}$


Substitute into the right-hand side (RHS):
$\text{RHS} = -3(Ce^{3t} - e^2) - 3e^2 = -3Ce^{3t} + 3e^2 - 3e^2 = -3Ce^{3t}$


Since $\text{LHS} = \text{RHS}$, the statement is true.


Correct Answer: true (2nd choice)



Item 26
Question: Consider the differential equation $\frac{1}{8x^3} \frac{dy}{dx} = \sqrt{x^4 + 9}$ with initial condition $(0, 1)$. First solve this to find $y(x)$, and then use it to answer this question: What is $y(2)$?


Options:



* None of these options

* $\frac{7}{3}$

* $\frac{5}{3}$

* $\frac{9}{3}$


Work:
$\frac{dy}{dx} = 8x^3\sqrt{x^4+9}$
$y = \int 8x^3\sqrt{x^4+9} , dx$
Let $u = x^4 + 9 \implies du = 4x^2 , dx \implies 2,du = 8x^3 , dx$
$y = \int 2\sqrt{u} , du = \frac{4}{3}u^{3/2} + C = \frac{4}{3}(x^4+9)^{3/2} + C$
Substitute $(0,1)$:
$1 = \frac{4}{3}(0+9)^{3/2} + C \implies 1 = \frac{4}{3}(27) + C \implies 1 = 36 + C \implies C = -35$
$y(x) = \frac{4}{3}(x^4+9)^{3/2} - 35$
Find $y(2)$:
$y(2) = \frac{4}{3}(2^4+9)^{3/2} - 35 = \frac{4}{3}(25)^{3/2} - 35 = \frac{4}{3}(125) - 35 = \frac{500}{3} - \frac{105}{3} = \frac{395}{3}$


Correct Answer: None of these options (1st choice)

---

## User

confirm answer is "all above statements are true"

---

## Gemini

Yes, selecting "All statements above are true" is the most logical choice here, though you've spotted a flaw in the test question itself.


The question asks which statement must be false, but based on the graph, every single statement provided is mathematically true.


Here is the step-by-step breakdown of why:



* $f(a)$ exists: True. There is a solid plotted point at $x = a$, giving it a defined $y$-value.

* $f(x)$ is defined for $x = a$: True. This is just another way of saying the first statement.

* $f$ is not continuous at $x = a$: True. For a function to be continuous, $\lim_{x \to a} f(x)$ must equal $f(a)$. The limit approaches the open circle (hole), but the actual function value $f(a)$ is the solid point below it. Because they do not match, the function has a removable discontinuity.

* $\lim_{x \to a} f(x)$ exists: True. The curve approaches the exact same $y$-value (the open circle) from both the left and right sides.


Because statements 1 through 4 are all true, the 5th statement ("All statements above are true") is also a true statement.


There is no definitively false statement available to choose from. It is highly likely the test bank contains a typo—either the prompt meant to ask which statement is true, or the third option was originally supposed to read "$f$ is continuous" (which would have been the false option). Given the situation, confirming that all the statements are true is the best way forward.

---

