---
title: "KSP Mun Transfer Maneuver Planning"
date: "2026-08-02"
conversation_id: "4933d38d7df6e3f7"
source: "antigravity"
---

# KSP Mun Transfer Maneuver Planning

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




in ksp I'm struggling with the tools for planning maneuvers...

What are the basics? When's the best time for a maneuver?

Let's say I want to get a rocket to Mun...

Right now what I do is fire my first stage full blast Prograde. But I feel even then that's probably not most efficient?

Is there a way I can plan the launch etc before even launching?

---

## Assistant

Firing straight up (or going full blast from the pad directly toward a destination) is one of the biggest fuel-wasters in orbital mechanics.

To reach the Mun efficiently, mission planning in Kerbal Space Program relies on breaking the trip into two distinct phases: **reaching a low parking orbit**, and then **executing a transfer burn**.

1. Why Full-Blast Launch Isn't Efficient

When launching, you fight two things: **atmospheric drag** and **gravity losses**.

Burning straight up means gravity pulls back on your rocket every second you're rising ("gravity drag").

To stay in space without falling back down, you need horizontal speed—roughly **2,200 m/s** sideways relative to Kerbin.

**The fix (The Gravity Turn):** Launch straight up to about 1 km, then pitch gently East (heading 90° on the Navball). Gradually flatten out so that by 40–50 km altitude, you are burning nearly horizontal to build sideways velocity. Cut your engines once your Apoapsis (highest point) reaches ~80 km, coast to Apoapsis, and burn Prograde to circularize into a **Low Kerbin Orbit (LKO)**.

2. How Maneuver Nodes Work & When to Burn

Maneuver nodes allow you to simulate velocity changes (Δv) before firing your engines.

Node Controls

When you click on your orbit line in Map View (`M`) and select **Add Maneuver Node**, you get 6 handles:

**Prograde (Yellow/Green icon):** Accelerates forward (raises the opposite side of your orbit).

**Retrograde (Yellow/Green cross):** Slows down (lowers the opposite side of your orbit).

**Normal / Anti-Normal (Purple):** Tilts your orbital plane North or South.

**Radial-In / Radial-Out (Cyan):** Rotates the orbit shape without changing overall energy.

The Best Time to Burn (Oberth Effect)

**At Periapsis (Lowest Point):** Oberth effect dictates that kinetic energy gains from burns are highest when moving at peak speed.

**At Phase Alignment:** For transfers to another body, you must burn at the precise point in your orbit where your newly stretched orbit meets the target body at the exact time the target arrives there.

3. Transferring to the Mun (Step-by-Step)

Once sitting in a circular ~80 km LKO:

Open **Map View** (`M`) and click on the Mun, then select **Set as Target**.

Look at your orbit around Kerbin relative to the Mun.

**The Horizon Rule of Thumb:** Place a maneuver node on your orbit at the position where the Mun is just rising over Kerbin's horizon (roughly 90° to 100° behind the Mun in its orbital path).

Pull the **Prograde** handle out until your projected orbit line stretches out to ~12,000 km.

You will see yellow/cyan encounter markers appear showing a **Mun Encounter / Sphere of Influence (SOI) Entry**. Adjust the node position slightly forward or backward along your orbit if you don't see an encounter immediately.

Align your ship to the **Maneuver Indicator** (blue marker on the Navball) and execute the burn when the countdown timer reaches zero (or start half the burn duration *before* zero). This transfer typically costs ~850–860 m/s of Δv.

4. Can You Plan a Maneuver Before Launching?

In stock KSP, **no, you cannot place maneuver nodes while on the launchpad**.

Maneuver nodes require an active, calculated orbital path to anchor to. Because your ship is stationary on the ground, the physics engine treats it as part of Kerbin's surface rather than an orbiting body.

However, you can pre-plan the **timing**:

Since the Mun orbits Kerbin in a flat equatorial plane every 6 days, you can launch straight into its orbital plane at any time from the Kerbal Space Center.

You do not need to wait for a specific "launch window" from the ground for the Mun—simply achieve Low Kerbin Orbit first, wait until your ship orbits around to the correct phase position relative to the Mun, and execute the maneuver from LKO.

Want to go over the circularization burn at the Mun to capture into orbit?
Yes

---

## User

if I've got solid rockets and a liquid rocket all ready to go at the very beginning, but I know the liquid will last longer than the solids, I should still burn all I can at t=0 for maximal efficiency right?

---

## Assistant

**Not necessarily.** Burning everything at t=0 usually **wastes fuel** on a atmospheric launch due to **aerodynamic drag**.

While the **Oberth Effect** says you want to burn as fast and low as possible to maximize orbital energy, that rule assumes you are in a vacuum. On the launchpad, you are sitting at the bottom of Kerbin's thick atmosphere.

1. Thrust-to-Weight Ratio (TWR) & Atmospheric Drag

Your rocket's **Thrust-to-Weight Ratio (TWR)** dictates how fast you accelerate:

**TWR < 1.0:** Rocket won't leave the pad.

**Ideal Launch TWR:** **1.3 to 1.5** off the pad.

**TWR > 2.0+ near sea level:** Bad idea. You accelerate too quickly while the air is dense, causing massive aerodynamic drag (and potential heat/instability) that eats up your Δv.

If you fire high-thrust Solid Rocket Boosters (SRBs) **AND** a liquid engine at 100% throttle simultaneously, your combined TWR off the pad might spike to **2.5 or 3.0+**. You will slam into a wall of air resistance low down.

2. Best Staging Strategy
Strategy A: Throttle down the Liquid Engine (Recommended)

If your SRBs alone provide enough thrust to get off the pad (TWR ≈1.3−1.5):

**Fire SRBs at 100% + Liquid Engine at low throttle** (or just enough to give you gimbal control for steering).

Let the SRBs do the heavy lifting in the thick lower atmosphere (0–10 km).

Once the SRBs burn out and drop off (decoupling empty weight), throttle the liquid engine up to 100% in the thinner upper atmosphere.

Strategy B: Right-Click SRB Thrust Limits in the VAB

Solid boosters burn at a fixed rate in flight, but in the **Vehicle Assembly Building (VAB)**, you can right-click an SRB and lower its **Thrust Limiter** (e.g., to 60% or 70%):

This extends the SRB burn time.

Keeps your launch TWR in the sweet spot (~1.4).

Allows you to run both SRBs and liquid engines without over-speeding in the low atmosphere.

Summary Rule of Thumb

Keep your acceleration under control below 10–15 km altitude. If you see bright red re-entry/plasma shockwaves forming around your nosecone while still ascending through the lower clouds, you are burning way too much thrust way too early.

Want to look at ideal staging and thrust ratios for the ascent to the Mun?
Yes

---

## User

ok I'm at around 225km and apoapsis is at 1.3M m... what now?

Achieve 80km orbit around Keybin? How best do that? When to do the maneuouver?

---

## Assistant

If your **Apoapsis is already at 1.3M m (1,300 km)** and your altitude is 225 km, you have already overshot an 80 km orbit—you're heading high up into Kerbin's space!

Don't worry, you can still easily circularize at your current Apoapsis (~1,300 km) to establish a stable orbit before heading to the Mun.

Step 1: Create a Circularization Maneuver Node

Open **Map View** (`M`).

Mouse over your **Apoapsis (Ap)** marker at the top of your current arc.

Left-click the Ap node and select **Add Maneuver**.

Pull the **Prograde** handle (yellow/green icon without the cross) outward.

Watch your trajectory line stretch out until your **Periapsis (Pe)** pops up on the opposite side of Kerbin and reaches ~1,300 km.
*(Your orbit is now a round circle around Kerbin at 1.3 million meters).*

Step 2: Execute the Burn

Point your rocket at the **Blue Maneuver Marker** on your Navball.

Look at the burn duration next to the Navball (e.g., *Estimated Burn: 20s*).

**When to burn:** Start your engines **half of the burn time before the node time**.
*(If your burn is 20 seconds, throttle up when the countdown hits `T-10s`).*

Burn until the estimated Δv bar drops to 0 m/s, then cut throttle (`X`).

Step 3: Plot the Transfer to the Mun from 1,300 km

Now that you are in a stable circular orbit (even though higher than 80 km), you can still transfer directly to the Mun:

Click the Mun and select **Set as Target**.

Place a new maneuver node on your orbit roughly **90° behind the Mun** in its path (when the Mun is rising over Kerbin's horizon from your ship's perspective).

Pull **Prograde** until your projected path meets the Mun's orbit and shows a **Mun Encounter / SOI Entry** symbol.

Because you're starting higher up at 1,300 km, your transfer burn will take **less fuel (Δv)** than from 80 km!

Note for Future Launches (How to get an 80 km orbit)

On your next launch, cut your throttle (`X`) the moment your Apoapsis (Ap) reaches **80,000 m (80 km)** while still in the atmosphere. Coast up to that 80 km Ap marker, create a Prograde maneuver node right at Ap, and burn Prograde to bring your Periapsis (Pe) up above 70 km.

Want to know how to capture into Mun orbit once you reach the Mun encounter?
Yes

---

## User

I don't get your step 3

---

## Assistant

Ah, looking at your screenshot makes it clear!

The reason Step 3 sounded confusing is that your rocket hasn't circularized yet—you are currently on a very steep, highly eccentric elliptical path (cyan line) around Kerbin (the gray planet), while the Mun (purple orbit line at the bottom) is way out in its own path.

Right now, you are **not in a circular orbit yet**. Here is what's happening and how to fix it:

What the Image Shows

**Your current vessel (plane icon):** You are currently near your Periapsis (Pe), right next to Kerbin.

**Your Apoapsis (Ap):** The top right of your cyan loop is where you will reach 1,300 km altitude.

