---
title: "how is there no coil component?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "4bd6b40e-c2b5-56fa-af71-179615d69d8c"
url: ""
---

# how is there no coil component?

> [!NOTE]
> Archived Gemini Thread: [how is there no coil component?]() | Date: 2026-08-13

## User

how is there no coil component?

---

## Gemini

The editor uses the term Inductor for a coil.


If you clear the word "coil" from your search bar and scroll down the components list (or search for "Inductor"), you will find it listed right between Heater and Integrated Circuit.


It will drop standard schematic symbols for an inductor into your workspace, which represents the coil you need.

---

## User

So I'm trying to make a circuit diagram for an electric motor that is just simply a coil with one end totally uninsulated all the way around, and the other end only half insultated so it spins when a magnet is underneath it.
I guess I'll just do an inductor symbol and call it a day?

---

## Gemini

That sounds like the classic DIY simple motor project (often called a Beakman's motor). It's a clever design where that half-insulated wire acts as a mechanical commutator, switching the current off for half of every rotation so the magnetic field doesn't pull the coil backward.


Using a single inductor symbol is definitely the standard way to represent the coil itself. To make the schematic truly reflect how your specific motor works, you can add a few simple details:


1. Label the Inductor
Leave the inductor symbol on the schematic, but change its text label from something generic like "L1" or "100 mH" to "Motor Coil (Hand-Wound)".


2. Add the Magnet
A standard inductor doesn't imply a permanent magnet is nearby. You can represent the magnet by adding a simple Label component right next to or underneath your inductor symbol and typing "Permanent Magnet (Fixed)" or "Neodymium Magnet".


3. Represent the "Switching" Effect (Optional)
Because the half-stripped insulation acts as an on/off switch as it spins, the circuit isn't continuously closed. If you want the diagram to technically show how it functions, you could place a Toggle Switch or a Push to Break Switch in series with the inductor and label it "Commutator (Half-insulated axle)".



How it looks put together:

* Power Source: A standard Battery or Cell.

* The Rotor: An Inductor symbol (labeled "Coil").

* The Commutator: A Switch symbol inline with the coil to represent the intermittent contact.

* The Stator: A text Label representing the permanent magnet positioned near the coil.


This setup keeps your diagram clean while accurately explaining the mechanics of your build to anyone looking at it.

---

## User

I don't know what kind of magnet it is. It was taken from the door of an outside trash bin enclosure.

---

## Gemini

That is very likely a ferrite (ceramic) magnet or a neodymium magnet housed in a plastic or metal bracket. Enclosure doors use them because they are weather-resistant and strong enough to keep heavy lids or doors from blowing open in the wind.


For your diagram, you don't need to overthink the exact chemical makeup. You can just finish placing your label text as "Latch Magnet" or "Enclosure Magnet" right underneath the inductor symbol to complete the circuit's story.


Since it's a salvaged magnet, here is a quick tip for your motor build: if it's a long, rectangular block magnet, the north and south poles are usually on the large flat faces, not the ends. Make sure one of those flat faces is facing up toward your coil to give it the best possible push!

---

## User

but how do I place it underneath it? It was literally underneath it and this is a top-down view

---

## Gemini

In a 2D schematic, you can't layer components directly on top of each other physically, because it would turn into an unreadable jumble of lines.


Instead, schematics handle the "top-down" 3D reality by using relative positioning.


Looking at your workspace, you can represent the magnet's physical position by placing your "Permanent Magnet" label component just a little bit to the left or right of the inductor symbol (right next to the loops), or directly below the bottom wire of the coil loop.


To make it completely clear that it sits underneath the coil in real life, you can update your label text to say:



"Permanent Magnet (Positioned underneath coil)"



That way, your diagram stays perfectly clean and readable, but anyone looking at it will instantly understand exactly how to position the magnet on the physical build.

---

## User

@Flash-Lite how to scale up an svg in Sketch without everything getting fucked up (like keep the border width and text sizes and positions etc)

---

## Gemini

To scale an SVG in Sketch while maintaining proportions, border weights, and text positioning, follow these steps:


1. Enable "Scale" Mode
Instead of using the Selection tool or dragging the handles in the main canvas (which often distorts elements), use the dedicated Scale tool.



* Select your SVG layer or group.

* Click the Scale button in the top toolbar (or press Command + K).

* In the dialog box, enter your desired scale percentage or new dimensions.

* Ensure Scale Fills and Borders is checked. This tells Sketch to recalculate the stroke weight proportionally as you resize.


2. Handle Borders Independently
If you want to resize the object but keep the border width exactly as it was (e.g., a 2px stroke should remain 2px), you need to adjust the settings after the scale:



* After scaling, select the path.

* Go to the Borders section in the Inspector panel.

* If the stroke looks "thicker" or "thinner," manually reset the border width to your desired pixel value. Sketch will retain the new scale while applying your preferred stroke weight.


3. Manage Text Positioning
SVG text often behaves unpredictably in Sketch because of how font scaling and bounding boxes work.



* Convert to Outlines: If the text is purely decorative and does not need to be edited, select the text layer and go to Layer > Convert to Outlines. Once it is a shape, it will scale perfectly with the rest of your SVG without font-size issues.

* Keep as Text: If you must keep the text editable, ensure the text layer is set to "Auto" width or height in the Inspector before scaling. After scaling, you may need to reset the font size manually if it didn't scale proportionally with the group.


4. Grouping for Consistency
To ensure everything stays relative:



* Place all your SVG elements into a single Group or Artboard.

* Select that parent Group/Artboard when using the Scale tool. This ensures that internal spacing and relative positions of shapes and text are transformed as a single unit rather than individual objects being stretched.



Are you noticing specific issues with text alignment or stroke thickness when you use the Scale tool?

---

