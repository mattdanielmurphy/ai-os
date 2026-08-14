---
title: "I feel these momenta ought to have vector symbols no? **Calc"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "70f56a72-236c-58f8-ac8d-519c1536f274"
url: ""
---

# I feel these momenta ought to have vector symbols no? **Calc

> [!NOTE]
> Archived Gemini Thread: [I feel these momenta ought to have vector symbols no? **Calc]() | Date: 2026-08-13

## User

I feel these momenta ought to have vector symbols no?
**Calculations:**
Because the car is traveling $76.9^\circ$ South of West, it has both **South ($y$)** and **West ($-x$)** momentum components. The motorcycle is traveling exactly East, meaning it only has an **East ($+x$)** momentum component. To find the initial momentums of both vehicles ($p_\text{car}$ and $p_\text{bike}$), we must separate the Conservation of Momentum into $x$ and $y$ dimensions.

*   **Step 1: The y-direction (South)**
    Since the bike has no southward momentum, **the car's initial southward momentum must equal the wreckage's final southward component**:
    $p_{\text{car}, y} = p_{f, y} = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \sin(23.4^\circ) = \mathbf{4833.10\ \text{kg}\cdot\text{m/s [S]}}$

*   **Step 2: Total Initial Momentum of the Car ($\vec{p}_\textbf{car}$)**
    Using the car's angle ($76.9^\circ$), we find its total initial momentum ($p_\text{car}$) and its westward component ($p_{\text{car}, x}$):
    $p_\text{car} = \frac{4833.10}{\sin(76.9^\circ)} = \mathbf{4962.24\ \text{kg}\cdot\text{m/s}}$
    $p_{\text{car}, x} = (4962.24) \cos(76.9^\circ) = \mathbf{1124.71\ \text{kg}\cdot\text{m/s [W]}}$

*   **Step 3: The x-direction (East/West)**
    The bike's initial eastward momentum must overcome the car's westward momentum to result in the final eastward wreckage momentum ($p_{f, x}$):
    $p_{f, x} = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \cos(23.4^\circ) = \mathbf{11168.6\ \text{kg}\cdot\text{m/s [E]}}$
    $p_\text{bike} = 11168.6 + 1124.71 = \mathbf{12293.3\ \text{kg}\cdot\text{m/s [E]}}$

---

## Gemini

You are absolutely correct. Since momentum is a vector quantity, using vector notation ($\vec{p}$) consistently throughout your report is not just good practice—it is necessary for technical accuracy, especially when dealing with multidimensional components in collision forensics.


Here is how you can update your notation to reflect the vector nature of those momenta:


Updated Vector Notation

* 
Step 1: The $y$-direction (South)
Since the bike has no southward momentum, the car's initial southward momentum component must equal the wreckage's final southward component:
$\vec{p}{\text{car}, y} = \vec{p}{f, y} = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \sin(23.4^\circ) = \mathbf{4833.10\ \text{kg}\cdot\text{m/s [S]}}$




* 
Step 2: Total Initial Momentum of the Car ($\vec{p}_\text{car}$)
Using the car's angle ($76.9^\circ$), we find its total initial momentum vector and its westward component:
$|\vec{p}\text{car}| = \frac{4833.10}{\sin(76.9^\circ)} = \mathbf{4962.24\ \text{kg}\cdot\text{m/s}}$
$\vec{p}{\text{car}, x} = |\vec{p}_\text{car}| \cos(76.9^\circ) = \mathbf{1124.71\ \text{kg}\cdot\text{m/s [W]}}$




* 
Step 3: The $x$-direction (East/West)
The bike's initial eastward momentum vector must account for the car's westward component to result in the final eastward wreckage momentum vector ($\vec{p}{f, x}$):
$\vec{p}{f, x} = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \cos(23.4^\circ) = \mathbf{11168.6\ \text{kg}\cdot\text{m/s [E]}}$
$\vec{p}\text{bike} = \vec{p}{f, x} + |\vec{p}_{\text{car}, x}| = \mathbf{12293.3\ \text{kg}\cdot\text{m/s [E]}}$






A Note on Technical Formatting
When you use this notation in your final report, keep these two conventions in mind to ensure clarity:



* Vector vs. Magnitude: Use $\vec{p}$ when referring to the full vector (which includes direction). Use $|\vec{p}|$ or simply $p$ (as you did in your scalar equations) when referring to the magnitude of that vector.

* Consistency: Now that you are using vector notation, ensure you apply it to the final table as well. For example, your table headers for velocities should be $\vec{v}_i$ and $\vec{v}_f$ to match your initial momentum calculations.


Does this adjustment satisfy the requirements for your lab submission, or would you like to review how the vector diagram in Figure 1 should be updated to reflect this notation?

---

## User

for some reason your vector symbols never render.
Can you just let me know from which of these I now have to remove the vector symbols (and add absolute bars for extra clarity) for?

---

## Gemini

