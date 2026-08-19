---
title: "Ideal Thrust-to-Weight Ratios by Application"
date: "2026-08-07"
conversation_id: "b583dea6d11eadc8"
source: "antigravity"
---

# Ideal Thrust-to-Weight Ratios by Application

## User

[2026-08-07 04:18 MDT-6] [context to this point is *] ok I get what you're saying, but I literally have ONE engine to choose from. So I think if I use thrust limiter, the VAB shows me a new TWR, but really all I'm doing is limiting my control. And in fact, it sounds like it's most efficient operating at 100% anyway, so we just have to carefully manage our in-flight TWR with throttling in-flight, and I'm happy to do that, but I want to know the in-flight TWR values you recommend for each stage

---

## Assistant

You are exactly right about being early in the tech tree. If you only have one liquid engine available (like the LV-T30 Reliant or LV-T45 Swivel), you are stuck with its mass. You can’t play the "design TWR" optimization game yet by swapping to a smaller vacuum engine.

You are also 100% correct about the thrust limiter in the VAB: limiting a liquid engine's thrust in the VAB is pointless. You are still hauling the full weight of the heavy engine into space, but artificially castrating its power.

Here is the most important thing about in-flight TWR: **You should not be trying to hold a specific TWR number during flight.**

Because your rocket is constantly burning fuel, it is constantly getting lighter. If you run your engine at 100%, your TWR *must* climb. If you try to hold a specific TWR (like keeping it at 1.5), you will be forced to constantly throttle down as you fly, which throws you right back into the gravity trap that ruined your last launch.

Instead of managing the *number*, you just manage the *rocket*. Here are the actual in-flight TWR values you will see with this specific build, and how you should be throttling:

Stage 4: Pad Liftoff (Lower SRBs)

**Expected In-Flight TWR:** Starts at **1.32**, climbs to around **2.5+** right before they burn out.

**Throttle Action:** You have no throttle control over solid boosters anyway. Just pitch slightly East (5 to 10 degrees) and let them burn.

Stage 3: Mid-Ascent (Upper SRBs)

**Expected In-Flight TWR:** Starts at **1.50**, climbs to **3.0+**.

**Throttle Action:** Still solid boosters, so no throttle control. By this point, you should be pitched to about 45 degrees. The air is thinning out, so a high TWR here is great for punching through the upper atmosphere.

Stage 1: Liquid Core Engine

**Expected In-Flight TWR:** Starts at **2.49**, will rapidly climb past **4.0+** as the tank empties.

**Throttle Action:** **100% Throttle.** Do not throttle down. You are above 30 km now. Pitch down to 10–20 degrees above the horizon.

**When to throttle:** The *only* time you pull the throttle back here is when your Apoapsis hits 80 km. Then you drop it instantly to **0%**.

The Coast and Circularization

**Expected In-Flight TWR:** **Max Available**.

**Throttle Action:** When you reach the peak of your arc (Apoapsis) in space, you want to blast your engine at **100%** again to circularize the orbit. You want that burn to be as short and explosive as possible so it happens precisely at the Apoapsis node.

**The TL;DR for your flight:** Never look at the in-flight TWR readout. Just leave the throttle at 100% until your Apoapsis hits 80 km, then cut it to 0%.

---

## User

[2026-08-07 04:29 MDT-6] [context to this point is 9452] Fuck!

Any idea what went wrong?

---

## Assistant

Oh man, I feel your pain. This is a classic Kerbal rite of passage. You actually did almost everything perfectly, but you fell victim to the most punishing navigational trap in the game.

Look at the very bottom of the Navball in `image_45135c.jpg`. Your heading (HDG) says **270°**.

**You launched West instead of East.**

Here is exactly why that drained your fuel tanks before you could reach orbit:

The Planetary Rotation Penalty

Just like Earth, Kerbin rotates to the East. When your rocket is sitting on the launchpad, it is already moving Eastward at about **174 m/s** just from the planet spinning underneath it.

**Launching East (Heading 90°):** You get that 174 m/s of velocity for free. You just need to build on top of it to reach the ~2,200 m/s required for orbit.

