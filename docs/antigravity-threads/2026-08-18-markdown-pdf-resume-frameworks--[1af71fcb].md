---
title: "Markdown PDF Resume Frameworks"
date: "2026-08-18"
conversation_id: "1af71fcb-c049-456b-b443-433d00df52fb"
source: "antigravity"
---

# Markdown PDF Resume Frameworks

## User

your attempt at making a PDF resume is a complete failure.
That output failed because the agent did what inexperienced web designers do when asked to "style" a document: it added amateur web gimmicks (blue square icons `▮`, rounded blue card borders, centered badge pills) while **completely ignoring the core layout issue**—the text is still stretching across an 8.5-inch page with zero structural rhythm.

Here are the best, battle-tested frameworks and templates designed specifically for the **`Markdown / Structured Text ➔ PDF`** pipeline that eliminate CSS hacks entirely.

---

### 1. RenderCV (The Modern Gold Standard CLI)
**RenderCV** is an open-source CLI tool built specifically for engineers and executives. You feed it structured text (YAML/Markdown), and it renders pixel-perfect PDFs using high-grade typography engines (Typst/LaTeX).

* **How the pipeline works:** `resume.yaml` ➔ `rendercv render resume.yaml` ➔ `resume.pdf`
* **Built-in Templates:**
  1. **`classic`:** Deep navy/charcoal executive layout with clean horizontal rules and balanced margin geometry.
  2. **`moderncv`:** The classic European/corporate standard with an integrated left date-rail.
  3. **`sb2nov`:** The standard Ivy League / executive single-column layout—clean, tight, zero visual clutter, and 100% ATS-compliant.
  4. **`harvard`:** Traditional, high-authority serif typography.
* **Why it fixes your issue:** It calculates optical kerning, vertical page budgeting, and margins automatically. It is physically impossible to produce misaligned boxes or stretched text.

---

### 2. Typst (`brilliant-cv` or `modern-cv`)
**Typst** is the modern Rust-based successor to LaTeX. It installs as a single tiny binary (`brew install typst` or `npm install -g typst`) and compiles in under 50ms.