It is frustrating when formatting doesn't render as expected. To ensure your report is both accurate and readable, here is the list of items from your calculations that should have the vector symbols ($\vec{p}$) removed and replaced with absolute value notation ($|\vec{p}|$) to correctly indicate they represent the magnitude of the momentum.


Items Requiring Correction



































Current NotationCorrectionReason$\vec{p}_{\text{car}, y}$$\vec{p}_{\text{car}, y}$\vec{p}_{f, y}$$\vec{p}_{f, y}$\vec{p}_{\text{car}}$$\vec{p}_{\text{car}}$\vec{p}_{\text{car}, x}$$\vec{p}_{\text{car}, x}$\vec{p}_{f, x}$$\vec{p}_{f, x}
Why this change is necessary

* Vector Notation ($\vec{p}$): Strictly speaking, $\vec{p}$ implies both a magnitude and a specific direction (e.g., $10\ \text{kg}\cdot\text{m/s}$ at $30^\circ$).

* Magnitude Notation ($|\vec{p}|$): When you are calculating the value of a component (like $4833.10\ \text{kg}\cdot\text{m/s}$) using sine or cosine, you are performing scalar arithmetic on the magnitude. Using $|\vec{p}|$ clarifies that you are dealing with the scalar length of that momentum vector.


Recommended Update for your "Step" equations
For maximum clarity in your report, format your equations like this:



$|\vec{p}{\text{car}, y}| = |\vec{p}{f, y}| = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \sin(23.4^\circ) = 4833.10\ \text{kg}\cdot\text{m/s}$



By removing the vector arrow from the variable name and adding the absolute value bars, you technically correctly distinguish between the "momentum vector" (which includes direction) and the "momentum magnitude" (the scalar value you calculated).


How are you planning to present these equations in your final document—are you using a specific editor like LaTeX or a standard word processor?

---

## User

This isn't working well.
Just change this for me. Please give me this back in a code block without changing any of the markdown formatting, just converting the vectors to magnitudes where applicable:

**Calculations:**
Because the car is traveling $76.9^\circ$ South of West, it has both **South ($y$)** and **West ($-x$)** momentum components. The motorcycle is traveling exactly East, meaning it only has an **East ($+x$)** momentum component. To find the initial momentums of both vehicles ($\vec{p}_\text{car}$ and $\vec{p}_\text{bike}$), we must separate the Conservation of Momentum into $x$ and $y$ dimensions.

*   **Step 1: The y-direction (South)**
    Since the bike has no southward momentum, **the car's initial southward momentum must equal the wreckage's final southward component**:
    $\vec{p}_{\text{car}, y} = \vec{p}_{f, y} = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \sin(23.4^\circ) = \mathbf{4833.10\ \text{kg}\cdot\text{m/s [S]}}$

*   **Step 2: Total Initial Momentum of the Car ($\vec{p}_\textbf{car}$)**
    Using the car's angle ($76.9^\circ$), we find its total initial momentum ($\vec{p}_\text{car}$) and its westward component ($\vec{p}_{\text{car}, x}$):
    $\vec{p}_\text{car} = \frac{4833.10}{\sin(76.9^\circ)} = \mathbf{4962.24\ \text{kg}\cdot\text{m/s}}$
    $\vec{p}_{\text{car}, x} = (4962.24) \cos(76.9^\circ) = \mathbf{1124.71\ \text{kg}\cdot\text{m/s [W]}}$

*   **Step 3: The x-direction (East/West)**
    The bike's initial eastward momentum must overcome the car's westward momentum to result in the final eastward wreckage momentum ($\vec{p}_{f, x}$):
    $\vec{p}_{f, x} = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \cos(23.4^\circ) = \mathbf{11168.6\ \text{kg}\cdot\text{m/s [E]}}$
    $\vec{p}_\text{bike} = 11168.6 + 1124.71 = \mathbf{12293.3\ \text{kg}\cdot\text{m/s [E]}}$

---

## Gemini

**Calculations:**
Because the car is traveling $76.9^\circ$ South of West, it has both **South ($y$)** and **West ($-x$)** momentum components. The motorcycle is traveling exactly East, meaning it only has an **East ($+x$)** momentum component. To find the initial momentums of both vehicles ($p_\text{car}$ and $p_\text{bike}$), we must separate the Conservation of Momentum into $x$ and $y$ dimensions.

* **Step 1: The y-direction (South)**
    Since the bike has no southward momentum, **the car's initial southward momentum must equal the wreckage's final southward component**:
    $|p_{\text{car}, y}| = |p_{f, y}| = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \sin(23.4^\circ) = \mathbf{4833.10\ \text{kg}\cdot\text{m/s [S]}}$

* **Step 2: Total Initial Momentum of the Car ($p_\textbf{car}$)**
    Using the car's angle ($76.9^\circ$), we find its total initial momentum ($|p_\text{car}|$) and its westward component ($|p_{\text{car}, x}|$):
    $|p_\text{car}| = \frac{4833.10}{\sin(76.9^\circ)} = \mathbf{4962.24\ \text{kg}\cdot\text{m/s}}$
    $|p_{\text{car}, x}| = (4962.24) \cos(76.9^\circ) = \mathbf{1124.71\ \text{kg}\cdot\text{m/s [W]}}$

