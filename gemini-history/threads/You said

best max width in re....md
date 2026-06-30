[2026-06-29 23:50] User:
best max width in rems for readability?

basically max line length, or rather ideal line length for readability

---

[2026-06-29 23:50] Assistant:
For optimal readability, the ideal line length is generally **45 to 75 characters per line** (including spaces). This is often considered the typographic "sweet spot" because it prevents the eye from getting too tired scanning long lines or breaking rhythm with frequent jumps on short ones.

When translating this rule of thumb into `rem` units (assuming the standard browser default base of 1rem=16px), the best `max-width` range is **`30rem` to `45rem`**.

Here is how that breaks down based on your target layout:

The Breakdown

**`30rem` to `35rem` (~480px – 560px):** Yields a tighter, highly scannable line length (around 45–55 characters). This works incredibly well for multi-column layouts, side blogs, or denser technical documentation where quick scanning is a priority.

**`38rem` to `40rem` (~608px – 640px):** The absolute sweet spot for long-form reading (around 60–70 characters). It hits the exact middle of the ideal range and feels natural for essays, articles, and documentation.

**`45rem` (~720px):** The upper limit for standard body text (around 75–80 characters). If you go much wider than this without increasing the `font-size` or `line-height`, the text can begin to feel like a wall.

Implementation Tip using `ch`

While `rem` is excellent for keeping your layout bound to the root font scale, you can also use the **`ch` (character) unit** for maximum precision. 1`ch` is equal to the width of the "0" glyph in your chosen typeface.

CSS

```
.article-body {
  /* Safely caps the width to roughly 65 characters wide */
  max-width: 65ch; 
  width: 100%;
}

```


If you stick with `rem`, setting your main text container to `max-width: 40rem;` is an excellent, bulletproof baseline for long-form reading.
