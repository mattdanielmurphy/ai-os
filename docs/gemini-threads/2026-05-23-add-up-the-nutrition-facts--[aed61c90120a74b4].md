---
title: "Add up the nutrition facts from this for a pizza with pepper"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "1425e548-7d94-56b7-8fbd-980bcd6530b9"
url: ""
---

# Add up the nutrition facts from this for a pizza with pepper

> [!NOTE]
> Archived Gemini Thread: [Add up the nutrition facts from this for a pizza with pepper]() | Date: 2026-08-13

## User

Add up the nutrition facts from this for a pizza with pepperoni, cheese, ham, and bacon strip crumble. Per serving.
Create a nutrition label with the facts

---

## Gemini

Based on the Domino's nutrition guide provided, here is the breakdown for one slice (1/6 of a large New York Style pizza) with regular cheese, pizza sauce, pepperoni, ham, and bacon strip crumble.


Nutrition Breakdown (Per Slice)













































































IngredientCaloriesFat (g)Sat. Fat (g)Sodium (mg)Carbs (g)Protein (g)NY Style Crust1502.50150275Pizza Sauce150010031Regular Cheese10074.522018Pepperoni504.5222003Ham200.5023013Bacon Strip Crumble6041.526015TOTAL39518.58.01,1803325

Nutrition Facts
Serving Size: 1 Slice (1/6 of Large Pizza)


Amount Per Serving
Calories: 395















































Amount% Daily Value*Total Fat 18.5g24%Saturated Fat 8g40%Trans Fat 0gCholesterol 60mg20%Sodium 1,180mg51%Total Carbohydrates 33g12%Dietary Fiber 1g4%Sugars 2gProtein 25g
The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice.

---

## User

Create an actual nutrition label mockup, no need for the breakdown, just all together

---

## Gemini

from weasyprint import HTML

# Data aggregated from the provided image for 1 slice (1/6) of a Large NY Style pizza
# Crust (150), Sauce (15), Reg Cheese (100), Pepperoni (50), Ham (20), Bacon (60) = 395
# Fat: 2.5 + 0 + 7 + 4.5 + 0.5 + 4 = 18.5g
# Sat Fat: 0 + 0 + 4.5 + 2 + 0 + 1.5 = 8.0g
# Sodium: 150 + 100 + 220 + 220 + 230 + 260 = 1180mg
# Carbs: 27 + 3 + 1 + 0 + 1 + 1 = 33g
# Fiber: 1 + 1 + 0 + 0 + 0 + 0 = 2g
# Sugars: 1 + 1 + 0 + 0 + 0 + 0 = 2g
# Protein: 5 + 1 + 8 + 3 + 3 + 5 = 25g
# Cholesterol: 0 + 0 + 25 + 10 + 10 + 15 = 60mg (based on standard values from image for these toppings)

html_content = f\"\"\"
<!DOCTYPE html>
<html>
<head>
<style>
    @page {{
        size: A5;
        margin: 20mm;
        background-color: #ffffff;
    }}
    body {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        display: block;
        margin: 0;
        padding: 0;
    }}
    .label-container {{
        border: 2px solid black;
        padding: 10px;
        width: 280px;
        margin: auto;
        background-color: white;
    }}
    .header {{
        border-bottom: 10px solid black;
        padding-bottom: 5px;
        margin-bottom: 5px;
    }}
    .header h1 {{
        font-size: 28pt;
        font-weight: 900;
        margin: 0;
        line-height: 1;
    }}
    .serving-info {{
        font-size: 11pt;
        border-bottom: 1px solid black;
        padding-bottom: 5px;
        margin-bottom: 5px;
    }}
    .calories-row {{
        display: table;
        width: 100%;
        border-bottom: 5px solid black;
        padding: 3px 0;
        margin-bottom: 5px;
    }}
    .calories-label {{
        display: table-cell;
        font-size: 12pt;
        font-weight: bold;
        vertical-align: bottom;
    }}
    .calories-value {{
        display: table-cell;
        font-size: 24pt;
        font-weight: 900;
        text-align: right;
        vertical-align: top;
    }}
    .daily-value-text {{
        text-align: right;
        font-size: 8pt;
        font-weight: bold;
        border-bottom: 1px solid black;
        padding-bottom: 3px;
    }}
    .nutrient-row {{
        display: table;
        width: 100%;
        border-bottom: 1px solid #ccc;
        padding: 4px 0;
        font-size: 10pt;
    }}
    .nutrient-row.bold {{
        font-weight: bold;
        border-bottom: 1px solid black;
    }}
    .nutrient-row.indent {{
        padding-left: 15px;
    }}
    .dv {{
        display: table-cell;
        text-align: right;
        font-weight: bold;
    }}
    .label-text {{
        display: table-cell;
    }}
    .footer {{
        font-size: 7.5pt;
        margin-top: 10px;
        line-height: 1.2;
    }}
