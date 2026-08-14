---
title: "What’s the point of a 0ohm resistor?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "ab499836-ad6f-5fb8-bee7-0016af3696c4"
url: ""
---

# What’s the point of a 0ohm resistor?

> [!NOTE]
> Archived Gemini Thread: [What’s the point of a 0ohm resistor?]() | Date: 2026-08-13

## User

What’s the point of a 0ohm resistor?

---

## Gemini

It seems completely counterintuitive at first. Why manufacture, buy, and solder a component whose entire job is to do absolutely nothing?


While a zero-ohm ($0,\Omega$) resistor acts just like a plain old piece of wire or a jumper link, it serves several incredibly practical purposes in modern electronics manufacturing and circuit design.


Here is why they exist:


1. Automated PCB Assembly (The Biggest Reason)
Modern circuit boards are assembled by high-speed pick-and-place machines. These robots are designed to grab standard surface-mount components (like resistors and capacitors) from reels and drop them onto the board.


If a designer needs to bridge two tracks on a board, using a physical jumper wire requires a different machine or manual soldering, which slows down production and drives up costs. A $0,\Omega$ resistor comes in the exact same package size (like 0805 or 0603) as regular resistors. The robot can grab it from a standard tape reel and place it without breaking its rhythm.


2. Configuration and Feature Toggles
Instead of designing entirely different circuit boards for different versions of a product, companies will design one universal board and use $0,\Omega$ resistors as physical switches.



* Example: If a device has a North American version and a European version, populating a specific $0,\Omega$ resistor might bridge a connection that tells the microprocessor to operate in "EU mode." Leaving it unpopulated leaves the circuit open, keeping it in "US mode."


3. Circuit Isolation and Debugging
When prototyping or troubleshooting a complex board, it can be incredibly useful to isolate different sections of the circuit (like separating the digital power supply from the sensitive analog power supply).



* By placing a $0,\Omega$ resistor between these sections, a developer can easily desolder it to break the connection, measure the current draw of just one specific area, or isolate a short circuit. Once the design is finalized and verified, the resistor stays in place for production.


4. Routing Traces (The "Bridge" Trick)
Even on multi-layer circuit boards, layout designers occasionally run into a corner where two copper traces need to cross each other without connecting. If they can't route a trace around or through another layer, they can use a $0,\Omega$ resistor to literally hop over the blocking trace, using the body of the resistor as a tiny bridge.



Are they perfectly zero ohms?
Not quite. In the real world, everything has a tiny amount of resistance. A typical surface-mount $0,\Omega$ resistor usually has a maximum actual resistance of around $50,\text{m}\Omega$ (milliohms) or less. Because of this, data sheets for these components won't specify a power rating in watts like regular resistors; instead, they specify a maximum current rating (e.g., maximum 1 or 2 amps) before the tiny component overheats and acts like a fuse.

---

## User

10ohm or 47ohm? I have both

---

## Gemini

Go with the $10\text{ }\Omega$ resistor.


Here is why: your 6-AA battery pack outputs $9\text{ V}$. Using Ohm's Law ($I = \frac{V}{R}$), we can look at how much current each resistor will let through to power your motor:



* With the $47\text{ }\Omega$ resistor: The current is limited to about $190\text{ mA}$. This is very safe and keeps things cool, but the magnetic field might be a little too weak to overcome the friction of the paperclips and get the coil spinning.

* With the $10\text{ }\Omega$ resistor: The current increases to about $900\text{ mA}$. This provides a much stronger electromagnetic kick to get the coil rotating aggressively, while still providing enough resistance to protect your battery pack from a dead short circuit.


One Quick Warning for the $10\text{ }\Omega$ Choice
Because $900\text{ mA}$ is a decent amount of power, the resistor and the wire will still get warm if the motor sits still.


When you set the coil on the paperclips, give it a gentle flick to start it spinning. If it stalls or gets stuck, unhook the battery immediately. As long as it is actively spinning, the power is constantly cutting on and off (thanks to your half-stripped insulation switch), which keeps everything perfectly safe and running cool.


