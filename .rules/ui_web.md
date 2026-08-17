# Web Application & UI Architecture Rules

- **No Default Dark Mode Invariant:** Generated HTML documents, tools, and UI prototypes MUST default to clean light themes (or adapt dynamically via system color scheme). Never force dark mode unless the user explicitly asks for it.
- **Strict Span-Only Styling Invariant**: For `thread.md`, conversation artifacts, and custom markdown layouts, agents MUST use `<span>` tags exclusively (with `display: block;`, `white-space: pre-wrap;`, and inline CSS) for all layout and styling containers. NEVER use `<div>`, `<p>`, or other block HTML tags. Use `<br>` or `<br><br>` tags within `<span>` to preserve line breaks and paragraph spacing without breaking out of the inline span container.
- **Architectural Preservation**: When debugging or refactoring established custom UI layouts, CSS modules, or templates, agents MUST isolate the exact root cause while strictly preserving existing styling and DOM structures. No unilateral style simplification.
- **Technology Stack**: Use HTML for structure, Javascript/Typescript for logic, and Vanilla CSS or CSS Modules for maximum control. Avoid TailwindCSS unless explicitly requested.
