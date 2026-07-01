[2026-06-30 23:02] User:
I'm working on an app that uses AI to generate vector art like logos but in a way where each layer is fully editable by a human and it's made sensibly; like where each path is an object, rather than the pixel-by-pixel unedited SVG messes AIs sometimes create.




I'm wondering about strategies here.

I feel like the best thing I can think of is you have one model that merely thinks about the prompt, thinks about the objects and layers to produce the final product, then makes several AI calls to generate each layer, and then potentially another AI assesses the final product and makes changes to it looks sensible.




The AIs actually generating the art will have rigid rules it must adhere to. Like using simple shapes wherever possible, not generating more than what is specifically asked of it...

---

[2026-06-30 23:02] Assistant:

