## Goal
The user requested enforcing a new "Human-Centric UI Architecture Rules" protocol. This mandated the removal of Tailwind CSS in favor of standard, vanilla CSS, organizing components into dedicated directories, and adding descriptive `data-ui` attributes to top-level elements for debugging discoverability. For this specific session, the primary focus was explicitly scoped to the styling migration (removing Tailwind and restoring semantic CSS) rather than immediately migrating the entire monolithic application into separated component directories.

## Changes Made
- **`AG_CONTEXT.md`**: Appended the new Human-Centric UI rules to ensure future agents follow the protocol for styling, file organization, and DOM tagging.
- **`package.json`**: Removed `tailwindcss`, `postcss`, `autoprefixer`, and `@tailwindcss/typography` from `devDependencies`.
- **`tailwind.config.js` & `postcss.config.js`**: Moved to `~/.Trash/`.
- **`index.html`**: Completely refactored to remove all Tailwind utility classes. Replaced them with clean, semantic classes (e.g., `projects-sidebar`, `top-header-bar`, `engine-selector`) and injected the required `data-ui` tags to mirror the component hierarchy.
- **`src/styles.css`**: Built a new vanilla CSS file using CSS variables for theme handling (light/dark mode) and standard semantic classes to maintain the exact visual design of the original Tailwind layout.
- **`src/main.ts`**: Replaced all dynamic injections of Tailwind classes (like `border-blue-500/30`) with new standardized CSS class modifiers (e.g., `thread-item-active`, `pause-btn-running`).

## What Worked
- Clean extraction of 190+ Tailwind utility classes into a unified CSS structure.
- Implementation of semantic class-naming conventions that adhere to standard vanilla CSS paradigms.
- DOM tagging `data-ui` successfully applied to all layout groups.

## What Didn't Work / Known Issues
- Fully refactoring the single `index.html` and 3000-line `main.ts` into individual `PascalCase` component directories (e.g., `src/components/ProjectsSidebar/ProjectsSidebar.module.css`) was deferred. The user explicitly noted: "But frankly all I care about in terms of this project right now is the styling. Otherwise it’s a big change I think." As a result, the code remains centrally located in `index.html` and `main.ts`, but future features should be built in isolated directories with scoped `.module.css`.

## Architecture Notes
- The application relies heavily on dynamic element creation (`document.createElement`) in `main.ts`, manipulating `className` strings for state changes (like active thread selections or engine toggling). Modifying styles requires keeping `main.ts` synced with the new vanilla CSS classes.
- Vite natively supports CSS modules, so when components are properly split into directories in the future, standard imports like `import styles from './Component.module.css'` will work seamlessly without extra bundler configuration.