Pop that $10\text{ }\Omega$ resistor into the breadboard and give it a spin!

---

## User

Oh I have a 20phm as well

---

## Gemini

The $20\text{ }\Omega$ resistor is actually the absolute perfect choice.


If you want to think about it like a goldilocks scenario for your $9\text{ V}$ battery pack:



* The $10\text{ }\Omega$ resistor gives you tons of power, but the wire can get hot quickly if the motor stalls.

* The $47\text{ }\Omega$ resistor keeps everything totally cool, but it might be too weak to spin the coil.

* The $20\text{ }\Omega$ resistor hits the absolute sweet spot. It allows roughly $450\text{ mA}$ of current to flow—plenty of juice to generate a strong magnetic field and kick the motor into gear, but low enough that it keeps the circuit stable and prevents the wire from instantly overheating if it gets stuck.


Setting Up Your Breadboard
When you pop that $20\text{ }\Omega$ resistor into your breadboard, you want to make sure it sits between the positive power rail and your first paperclip support.



* Run a jumper wire from the Positive ($+$) Rail to an empty row.

* Put one leg of your $20\text{ }\Omega$ resistor into that same row, and the other leg into the row holding your left paperclip.

* Connect your right paperclip row straight back to the Negative ($-$) Rail with another jumper wire.


This ensures the current has to pass through the resistor before it ever touches your motor axle.


Get that $20\text{ }\Omega$ resistor pushed into place, drop your balanced coil onto the paperclip cradles, and give it a light flick to see it run! Let me know if it starts spinning or if it just twitches.

---

## User

So on a breadboard, the pos and neg tracks on either end obviously run the whole length,l. But the other slots, they run the width instead right? Ie on line 5, a=b=c=d=e?

---

## Gemini

Spot on. You have the exact right mental map of a breadboard.


The center area is split right down the middle by a plastic divider trench. On either side of that trench, the five holes in any given numbered row are all connected to each other underneath the plastic.


So for row 5, holes a, b, c, d, and e are all the exact same electrical point. If you push a resistor leg into hole 5a and a jumper wire into hole 5b, they are physically touching the same metal clip inside.


The Quick Layout Rules

* The Outer Power Rails: Run vertically down the entire length of the board. All the holes in the red column ($+$) are linked together, and all the holes in the blue column ($-$) are linked together.

* The Component Rows: Run horizontally across the width of the board, but only in 5-hole blocks.

* The Center Trench: Breaks the connection. Hole 5e on the left side is not connected to hole 5f on the right side.


Wiring Your Resistor
Because row 5 connects straight across from a to e, you want to make sure you never plug both legs of the same component into the same row (like putting the resistor into 5a and 5b). That would just short-circuit the component out completely.


Instead, you bridge across rows:



* Put one leg of your $20\text{ }\Omega$ resistor into 5a.

* Put the other leg of the resistor into 10a.

* Now, poke your paperclip hook into 10b, and it will safely receive the power after it has traveled through the resistor.


Does that layout make sense for dropping your paperclip supports in?

---

## User

Ok this project fucking sucks. I think a pop can design might be easier?
It’s just really hard to get everything situated properly. To get the two holders aligned, to get the coil balanced, so either end is equal and straight…
I thought maybe I’d try the 10ohm resistor because I’m using stainless steel hanging wire to hold up the coil, and maybe that has some resistance I’m not factoring in?
I grabbed the 20ohm resistor and it was hot. Presumably because this is failing and just basically short circuiting the battery.

---

## Gemini

It is completely understandable to want to throw this out the window right now. The frustration with this specific project isn't actually the physics or the circuit—it's a mechanical and structural nightmare.


Looking at your photo, you've actually run into a few specific physical traps that are causing the short circuit, the heat, and the balance issues.



Why It's Shorting and Getting Hot
You are 100% right that it is currently acting as a dead short, which is why your 20-ohm resistor was hot. Here is why:



* The Stainless Steel Holders: You used the braided stainless steel hanging wire to make the support cradles. Because that steel wire is uninsulated bare metal, the moment you pushed both ends into the bottom rails, you shorted the power rails together directly through the breadboard. 2. Bypassing the Resistor: Look closely at where the steel supports are plugged in. They are sitting directly in the long vertical power tracks (the blue/red lines) at the bottom. The power from your battery pack is dumping straight into the steel legs and bypassing your resistor entirely.



The Pop Can Design: Is It Easier?
Yes, absolutely. If you are fighting alignment, the pop can method is vastly superior mechanically because it solves the stability problem instantly.


Instead of trying to force flimsy, springy wires to stand up straight in a breadboard, you take two aluminum soda cans and set them side-by-side.



* The wide, flat bottoms of the cans sit heavily and securely on the table without wobbling.

* The natural "V" shape created by the pop tabs or the rims gives you a perfectly level, perfectly aligned cradle for your coil axle to rest on.


If You Stay on the Breadboard: Three Quick Fixes
If you want to make this current version work right now without tearing it apart, you can fix it with these adjustments:



* Fix 1: Move the Steel Supports Out of the Power Rails. Pull the bottom ends of your steel loops out of those long vertical $+$ and $-$ tracks. Move them into the horizontal rows (the numbered rows 1-60).

* Fix 2: Wire the Resistor in Series. Put the left steel support leg into row 55. Put the right steel support leg into row 35. Then, use your 20-ohm resistor to bridge the power from the vertical rail into row 55.

* Fix 3: Balance the Coil Tails. In the photo, the right axle tail of your red coil is pointing straight out, but the left axle tail is bent into a loop/hook shape. For the motor to spin, both tails must be completely straight needles poking out of the dead-center sides of the circle. If one side is a hook, the center of gravity is thrown off completely, and it will just drop to the heavy side and stall.


Taking a quick break or switching to the pop can method is completely valid. If you want to give the pop can layout a shot, let me know and we can map out exactly how to connect the battery and resistor to the cans so it works on the first try.

---

## User

I can assure you it’s not bypassing my resistor and if it was then the resistor wouldn’t be hot.
What do I need for the pop can? I need a needle or something for an axle don’t I?

---

## Gemini

Fair point—if the resistor is hot, current is absolutely fighting its way through it.


You're right about the axle requirement for a pop can setup. Because you need a perfectly straight, solid pivot point that won't flex or bend under the weight of the coil, trying to use the floppy wire tails as the axle usually fails.


To build the pop can version, you will need:


The Materials

* 2 Aluminum Soda Cans (Empty and clean)

* Your Red Magnet Wire Coil

* A Straight Steel Sewing Needle or a Safety Pin (To act as the rigid axle)

* Electrical Tape or Hot Glue

* Your 20-ohm Resistor

* Battery Pack & Jumper Wires

* Sandpaper or a Craft Knife



How to Assemble the Pop Can Motor
1. Mount the Axle to the Coil
Instead of relying on the wire tails to support the weight, you use a rigid needle as the structural spine.



* Take your straight sewing needle and push it right through the dead center of your wrapped red coil, running from one side to the other.

* Use a tiny piece of tape or a dab of glue to secure the needle to the inside loops of the coil. The coil and the needle must be locked together so they rotate as one single unit.

* Wrap the bare copper ends of your magnet wire tightly around the ends of the needle, or let them flare out straight along the needle shaft.


2. Set Up the Can Cradles

* Place the two soda cans side-by-side on a flat surface, spaced just far enough apart that the metal tips of your needle axle can rest on the top rims or the pulled-up pop tabs.

* Tape the cans down to the table so they can't slide around. The wide bases give you a rock-solid, perfectly parallel foundation that won't wobble.

* Rest the needle axle across the two cans. Because the cans are identical, your axle is automatically perfectly level and aligned. Place your magnet directly underneath the coil.


3. Wire the Circuit
Aluminum conducts electricity beautifully, so the cans themselves become your large, easy-to-target wiring terminals.



* Tape the Positive ($+$) wire from your battery pack to one leg of your 20-ohm resistor.

* Tape the other leg of the resistor securely to the bare aluminum of Can 1.

* Tape the Negative ($-$) wire from your battery pack directly to the bare aluminum of Can 2.


