---
title: "help me finish and refine this procedure write-up. What I've"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "31d0e0fa-e109-5840-a603-1e8ab3613b6a"
url: ""
---

# help me finish and refine this procedure write-up. What I've

> [!NOTE]
> Archived Gemini Thread: [help me finish and refine this procedure write-up. What I've]() | Date: 2026-08-13

## User

help me finish and refine this procedure write-up.
What I've got so far:
```
# PH12 U6: DC Motor Lab

<div class="metadata-header">
  <div><strong>Teacher:</strong> Naresh Chand</div>
  <div><strong>Student:</strong> Matthew Murphy</div>
  <div><strong>Date:</strong> June 6, 2026</div>
</div>

### Procedure

**Procedure:**
1. Create a motor coil ($M$) by winding a length of magnetic wire around a pill bottle, securing the coil by wrapping either end of the wire around the body of the coil an equal amount of times per side to ensure symmetry for ideal spinning.
2. Prepare the magnetic wire coil by carefully scraping the enamel insulation off of either end of the wire, ensuring to leave the insulation intact on one side of one end (creating the Commutator, $C$.), making sure that when the loop is vertical, the bottom of the axel is uninsulated.
3. Place two lengths of stainless steel picture hanging wire, with a loop in the middle of each length into either side of the breadboard, one in the positive rail and one in the negative rail, ensuring the two loops are parallel and able to support the coil.
4. Place the ends of the coil wire through either side of the loop so that the coil is suspended between the two pieces of picture hanging wire.


![Photo diagram of DC Motor apparatus](diagram-1.png)
<div align="center" class="figure-caption">
  <em><strong>Figure 1:</strong> Photo diagram of DC Motor apparatus.</em>
</div>
```

Maintain my markdown formatting. Return the completed version in the same formatting in a markdown code block. Add the second, proper circuit diagram as well, it's diagram-2.png.
Make sure to reference the letters I've assigned to each component in the procedure and elsewhere.

Explain how it works as well, following the instructions given below.

These are the project instructions:
```
Objective
Construct a motor
There are two parts to this project:
Part 1: The Motor
• The motor may not be made be made out of any pre-manufactured parts.
• The motor should be mounted on a platform and not be held up by hand.
• The motor should start upon request (within 10 seconds).
• Once spinning, the motor should maintain a stable rotational speed without any additional human
assistance (e.g. holding the motor up).
• Ensure you have proper wire for your motor. If the wire is not insulated, the current will not differentiate
between the different turns in the coil. Magnet wire may be used which is a type of wire coated with a
thin layer of insulation.
Part 2: Written Component
• Include:
1. a description of how the motor is constructed, and
2. the theory behind your motor explaining how it works.
• Labelled diagrams should be included. Pictures and diagrams must of of your own motor and may not
be copied from the internet or other source.
Safety
• Do not exceed 12 volts to power the motors
• Do not allow the battery to be shorted for a long period of time (e.g. motor is connected but not
spinning).
```

---

## Gemini

Here is the completed and refined lab write-up. The procedure has been expanded to include the remaining components from your diagrams, the second schematic has been formatted to match, and a comprehensive theory section has been added to address the project rubric.


# PH12 U6: DC Motor Lab

<div class="metadata-header">
  <div><strong>Teacher:</strong> Naresh Chand</div>
  <div><strong>Student:</strong> Matthew Murphy</div>
  <div><strong>Date:</strong> June 6, 2026</div>
</div>

### Construction Procedure

**Procedure:**
1. Create a motor coil ($M$) by winding a length of magnetic wire around a pill bottle, securing the coil by wrapping either end of the wire around the body of the coil an equal amount of times per side to ensure symmetry for ideal spinning.
2. Prepare the magnetic wire coil by carefully scraping the enamel insulation off of either end of the wire, ensuring to leave the insulation intact on one side of one end (creating the Commutator, $C$), making sure that when the loop is vertical, the bottom of the axle is uninsulated. The opposite end should be completely scraped to act as an Uninsulated Axle ($U$).
3. Place two lengths of stainless steel picture hanging wire, with a loop in the middle of each length into either side of the breadboard, one in the positive rail and one in the negative rail, ensuring the two loops are parallel and able to support the coil.
4. Place the ends of the coil wire through either side of the loop so that the coil is suspended securely between the two pieces of picture hanging wire.
5. Connect a 9V Battery ($B$) to the breadboard's power rails.
6. Insert a Switch ($S$) into the circuit to control the current flow.
7. Place a $10\,\Omega$ Resistor ($R$) in series with the circuit. This prevents the battery from shorting out and overheating if the motor is connected but stationary.
8. Position a Permanent Magnet ($P$) on the breadboard directly beneath the suspended Motor Coil ($M$).

![Photo diagram of DC Motor apparatus](diagram-1.png)
<div align="center" class="figure-caption">
  <em><strong>Figure 1:</strong> Photo diagram of DC Motor apparatus.</em>
</div>

![Schematic circuit diagram of DC Motor](diagram-2.png)
<div align="center" class="figure-caption">
  <em><strong>Figure 2:</strong> Schematic circuit diagram of the constructed DC Motor.</em>
</div>

### Theory of Operation

The motor operates on the principle of magnetic force acting on a current-carrying conductor. When the Switch ($S$) is closed, current flows from the 9V Battery ($B$), through the protective $10\,\Omega$ Resistor ($R$), up the support wires, and into the Motor Coil ($M$). Because the coil is made of insulated magnet wire, the current is forced to travel through the loops rather than shorting across them, transforming the coil into an electromagnet with its own magnetic field.

This induced magnetic field interacts with the stationary magnetic field of the Permanent Magnet ($P$) positioned beneath it. The resulting repulsive and attractive magnetic forces create a torque that pushes the Motor Coil ($M$), initiating rotation. 

If the current were to flow continuously, the coil would simply align its magnetic poles with the permanent magnet and come to a stop. To achieve continuous rotation, the Commutator ($C$)—the half-insulated axle—acts as a mechanical switch. As the coil completes half a rotation, the insulated portion of the axle rotates into contact with the supporting wire. This breaks the circuit, temporarily cutting off the current and collapsing the coil's magnetic field.

During this brief disconnection, the rotational momentum of the coil carries it forward through the "dead zone." Once it completes the half-turn, the scraped, conductive side of the Commutator ($C$) re-establishes contact with the support wire. The current resumes, generating another magnetic push in the exact same rotational direction. This continuous cycle of pulsing magnetic torque allows the motor to maintain a stable rotational speed without assistance.

---

## User

remove background

---

## Gemini

I have removed the background and isolated the experimental setup, leaving a clean, transparent background as requested.

---

## User

white bg please

---

## Gemini
## Gemini — 2026-06-06 23:42

---

## User

with no shadows, just pure white

---

## Gemini
## Gemini — 2026-06-06 23:44

---

## User

ok, here's the latest version.

```
# PH12 U6: DC Motor Lab

<div class="metadata-header">
  <div><strong>Teacher:</strong> Naresh Chand</div>
  <div><strong>Student:</strong> Matthew Murphy</div>
  <div><strong>Date:</strong> June 6, 2026</div>
</div>

### Construction Procedure

**Procedure:**
1. Create a motor coil ($M$) by winding a length of magnetic wire around a pill bottle, securing the coil by wrapping either end of the wire around the body of the coil an equal amount of times per side to ensure symmetry for ideal spinning.
2. Prepare the magnetic wire coil by carefully scraping the enamel insulation off of either end of the wire, ensuring to leave the insulation intact on one side of one end (creating the Commutator, $C$), making sure that when the loop is vertical, the bottom of the axle is uninsulated. The opposite end should be completely scraped to act as an Uninsulated Axle ($U$).
3. Place two lengths of stainless steel picture hanging wire, with a loop in the middle of each length into either side of the breadboard, one in the positive rail and one in the negative rail, ensuring the two loops are parallel and able to support the coil.
4. Place the ends of the coil wire through either side of the loop so that the coil is suspended securely between the two pieces of picture hanging wire.
5. Connect a 9V Battery ($B$) to the breadboard's power rails.
6. Insert a Switch ($S$) into the circuit to control the current flow.
7. Place a $10\,\Omega$ Resistor ($R$) in series with the circuit. This prevents the battery from shorting out and overheating if the motor is connected but stationary.
8. Position a Permanent Magnet ($P$) on the breadboard directly beneath the suspended Motor Coil ($M$).

![Photo diagram of DC Motor apparatus](diagram-1.png)
<div align="center" class="figure-caption">
  <em><strong>Figure 1:</strong> Photo diagram of DC Motor apparatus.</em>
</div>

![Schematic circuit diagram of DC Motor](diagram-2.png)
<div align="center" class="figure-caption">
  <em><strong>Figure 2:</strong> Schematic circuit diagram of the constructed DC Motor.</em>
</div>

![Close-up photo of the DC Motor apparatus](suspended-motor-closeup.jpeg)
<div align="center" class="figure-caption">
  <em><strong>Figure 3:</strong> Close-up photo of the constructed DC Motor apparatus showing the looped supporting stainless steel wires.</em>
</div>

![Close-up photo of the top of the circuit](top-of-circuit-closeup.jpeg)
<div align="center" class="figure-caption">
  <em><strong>Figure 4:</strong> Close-up photo of the top of the circuit, showing the battery, makeshift switch, and resistor.</em>
</div>



### Theory of Operation

The motor operates on the principle of magnetic force acting on a current-carrying conductor. When the Switch ($S$) is closed, current flows from the 9V Battery ($B$), through the protective $10\,\Omega$ Resistor ($R$), up the support wires, and into the Motor Coil ($M$). Because the coil is made of insulated magnet wire, the current is forced to travel through the loops rather than shorting across them, transforming the coil into an electromagnet with its own magnetic field.

This induced magnetic field interacts with the stationary magnetic field of the Permanent Magnet ($P$) positioned beneath it. The resulting repulsive and attractive magnetic forces create a torque that pushes the Motor Coil ($M$), initiating rotation. 

If the current were to flow continuously, the coil would simply align its magnetic poles with the permanent magnet and come to a stop. To achieve continuous rotation, the Commutator ($C$)—the half-insulated axle—acts as a mechanical switch. As the coil completes half a rotation, the insulated portion of the axle rotates into contact with the supporting wire. This breaks the circuit, temporarily cutting off the current and collapsing the coil's magnetic field.

During this brief disconnection, the rotational momentum of the coil carries it forward through the "dead zone." Once it completes the half-turn, the scraped, conductive side of the Commutator ($C$) re-establishes contact with the support wire. The current resumes, generating another magnetic push in the exact same rotational direction. This continuous cycle of pulsing magnetic torque allows the motor to maintain a stable rotational speed without assistance.
```

Note that I don't actually have a switch, so I'm just using a jumper wire that I am manually plugging/unplugging from the breadboard.

---

## Gemini

Here is the updated write-up. I've adjusted Step 6 in the procedure and the opening of the Theory of Operation section to accurately describe your makeshift jumper-wire switch.


# PH12 U6: DC Motor Lab

<div class="metadata-header">
  <div><strong>Teacher:</strong> Naresh Chand</div>
  <div><strong>Student:</strong> Matthew Murphy</div>
  <div><strong>Date:</strong> June 6, 2026</div>
</div>

### Construction Procedure

**Procedure:**
1. Create a motor coil ($M$) by winding a length of magnetic wire around a pill bottle, securing the coil by wrapping either end of the wire around the body of the coil an equal amount of times per side to ensure symmetry for ideal spinning.
2. Prepare the magnetic wire coil by carefully scraping the enamel insulation off of either end of the wire, ensuring to leave the insulation intact on one side of one end (creating the Commutator, $C$), making sure that when the loop is vertical, the bottom of the axle is uninsulated. The opposite end should be completely scraped to act as an Uninsulated Axle ($U$).
3. Place two lengths of stainless steel picture hanging wire, with a loop in the middle of each length into either side of the breadboard, one in the positive rail and one in the negative rail, ensuring the two loops are parallel and able to support the coil.
4. Place the ends of the coil wire through either side of the loop so that the coil is suspended securely between the two pieces of picture hanging wire.
5. Connect a 9V Battery ($B$) to the breadboard's power rails.
6. Create a makeshift Switch ($S$) using a jumper wire that can be manually plugged into and unplugged from the breadboard to control the current flow.
7. Place a $10\,\Omega$ Resistor ($R$) in series with the circuit. This prevents the battery from shorting out and overheating if the motor is connected but stationary.
8. Position a Permanent Magnet ($P$) on the breadboard directly beneath the suspended Motor Coil ($M$).

![Photo diagram of DC Motor apparatus](diagram-1.png)
<div align="center" class="figure-caption">
  <em><strong>Figure 1:</strong> Photo diagram of DC Motor apparatus.</em>
</div>

![Schematic circuit diagram of DC Motor](diagram-2.png)
<div align="center" class="figure-caption">
  <em><strong>Figure 2:</strong> Schematic circuit diagram of the constructed DC Motor.</em>
</div>

![Close-up photo of the DC Motor apparatus](suspended-motor-closeup.jpeg)
<div align="center" class="figure-caption">
  <em><strong>Figure 3:</strong> Close-up photo of the constructed DC Motor apparatus showing the looped supporting stainless steel wires.</em>
</div>

![Close-up photo of the top of the circuit](top-of-circuit-closeup.jpeg)
<div align="center" class="figure-caption">
  <em><strong>Figure 4:</strong> Close-up photo of the top of the circuit, showing the battery, makeshift switch, and resistor.</em>
</div>

### Theory of Operation

The motor operates on the principle of magnetic force acting on a current-carrying conductor. When the makeshift Switch ($S$) is closed by plugging the jumper wire into the breadboard, current flows from the 9V Battery ($B$), through the protective $10\,\Omega$ Resistor ($R$), up the support wires, and into the Motor Coil ($M$). Because the coil is made of insulated magnet wire, the current is forced to travel through the loops rather than shorting across them, transforming the coil into an electromagnet with its own magnetic field.

This induced magnetic field interacts with the stationary magnetic field of the Permanent Magnet ($P$) positioned beneath it. The resulting repulsive and attractive magnetic forces create a torque that pushes the Motor Coil ($M$), initiating rotation. 

If the current were to flow continuously, the coil would simply align its magnetic poles with the permanent magnet and come to a stop. To achieve continuous rotation, the Commutator ($C$)—the half-insulated axle—acts as a mechanical switch. As the coil completes half a rotation, the insulated portion of the axle rotates into contact with the supporting wire. This breaks the circuit, temporarily cutting off the current and collapsing the coil's magnetic field.

During this brief disconnection, the rotational momentum of the coil carries it forward through the "dead zone." Once it completes the half-turn, the scraped, conductive side of the Commutator ($C$) re-establishes contact with the support wire. The current resumes, generating another magnetic push in the exact same rotational direction. This continuous cycle of pulsing magnetic torque allows the motor to maintain a stable rotational speed without assistance.

---