**Launching West (Heading 270°):** You have to spend 174 m/s of your fuel just to cancel out the planet's rotation, and *then* build up your 2,200 m/s in the other direction.

Going West essentially slaps a **~350 m/s penalty** on your fuel budget. Because your rocket was perfectly engineered with 3,512 m/s of total Δv, you had just enough fuel to make it going East, but not enough to fight the planet's rotation going West. You ran out of fuel at 2,195 m/s—agonizingly close to a stable orbit, but falling just short!

The Fix for the Next Flight

Your throttle management was likely spot-on this time since you made it that high and fast before running dry.

When you launch again, just make sure when you start your gravity turn, you tap **`D`** to pitch your nose toward the **90° line** on the Navball, rather than tapping **`A`** to go toward 270°. You will absolutely make orbit with fuel to spare!

---

## User

[2026-08-07 04:36 MDT-6] [context to this point is 10012] omg! That's why you said to go East!

Fuckkkk. Well I got close!

I fucked up by not waiting till apoapsis

I think I wasted too much going from about 60% on that liquid engine to full blast when I got to 30km based on your "Max Available"...

My apoapsis was 550km, so I'm sure I could have made it to orbit, right?

---

## Assistant

Haha, exactly! Launching West is the ultimate sneaky Kerbal trap. But you are 100% correct in your realization: **you absolutely had enough fuel to make it to orbit.**

Looking at `image_450855.jpg`, you built a massive, highly elliptical suborbital arc. Pushing your Apoapsis all the way out to 550 km is exactly what drained the rest of your circularization fuel!

Here is the breakdown of where the fuel went and how close you actually were:

The 550 km Overshoot

When I said "Max Available" at 30 km, you were right to throttle up to 100%. The fatal error was *staying* at 100% past your target.

**The Target:** You only needed to push that Apoapsis to 80 km.

**The Drain:** Pumping an Apoapsis from 80 km all the way up to 550 km takes several hundred m/s of Delta-v.

Because you didn't hit **`X`** (cut throttle) the exact moment your Apoapsis crossed the 80 km mark, your engine just kept chewing through your reserve fuel to throw you deeper into space, leaving you with nothing to circularize once you got there.

You Had the Delta-v

Even with the ~350 m/s penalty from launching West, your rocket had enough juice to survive the mistake. If you had cut the throttle at an 80 km Apoapsis, you would have coasted up to space with a very healthy amount of fuel left in that liquid stage.

Once you reached that 80 km peak, you would have pointed Prograde, blasted the engine again, and that remaining fuel would have easily bridged the gap to pull your Periapsis up and out of the atmosphere.

You've got the build and you've got the ascent profile down. For the next run, it all comes down to four steps:

Tap **`D`** (East / 90°) for the gravity turn.

Full blast in the upper atmosphere.

Stare at the Map View and **kill the engine exactly at 80 km Ap**.

Coast to the top, point Prograde, and burn to circularize!

---

## User

[2026-08-07 04:37 MDT-6] [context to this point is 10598] Oh!

I'm so early in career mode I'm not used to not being able to see the markers... idk when apoapsis is at 80km really

---

## Assistant

Ah, that makes total sense! In early career mode, before you upgrade the **Tracking Station** and **Mission Control**, you don't have maneuver nodes or patched conics, which makes planning burns feel like flying blind.

Fortunately, you can still track your exact Apoapsis height in real-time using two quick stock tricks:

1. Pin the Apoapsis Marker in Map View

When you hit **`M`** to open the Map View, you can lock the readout on screen so you don't have to keep hovering over it while throttling:

Switch to **Map View (`M`)**.

Find the **`Ap`** marker on your gray trajectory curve.

**Left-click on the `Ap` marker.**

The altitude box will "pin" open, showing you the exact number live as it rises.

Watch that number climb while burning, and hit **`X`** the second it reaches **80,000 m (80 km)**.

2. Use the In-Flight Telemetry Panel (Bottom-Left)