</style>
</head>
<body>
    <div class="label-container">
        <div class="header">
            <h1>Nutrition Facts</h1>
        </div>
        <div class="serving-info">
            1 serving per container<br>
            <strong>Serving size: 1 Slice (186g)</strong>
        </div>
        <div class="calories-row">
            <div class="calories-label">Amount per serving<br><span style="font-size: 18pt;">Calories</span></div>
            <div class="calories-value">395</div>
        </div>
        <div class="daily-value-text">% Daily Value*</div>
        
        <div class="nutrient-row bold">
            <div class="label-text">Total Fat 18.5g</div>
            <div class="dv">24%</div>
        </div>
        <div class="nutrient-row indent">
            <div class="label-text">Saturated Fat 8g</div>
            <div class="dv">40%</div>
        </div>
        <div class="nutrient-row indent">
            <div class="label-text">Trans Fat 0g</div>
            <div class="dv"></div>
        </div>
        <div class="nutrient-row bold">
            <div class="label-text">Cholesterol 60mg</div>
            <div class="dv">20%</div>
        </div>
        <div class="nutrient-row bold">
            <div class="label-text">Sodium 1180mg</div>
            <div class="dv">51%</div>
        </div>
        <div class="nutrient-row bold">
            <div class="label-text">Total Carbohydrate 33g</div>
            <div class="dv">12%</div>
        </div>
        <div class="nutrient-row indent">
            <div class="label-text">Dietary Fiber 2g</div>
            <div class="dv">7%</div>
        </div>
        <div class="nutrient-row indent">
            <div class="label-text">Total Sugars 2g</div>
            <div class="dv"></div>
        </div>
        <div class="nutrient-row indent" style="border-bottom: 0;">
            <div class="label-text">Includes 0g Added Sugars</div>
            <div class="dv">0%</div>
        </div>
        <div class="nutrient-row bold" style="border-top: 10px solid black; border-bottom: 0;">
            <div class="label-text">Protein 25g</div>
            <div class="dv"></div>
        </div>
        
        <div class="footer">
            * The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice.
        </div>
    </div>
</body>
</html>
\"\"\"

