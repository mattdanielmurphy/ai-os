[2026-06-29 16:53] User:
I thought emojis were vector?

Why is a scaled up emoji in Sketch rendering like a low res raster?

---

[2026-06-29 16:53] Assistant:
While it seems logical that emojis should be vector—given they are part of text strings that scale perfectly in a word processor—they are actually handled quite differently under the hood by operating systems.

Here is exactly why you are seeing pixelation when scaling them up in Sketch.

The Standard Emoji Font File

On macOS, emojis are contained within a system font file called **Apple Color Emoji**. Unlike standard text fonts (like Helvetica or San Francisco), which use vector outlines (`.ttf` or `.otf` formats with Bézier curves), Apple's emoji font relies heavily on **embedded raster PNG images**.

To maintain performance and support complex gradients, shadows, and textures, Apple embeds pre-rendered PNGs at specific pixel dimensions inside the font file (typically ranging from 20×20 pixels up to 160×160 or 512×512 pixels for newer assets).

Why Sketch Displays Pixels

When you type an emoji into a text layer in Sketch, the OS renders the specific bitmap size closest to your current font size.

If you scale that text layer up to a massive size (e.g., 500pt or 1000pt):

You surpass the maximum native resolution of the embedded PNG.

Sketch has no choice but to stretch the largest available bitmap asset to fill the bounding box.

Because it is stretching a raster image, you get the classic fuzzy, low-res pixelation.

How to Get a Vector Version

If you need sharp, infinitely scalable emojis for a design project in Sketch, you have a couple of workarounds:

**Use an SVG Library:** Download the vector version (`.svg`) of the emoji from open-source libraries like **Twemoji** (Twitter's emoji set) or **OpenMoji**. These are built purely with vector paths.

**Apple's Alternative:** If you specifically need Apple's design style, you can use the **SF Symbols** application. Many of the symbols correspond directly to emoji concepts and copy over into Sketch as clean, native vector paths.