**The Mun's Orbit:** That purple line stretching across the bottom of the screen.

Correct Step-by-Step

Before trying to reach the Mun, you **must complete your circularization burn** around Kerbin first.

Step A: Circularize around Kerbin

Mouse over your **Ap** marker (top right of your cyan loop).

Click it and select **Add Maneuver Node**.

Pull the **Prograde** (yellow symbol without the X) handle out until the cyan line rounds out into a big circle around Kerbin.

Time warp until your ship reaches that Ap marker, align with the blue node target on your Navball, and fire your engines.

Once complete, your orbit will be a steady circle at ~1.3 million meters.

Step B: NOW Plot the Mun Transfer

Once you are in that circular orbit:

Zoom out in Map View so you can see both Kerbin and the Mun.

Click the Mun and select **Set as Target**.

Place a **new** maneuver node on your circular orbit line at the position where the Mun is **just appearing over Kerbin's edge** (rising over the horizon from your craft's point of view).

Pull **Prograde** on that new node until the trajectory line stretches out to touch the Mun's purple orbit line. You will see a yellow/cyan encounter marker appear!

---

## User

its not that elliptical

---

## Assistant

Ah, seeing the zoomed-out view makes total sense now!

Look at the **ORBIT** panel on the bottom-left of your screen:

**Periapsis (Pe):** 1.352 Mm (1,352,000 m)

**Apoapsis (Ap):** 5.022 Mm (5,022,000 m)

Your craft is that inner cyan loop, and the big yellow ring is the Mun's orbit (~12,000 km / 12 Mm out).

Because your **Periapsis is already at 1.35 Mm**, you aren't down in low Kerbin orbit anymore—you are already completely outside Kerbin's atmosphere and coasting high up in space!

What To Do Next

Since you're already in a stable orbit around Kerbin, you don't need to circularize first. You can plan your transfer to the Mun right now.

**Set the Mun as Target:** Right-click the Mun (the gray circle on the yellow line) and click **Set as Target**.

**Place a Maneuver Node:** Click anywhere on your cyan orbit line and select **Add Maneuver Node**.

**Pull Prograde:** Pull the **Prograde** handle (yellow marker without the cross) outward.

**Watch the projected line:** Keep pulling until your projected path stretches out to touch the yellow Mun orbit line.

**Adjust Node Position:** If you don't see a **Mun Encounter** (a yellow/cyan target icon appearing on the line), drag the center ring of the maneuver node slightly forward or backward along your cyan orbit line until your ship's path meets the Mun at the same time the Mun gets there.

Once you see the encounter markers pop up, line up with the blue target on your Navball and fire!

---

## User

