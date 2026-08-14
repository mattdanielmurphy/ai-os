---
title: "my horizontal axis is going to be inverse square distance, 1"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "294a6f71-2fb8-5456-9e6c-492c93a705e8"
url: ""
---

# my horizontal axis is going to be inverse square distance, 1

> [!NOTE]
> Archived Gemini Thread: [my horizontal axis is going to be inverse square distance, 1]() | Date: 2026-08-13

## User

my horizontal axis is going to be inverse square distance, 1/r^2 shown in hundredths. So how do I show that properly? "Inverse Square Distance, 1/r^2 ([1/m^2]*10^-4)?

---

## Gemini

To represent this properly on your axis, you want to ensure the reader knows exactly how to multiply the numbers on the scale to get the "real" values.


The standard scientific notation for an axis is to show the variable, the unit, and the multiplier that was applied to the data.


Recommended Formatting
If your axis values are in hundredths (e.g., $0.01, 0.02, 0.03$), your label should look like this:


Inverse Square Distance, $1/r^2$ ($10^{-2} \text{ m}^{-2}$)



Why this works

* The Multiplier ($10^{-2}$): This tells the reader that the number "1" on your axis actually represents $1 \times 10^{-2}$ (one hundredth).

* The Unit ($\text{m}^{-2}$): Placing the unit in parentheses is the standard convention in physics and engineering.

* Clarity: Using $10^{-2}$ is more standard in academic papers than writing "hundredths" or using the asterisk notation you suggested ($[1/m^2] * 10^{-4}$), which can be confusing to follow.


Alternative (Power of 10 in the units)
If you prefer the style you were leaning toward, the mathematically "cleanest" way to write it is:



$1/r^2$ ($\text{cm}^{-2}$)



If you are working in centimeters, "hundredths" of a meter squared often naturally converts to $1/\text{cm}^2$. However, if you must stick to meters, the $10^{-2}$ version above is your best bet.


A quick tip for Google Sheets: Since I see you are working in a spreadsheet, you can go to Chart Editor > Axes > Horizontal Axis Title and paste the text there. Most spreadsheet programs don't support true LaTeX superscripts in titles, so you may need to use the caret symbol:
Inverse Square Distance, 1/r^2 (10^-2 m^-2)

---

## User

I get your confusion, it's hundreds of a cm. So m^-4 is what I want

---

## Gemini

If your units are in $m^{-4}$ because of the square of the inverse (converting $cm^{-2}$ to $m^{-2}$ involves a factor of $10^4$, and squaring or further manipulating these leads you to $10^{-4}$), you want to be very precise so the scale remains readable.


Since your spreadsheet shows values like 1.36, 2.71, and 4.07 on the axis, here is how to label it properly to account for that $10^{-4}$ factor:


The Standard Scientific Label
Inverse Square Distance, $1/r^{2}$ ($\times 10^{-4} \text{ m}^{-2}$)



Why this is the "Proper" way:

* The Multiplier: By putting $\times 10^{-4}$ inside the parentheses with the unit, you are telling the reader: "The number 4.07 on this graph actually represents $4.07 \times 10^{-4}$."

* Avoiding Confusion: If you just write $m^{-4}$, a reader might think the distance was raised to the fourth power. Keeping it as $m^{-2}$ with a scientific multiplier ($10^{-4}$) clarifies that the unit of measurement is area-based, but the scale has been shifted for readability.


How to type it in your Chart Editor:
Since Google Sheets doesn't support subscript/superscript in axis titles, copy and paste this:



Inverse Square Distance, 1/r^2 (x10^-4 m^-2)



Data Check
Looking at your current chart, your points are forming a very clean linear trend. If those x-axis values (1.36, 2.71, etc.) are indeed the results of your $1/r^2$ calculation in $m^{-2}$ but scaled by $10^{-4}$ to make them whole numbers, the label above is exactly what a lab instructor or peer reviewer would expect to see.

---

## User

Holy shit this is confusing.
so m^-2 means 1/m^2
and then x10^-4 m^-2 means 1/hundredths of a cm^2?

---

## Gemini

It is a total brain-bender because you’re dealing with "inverses of inverses." Let’s strip away the math jargon and look at what those units actually represent in the physical world.


The Short Answer
Yes, you have the logic right, but let’s clarify the "why" so it clicks:



* $m^{-2}$ is just scientific shorthand for $1/m^2$.

* $10^{-4} \text{ m}^{-2}$ is indeed equivalent to $1/\text{cm}^2$.