* **Step 3: The x-direction (East/West)**
    The bike's initial eastward momentum must overcome the car's westward momentum to result in the final eastward wreckage momentum ($|p_{f, x}|$):
    $|p_{f, x}| = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \cos(23.4^\circ) = \mathbf{11168.6\ \text{kg}\cdot\text{m/s [E]}}$
    $p_\text{bike} = 11168.6 + 1124.71 = \mathbf{12293.3\ \text{kg}\cdot\text{m/s [E]}}$

---

## User

You seem to have removed ALL the vector symbols even when I think we should have it?

---

## Gemini

You are right to be cautious. The goal is to distinguish between when you are treating momentum as a magnitude (the numerical value you calculated) and when you are referring to it as a full vector quantity (which includes the direction).


In your report, you should use the vector notation ($\vec{p}$) when referring to the momentum as a general concept or when defining the system, and use magnitude notation ($|\vec{p}|$) specifically within the equations where you are performing scalar calculations.


Here is a guide on where to keep the vector symbol and where to use the magnitude bars:


1. Where to use the Vector Symbol ($\vec{p}$)
Keep the vector symbol in conceptual discussions or when defining variables, as it reminds the reader that direction is inherent to the property.



* Initial Definitions: "To find the initial momenta of both vehicles ($\vec{p}{\text{car}}$ and $\vec{p}{\text{bike}}$)..."

* Final Variable Lists: In your table headers, use $\vec{v}_i$ and $\vec{v}_f$.

* Conceptual Statements: "Momentum is a vector quantity that is conserved..."


2. Where to use Magnitude Bars ($|\vec{p}|$)
Use these inside your actual step-by-step math, where you are using trigonometric components to solve for a specific scalar value.


Corrected Section for your Report:



To find the initial momenta of both vehicles ($\vec{p}{\text{car}}$ and $\vec{p}{\text{bike}}$), we must separate the Conservation of Momentum into $x$ and $y$ dimensions.



* 
Step 1: The y-direction (South)
Since the bike has no southward momentum, the car's initial southward momentum component must equal the wreckage's final southward component:
$|\vec{p}{\text{car}, y}| = |\vec{p}{f, y}| = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \sin(23.4^\circ) = \mathbf{4833.10\ \text{kg}\cdot\text{m/s [S]}}$




* 
Step 2: Total Initial Momentum of the Car ($\vec{p}_{\text{car}}$)
Using the car's angle ($76.9^\circ$), we find the total magnitude of the car's initial momentum ($|\vec{p}{\text{car}}|$) and its westward component ($|\vec{p}{\text{car}, x}|$):
$|\vec{p}{\text{car}}| = \frac{4833.10}{\sin(76.9^\circ)} = \mathbf{4962.24\ \text{kg}\cdot\text{m/s}}$
$|\vec{p}{\text{car}, x}| = |\vec{p}_{\text{car}}| \cos(76.9^\circ) = \mathbf{1124.71\ \text{kg}\cdot\text{m/s [W]}}$






Does this clarify the distinction between the conceptual vector and the scalar magnitude required for your math?

---

## User

but, don't you think this sentence "To find the initial momenta of both vehicles (p 
car
​
  and p 
bike
​
 ), we must separate the Conservation of Momentum into x and y dimensions" should have those momenta symbols with vector arrows?

---

## Gemini

You are absolutely right. In that specific sentence, you are referring to the initial momentum of the vehicles as physical vector quantities—you are defining the variables for the system.


In that context, the vector notation is correct because you are discussing the variables themselves, not calculating their magnitudes yet.


You should use the vector arrows in that introductory sentence, and then switch to the magnitude notation (the absolute value bars) only when you are showing the actual math equations where you compute the values.


Here is how that passage should look to be both technically correct and consistent:



"To find the initial momenta of both vehicles ($\vec{p}{\text{car}}$ and $\vec{p}{\text{bike}}$), we must separate the Conservation of Momentum into $x$ and $y$ dimensions.



* Step 1: The y-direction (South)
Since the bike has no southward momentum, the car's initial southward momentum component must equal the wreckage's final southward component:
$|\vec{p}{\text{car}, y}| = |\vec{p}{f, y}| = (1612.52\ \text{kg})(7.54689\ \text{m/s}) \sin(23.4^\circ) = \mathbf{4833.10\ \text{kg}\cdot\text{m/s [S]}}$"



This approach maintains the distinction:



* $\vec{p}$: Use this when referring to the vector property in prose or variable definitions.

* $|\vec{p}|$: Use this when performing the scalar arithmetic to find the numerical component values.


Does having the vector arrows in that introductory sentence help clear up the formatting confusion for the rest of your report?

---

