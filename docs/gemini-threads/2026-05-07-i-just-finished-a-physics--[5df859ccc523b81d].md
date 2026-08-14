---
title: "I just finished a physics test and I couldn’t I don’t think "
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "ae598dcd-854b-5c21-8e6d-5261a5732f59"
url: ""
---

# I just finished a physics test and I couldn’t I don’t think 

> [!NOTE]
> Archived Gemini Thread: [I just finished a physics test and I couldn’t I don’t think ]() | Date: 2026-08-13

## User

I just finished a physics test and I couldn’t I don’t think find the right answer.
Question was, a 3kg cart rolls down a frictionless track and then enters a loop with a radius of 6m. What’s the minimum velocity the cart must travel to complete the loop?
Therefore how high up should the cart be released from at the start?

My attempt was basically: ma_c=F_g
a_c=g
Then solved for v.
Now I know the velocity at the top of the track.
Then I use kinematic equation vf^2=vi^2+.5ad where a is g, solve for vi to get initial min velocity to complete the loop.

then use that equation again to solve for release height to reach that velocity.

I ended up with a release height of 4m I think. Which makes no sense. How could something fall 4m and come back up 12m (top of the loop)?
I figured I must have gotten the a_c derivation wrong.
I thought ok there’s gravity and there’s the normal force both pressing/pulling down on the cart when on top of the loop, so maybe a_c=2g?
Even that gives a release height of 7m, which doesn’t seem plausible.

---

## Gemini

You're absolutely right to trust your intuition there—a release height of 4m or 7m wouldn't provide enough energy to crest a 12m peak.


The issue isn't actually your centripetal acceleration derivation ($a_c = g$ is correct for the minimum case); it's that kinematics (the equations of motion) are difficult to apply here because the direction of acceleration is constantly changing as the cart moves along the curve.


Conservation of Energy is the tool designed for this.


1. Finding Minimum Velocity ($v_{top}$)
At the very top of the loop, for the cart to stay on the track with "minimum" speed, the Normal force drops to zero. Gravity is the only thing providing the centripetal force.


$$mg = \frac{mv^2}{r}$$
$$g = \frac{v^2}{r}$$
$$v = \sqrt{gr}$$


Using $g = 9.8$ and $r = 6$:
$$v_{top} = \sqrt{9.8 \times 6} \approx 7.67 \text{ m/s}$$


2. Finding Release Height ($h$)
Instead of kinematics, we compare the total energy at the Start (all potential) to the total energy at the Top of the Loop (potential + kinetic).



* Energy at Start: $mgh_{start}$

* Energy at Top: $mgh_{loop} + \frac{1}{2}mv_{top}^2$


Since the track is frictionless, $E_{start} = E_{top}$:
$$mgh_{start} = mg(2r) + \frac{1}{2}mv_{top}^2$$


(Note: The height at the top of the loop is the diameter, or $2r$). We can cancel the mass ($m$) and substitute $v^2 = gr$ from our first step:


$$gh_{start} = g(2r) + \frac{1}{2}(gr)$$
$$h_{start} = 2r + 0.5r$$
$$h_{start} = 2.5r$$


The Result
For a radius of 6m:
$$h = 2.5 \times 6 = 15 \text{ meters}$$


This explains why your 4m and 7m results felt off. To get through a loop of diameter 12m, you need to start at least 15m up to account for the kinetic energy required to maintain contact at the apex.


How did the rest of the physics test feel overall?

---

## User

FUCK.
In my attempt to “fix it” I just changed the only part I’d gotten right originally.
God, it’s so upsetting to get a question wrong like that.

---

## Gemini

It’s incredibly frustrating when you have the correct intuition (setting $a_c = g$), but the technical execution trips you up. That "mid-test pivot" is usually where things go sideways because you're fighting against the clock and your own adrenaline.


If it helps for next time, there is a reason $h = 2.5r$ is such a common result in these problems. You can visualize the energy breakdown like this:



* 2.0r of that height is just to get the cart back up to the top of the loop (Potential Energy).

* 0.5r of that height is the "speed tax" required to keep the cart pressed against the track so it doesn't fall (Kinetic Energy).


Since you actually derived the $v = \sqrt{gr}$ part correctly in your first head-space, you clearly understand the physics of the forces involved. The transition from kinematics to energy is usually the "ah-ha" moment for most people in this unit.


Are you moving into work and energy for the rest of the term, or was this the final topic before moving on to something like electromagnetism?

---

