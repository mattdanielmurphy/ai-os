---
title: "B is confined to radius a, which is less than radius b. B ch"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "9a8e9366-71dc-527f-86c5-48778b17f588"
url: ""
---

# B is confined to radius a, which is less than radius b. B ch

> [!NOTE]
> Archived Gemini Thread: [B is confined to radius a, which is less than radius b. B ch]() | Date: 2026-08-13

## User

B is confined to radius a, which is less than radius b.
B changing constantly.
EMF in radius b=e
Why is emf in radius 2b = 2e?
I thought emf would stay the same because it’s confined to the same area. 
When that was wrong I thought ok, pi*r², so (2r)² is 4r, so 4e is the answer

---

## Gemini

Your original intuition was actually completely correct. The electromotive force ($\text{emf}$) does not change when you move from radius $b$ to radius $2b$.


If a test or an answer key told you that the $\text{emf}$ at $2b$ is $2e$, the answer key is mistaken.


Here is exactly why your first instinct was right, and why the other mathematical patterns don't apply here.



The Physics: Faraday's Law of Induction
Faraday's Law states that the induced $\text{emf}$ around a closed loop is equal to the time rate of change of the magnetic flux ($\Phi_B$) passing through that loop:


$$\text{emf} = -\frac{d\Phi_B}{dt}$$


Magnetic flux is defined as the magnetic field times the area it passes through: $\Phi_B = B \cdot A_{\text{with field}}$.


Let's look at the two different loops:



* 
For the loop of radius $b$:
The magnetic field $B$ only exists inside the small inner circle of radius $a$. The space between radius $a$ and radius $b$ has zero magnetic field.
Therefore, the area containing the magnetic flux is just the area of the inner circle: $A = \pi a^2$.
$$\Phi_{B,\text{ loop } b} = B \cdot (\pi a^2)$$
$$\text{emf}_b = -\frac{dB}{dt} \cdot \pi a^2 = e$$




* 
For the loop of radius $2b$:
Even though this loop is much larger, the magnetic field is still strictly confined inside the same inner circle of radius $a$. The extra space between $b$ and $2b$ contains no magnetic field and contributes zero additional flux.
Therefore, the area enclosing the magnetic flux is still exactly the same: $A = \pi a^2$.
$$\Phi_{B,\text{ loop } 2b} = B \cdot (\pi a^2)$$
$$\text{emf}_{2b} = -\frac{dB}{dt} \cdot \pi a^2 = e$$





Because both loops enclose the exact same amount of changing magnetic flux, $\text{emf}_{2b} = \text{emf}_b = e$.



Where the "Double" or "Quadruple" Confusion Comes From
If the question or grading tool insisted the answer is $2e$, it is likely confusing $\text{emf}$ with the induced electric field ($E$).


$\text{emf}$ is the work done per unit charge around the entire loop, which is the integral of the electric field along the path length ($2\pi r$):


$$\text{emf} = \oint E \cdot dl = E \cdot (2\pi r)$$


Because $\text{emf}$ is a constant value ($e$) outside radius $a$, we can look at what happens to the actual electric field strength at different distances:



* At radius $b$: $e = E_b \cdot (2\pi b) \implies E_b = \frac{e}{2\pi b}$

* At radius $2b$: $e = E_{2b} \cdot (2\pi (2b)) \implies E_{2b} = \frac{e}{4\pi b}$


As you move further out, the induced electric field strength drops by half ($E_{2b} = \frac{1}{2}E_b$) because the same total $\text{emf}$ is spread out over a perimeter that is twice as long.


If the answer key states the value doubles, it may have incorrectly multiplied the field scaling or inverted the radius relationship. Stick to your core concept: no new flux means no new $\text{emf}$.

---