If you are running a recent version of KSP, you don't even need to switch to Map View to see your Apoapsis:

On the main flight screen, look at the bottom-left corner (near your staging list and velocity display).

Click the small **Orbital Telemetry icon** (it looks like a small planet with an orbit around it).

This opens a live readout on your HUD that shows your current **Apoapsis (Ap)** and **Periapsis (Pe)** altitudes, along with `Time to Apoapsis`.

Visual Cues for Space

If you ever get distracted during a burn:

**70 km** is the absolute edge of Kerbin's atmosphere.

The moment you cross 70 km, the sky instantly turns pitch black, the wind noise cuts out completely, and the altimeter bar at the top of the screen turns blue/black.

If your engine is still firing when the sky turns completely black, your Apoapsis is already well out in space! Pinning that `Ap` node in Map view or opening the bottom-left telemetry tab will keep you right on target for 80 km.

---

## User

[2026-08-07 04:45 MDT-6] [context to this point is 11177] god damn it.

Ok when do I have go to 80˚ heading in terms of altitude on launch?

---

## Assistant

To make sure we're on the exact same page with the Navball:

**Heading:** The compass degree at the bottom (90
∘
 is **East**).

**Pitch:** The white ladder lines (90
∘
 is **Straight Up**, 80
∘
 is a **10
∘
 tilt** off vertical).

You want to pitch over to the **80
∘
 pitch line** (pointing East toward heading 90
∘
) at **1.0 km−1.5 km altitude** (or as soon as your speed hits about **100 m/s**).

The Step-by-Step Pitch Schedule

Here is the exact pitch ladder angle you should match to your altitude during the launch:

Altitude	Target Pitch Angle	Action on Navball
**0−1.5 km**	**90
∘** (Straight Up)	Fly straight up. Reach ∼100 m/s.
**1.5 km**	**80
∘**	Tap **`D`** to pitch 10
∘
 East (toward 90
∘
 heading).
**5 km**	**60
∘
−70
∘**	Let the nose gradually fall East.
**10−15 km**	**45
∘**	You should be halfway between vertical and the horizon.
**30 km**	**20
∘
−30
∘**	Air is thin; lean heavily into horizontal acceleration.
**45 km+**	**10
∘
−15
∘**	Point almost flat to the horizon until **Ap hits 80 km**, then hit **`X`**.
Quick Launch Sequence Checklist

Throttle **100%**, launch.

At **1.5 km**, tap **`D`** down to the **80
∘
 line**.

Set SAS to **Prograde** (if unlocked) or manually follow the prograde marker as it drifts down.

Pin your **Apoapsis readout** (`Ap`) in Map view or open the bottom-left telemetry tab.

Hit **`X`** the instant `Ap` reaches **80,000 m**.

---

## User

[2026-08-07 04:50 MDT-6] [context to this point is 11613] When I get to apoapsis, should I point directly east? Or just on the prograde marker?

---

## Assistant

Point **directly on the Prograde marker**.

First off: look at that readout—**81.24 km Apoapsis locked**, and **1,503 m/s** of fuel left in Stage 1! You nailed the MECO cut-off. You are in prime position to reach orbit.

Why the Prograde Marker?

**Prograde is your vector of motion:** It shows the exact direction your rocket is traveling through space.

**Maximizing Efficiency:** Burning directly on Prograde puts 100% of your engine thrust into expanding the opposite side of your orbit (raising your Periapsis) without wasting fuel or tilting your orbital plane.

**They're almost the same thing anyway:** Because you launched East, your Prograde marker will naturally sit right on the **90
∘
 East line** at **0
∘
 pitch (horizon)** once you coast up to Apoapsis.

Final Steps to Lock In Orbit

**Coast to Space:** Leave throttle at 0% and let your rocket coast past 70 km out of Kerbin's atmosphere.

**Align:** Rotate your rocket so your nose is pointed **dead-center on the green Prograde marker**.

**The Burn:** As you approach Apoapsis (around 10–15 seconds before hitting the peak):

Throttle up to **100%**.

