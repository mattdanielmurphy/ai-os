---
title: "I was just looking into the 3d printing services offered by "
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "12c5f5be-80a5-52e9-ab92-9594f2c036ba"
url: ""
---

# I was just looking into the 3d printing services offered by 

> [!NOTE]
> Archived Gemini Thread: [I was just looking into the 3d printing services offered by ]() | Date: 2026-08-13

## User

I was just looking into the 3d printing services offered by my library. They say PLA via FDM is $.1/g of the final product, and resin is $7 flat fee plus $.25 per gram.
Is that a reasonable cost?
How much would various commonly printed things cost?
Depends on the density of the print too obviously.

---

## Gemini

The pricing you've quoted for the library—likely the Edmonton Public Library (EPL)—is actually excellent for a public service.


At $0.10/g for PLA, they are essentially charging you only for the cost of the raw material (a standard 1kg spool costs roughly $20–$30, or $0.02–$0.03/g). The extra few cents per gram cover electricity, nozzle wear, and failed prints. Commercial services usually charge a "setup fee" per part plus a significantly higher markup on the plastic, often landing at $10–$20 for even small parts.


Cost Breakdown for Common Prints
Since FDM (PLA) uses infill (a honeycomb-like interior) and Resin is typically printed solid (unless manually hollowed), the weights and costs differ significantly for the same object.










































ItemEst. Weight (PLA)Est. Cost (PLA)Est. Weight (Resin)Est. Cost (Resin)"Benchy" (Tugboat)~12g$1.20~15g$10.75Standard D&D Mini~3–5g$0.50~5–8g$8.25–$9.00Headphone Stand~150g–200g$15.00–$20.00~250g+$70.00+Smartphone Stand~30g–50g$3.00–$5.00~60g$22.00

Which Service Should You Use?
You mentioned the density factor, and you're spot on. Here is how to choose between the two based on those costs:



* Go with PLA ($0.10/g) for:

* Functional items: Brackets, organizers, or tools.

* Large items: The "flat fee" for resin makes large prints like a headphone stand or a laptop riser prohibitively expensive.

* Low-density needs: You can set a PLA print to 10% infill to keep it lightweight and cheap.




* Go with Resin ($7 + $0.25/g) for:

* High Detail: If you are printing a tabletop miniature or a jewelry prototype where you don't want to see "layer lines."

* Batch Printing: The $7 fee is usually per print job. If you can fit five small miniatures on one resin build plate, that flat fee is distributed, making each mini about $2.50–$3.00 total.





A Note on "Density" (Infill)
In the slicing software (like Cura or PrusaSlicer), you can control the Infill Density.



* 10–15%: Standard for most decorative items. It’s mostly air inside.

* 30–50%: "Heavy duty" for parts that need to take some weight.

* 100%: Rarely needed for PLA, but the default for resin.


If you're printing something chunky like a paperweight, the PLA version will be significantly cheaper because it’s hollow, whereas the resin version will be a solid, heavy, and expensive block of plastic.

---

## User

How hard is it to just sand away the lines on a PLA print?
Suppose it depends on the design

---

## Gemini

It is definitely doable, but PLA presents a specific challenge compared to other plastics or wood: friction heat.


Because PLA has a relatively low glass transition temperature (around 60°C), sanding too vigorously will cause the plastic to soften and "gum up" rather than turn into a fine powder. Instead of a smooth surface, you end up with messy, melted plastic pills.


The Sanding Process
To do it effectively, you generally need to follow a "Wet Sanding" workflow:



* Start Coarse: Begin with 120 or 220 grit to knock down the ridges of the layer lines.

* Wet Sanding: Use waterproof sandpaper and a bowl of water. Frequently dipping the paper/part in water keeps the plastic cool and prevents the sandpaper from clogging.

* Progression: Move through grits—400, 600, 800, and finally 1000+ if you want a polished look.

* Finish: Sanded PLA looks "ashy" or white. You’ll need to apply a clear coat, mineral oil, or paint to bring back the original color and depth.



How Design Dictates the "Hardness"
The difficulty scale depends entirely on the geometry of your print:
































Geometry TypeDifficultyWhy?Flat SurfacesEasyYou can use a sanding block to maintain perfectly flat planes.Large CurvesModerateRequires flexible sanding pads or sponges to avoid creating flat spots on the curve.Intricate DetailsHardSanding inside tiny crevices or around small protrusions is tedious. You risk "rounding off" sharp details you wanted to keep.Holes/ChannelsVery HardRequires specialized tools like needle files or sandpaper wrapped around toothpicks.
Better Alternatives for a Smooth Finish
If the thought of hours of wet sanding sounds unappealing, most people use the "Fill and Sand" method:



* Filler Primer: Spray the part with a high-build automotive filler primer. This fills the "valleys" between the layer lines so you are mostly sanding the primer rather than the plastic.

* Wood Filler/Spot Putty: For deep gaps or "zits," dab on some thinned-out wood filler or Bondo spot putty, then sand it flush.

* 3D Gloop/Epoxy: Coating the print in a thin layer of XTC-3D (an epoxy resin) self-levels and hides layer lines almost entirely, though it can obscure very fine details.


Pro-Tip: If you know you're going to sand a part, increase your Wall Count (Perimeters) in your slicer to 3 or 4. This ensures you don't accidentally sand through the outer shell and expose the hollow infill inside.


Is there a specific project you're thinking of printing that has complex details?

---