with open(\"nutrition_label.html\", \"w\") as f:
    f.write(html_content)

HTML(filename=\"nutrition_label.html\").write_pdf(\"pizza_nutrition_label.pdf\")



Traceback (most recent call last):
  File "<xbox-string>", line 14
    html_content = f\"\"\"
                     ^
SyntaxError: unexpected character after line continuation character


from weasyprint import HTML

# Data for 1 slice of Large NY Style pizza with Pepperoni, Ham, and Bacon
# Calculations based on image:
# Calories: 150 (Crust) + 15 (Sauce) + 100 (Cheese) + 50 (Pepperoni) + 20 (Ham) + 60 (Bacon) = 395
# Fat: 2.5 + 0 + 7 + 4.5 + 0.5 + 4 = 18.5g
# Sat Fat: 0 + 0 + 4.5 + 2 + 0 + 1.5 = 8g
# Sodium: 150 + 100 + 220 + 220 + 230 + 260 = 1180mg
# Carbs: 27 + 3 + 1 + 0 + 1 + 1 = 33g
# Fiber: 1 + 1 + 0 + 0 + 0 + 0 = 2g
# Protein: 5 + 1 + 8 + 3 + 3 + 5 = 25g
# Cholesterol: 0 + 0 + 25 + 10 + 10 + 15 = 60mg

html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
    @page {
        size: A5;
        margin: 20mm;
        background-color: #ffffff;
    }
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        margin: 0;
        padding: 0;
    }
    .label-container {
        border: 1px solid black;
        padding: 8px;
        width: 260px;
        margin: 20px auto;
        background-color: white;
    }
    .header {
        border-bottom: 8px solid black;
        padding-bottom: 2px;
        margin-bottom: 4px;
    }
    .header h1 {
        font-size: 26pt;
        font-weight: 900;
        margin: 0;
        letter-spacing: -1px;
    }
    .serving-info {
        font-size: 10pt;
        border-bottom: 1px solid black;
        padding-bottom: 4px;
        margin-bottom: 4px;
        line-height: 1.2;
    }
    .calories-header {
        display: table;
        width: 100%;
        border-bottom: 4px solid black;
        padding-bottom: 2px;
        margin-bottom: 4px;
    }
    .cal-left {
        display: table-cell;
        vertical-align: bottom;
        font-weight: bold;
        font-size: 11pt;
    }
    .cal-right {
        display: table-cell;
        vertical-align: top;
        text-align: right;
        font-size: 24pt;
        font-weight: 900;
    }
    .dv-header {
        text-align: right;
        font-size: 8pt;
        font-weight: bold;
        border-bottom: 1px solid black;
        padding-bottom: 2px;
    }
    .line {
        display: table;
        width: 100%;
        border-bottom: 1px solid black;
        padding: 3px 0;
        font-size: 10pt;
    }
    .line.indent {
        padding-left: 12px;
        width: calc(100% - 12px);
    }
    .line.bold {
        font-weight: bold;
    }
    .left {
        display: table-cell;
    }
    .right {
        display: table-cell;
        text-align: right;
        font-weight: bold;
    }
    .thick-line {
        border-bottom: 8px solid black;
    }
    .footer {
        font-size: 7pt;
        margin-top: 6px;
        line-height: 1.1;
    }
</style>
</head>
<body>
    <div class="label-container">
        <div class="header">
            <h1>Nutrition Facts</h1>
        </div>
        <div class="serving-info">
            1 serving per container<br>
            <strong>Serving size     1 Slice (186g)</strong>
        </div>
        <div class="calories-header">
            <div class="cal-left">Amount per serving<br><span style="font-size: 16pt;">Calories</span></div>
            <div class="cal-right">395</div>
        </div>
        <div class="dv-header">% Daily Value*</div>
        
        <div class="line bold">
            <div class="left">Total Fat 18.5g</div>
            <div class="right">24%</div>
        </div>
        <div class="line indent">
            <div class="left">Saturated Fat 8g</div>
            <div class="right">40%</div>
        </div>
        <div class="line indent">
            <div class="left"><em>Trans</em> Fat 0g</div>
            <div class="right"></div>
        </div>
        <div class="line bold">
            <div class="left">Cholesterol 60mg</div>
            <div class="right">20%</div>
        </div>
        <div class="line bold">
            <div class="left">Sodium 1180mg</div>
            <div class="right">51%</div>
        </div>
        <div class="line bold">
            <div class="left">Total Carbohydrate 33g</div>
            <div class="right">12%</div>
        </div>
        <div class="line indent">
            <div class="left">Dietary Fiber 2g</div>
            <div class="right">7%</div>
        </div>
        <div class="line indent">
            <div class="left">Total Sugars 2g</div>
            <div class="right"></div>
        </div>
        <div class="line indent">
            <div class="left">  Includes 0g Added Sugars</div>
            <div class="right">0%</div>
        </div>
        <div class="line bold thick-line">
            <div class="left">Protein 25g</div>
            <div class="right"></div>
        </div>
        
        <div class="footer">
            * The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice.
        </div>
    </div>
</body>
</html>
"""

with open("nutrition_label.html", "w") as f:
    f.write(html_content)

HTML(string=html_content).write_pdf("pizza_nutrition_label.pdf")


Your PDF nutrition label for one slice of the large New York Style pizza (with regular cheese, pepperoni, ham, and bacon) is ready.


[file-tag: code-generated-file-0-1779508392349134824]


This label reflects the combined totals per serving (1/6 of the pizza):



* Calories: 395

* Total Fat: 18.5g (24% DV)

* Sodium: 1,180mg (51% DV)

* Protein: 25g

---

## User

that sodium can't possibly be right!

---

## Gemini

It is definitely a "sticker shock" moment, but those numbers are accurate based on the Canadian nutrition guide you uploaded.


Pizza is a high-sodium food by nature, but this specific combination—New York Style with three different cured meats—hits the daily limit very quickly.


Why the Sodium is so High
To put it in perspective, the Daily Value (DV) for sodium is typically 2,300mg. One single slice of this pizza (1,180mg) puts you at 51% of your entire day's recommended intake.


Here is where that salt is coming from (per slice):



* The "Salty Trio": The Pepperoni (220mg), Ham (230mg), and Bacon (260mg) alone contribute 710mg.

* The Foundation: The New York Style crust (150mg), pizza sauce (100mg), and regular cheese (220mg) add another 470mg.


Sodium Comparison
To see how that 1,180mg stack up against other common high-sodium items:



* Large order of McDonald's Fries: ~400mg

* A standard bag of Potato Chips (50g): ~250mg

* One bowl of Canned Chicken Noodle Soup: ~800mg to 900mg


If you were to eat two slices, you would be at 2,360mg, which exceeds the recommended daily limit for most adults in just one sitting. If you're looking to dial it back, swapping even one of those meats for a vegetable like green peppers or mushrooms (which have 0mg sodium) makes a massive difference.

---

## User

And for one measly slice. I had 5/8 of a whole pizza, 4400mg of sodium.
My total sodium intake today was 10800mg!!
And I'm trying to be cautious of my sodium intake because i'm frequently dehydrated.
No fucking wonder I guess.
Christ. Feel so dumb eating all that pizza AND wings.
I fucking KNEW I should have put it in the fridge. I knew I wouldn't be able to resist with it across the room in the box; but I didn't put it away...

---

## Gemini

That is an intense amount of salt—nearly five times the daily recommended limit in a single day. It’s completely understandable why you’re feeling frustrated, especially when you’re already dealing with chronic dehydration.


Don't beat yourself up too much, though. Pizza is scientifically engineered to be hyper-palatable; once that box is open and the smell is in the room, the "just one more slice" reflex is incredibly hard to shut off. It’s a design feature of the food, not a personal failing.


What 10,800mg of Sodium is Doing Right Now
Sodium acts like a sponge in your body. When you have that much in your system, it pulls water out of your cells and into your bloodstream to dilute the salt.



* The Dehydration Cycle: This is exactly why you feel "frequently dehydrated." Your body is desperately using its water reserves to manage the salt spike.

* The "Pizza Hangover": You'll likely notice some significant water retention (bloating) and potentially a headache tomorrow.


Immediate Damage Control
Since the salt is already in the system, the goal now is to help your kidneys flush it out without further stressing your body:



* Hydrate, but don't "Drown": Don't try to chug a gallon of water in an hour. Drink steady, consistent amounts of plain water throughout the rest of the evening and tomorrow.

* Potassium is your Friend: Potassium helps counter the effects of sodium and encourages its excretion. If you have a banana, an avocado, or some spinach in the kitchen, eating one of those now can help balance the scales slightly.

* Avoid the "Hair of the Dog": Your body will likely crave more salt or sugar tomorrow as it tries to regulate. Try to stick to whole, unprocessed foods (like oats, eggs, or fresh fruit) for the next 24 hours to give your system a break.


The "Box Across the Room" Strategy
For next time, since you mentioned the struggle with the box being right there: the "out of sight, out of mind" trick is actually a legit psychological tactic. If you're not ready to stop but know you should, move the remaining slices into a Tupperware container and put them in the fridge before you sit down to eat the first few. Breaking that visual "cue" of the open box makes it much easier to listen to your actual hunger signals.


How are you feeling right now—just thirsty, or are you starting to feel that heavy "salt lethargy" kick in?

---

## User

I sometimes wish I could somehow be in a place where I literally can't eat the junk food that I want.
I guess I'm doing better all around, just have some bad days here and there.
I wish dominos just wasn't an option...

---

## Gemini

That "forced environment" craving is a real thing—it's essentially the desire to outsource your willpower to your surroundings so you don't have to spend "mental fuel" fighting the urge.


Living in Fort Saskatchewan probably doesn't help much when Domino's is just a few taps away on your phone and a 5-minute drive from almost anywhere in town. It’s the "frictionless" nature of it that makes it so dangerous on a bad day.


The Science of "Decision Fatigue"
You mentioned you're doing better all around, but then have these "bad days." That usually happens because willpower is a finite resource. After a long day of web development, navigating your grade 12 physics problems, or managing your nonprofit, your "executive function" is basically tapped out.


When you're mentally exhausted, your brain stops weighing long-term goals (like hydration and health) and starts prioritizing immediate rewards (salt, fat, and dopamine).


Creating Your Own "No-Option" Zone
Since you can't physically move to a desert island, you can try to build "digital friction" to make Domino's feel like less of an option:



* The "Account Delete" Move: If you have the Domino's app or a saved profile with your credit card, delete it. Having to manually type in sixteen digits every time you want a pizza is often enough "friction" to let your logical brain catch up and say, "Wait, do I really want to feel like garbage tomorrow?"

* The "6:00 PM Shutdown": Since you know the "box across the room" is your kryptonite, try the "Plate and Hide" rule. When the pizza arrives, immediately put 2 slices on a plate and put the entire box in the fridge before you take the first bite. If the box stays in the kitchen, the "visual cue" isn't sitting in your peripheral vision while you're at your desk or on the couch.

* Stock the "Emergency" Counter-Cravings: When that salt-craving hits, it’s usually your body's way of asking for a quick hit of energy. Having high-intensity (but slightly better) snacks—like really sharp aged cheddar or even some salted nuts—can sometimes satisfy that "punchy flavor" requirement you like without the 4,400mg sodium payload.


You’re doing the heavy lifting with your education and your career right now. One night of "pizza-induced salt poisoning" is a setback, sure, but it doesn't erase the progress you've made in your routine.


Since you're working through Physics and Precalc right now, do you find these "cheat days" usually happen after a particularly brutal study session?

---

## User

Yeah, that account deletion thing isn't actually as big of a barrier because I drive to pick it up, so I can just pay when I get there.
I don't crave salty food. I didn't even really want pizza until my dad suggested it.

---

## Gemini

Ah, the "Dad Variable." That changes the math entirely. It’s not an internal craving you’re fighting; it’s a social suggestion that bypasses your mental defenses because it’s external and convenient.


Since you're driving to pick it up in Fort Saskatchewan anyway, that "digital friction" definitely won't stop you. The friction has to happen at the point of decision or the point of consumption.


The "Suggestive Default" Strategy
If your dad is usually the one sparking the idea, you can try "pre-loading" an alternative. When the "should we get food?" conversation starts, having a pre-decided "Plan B" that still hits that intense flavor profile you like can help:



* The Counter-Offer: If he suggests Domino's, have a go-to alternative that is "pick-up-able" but slightly less of a sodium bomb (or at least comes in smaller controlled portions).

* The "Half-Order" Rule: Since you mentioned you didn't even really want it until it was there, you could try making a pact with him: "I'll go grab it, but let's only get a Medium/Small." It’s much harder to eat 5/8 of a pizza when the pizza itself is smaller.


Breaking the "In-Room" Visual
You nailed the problem earlier: the box across the room. Once you’re back home and that box is open in the living room or kitchen, it’s no longer about hunger—it’s about proximity.


Since you're the one driving to get it, you actually have the "First Possession" advantage:



* The Kitchen Transfer: The second you walk through the door with the hot box, put it on the counter.

* Plate it immediately: Put your slices on a plate.

* The Box Lockdown: Put the box in the fridge or a different room before you sit down to eat.


If you have to stand up, walk to the kitchen, and open the fridge for a "bonus" slice, your brain has enough time to realize, "I'm already at 3,000mg of sodium, maybe I'm good."


For the Dehydration
Since you're feeling it now, how are you handling the water intake? If you've got any potassium-heavy stuff in the house (bananas, potatoes, even milk), having a bit of that now might take the edge off that "salt-parched" feeling before you head to bed.


Are you finding that these "suggested" meals usually happen on nights when you're both just too wiped to cook?

---

## User

people whose noses can be pushed in flat

---

## Gemini

This specific physical trait—where a person can push the tip of their nose completely flat against their face because it lacks a rigid nasal bone or sturdy cartilage bridge—is a hallmark feature of Binder's syndrome (also known as maxillonasal dysplasia).


Binder's Syndrome
This is a rare congenital condition characterized by the underdevelopment (hypoplasia) of the nasal bone and the anterior nasal spine (the bony area right under the nose). Because the underlying skeletal support is missing or significantly reduced:



* The nose has a flattened, shortened appearance.

* The nasal tip can easily be compressed or pushed inward flat against the face.

* The upper lip may tilt inward, altering the profile of the face.



Other Potential Causes
Outside of Binder's syndrome, a nose that can be pressed entirely flat is typically the result of structural loss due to injury, severe inflammation, or surgical history:



* Severe Nasal Trauma (Boxer's Nose): Repeated, severe fractures to the nasal septum can destroy the cartilaginous support structure. When the cartilage collapses entirely, it results in a "saddle nose" deformity, where the middle bridge sinks, and the tip loses its structural integrity.

* Saddle Nose Deformity (Non-Traumatic): This structural collapse can also happen due to conditions that destroy nasal cartilage, such as granulomatosis with polyangiitis (GPA), advanced relapsing polychondritis, or severe infections.

* Total Septal Hematoma or Abscess: If an injury causes blood or pus to collect under the septal lining and it goes untreated, the cartilage loses its blood supply, dies (necrosis), and dissolves, leaving the nose without its central support column.

* Hypermobility Syndromes: Conditions like Ehlers-Danlos Syndrome (EDS) affect connective tissues. While it doesn't eliminate the nasal bone, extremely lax cartilage can sometimes allow the nose to bend or flatten much further than normal.

---