The "Wait, Why?" Breakdown
Think of it this way: A square meter is huge ($100\text{ cm} \times 100\text{ cm} = 10,000\text{ cm}^2$).



* The Scale: $1\text{ m}^2 = 10,000\text{ cm}^2$ (which is $10^4\text{ cm}^2$).

* The Inverse: When you flip that into an "inverse square," everything reverses.

* $1/\text{cm}^2$ is 10,000 times larger than $1/\text{m}^2$.

* Therefore, $1/\text{cm}^2 = 10^4 \text{ m}^{-2}$.





The Confusion Point:
When you see $10^{-4} \text{ m}^{-2}$ on a graph, it usually means the "real" numbers were so tiny (like $0.000136$) that the scientist multiplied them by $10,000$ just to make them look like normal numbers ($1.36$) on the axis.



Translation: Your axis label $(\times 10^{-4} \text{ m}^{-2})$ is basically telling the reader: "I moved the decimal point 4 places to the right to make this readable for you."



How it looks on your Chart
On your spreadsheet, your x-axis has values like 1.36 and 2.71.



* If you label it $(1/\text{cm}^2)$, you are saying "This is 1.36 units per square centimeter."

* If you label it $(\times 10^{-4} \text{ m}^{-2})$, you are saying "This is $1.36 \times 10^{-4}$ units per square meter."


Both mean the exact same thing. Most physics teachers prefer the $m^{-2}$ version because meters are the standard (SI) unit, even if the math makes your head spin for a second.


Does that make the decimal movement a bit clearer, or should we look at one of your specific data points to trace the math?

---

## User

I keep telling you, we don't want hundredths of a meter, we want hundredths of a centimeter!

---

## Gemini

I hear you—I was definitely over-complicating it by trying to force it back into meters. Let’s stick strictly to your hundredths of a centimeter requirement.


If your axis values (like 1.36, 2.71, etc.) represent hundredths of a $1/\text{cm}^2$, here is how you show that properly without the "physics-speak" getting in the way:


The Best Label for Your Chart
Inverse Square Distance, $1/r^2$ ($10^{-2} \text{ cm}^{-2}$)



Breaking down the notation:

* The Unit ($\text{cm}^{-2}$): This is just the formal way to write $1/\text{cm}^2$.

* The Multiplier ($10^{-2}$): This is the mathematical way to say "hundredths." When a reader sees that $10^{-2}$ in the label, they know that the "1.36" on your axis actually means $1.36$ hundredths (or $0.0136$) of a $1/\text{cm}^2$.


How to put it in your spreadsheet:
Since you can't do fancy formatting in the axis title box, copy and paste this:



Inverse Square Distance, 1/r^2 (10^-2 cm^-2)



Why not $m^{-4}$?
You mentioned $m^{-4}$ earlier—if you use that, it implies you are measuring a "per meter-to-the-fourth" value, which would likely confuse your instructor. Sticking to $\text{cm}^{-2}$ keeps it clearly tied to the actual distance units you measured in the lab.


Does that label look like it fits the scale you're seeing on your graph?

---

## User

Maybe I'll just say fuck it, and not do any scaling. just cm^-2

---

## Gemini

That is a completely valid choice and usually the safest one to avoid a massive headache. If you remove the scaling and just use $cm^{-2}$, you are letting the raw numbers speak for themselves.


Looking at your spreadsheet, your x-axis values (1.36, 2.71, etc.) are already very clean. If those are the actual results of your $1/r^2$ calculation using centimeters, then your label is perfect as:


Inverse Square Distance, $1/r^2$ ($cm^{-2}$)



Why "Fuck It" is actually a good strategy:

* Zero Ambiguity: There is no "Wait, did they multiply or divide by 100?" from your instructor.

* Direct Correlation: The number on the axis is exactly what you calculated in your data table.

* Standard Practice: In many undergraduate labs, it is actually preferred to keep the units simple rather than trying to force everything into scientific notation if the numbers are already easy to read.


One final check
Before you close the spreadsheet, just double-check one thing:
If your distance $r$ was 5 cm, then $r^2$ is 25, and $1/r^2$ is 0.04.



* If your graph shows 0.04, use $cm^{-2}$.

* If your graph shows 4.0, you did scale it, and you'd need that $10^{-2}$ we talked about.


As long as the number on the axis matches the number in your calculator, you're golden. Should I help you double-check one of those data points against your distance column?

---