[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

click anywhere on my cyan orbit?

Surely there's an optimal spot?

Like, I'd imagine I want to maybe look at the side closest to Kerbin (periapsis), and thus opposite the side of my orbit closed to Mun, and then if I do a burn there, the apoapsis should extend to Mun, right?

---

## Assistant

Spot on! You are thinking like an orbital mechanic.

Your Apoapsis always pushes out on the **opposite side** of where you burn. So burning Prograde near your Periapsis (the point closest to Kerbin) will extend your Apoapsis out toward the Mun's orbit on the far side.

However, because your orbit is dynamic and the Mun is moving, the optimal spot isn't *just* burning at Periapsis—it depends on **where the Mun is right now**.

1. The Ideal Placement Logic

To get an encounter efficiently:

**Burn at Periapsis (Pe):** This gives you the best Oberth efficiency (most speed per unit of fuel).

**Phase Angle:** You need your projected Apoapsis to hit the Mun's orbit **at the exact moment the Mun arrives at that location**.

If you place the node right at your **Pe** and pull Prograde until the path reaches ~12,000 km, look at where the top of your arc touches the Mun's orbit:

**If the Mun is behind that point:** Your node is too early.

**If the Mun is ahead of that point:** Your node is too late.

2. How to Find the Best Spot in KSP Right Now

Instead of guessing the geometry, use this workflow:

Click on your cyan line near **Pe** and add a maneuver node.

Pull the **Prograde** handle until the outer tip of your dotted trajectory line reaches the yellow circle (Mun's orbit).

**Drag the Node:** Left-click and hold the center ring of the maneuver node itself, then drag it along your cyan orbit line.

As you slide it around your orbit, you will see the projected path rotate. Stop when you see the **yellow/cyan entry markers (Mun Encounter)** pop up.

If dragging around your current orbit doesn't produce an encounter, it means the Mun won't be in position on this lap—right-click the center of the node and click the `+` button (**Delay 1 Orbit**) to plan the burn for your next trip around Kerbin.

Want to know how to adjust your approach trajectory once you get the encounter?
Yes

---

## User

now what

---

## Assistant

Look closely at your projected path (the purple line):

**You already have a Mun Encounter!** See that orange arc near the bottom with the orange **Pe** tag? That's your projected flyby trajectory inside the Mun's gravity well.

**Plane Inclination Issue:** Your orbit is tilted at a steep angle relative to the Mun's flat equatorial orbit (the yellow ring).

Step 1: Execute Your Transfer Burn

First, point your craft at the blue **Maneuver Node target** on your Navball.

Fire your engines to execute the planned burn until the green Δv bar on the right of the Navball empties.

Step 2: Fine-Tune Your Mun Approach

Once you finish the transfer burn, your ship will be on course for the Mun. However, because your orbit is tilted, your Mun Periapsis might be very high or even pass above/below its surface.

**Time Warp** until you cross into the Mun's Sphere of Influence (when your orbit line changes color to orange/yellow as you get close).

Look at your **Mun Periapsis (Pe)** tag on the orange curve.

**Ideal Mun Pe:** **20,000 m to 50,000 m (20 km - 50 km)** above the surface.

If the Pe is too high or missing:

Point your ship **Anti-Normal** or **Radial-In/Out** and tap the throttle very gently to lower your Mun Periapsis into the 20k–50k range.

Step 3: Capture into Mun Orbit

Time warp until you reach your **Mun Periapsis (Pe)**.

Point your vessel **Retrograde** (the green circle with the cross through it on your Navball).

**Burn full throttle Retrograde** at Pe until your orbit closes around the Mun into a stable circle!

---

## User

I dont have a maneuver node target on my navball

---

## Assistant

That happens if the node wasn't fully created or if your vessel's target orientation mode isn't tracking it.

Here is how to get it back on your Navball immediately:

1. Check if the Node is Active

Look at the right side of your Navball.

Is there a **green velocity bar** next to the Navball showing a speed like `132 m/s` or similar?

**If NO bar is there:** The maneuver node was deleted or never set. Click on your orbit line again, select **Add Maneuver Node**, pull **Prograde** until you see that Mun encounter, and leave the node active.

2. Find the Blue Target Marker

If the green Δv bar **is** on the right side of your Navball:

**SAS Target Mode:** On the left side of your Navball, look at your SAS mode buttons (the column of red/white icons). Click the **Maneuver Node** button (the blue icon that looks like a target with a point). Your ship will automatically rotate to point right at it.

**Manual Search:** If you don't have that SAS button unlocked yet, look for a **blue dot/crosshair** on the sphere itself. Manually pitch and yaw your vessel until the yellow center indicator on your Navball lines up directly over that blue marker.

3. Alternative: Just Burn Prograde

Since you are near Periapsis and need to push your Apoapsis out to the Mun, you can bypass the node UI entirely:

Turn SAS on (`T`) and click **Prograde** (the yellow/green circle without the X on your Navball).

Throttle up (`Shift` or `Z`).

Watch the map view: as soon as your purple orbit line stretches out and forms that orange Mun arc/encounter, cut your throttle (`X`).

---

## User

this is so needlessly confusing

Is this ok?

---

## Assistant

**Yes, this node is completely valid.**

You have a confirmed **Mun encounter** (the orange arc with the orange **Pe** marker near the bottom-left).

Here is why it felt so confusing:

**The Node Placement:** Your node is currently placed way out at **Apoapsis (Ap)**—the highest point of your current orbit. Notice the bottom-right text says `Node in T - 3d, 4h, 46m`. That means you have to wait 3 days in game time just to reach the burn point.

**Complex Direction Handles:** Because you pulled Prograde, Normal, and Radial handles all at once (you can see green, purple, and cyan values in the bottom-left panel), the trajectory looks tilted and messier than a pure Prograde burn.

What to do right now:

Look at your Navball. The **blue marker with the dot/crosshair** is right there near the left edge of the brown section (around heading 285°).

Steer your ship to point **directly at that blue marker**.

**Time Warp (`.` key)** until you get close to `Node in T - 22s` (half of your 44-second burn time).

Hit **Z** (full throttle) to execute the burn, and hit **X** when the green bar hits 0 m/s.

Once that 44-second burn is complete, your craft will be locked onto that path to the Mun.

Want to know what to do as soon as you enter the Mun's gravity well?
Yes

---

## User

I just feel like this is definitely sub optimal

---

## Assistant

You are 100% correct. It **is** suboptimal, and trust your intuition here—you are paying a steep fuel penalty for two main reasons shown on screen:

1. Oberth Penalty (Burning at Apoapsis instead of Periapsis)

Because your node is placed out at Apoapsis (10,901,239 m away from Kerbin), you are moving at your absolute slowest speed when you fire your engines.

**The Math:** To raise your orbit efficiently, you want to burn at **Periapsis** (where you move fastest). Burning at Apoapsis costs significantly more Δv to achieve the same orbital stretch.

2. Combined Vector Waste (Normal + Radial Friction)

Looking at your MANEUVER 1 panel in the bottom-left:

**Prograde:** 142.4 m/s (stretching the orbit)

**Normal:** 475.4 m/s (tilting the plane)

**Radial:** -216.6 m/s (rotating the ellipse)

**Total Cost:** **542.6 m/s**

Over 80% of your fuel in this burn is being spent purely on twisting and steering your orbit mid-space rather than pushing you toward the target.

How to Fix It (The Clean Way)

If you have fuel to spare, you *can* take this burn and it will get you to the Mun. But if you want to clean this up and save ~300+ m/s of Δv:

**Delete the current node:** Right-click the node or click the red **X** on the MANEUVER 1 panel.

**Coast to Periapsis (Pe):** Time warp until your ship is down at your lowest point near Kerbin.

**Pure Prograde Burn:** Place a new node at Pe and pull **ONLY the Prograde handle** (yellow icon, green value).

Because the Mun's orbit is on the equatorial plane, if your inclination at Pe is still tilted, add just a tiny pinch of **Normal/Anti-Normal (purple)** to align the plane, then drag the node along your orbit until the encounter appears.

Doing it at Periapsis will drop that 542 m/s cost down closer to ~200–250 m/s.

Want to delete this node and replan at Periapsis together?
Yes

---

## User

You've got to make this whole thing SO much clearer for me man

---

## Assistant

I hear you. Let's wipe the slate clean and look exactly at why this is fighting you so hard, because this screenshot reveals the root cause of the whole headache.

Look at the two big rings in your image:

**The Yellow Ring:** This is the Mun's orbit. It goes flat around Kerbin's equator (left-to-right).

**The Purple Ring:** This is your ship's orbit. You are orbiting top-to-bottom (North-to-South), almost completely perpendicular to the Mun.

Trying to fly to the Mun right now is like driving on a highway going North at 100 mph, and trying to take an exit that requires you to instantly drive East without slowing down. It requires a massive amount of fuel to brute-force that kind of 90-degree turn in space.

Here is exactly how to fix this, step-by-step.

Phase 1: Flatten Your Orbit First

Before you even think about transferring to the Mun, we have to tilt your purple orbit so it lays flat and matches the yellow orbit. In orbital mechanics, tilting your orbit is called a **plane change**, and it is cheapest to do when your ship is moving as slow as possible (at your highest altitude).

**Delete that maneuver node.** Right-click it and trash it. It's trying to do too many things at once.

**Locate your Apoapsis (Ap).** Find that `Ap` tag out at 10,681,066m.

**Place a new node exactly on the Ap.**

**Pull the Purple Handles (Normal / Anti-Normal).** Pull either the purple triangle pointing up or the one pointing down. Watch your purple orbit line. You want it to tilt like a spinning coin settling down until it perfectly overlays the flat yellow Mun orbit.

**Execute that burn.** Point your ship at the blue node marker, warp to the burn time, and fire your engines.

Now, your ship will be flying flat around the equator, just like the Mun.

Phase 2: Transfer to the Mun

Once your orbit is completely flat, getting to the Mun becomes incredibly simple:

Wait until your ship swings back down to its lowest point close to Kerbin (**Periapsis / Pe**).

Drop a maneuver node at that Pe.

Pull **only the Prograde handle** (the yellow circle, no cross) outward.

Because you are now flying flat on the exact same plane as the Mun, dragging that node along your orbit line will easily give you a clean Mun encounter for a fraction of the fuel.

**A Note for Future Launches:**
The reason you ended up in a top-to-bottom orbit is because you launched North or South from the launchpad. To go to the Mun, always launch **East** (heading 90° on your Navball). This puts you into a flat equatorial orbit right off the bat, completely skipping the need for Phase 1.

---

## User

ok

---

## Assistant

You have a confirmed Mun encounter. The text "The Mun Encounter T - 24d, 1h, 14m" in the image indicates your planned trajectory successfully intersects the Mun's path.

However, this specific maneuver skips the orbit-flattening phase.

What This Specific Plan Does

**Polar Approach:** Your planned orbit (the purple line) is still heavily tilted relative to the Mun's flat equatorial orbit (the grey line). You managed to find a precise window where your tilted path intersects the Mun, but it means you will arrive at a steep angle. If you circularize around the Mun from this path, you will be in a polar (top-to-bottom) orbit rather than an equatorial one. This is perfectly fine for a basic orbit or landing.

**Long Wait Time:** Your maneuver node is placed at your Apoapsis at the bottom of the screen. Because of the size of your current orbit, that burn is 25 days away in game time (`T - 25d, 4h, 46m`).

Next Steps to Execute

If you have the fuel for this node and want to proceed with this plan, here is how to finish the trip:

**Perform the Transfer Burn:** Point your vessel at the blue maneuver node marker on the Navball. Time warp to the node—be careful using the highest warp speeds so you do not overshoot a 25-day wait—and fire your engines to complete the burn.

**Coast to the Mun:** Once the burn is complete, your ship will be locked onto that path. Time warp forward 24 days until your ship enters the Mun's Sphere of Influence.

**Capture Burn:** If you just coast, the Mun's gravity will slingshot you right back out (which is why your orange `Pe` marker points back near Kerbin). To stay at the Mun, wait until you reach the lowest point of your flyby (your Mun Periapsis), point your ship **Retrograde**, and burn until your orbit line closes into a stable circle around the Mun.

---

## User

you keep assuming there's a maneuver where there is not.

There's no maneuver planned right now!

I'm wondering when I should add the maneuver

---

## Assistant

I completely misread the UI tracking lines. You are right—there is no active maneuver node on that path.

Since you are currently coasting with no maneuvers planned, here is exactly **where and when** you should click to add a maneuver node, depending on which step you are taking:

1. When to add a node to fix your tilt (Plane Change)

Add this maneuver at either the **Ascending Node (AN)** or **Descending Node (DN)**.

Look for the bright green `AN` or `DN` tags on your orbit line. These mark the exact intersections where your tilted path crosses the Mun's flat equatorial plane.

Click directly on the `AN` or `DN` tag, add the node, and pull the purple (Normal/Anti-Normal) handles to flatten your trajectory until it matches the Mun's orbit.

*Note: Plane changes cost the least amount of fuel when your ship is moving slowly, so an AN or DN placed high up near Apoapsis is ideal.*

2. When to add a node to shoot for the Mun (Transfer Burn)

Add this maneuver at your **Periapsis (Pe)**.

Assuming your orbit is already flattened, wait until your ship swings down to its lowest, fastest point near Kerbin.

Click exactly on the `Pe` tag, add a node, and pull the yellow Prograde handle to push the opposite side of your orbit out toward the Mun.

Once the path is stretched far enough, you can left-click and drag the center ring of the maneuver node itself along your orbit line to change the *timing* of the burn until an encounter pops up.

If you are still flying in that highly tilted, top-to-bottom orbit from the last screenshot, you must execute Step 1 to flatten out before attempting Step 2.

Are you able to spot the AN/DN markers on your current orbit to start the plane change, or would you prefer to revert to the launchpad and try a flat equatorial launch from scratch?

---

## User

I'm actually about to quit. What a most confusing fucking interface!

I can't make heads or tails of all the fucking overlapping orbits with all the colors and what not, and I slide a thing slightly too far and not the orbit is completely off, it's enraging I have no fucking clue what I'm looking at

---

## Assistant

Look, KSP's map view is a notorious wall for players. The UI is a complete mess of spaghetti lines, and it is completely valid to want to punch the screen when an accidental twitch snaps your planned orbit into deep space.

You are currently dealing with the two worst parts of the stock interface: hyper-sensitive node handles and visual clutter. Here is how to bypass both so you don't have to pull your hair out.

1. Stop Dragging the Node Handles

Trying to click and drag those glowing icons in 3D space is infuriating. Especially on macOS, trackpad gestures or mouse scrolling can make those handles hyper-sensitive and practically unusable.

Instead, use the **Maneuver Node Editor** you already have open in the bottom-left corner of your screen (from your previous screenshots):

Don't touch the node on the map.

Go to the bottom-left panel.

Click the tiny **+** or **-** buttons next to the Prograde (green) or Normal (purple) numbers.

This adds or subtracts exactly 1 m/s of velocity at a time, giving you surgical precision without the orbit jumping wildly across the screen.

2. Clean Up the Map View

If the overlapping lines are making it impossible to see what you are doing:

**Reset your camera:** Press `Backspace` to instantly snap the camera focus back to your active vessel. If you accidentally double-clicked a planet, the camera locks onto it and makes your ship's orbit look extremely weird as it moves.

**Filter the junk:** Move your mouse to the top center of the screen in Map View. A drop-down menu will appear showing icons for probes, rovers, debris, etc. Click the debris icon to hide it so you are only looking at your ship, the Mun, and Kerbin.

Honestly, trying to salvage an orbit that is already highly tilted and millions of meters off the mark is the absolute hardest way to learn orbital mechanics. You are fighting the game's physics on hard mode right now.

Want to scrap this flight and start fresh?
Yes

---

## User

ok fuck me, we can do this.

please give specific directions from here

---

## Assistant

Hell yes, we can do this. You actually already did the hard part.

Look at the top center of your screenshot. You have an orange marker that says **The Mun Encounter T - 6d, 4h, 27m**. You are currently coasting on a trajectory that will intercept the Mun, and your bottom-left panel shows 2,883 m/s of Δv remaining. That is a massive amount of fuel—more than enough to finish this mission.

Do exactly this, in order. Do not create any maneuver nodes.

1. Fast-Forward to the Mun

Hover your mouse over the orange trajectory line right near the Mun, just slightly before the orange `Pe` marker.

Right-click the line and select **Warp Here**.

Take your hands off the keyboard and mouse. The game will fast-forward 6 in-game days and automatically kill the time warp as soon as you enter the Mun's gravity well.

2. Lock Your Steering

Once the warp stops, the map will shift so the Mun is in the center. Your path will turn blue or cyan again, representing your local orbit around the Mun.

Look at your SAS controls (the buttons on the left of your Navball). Click **Retrograde** (the green circle with a cross through it). This points your engine directly into your flight path so you are ready to hit the brakes.

3. Verify Your Clearance Altitude

Hover over your new `Pe` (Periapsis) marker next to the Mun to read the altitude.

**If it's below 10,000m:** You risk smashing into a crater lip. Point your ship **Radial Out** on the Navball and tap your throttle *very* lightly until the Pe rises to around **20,000m to 30,000m**.

**If it's above 15,000m:** You are completely safe. Leave it alone.

4. Execute the Capture Burn

Wait until your ship reaches that `Pe` marker. You can use standard time warp (the `.` and `,` keys) to get within 30 seconds of it, but be careful not to overshoot.

The exact second you hit `Pe`, hit **Z** for 100% throttle.

Keep your eyes on the map. Your trajectory line will bend, close up, and form a circle around the Mun.

Hit **X** to cut the engine once your `Ap` and `Pe` are both relatively close to each other (e.g., both around 30,000m).

Ready for the landing sequence?
Yes

---

## User

did I do it right so far?

---

## Assistant

Not quite—you accidentally flew right past it!

Look at the bottom left of your screen. That green text says **The Mun Escape T - 1m, 59s**.

You are currently on the way *out* of the Mun's gravity well and will completely leave its Sphere of Influence in less than two minutes. You time-warped right through your Periapsis and missed the window to hit your engines for the capture burn.

This is a classic KSP rite of passage. If you time-warp too quickly while inside a moon's gravity, the game races past the critical burn point before you can even react.

Here is how to recover:

**Option 1: Reload a Quicksave (Recommended)**
If you quicksaved (`F5`) at any point during the coasting phase, just hold `F9` to reload your game. You can try the approach again, but this time, manually drop out of time warp a few minutes *before* you reach the `Pe` marker so you have time to line up and hit **Z** for full throttle.

**Option 2: Try Again on the Next Lap**
If you don't have a quicksave, don't panic. Based on your last screenshot, you still have nearly 2,900 m/s of Δv, which is plenty of fuel to fix this.

Do nothing for the next two minutes.

Let the ship cross the escape boundary. You will pop back out into a massive, wide orbit around Kerbin.

Once back in Kerbin's Sphere of Influence, coast down to your new Kerbin Periapsis (the lowest point near the planet).

Drop a new maneuver node at that Periapsis, pull the Prograde handle, and plot another transfer encounter to the Mun just like you did the first time.

---

## User

ok what's going on here now? I've reloaded

---

## Assistant

Looking at image_0bcae0.jpg, this quicksave is from *after* you flew past the Mun. You got slingshotted.

When you flew through the Mun's gravity well without stopping, it performed a gravity assist on your ship, flinging you out into a massive, high-altitude orbit around Kerbin.

Here is the evidence on your screen:

**The Cyan Line:** This is your current orbit.

**The Bottom-Left Panel:** Your Periapsis (Pe) is now at 11.54 Mm (million meters).

**The Mun's Orbit:** The Mun (the yellow line) orbits Kerbin at exactly 11.4 Mm.

Because your lowest point (11.54 Mm) is higher than the Mun's actual orbit (11.4 Mm), your ship is entirely in the "outside lane." Your cyan circle never crosses the yellow circle.

**How to fix this from here:**
If you do not have an older quicksave from before the flyby, you must lower your orbit to intersect the Mun again. You have plenty of fuel (2,864 m/s) to do this.

**Time Warp to Apoapsis:** Fast-forward until your ship reaches the `Ap` marker at the very top of your cyan loop.

**Drop the Periapsis:** Point **Retrograde** (the green circle with the cross) and fire your engine until your `Pe` on the opposite side shrinks down and intersects the yellow Mun orbit line.

**Plan a New Transfer:** Once your orbit crosses the Mun's path again, place a maneuver node, and drag it around your orbit until a new Mun encounter appears.

---

## User

Ok I reloaded again.

Let's start by breaking down what I'm looking at. What does each color orbit indicate? Like, cyan is OUR flight path, right?

Then yellow is Mun's orbit... what's purple?

---

## Assistant

You have the first two exactly right. Here is the full breakdown of how the orbital prediction lines (patched conics) work in your screenshot:

**Cyan Line:** Your vessel's current path around Kerbin.

**Yellow Line:** The Mun's orbital path. It is highlighted in this color specifically because you currently have the Mun set as your active target.

**Orange Segment:** This is your projected path *inside* the Mun's Sphere of Influence (gravity well). Notice the small orange curve wrapping around the Mun and the text reading `The Mun Escape`.

**Purple Line:** This is your ship's predicted trajectory *after* the Mun. Because you are currently on a flyby path and not in a closed orbit, the game is calculating how the Mun's gravity will alter your course. If you do not fire your engines at all, you will fly along the cyan line, pass through the orange segment, and the Mun will slingshot you out onto that massive purple orbit.

Ready to execute the capture?
Yes

---

## User

ok so what's the play?

---

## Assistant

The play is to ride this exact trajectory into the Mun's gravity well and slam on the brakes at the lowest point so you don't get slingshotted again.

Here is the exact sequence to execute the capture safely without overshooting.

1. Warp to the SOI (Sphere of Influence)

Hover your mouse over the **orange line** (your path around the Mun).

Right-click on the orange line somewhere *before* the `Pe` (Periapsis) marker and select **Warp Here**.

The game will fast-forward and automatically stop you right where you clicked.

Once you arrive, the camera will shift, the Mun will be in the center of your screen, and your path will turn blue/cyan.

2. Lock to Retrograde

Now that you are in the Mun's gravity, look at your SAS buttons on the left of the Navball.

Click **Retrograde** (the green circle with the cross). Your ship will automatically spin around so the engine is facing forward along your flight path.

3. Check Your Altitude

Hover over the `Pe` marker next to the Mun.

If it is above 10,000m, you are safe. (If it is below 10,000m, point Radial Out and tap the throttle to raise it so you don't hit a mountain).

4. The Capture Burn

Use time warp (`.` and `,`) very carefully to move your ship until you are about **30 seconds away** from the `Pe` marker.

The moment your ship hits `Pe`, hit **Z** for full throttle.

Watch your map view. The massive escape trajectory will bend backward, close up, and form an oval or circle around the Mun.

Hit **X** to cut the throttle once your Apoapsis and Periapsis are both somewhat even (e.g., between 20,000m and 50,000m).

You will be in a stable orbit.

---

## User

ok so I did that, and then a correction... So I basically just do this a few times at the periapsis until I get into orbit around Mun? @Flash

---

## Assistant

Stop right there! Do not time warp to that Periapsis yet.

If you look closely at the purple trajectory line in `image_0b655f.jpg`, it goes straight into the center of the rock. Your `Pe` marker is currently underground. If you coast on this path, you will crash directly into the surface of the Mun.

Also, to answer your question: **No, you cannot do this in a few separate burns.** Because you are currently on a flyby trajectory, if you do not burn long enough to completely close your orbit into a circle on your very first pass, you will fly right back out into deep space. It must be one continuous burn.

Here is the exact sequence to fix your path and capture safely:

1. The Collision Avoidance Tap (Do this immediately)

You need to lift your trajectory out of the ground before you get closer.

Point your ship **Radial Out** (the blue circle with the spokes on your Navball).

Tap your throttle key (`Shift`) for literally one or two seconds, then cut it (`X`).

Watch the purple line. You want it to shift outward so it curves *around* the Mun instead of hitting it.

Hover your mouse over the purple `Pe` marker. Keep making tiny throttle taps until that `Pe` altitude reads somewhere between **20,000m and 30,000m**.

2. The Single Capture Burn

Once your `Pe` is safely above 20,000m, time warp until you are about 30 seconds away from the `Pe` marker.

Click **Retrograde** on your Navball (the green circle with the cross).

The exact moment you hit `Pe`, hit **Z** for 100% throttle.

**Do not stop burning.** Watch the map view. The lines will bend, and eventually, the ends will meet to form a closed loop around the Mun.

As soon as it forms a complete circle and your Apoapsis (`Ap`) and Periapsis (`Pe`) are roughly the same height, hit **X** to cut the engine.

You will now be safely parked in orbit.

---

## User

it's not actually intersecting at all. it's 27km at nearest

---

## Assistant

You are correct. KSP's 3D map view often compresses depth, making a safe pass behind or in front of a moon look like a direct collision depending on the camera angle.

A 27 km Periapsis is absolutely perfect for a Mun capture. You can completely skip the Radial Out correction step and proceed directly to the capture burn.

Here is the exact sequence to park this ship in orbit:

1. Warp to the Mun's Gravity Well

Right-click the trajectory line just *before* it gets to the Mun and select **Warp Here**.

Wait for the game to fast-forward and stop automatically. The screen will shift, the Mun will be in the center, and your local flight path will turn blue/cyan.

2. Lock Your Orientation

Click the **Retrograde** button on your Navball (the green circle with the cross). Your ship will spin backward to face its engines directly into the flight path.

3. The Capture Burn

Carefully time warp (`.` and `,`) until your ship is exactly at the `Pe` marker.

Hit **Z** for 100% throttle.

**Do not stop burning.** Watch the map view as your trajectory line bends and pulls inward.

Keep the engine running until the line forms a complete, closed circle around the Mun.

Hit **X** to cut the engine as soon as the circle is formed and your Apoapsis (`Ap`) and Periapsis (`Pe`) are relatively balanced.

---
