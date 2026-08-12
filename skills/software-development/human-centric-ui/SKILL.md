---
name: human-centric-ui
description: "Build UIs the user's way: CSS Modules, data-ui attributes, single-component directories, no Tailwind/inline styles, Mantine component library."
version: 1.0.0
author: Hermes Agent (derived from user preferences stated across sessions)
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [frontend, css, mantine, react, ui-architecture, conventions]
    related_skills: [plan, ai-os]
---

# Human-Centric UI Architecture

Use this skill when building ANY frontend UI for the user. These rules apply across all their projects (Conduit, CockBand, StudyEngine, Piano OS, ai-os, etc.).

## Core Rules (Non-Negotiable)

### 1. Styling

- **NO Tailwind CSS, utility-class frameworks, or inline styles (`style="..."`).**
- Use standard CSS via **CSS Modules** (`ComponentName.module.css`).
- Keep presentation layout separate from logic. A human must be able to open the `.css` file and tweak margins, colors, and padding using standard web specifications.
- Exception for dynamic layout calculations (resizing splitters, panel dimensions, user-selected theme colors) — these can use inline styles, but only when absolutely necessary.
- SCSS/SASS variables (in a central `variables.scss` or `styles/` directory) are acceptable for token management.

### 2. File Organization

- Every UI component lives in its own **dedicated directory** named after the component (PascalCase).
- **One component per file.** No multi-component files. If a component needs a sub-item (like a list row), spin it out into its own folder.
- Each component directory typically contains:
  ```
  ComponentName/
  ├── ComponentName.tsx      # the component
  ├── ComponentName.module.css  # its styles
  └── index.ts               # re-export
  ```
- File structure should **mirror visual hierarchy** where practical.

### 3. DOM Tagging for Human Maintenance

- The **top-level element** of every component MUST include a `data-ui` attribute matching the component or feature name.
- Convention: `data-ui="kebab-case-component-name"` (e.g., `data-ui="floating-shell"`, `data-ui="midi-track-row"`).
- This allows human operators to inspect an element in browser DevTools and instantly grep-source-map it back to the component file.

### 4. Component Library Preference

- Use **Mantine v7** as the primary UI component library.
  - It uses standard CSS variables — compatible with CSS Modules.
  - No Tailwind dependency.
  - Import on demand: `@mantine/core`, `@mantine/hooks`, `@mantine/notifications`.
- Do NOT use shadcn/ui, Radix primitives directly, or headless UI libraries unless no Mantine equivalent exists.
- Wire up PostCSS with `postcss-preset-mantine` for proper Mantine CSS processing.

## Implementation Patterns

### Starting a new frontend project with Mantine

```bash
# After project scaffolding (Vite, Wails, etc.)
pnpm add @mantine/core @mantine/hooks @mantine/notifications @mantine/hooks
pnpm add -D postcss postcss-preset-mantine postcss-simple-vars
```

**postcss.config.cjs:**
```js
module.exports = {
  plugins: {
    'postcss-preset-mantine': {},
    'postcss-simple-vars': {
      variables: {
        'mantine-breakpoint-xs': '36em',
        'mantine-breakpoint-sm': '48em',
        'mantine-breakpoint-md': '62em',
        'mantine-breakpoint-lg': '75em',
        'mantine-breakpoint-xl': '88em',
      },
    },
  },
};
```

### Component skeleton (React + Mantine + CSS Modules)

```tsx
// FeatureWidget/FeatureWidget.tsx
import { Text } from '@mantine/core';
import classes from './FeatureWidget.module.css';

interface FeatureWidgetProps {
  title: string;
}

export function FeatureWidget({ title }: FeatureWidgetProps) {
  return (
    <div className={classes.container} data-ui="feature-widget">
      <Text className={classes.title} data-ui="feature-widget-title">
        {title}
      </Text>
    </div>
  );
}
```

```css
/* FeatureWidget/FeatureWidget.module.css */
.container {
  background: var(--app-window-bg);
  backdrop-filter: blur(var(--app-window-blur));
  border-radius: var(--mantine-radius-md);
  padding: var(--mantine-spacing-md);
}
```

### CSS variables pattern

Centralize in `src/styles/variables.scss` (or similar):

```scss
:root {
  --app-window-bg: rgba(30, 30, 35, 0.85);
  --app-window-blur: 20px;
  --app-shell-radius: 16px;
  --app-shell-padding: 12px;
  --app-font-size-lg: 16px;
  --app-border-subtle: 1px solid rgba(255, 255, 255, 0.08);
}
```

## Verification Checklist

Before claiming UI work is done, verify:

- [ ] `grep -r 'style=' src/` returns zero matches
- [ ] `grep -r 'className=.*:' src/` returns zero matches (no Tailwind utility classes)
- [ ] Every component directory has a dedicated `*.module.css` file
- [ ] Every top-level element has a `data-ui` attribute
- [ ] No multi-component files exist
- [ ] `data-ui` values are kebab-case, grep-searchable strings
- [ ] Mantine is imported from `@mantine/*` packages, not shadcn or Radix

## Pitfalls

- **"Just this once" inline styles** — resist the urge. Even one inline style sets a precedent. Route it to CSS Modules.
- **Tailwind creep** — if you scaffold with a template that includes Tailwind, strip it out immediately. Do not leave the config files sitting around.
- **Mantine classNames vs CSS Modules** — when using Mantine's `classNames` prop (not `className`), pass an object with Mantine's internal slot keys (`root`, `input`, `label`, etc.), not arbitrary class names. Use CSS Modules `classes.*` as the values.
- **PostCSS config** — Mantine v7 requires `postcss-preset-mantine` to resolve its CSS variables. Without it, Mantine components render unstyled.
- **data-ui at component root ONLY** — one per component, at the top-level wrapper. Do not spam `data-ui` on every nested div.

## See Also

- `plan` skill — for how to structure implementation plans (which follow these UI rules)
- Reference implementations: Conduit (`~/projects/ai-os/conduit`) uses this architecture