Watch your **PERIAPSIS** readout in that bottom-left box climb out of the negative numbers.

**Shutdown:** The second Periapsis crosses **70,000 m (70 km)**, hit **`X`** to cut engines.

Congratulations on your first stable Low Kerbin Orbit!

---

## User

[2026-08-07 04:53 MDT-6] [context to this point is 12044] god damn it. ap/per: 265km/14km

And I'm really focusing here lol

---

## Assistant

Don't hit restart—**this flight is 100% salvageable right now!**

You didn't fail; you just accidentally pushed your peak higher! You are currently sitting on a suborbital arc that peaks at **265 km**, and your craft is climbing out of the atmosphere toward it.

Why did Apoapsis jump to 265 km?

If you start burning Prograde **before** reaching Apoapsis while you are still climbing, your engine pushes the peak of your trajectory *further away* instead of pulling the bottom of your orbit up.

Because you started the burn a little early, your engine kept pumping energy into raising your Apoapsis (81 km→265 km) while Periapsis only made it to 14 km.

How to Save It Right Now (In-Flight)

You don't need to revert to launch. Just do this:

**Cut Throttle (`X`):** Make sure your engine is completely off (0% throttle).

**Coast to the NEW Apoapsis:** Let your rocket coast all the way up out of the atmosphere toward your new 265 km peak.

**Point Prograde:** Lock SAS to **Prograde**.

**Burn at 265 km:** As you approach the 265 km mark (about 15 seconds before reaching the peak), slam the throttle to **100%**.

**Watch Periapsis:** Watch your **Periapsis** number climb from 14 km→70 km+.

**Cut Engines (`X`):** The instant Periapsis crosses 70 km, kill the engine!

That’s it! You’ll end up in a slightly higher orbit (265 km×80 km), but **it will still be a completely valid, stable orbit!**

---

## User

[2026-08-07 04:54 MDT-6] [context to this point is 12496] I meant to say: I'm out of fuel! so it's not savable unless I can send a rescue mission. Even then, I don't think it's possible to refuel these early ships?

---

## Assistant

Ah, got it! That changes things—but there is actually **huge good news** here: **Your Kerbal is not stranded!**

Because your Periapsis is down at **14 km**, Kerbin's atmosphere is going to do all the work for you. 14 km is deep inside the thick lower air.

Why You Don't Need a Rescue Mission

**Aerobraking will bring you home:** Every time your craft passes through that 14 km Periapsis, atmospheric drag will scrub off your velocity. Because your orbit is so wide, you will re-enter the atmosphere on this pass, slow down naturally, and fall back to the surface.

**You get to keep your Science and Funds:** You didn't lose the craft or the Kerbal. Once you land safely, you can hit **Recover Vessel** at the top of the screen to claim all the science points and funds from reaching space!

Can You Refuel / Rescue Ships Early On?

**Refueling:** No. Transferring fuel between ships requires **Docking Ports** and an upgraded **Research & Development facility** to allow resource transfer. You won't be doing in-space refueling for a while.

