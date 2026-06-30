[2026-06-30 14:54] User:
i'm curious about making a DIY bean-to-cup pour over machine.

I have a hand grinder.

Even if it was just like semi-automated that would be awesome.

---

[2026-06-30 14:54] Assistant:
Building a DIY bean-to-cup machine is an awesome engineering puzzle. Since you already have a high-quality hand grinder, motorized automation becomes a lot more achievable. Instead of designing a complex industrial burr carrier from scratch, you can use your existing hand grinder as the core mechanical component and build the automation around it.

A semi-automated system handles the two most tedious, precision-dependent parts of the process: spinning the crank at a consistent speed and managing the water delivery stages (bloom, pulses, and timing).

The Core Architecture

To make this modular and highly reliable, you can split the machine into two distinct stations or stack them vertically in a rigid frame.
A fully integrated custom DIY coffee machine. Source: Instructables

1. The Grinder Drive (Bean-to-Cup Execution)

Instead of manual cranking, you build a motorized dock for your hand grinder.

**The Motor:** A high-torque, low-RPM DC gear motor (like a worm gear motor) or a beefy NEMA 23 stepper motor. Hand grinding requires considerable torque, especially for light roasts, so a direct-drive small motor will stall. A worm gear motor is perfect because it inherently prevents back-driving and provides massive torque at 60–100 RPM.

**The Coupling:** Remove the magnetic or screw-on handle from your grinder and expose the central hex shaft. Use a flexible jaw coupling (often called a spider coupling) to connect the motor shaft to the grinder shaft. This misaligned-tolerant coupling protects the internal bearings of your grinder from being ruined by slight construction errors.

**The Mount:** The frame needs to be incredibly rigid (aluminum extrusion or thick 3D-printed blocks) to handle the rotational counter-torque when the beans catch.

2. The Liquid Handling (Automated Pour Over)

Once the grinds fall directly into the filter basket below, the water delivery system takes over.

**The Flow Control:** Instead of trying to pump boiling water directly (which ruins cheap pumps and causes airlocks), use a dual-vessel system. A standard electric kettle heats the water. A small, food-grade 12V perisatltic pump or a high-temperature diaphragm pump draws the hot water from the kettle and pushes it to the brew head.

**The Brew Head:** To replicate a good manual pour, you can use a static shower-screen distribution plate, or mount the water nozzle to a small 9g hobby servo motor to physically sweep the stream in a circle over the coffee bed.

High-Level Control Logic

An Arduino, ESP32, or Raspberry Pi Pico can run the entire process using a simple solid-state relay (SSR) for the motor and a MOSFET to pulse the water pump.


```
[Start Button] 
      │
      ▼
[Turn on Grinder Motor] ──► (Runs until current drop / timeout detected)
      │
      ▼
[Run Water Pump: Bloom] ──► (e.g., 50g water / 40 second pause)
      │
      ▼
[Loop Pulse Pours] ─────► (Activate pump for X seconds, rest for Y seconds)
      │
      ▼
[Finish / Audio Alert]

```

Three Hurdles to Plan For

**The Torque Spike:** Light roast beans are incredibly dense. When the motor first starts, if a bean is already wedged in the burrs, the startup current will spike massively. Your power supply and motor driver (like a Cytron or a rugged stepper driver) need to handle at least 2–3 times the running current without tripping.

**Static and Retention:** Without a human shaking the grinder, static will cause chaff and fine particles to stick to the exit chute. Designing a mounting position that places the grinder exit as close to the filter cone as possible is critical.

**Water Temperature:** Standard plastic pumps melt or leach chemicals at 95°C (194
∘
F−205
∘
F). Make sure any tubing is food-grade platinum-cured silicone, and the pump body itself is rated for boiling liquids (silicone or PPS materials).