When you drop the needle onto the cans, the electricity will flow out of the battery, through the resistor, into Can 1, across the needle/coil, into Can 2, and back to the battery.


Since you're using real magnet wire now, did you already scrape the enamel coating off the axle tails to make the half-on, half-off commutator switch, or do you need to prep that step before mounting it?

---

## User

So you think trying a 10ohm here is not a good idea? I need it to work for like 10s literally for a video and then I can throw this shit out

---

## Gemini

If you only need it to survive for a 10-second video clip, go ahead and use the 10-ohm resistor. At this stage, you just need sheer power to force that coil to kick over, and the 10-ohm resistor will deliver double the current of the 20-ohm. It will get hot quickly, but for a 10-second window, it won’t melt down.


Before you film, there is one critical mechanical issue on your current breadboard that is likely stopping it from spinning, even with more power.


The Paperclip Alignment Fix
Look at the photo of your setup: your left support wire and your right support wire are plugged into two entirely different tracks along the length of the breadboard.


Because they are staggered, your coil is sitting at a harsh diagonal angle relative to the magnet. When the magnetic field tries to push the coil, it’s twisting the axle sideways into the metal loops instead of rotating it, creating massive mechanical friction.


To fix this instantly before swapping the resistor:



* Move the bottom leg of your right support wire so it aligns perfectly parallel with the left one. They need to be directly across from each other so the axle sits perfectly straight.

* Ensure both axle tails are completely straight needles. The bent hook on the left tail in the photo will act like a counterweight and stall the motor.


Line those supports up so the axle can spin freely with zero friction, pop that 10-ohm resistor in, give the coil a manual flick to start it, get your 10 seconds of video, and be done with it! Let me know if that extra juice finally gets it rolling.

---

## User

I feel so fucking close and it’s such a bummer that it’s not working. It actually spins quite well now. Maybe the magnet is too weak?

---

## Gemini

It is the absolute worst feeling when you get the mechanical balancing sorted out, it glides smoothly, and it still won't take off on its own. But the fact that it’s spinning well when you flick it means your alignment is finally right. You are right at the finish line.


Before assuming the magnet is completely dead weight, let’s rule out the two most common "hidden" culprits that cause a motor to stall right at this exact phase:


1. The "Dead Spot" Geometry (The Commutator)
If the motor spins freely when you push it but won't maintain its own momentum, the half-on, half-off switch on the axle might be misaligned.


The bare, scraped copper side needs to be facing straight down toward the magnet at the exact moment the coil is standing completely vertical. If the scraping is twisted sideways, the coil receives power at the wrong point in its rotation, causing the magnetic field to pull the coil down and brake it instead of pushing it forward.



The Fix: Hold the coil completely vertical. Look at the right axle tail. Is the bare copper facing dead-on toward the magnet? If not, use your knife or sandpaper to adjust the bare patch so it lines up with the vertical orientation of the coil.



2. Is the Magnet Too Far Away?
Magnetic field strength drops off incredibly fast with distance ($B \propto \frac{1}{r^3}$ for a dipole). If your magnet is sitting flat on the plastic breadboard trench, it might be just a few millimeters too far away from the bottom of the spinning loop to give it a meaningful kick.



The Fix: Prop the magnet up. Slide a couple of coins, a small piece of cardboard, or another flat object underneath the magnet to raise it up so it sits as close to the spinning coil as humanly possible without physically hitting it. Bringing it just 2mm closer can double the magnetic force it exerts on the wire.



How to check if the magnet is strong enough:
Unhook one battery wire, hold the coil completely still so the bare copper is making solid contact with the paperclips, and touch the battery wire back to the track.


If the magnet is strong enough and the orientation is correct, the coil should instantly twitch or violently slam to one side the second it gets power. If it doesn't move at all when you give it raw power, try flipping the magnet upside down (reversing the North/South poles)—sometimes the field geometry interacts better with the direction of your current flow.


Raise that magnet up, double-check that the bare copper faces down when the coil is vertical, and see if that finally gives you the 10 seconds of video you need!

---