**How Rescue Missions Work Early Game:** Instead of refueling, early rescue missions involve launching an uncrewed ship (or a ship with a 2-pod capsule with one empty seat), flying close to the stranded craft, and having the Kerbal **EVA spacewalk** across open space from the old pod into the new one. *(This requires upgrading the Astronaut Complex to allow EVAs outside of Kerbin's atmosphere).*

What to Do Right Now

Since you are out of fuel and heading back down:

**Orient for Re-entry:** Point your craft **Retrograde** (so the bottom heatshield/engine takes the heat of re-entry).

**Decouple (if applicable):** If your command pod has a decoupler, drop the empty liquid fuel tank and engine so only the light capsule re-enters.

**Check Parachutes:** Make sure your parachutes are staged properly in **Stage 0**.

**Ride It Out:** Let the atmosphere slow you down, deploy chutes below 2 km, land safely, and recover the craft!

The Takeaway

You successfully built a rocket with enough power to reach space, executed the gravity turn, and proved your staging works. The *only* thing that stopped you was starting the orbital burn too early.

Land this ship, cash in the science, and on your very next attempt, you'll lock in that orbit!

---

## User

[2026-08-07 04:55 MDT-6] [context to this point is 13222] so does it count as reaching orbit as far as the mission and science etc is considered?

---

## Assistant

**Short answer:** No for contracts, but **yes for science!**

Here is how KSP splits the difference under the hood:

1. Contracts & World's First Milestones: ❌ No

To trigger the "Achieve Orbit around Kerbin" contract or World's First milestone, KSP explicitly checks for one condition: **your Periapsis must be above 70 km**.

Because your Periapsis was 14 km, the game code tagged your flight situation as **`SUB_ORBITAL`** rather than **`ORBITING`**. You won't get the contract payout or the orbit achievement notification on this run.

2. Science Points & Recovery:  Yes!

Science isn't tied to your orbit state; it’s tied purely to your **current altitude**.

**Space Science:** Any Crew Reports, EVA Reports, Mystery Goo, or Temperature readings you took while your craft was above 70 km count as **"In Space Low"** (70 km – 250 km) or **"In Space High"** (>250 km).

**Recovery Bonus:** When you recover the capsule after landing, you will get 100% of the science value for those space experiments, plus the milestone funds for reaching high altitude/space.

Summary

You got all the juicy space science and proved your launch vehicle works! You just need one clean run with a Periapsis over 70 km to claim the official contract money.

---

## User

[2026-08-07 05:25 MDT-6] [context to this point is 13621] I want to land, but I keep burning up on re-entry. I lowered my periapsis to 20km, I thought that was good?

---

## Assistant

That is actually the counter-intuitive trap of re-entry in KSP!

A **20 km Periapsis** feels like it should be safe because it guarantees you hit the air, but from a high peak like 265 km, a 20 km Periapsis actually makes re-entry **much harsher**.

Plunging down to 20 km at over 2,000 m/s forces your rocket into a super steep dive straight into the thickest, densest part of the atmosphere. The air doesn't have enough time to slow you down gradually, so the friction and dynamic pressure spike instantly, melting your ship.

The Sweet Spot: 45 km−55 km Periapsis

To survive high-speed re-entry, you want a **shallow, gentle entry profile**:

**Target Periapsis:** Set your Periapsis between **45 km and 55 km**.

**Why it works:** At 45 km−55 km, the air is very thin. It acts like a soft brake, letting you skim through the upper atmosphere to bleed off extreme kinetic energy gently over a long distance without generating lethal heat.

The Safe Re-entry Checklist

If you are loading a quicksave to try the landing again, follow these exact steps:

1. Strip the Craft (Ditch the Engine)

If you have a decoupler below your pod, **stage it and drop the empty fuel tank and heavy engine** before entering the atmosphere (>70 km).

Heavy, top-heavy, or long rockets flip easily during re-entry. You want to re-enter with **only the command pod** (and heat shield).

2. Lock SAS to Retrograde

Point your pod's heat shield (the flat bottom) directly into the wind by setting SAS to **Retrograde**.

The heat shield is designed to absorb thousands of degrees of friction, whereas the nose/parachute will explode instantly if exposed to direct heat.

3. Hold Your Orientation

Do **not** touch the controls once heat effects start glowing. Let SAS hold the heat shield into the wind.

The pod will naturally want to stay bottom-first because its heavy base acts like the head of a badminton shuttlecock.

4. Wait for Parachutes

Do **not** deploy parachutes during the fiery plasma phase.

Wait until your speed drops below **250 m/s** and altitude is below **2 km**. The parachute icon in your staging stack will turn from red/unsafe to clear/safe.

If You have zero RCS/Monopropellant and no fuel left to raise Pe:

If your Periapsis is locked at 20 km and you have zero fuel left to change it:

Ditch everything except the pod immediately.

Hold Retrograde.

If you have a heat shield attached to the pod, ensure its ablator is full. The bare pod alone can survive a 20 km plunge *if* it drops all extra mass and stays locked dead-center Retrograde the entire time!

---