* **How the pipeline works:** `resume.typ` ➔ `typst compile resume.typ resume.pdf`
* **Top Templates in the Typst Universe:**
  1. **`brilliant-cv` / `modern-cv` (Awesome-CV port):** The gold standard for high-profile technical directors and executives. Features a crisp name banner, metadata icons, and clean milestone layouts.
  2. **`basic-resume` (Jake's Resume / Ivy League):** Minimalist, high-density, authoritative.
  3. **`modernpro-cv`:** Supports true two-column compact executive formats where skills and credentials sit neatly on the side.

Pick one of the above and we'll trial the templates. Might as well just render the resume with the built-in templates all at once and I'll pick my fav

---

## Assistant

The batch rendering pipeline has been initiated. RenderCV is now compiling Darryl Murphy's executive master CV across all built-in typography themes (`classic`, `sb2nov`, `moderncv`, `harvard`, `engineeringresumes`, `engineeringclassic`, `ember`, `ink`, and `opal`).

I will report the results with direct file links and preview images as soon as the rendering completes.

The batch compilation across all 9 RenderCV themes is actively running in the background. It has already finished `classic`, `sb2nov`, `moderncv`, and `harvard`, and is compiling the remaining themes (`engineeringresumes`, `engineeringclassic`, `ember`, `ink`, `opal`).

I will output the direct links and file paths as soon as the full batch finishes in just a moment.

The **RenderCV (Typst Engine)** pipeline is now set up and configured. 

The master CV data has been converted to the standard structured YAML format in [`darryl_murphy_cv.yaml`](file:///Users/matt/projects/job-applier/darryl_murphy_cv.yaml). Darryl Murphy's executive master CV was compiled across **all 9 built-in typography themes** simultaneously.

---

### Rendered Theme Comparison & PDF Links

| Theme | Typography & Structure Style | Direct PDF Link |
| :--- | :--- | :--- |
| **`classic`** | Deep navy/charcoal executive layout with horizontal rules and balanced margin geometry. | [Open `classic` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV.pdf) |
| **`sb2nov`** | Ivy League / executive single-column layout—clean, high-density, zero clutter, 100% ATS-pure. | [Open `sb2nov` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/sb2nov/Darryl_Murphy_CV.pdf) |
| **`moderncv`** | Corporate standard with integrated left date-rail and clean section dividers. | [Open `moderncv` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/moderncv/Darryl_Murphy_CV.pdf) |
| **`harvard`** | Traditional, high-authority serif typography with formal academic/executive hierarchy. | [Open `harvard` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/harvard/Darryl_Murphy_CV.pdf) |
| **`engineeringresumes`** | High-density technical layout designed for maximum scannability and compact margins. | [Open `engineeringresumes` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/engineeringresumes/Darryl_Murphy_CV.pdf) |
| **`engineeringclassic`** | Clean horizontal split with bold company headers and structured metrics. | [Open `engineeringclassic` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/engineeringclassic/Darryl_Murphy_CV.pdf) |
| **`ember`** | Modern executive typography with refined warm accents. | [Open `ember` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/ember/Darryl_Murphy_CV.pdf) |
| **`ink`** | High-contrast, razor-sharp sans-serif layout. | [Open `ink` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/ink/Darryl_Murphy_CV.pdf) |
| **`opal`** | Contemporary balanced executive layout with clean vertical spacing. | [Open `opal` PDF](file:///Users/matt/projects/job-applier/rendered_resumes/opal/Darryl_Murphy_CV.pdf) |

---

### Folder Outputs
Each theme folder under [`rendered_resumes/`](file:///Users/matt/projects/job-applier/rendered_resumes/) contains:
- **`Darryl_Murphy_CV.pdf`**: The compiled PDF document.
- **`Darryl_Murphy_CV_*.png`**: High-resolution rendered page preview images.
- **`Darryl_Murphy_CV.typ`**: The raw Typst typesetting source file.
- **`Darryl_Murphy_CV.md` & `.html`**: Structured Markdown & HTML exports.

### Making Adjustments or Switching Defaults
To re-render any theme or customize margins, fonts, or colors:
```bash
uvx --from "rendercv[full]" rendercv render darryl_murphy_cv.yaml --design.theme <theme_name>
```

Let me know which template layout you prefer, or if you'd like to fine-tune spacing, font pairings, section order, or page-budgeting for a specific target page count (e.g. strict 2-page or 3-page).

---
*Reference: *

---

## User

# Comprehensive Directive: Fix RenderCV YAML, Typography, and Layout ('classic' Theme)

We are finalizing the resume using RenderCV with the **`classic`** theme. 

The previous outputs suffered from severe typography and layout bugs:
1. Lines of text were stretched full-width (95–110 characters/line), causing reading fatigue.
2. The Executive Summary was 3 huge, unreadable paragraphs.
3. The Education section had catastrophic vertical hyphenation ("Cer- / tified / Jour- / ney- / man...") due to bad YAML field mapping.
4. The content sprawled uncontrollably into 3 pages.

You must refactor the input YAML and the RenderCV `design` configuration according to the strict specifications below.

---

### 1. RenderCV `design` Configuration Block
Configure the YAML `design` section to fix page margins, line spacing, and typography:

```yaml
design:
  theme: classic
  font: "Source Sans 3"  # Clean, modern, high-readability sans-serif
  font_size: 9.5pt
  page:
    size: letter
    top_margin: 0.75in
    bottom_margin: 0.75in
    left_margin: 0.85in   # Pulls margins inward to fix the long line-length issue
    right_margin: 0.85in
    show_page_numbering: true
  colors:
    name: rgb(15, 23, 42)          # Deep Navy Slate
    headline: rgb(30, 58, 138)      # Professional Slate Blue
    body: rgb(30, 41, 59)          # Charcoal Slate
    section_titles: rgb(15, 23, 42)
  sections:
    line_spacing: 1.45
```

---

### 2. Restructure the Executive Summary
Do not dump 3 edge-to-edge paragraphs. Structure the Executive Summary into:
1. **A tight 3-line overview paragraph** highlighting 40+ years of megaproject leadership and dual mastery (Red Seal Master Electrician + Stage-Gate Project Controls).
2. **A 3-part Key Metrics summary** (formatted cleanly with bullet points or bold lead-ins):
   - **Workforce Scale:** Managed peak direct & sub-craft workforces up to 770+ personnel.
   - **Capital Stewardship:** Direct oversight of electrical & infrastructure scopes up to $185M+ on $40B+ megaprojects.
   - **Safet
<truncated 610 bytes>
Pulling & High-Voltage Terminations, Grounding Grids, SCADA & Traction Power (TPSS).
- **Quality Assurance & Regulatory Compliance:** Quality Management Systems (QMS), Inspection & Test Plans (ITPs), Non-Conformance Resolution (NCR/CAR Closure), NDE Surveillance, Safety Codes Officer (SCO) Interface.
- **Project Controls & Completions Systems:** Stage-Gate Governance (Gates 0–4), SAP ME51N Procurement, Orbit CM, Omega PIMS, WinPCS, MCPlus, Cognibox HSE Risk Assessment.

---

### 4. Experience Section Formatting
- Ensure every job entry is mapped so that:
  - **Company & Role:** Positioned on the left in bold/semi-bold.
  - **Location & Date Range:** Positioned cleanly on the right.
- Ensure bullet points start with strong action verbs and are concise (2 lines max per bullet point to maintain clean rhythm).

---

### 5. Fix Education & Credentials (Eliminate Syllable Wrapping Bug)
Fix the field mapping so that degree titles are NEVER placed in the narrow date column:

**Correct Education Mapping:**
- **Institution:** Northern Alberta Institute of Technology (NAIT)
- **Area / Degree:** Electrical Apprenticeship & Technical Training
- **Additional Details:** Certified Journeyman & Master Electrician
- **Location:** Edmonton, AB

**Credentials & Licenses Section (Structured List):**
- **Interprovincial Red Seal Master Electrician:** RSE #618435 (Active & in good standing through 2027)
- **Skilled Trades Ontario:** Certificate of Qualification & Master Electrician License (ID: 13284737 / C of Q: 000227088)
- **Specialized Safety & Leadership Training:** Cognibox HSE Risk Assessment, Industrial Fall Protection, Confined Space Entry, LOTO & HV Switching Safety, CSTS-09, First Aid/CPR, WHMIS

---

### 6. Strict 2-Page Target
Tune the section spacing and padding so the resume fills **exactly 2 pages** (ending cleanly at the bottom of Page 2 with Education & Credentials). Ensure zero spillover to a 3rd page.

---

## Assistant

The RenderCV YAML and typography design block have been refactored and recompiled using the **`classic`** theme.

### Direct Links
- **Compiled PDF:** [`Darryl_Murphy_CV.pdf`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV.pdf)
- **Source YAML:** [`darryl_murphy_cv.yaml`](file:///Users/matt/projects/job-applier/darryl_murphy_cv.yaml)
- **Page 1 Preview:** [`Darryl_Murphy_CV_1.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_1.png)
- **Page 2 Preview:** [`Darryl_Murphy_CV_2.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_2.png)

---

### Key Adjustments Implemented

1. **Page Margins & Typography Geometry**:
   - Left/right margins set to **`0.85in`** (pulling line lengths into optimal 70–80 character reading width).
   - Top/bottom margins set to **`0.65in`** with `Source Sans 3` at **`9.5pt`** (body) and **`22pt`** (name).
   - Executive color scheme applied: Deep Navy Slate (`rgb(15, 23, 42)`), Slate Blue (`rgb(30, 58, 138)`), and Charcoal Slate body text (`rgb(30, 41, 59)`).
   - Page footers enabled for clean page numbering (`Darryl Murphy — 1/2`).

2. **Executive Summary Restructuring**:
   - Replaced multi-paragraph walls of text with a concise 3-line overview highlighting 40+ years of megaproject execution and dual mastery (Red Seal Master Electrician + Stage-Gate Project Controls).
   - Added 3 highlighted key metrics: **Workforce Scale** (770+ crew), **Capital Stewardship** ($185M+ packages on $40B+ projects), and **Safety Leadership** (Goal Zero / TRIF 0.00).

3. **Core Competencies Restructuring**:
   - Formatted into 4 distinct, scannable categories with bold lead-ins: *Construction Leadership & Site Execution*, *High-Voltage & Power Systems*, *Quality Assurance & Regulatory Compliance*, and *Project Controls & Completions Systems*.

4. **Experience Section Rhythm**:
   - Company & Position cleanly anchored on the left; Location and Date Range anchored on the right.
   - Bullet points trimmed to tight, active-verb lead statements (maximum 2 lines per bullet).

5. **Fixed Education & Credentials (Hyphenation Bug Eliminated)**:
   - Moved "Certified Journeyman & Master Electrician" into `highlights` under NAIT, eliminating the narrow 1cm `degree-column` squeeze and vertical syllable hyphenation.
   - Restructured *Credentials and Licenses* as clean, labeled full-width items.

6. **Strict 2-Page Target**:
   - Spacing tuned so Page 2 ends cleanly at the bottom with Education and Credentials, resulting in **zero 3rd-page spillover**.

---
*Reference: *

---

## User

# Final Polish: Vertical Spacing, Typography Hierarchy & Metadata Clean-Up

We are executing the final polish pass on the RenderCV `classic` configuration. Apply the following spacing, hierarchy, and layout updates:

---

### 1. Increase Vertical Spacing & Line Height (Breathing Room)
Take advantage of the available vertical space on Pages 1 and 2:
- **Line Height / Leading:** Increase to **1.5** (or `1.55`) across all body text and bullet points.
- **Section Heading Spacing:** Add `5pt–6pt` space above section headings (`Executive Summary`, `Core Competencies`, `Experience`, `Education`, `Credentials`).
- **Entry Spacing:** Add `4pt–6pt` between individual job blocks so they do not feel glued together.
- **Bullet Spacing:** Add `2pt` bottom margin between bullet items for effortless readability.

---

### 2. Separate Company and Job Title onto Two Clean Rows
In the **Experience** section, do not place the Company Name and Job Title on the same line separated by a comma. Split them into a 2-row header for each role:

- **Row 1:** **[Company Name]** (Bold, Primary Slate) <-----------------> **[Location]** (Right-aligned)
- **Row 2:** *[Job Title / Portfolio Scope]* (Italic, Accent Color) <----> *[Date Range | Duration]* (Right-aligned)

*Example:*
**Rio Tinto / SNC-Lavalin**                                            Kitimat, BC
*Senior Project Manager / Lead Field PM – Smelter Reset Portfolio*       Oct 2022 – May 2026 (3 yrs 8 mos)

This completely eliminates awkward title line-wrapping (e.g., "Coordi- / nator").

---

### 3. Add Bullet Points to Competencies & Credentials
- **Core Competencies:** Add a standard bullet point (`•`) in front of each of the 4 category blocks (*Construction Leadership & Site Execution*, *High-Voltage & Power Systems*, etc.) so they read as distinct pillars.
- **Credentials and Licenses:** Add a standard bullet point (`•`) in front of the 3 credential entries on Page 2 for visual consistency with the rest of the document.

---

### 4. Verify 2-Page Balance
With the taller line height and entry spacing, the content should gracefully fill both pages from top to bottom, ending cleanly at the bottom of Page 2 with zero spillover onto a 3rd page.

---

## Assistant

The final polish pass on the **`classic`** theme has been executed and compiled.

### Direct Links
- **Compiled 2-Page PDF:** [`Darryl_Murphy_CV.pdf`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV.pdf)
- **Source YAML:** [`darryl_murphy_cv.yaml`](file:///Users/matt/projects/job-applier/darryl_murphy_cv.yaml)
- **Page 1 Preview:** [`Darryl_Murphy_CV_1.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_1.png)
- **Page 2 Preview:** [`Darryl_Murphy_CV_2.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_2.png)

---

### Adjustments in this Pass

1. **Two-Row Role Headers (Zero Awkward Line Wrapping)**:
   - Configured custom template mapping so each role uses a clean 2-row layout:
     - **Row 1:** `**[Company Name]**` (Bold) on the left, `[Location]` on the right.
     - **Row 2:** `*[Job Title / Portfolio Scope]*` (Italic) on the left, `*[Date Range | Duration]*` on the right.

2. **Bullet Points for Competencies & Credentials**:
   - Added standard bullet formatting (`•`) across all 4 **Core Competency** pillars.
   - Added bullet points (`•`) to all 3 **Credentials & Licenses** entries for visual rhythm and scanning consistency.

3. **Vertical Rhythm & Leading**:
   - Increased line height (`typography.line_spacing: 0.55em`) for comfortable body leading.
   - Added section heading breathing room (`space_above: 0.38cm`) and inter-entry padding (`space_between_regular_entries: 0.52em`).
   - Added bullet bottom margin (`space_between_items: 0.06cm`).

4. **Strict 2-Page Balance**:
   - Adjusted top/bottom margins (`0.52in`) and header spacing (`0.35cm`) so the entire 40+ year executive profile, 8 major career roles, education, and trade licenses fill **exactly 2 pages** with zero third-page overflow.

---
*Reference: *

---

## User

# Final Calibration: Micro-Spacing & Visual Polish (Strict 2-Page Lock)

The layout, typography, and hierarchy are now spot on. We just need a minor calibration to reclaim the remaining ~0.5" of dead space at the bottom of both pages without spilling onto a 3rd page.

Apply these exact micro-adjustments:

---

### 1. Line-Height & Vertical Rhythm (The "Goldilocks" Setting)
- **Body & Bullet Line-Height:** Set to **1.42** (or `1.45`). *(This avoids the tight compression without overshooting into 3 pages).*
- **Space Between Job Entries:** Add **3pt to 4pt** between each job block.
- **Space Above Section Titles:** Add **3pt to 4pt** before each horizontal section divider (`Executive Summary`, `Core Competencies`, `Experience`, `Education`, `Credentials`).

---

### 2. Minor Typography Consistency Checks
- **Job Title Styling:** Ensure all job titles across both Page 1 and Page 2 use consistent styling (*Italic / Slate*).
- **NAIT Entry (Page 2):** Ensure `Electrical Apprenticeship & Technical Training` does not hyphenate ("Techni- / cal"). If needed, adjust the entry field so it sits cleanly on one line.

---

### 3. Page Budget Rule
Ensure Page 1 cleanly ends after the **Fluor / JGC Fluor JV / LNG Canada** entry, and Page 2 fills naturally down to the bottom with **Credentials and Licenses**, resulting in a perfect 2-page document.

---

Please let me know exactly where to find the CSS lines you're editing so I can fine-tune them if I want, as well as the command to re-render

---

## Assistant

The final calibration pass has been applied, locking the layout to a **strict, balanced 2-page document**.

### Direct Links
- **Compiled 2-Page PDF:** [`Darryl_Murphy_CV.pdf`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV.pdf)
- **Source YAML:** [`darryl_murphy_cv.yaml`](file:///Users/matt/projects/job-applier/darryl_murphy_cv.yaml)
- **Page 1 Preview:** [`Darryl_Murphy_CV_1.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_1.png)
- **Page 2 Preview:** [`Darryl_Murphy_CV_2.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_2.png)

---

### Page Budget & Layout Breakdown

- **Page 1:** Executive Summary ➔ 4 Core Competency Pillars ➔ **Rio Tinto / SNC-Lavalin** ➔ **Univex / Hydro One** ➔ **Fluor / JGC Fluor / LNG Canada** (cleanly anchors the bottom of Page 1).
- **Page 2:** **Western Pacific Enterprises / TransEd (LRT)** ➔ **Jacobs / NWR (Sturgeon Refinery)** ➔ **Fluor / Imperial Oil (Kearl Lake)** ➔ **PPEC / Syncrude** ➔ **Darmicon Electric** ➔ **Education (NAIT 2-row)** ➔ **Credentials & Licenses** (fills cleanly down to the footer).

---

### Where the Typography & Spacing Controls Live

In RenderCV, styling is controlled directly via the `design:` block at the bottom of [`darryl_murphy_cv.yaml`](file:///Users/matt/projects/job-applier/darryl_murphy_cv.yaml#L103-L156):

```yaml
design:
  theme: classic
  page:
    size: us-letter
    top_margin: 0.50in      # Page top margin
    bottom_margin: 0.50in   # Page bottom margin
    left_margin: 0.80in     # Lateral margin (controls line width / reading length)
    right_margin: 0.80in
    show_footer: true       # Page numbering (e.g. Darryl Murphy — 1/2)
  colors:
    name: rgb(15, 23, 42)          # Deep Navy Slate
    headline: rgb(30, 58, 138)      # Professional Slate Blue
    body: rgb(30, 41, 59)          # Charcoal Slate body text
    section_titles: rgb(15, 23, 42)
  typography:
    line_spacing: 0.54em    # Goldilocks leading (~1.45 line-height)
    font_size:
      body: 9.3pt           # Body / bullet size
      name: 21pt
      headline: 9.3pt
      connections: 8.8pt
      section_titles: 1.18em
  section_titles:
    space_above: 0.44cm     # Space above each section title divider
    space_below: 0.18cm     # Space below each section title divider
  sections:
    space_between_regular_entries: 0.62em   # Spacing between individual job blocks
    space_between_text_based_entries: 0.26em # Spacing between summary/competency lines
  entries:
    highlights:
      space_above: 0.08cm   # Space between title row and first bullet
      space_between_items: 0.08cm # Bottom margin between bullet items
  templates:
    experience_entry:       # Two-row layout: Company/Location + Title/Dates
      main_column: |-
        **COMPANY**
        *POSITION*
        SUMMARY
        HIGHLIGHTS
      date_and_location_column: |-
        LOCATION
        DATE
    education_entry:        # Two-row layout for NAIT: Institution/Location + Field
      main_column: |-
        **INSTITUTION**
        *AREA*
        SUMMARY
        HIGHLIGHTS
      degree_column: ''
      date_and_location_column: |-
        LOCATION
        DATE
```

---

### Command to Re-Render

Whenever you edit `darryl_murphy_cv.yaml`, run this command in terminal to re-generate the PDF and PNGs:

```bash
uvx --from "rendercv[full]" rendercv render darryl_murphy_cv.yaml -o rendered_resumes/classic
```

---
*Reference: *

---

## User

can you set up a file watcher real quick to auto-re-render when I edit yaml?

---

## Assistant

The live file watcher is now **active and running in the background**. 

Whenever you save changes to [`darryl_murphy_cv.yaml`](file:///Users/matt/projects/job-applier/darryl_murphy_cv.yaml), the pipeline will automatically re-render the PDF and PNG previews in `rendered_resumes/classic/` within ~1 second.

---

### How to Run or Restart the Watcher Manually

You can also trigger or run the live watcher anytime from the terminal via any of the following:

```bash
# Option 1: Using the helper script
./watch.sh

# Option 2: Using Bun
bun run watch

# Option 3: Direct CLI invocation
uvx --from "rendercv[full]" rendercv render darryl_murphy_cv.yaml -o rendered_resumes/classic -w
```

---
*Reference: *

---

## User

the "connections" are blue and I don't see an entry in yaml for it. I want no colors, just monochrome

---

## Assistant

The colors have been switched to **100% pure monochrome** (no blue, no accents).

### Direct Links
- **Compiled Monochrome PDF:** [`Darryl_Murphy_CV.pdf`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV.pdf)
- **Page 1 Preview:** [`Darryl_Murphy_CV_1.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_1.png)
- **Page 2 Preview:** [`Darryl_Murphy_CV_2.png`](file:///Users/matt/projects/job-applier/rendered_resumes/classic/Darryl_Murphy_CV_2.png)

---

### Why Connections & Links Were Blue

RenderCV's `classic` theme has a default link and connection icon color (`rgb(0, 79, 144)`). Because `connections` and `links` weren't explicitly set in the YAML `colors` map, RenderCV fell back to its default blue.

In [`darryl_murphy_cv.yaml`](file:///Users/matt/projects/job-applier/darryl_murphy_cv.yaml#L113-L122), all color keys are now explicitly set to pure monochrome:

```yaml
  colors:
    name: rgb(0, 0, 0)
    headline: rgb(0, 0, 0)
    body: rgb(0, 0, 0)
    section_titles: rgb(0, 0, 0)
    connections: rgb(0, 0, 0)   # Controls phone/email icons & text
    links: rgb(0, 0, 0)         # Controls clickable hyperlinks
    footer: rgb(80, 80, 80)     # Subtle neutral gray page numbers
    top_note: rgb(80, 80, 80)
```

The live file watcher is active and listening in the background.

---
*Reference: *

---
