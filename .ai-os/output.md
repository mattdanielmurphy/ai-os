# Styling Fix: Dark Mode Theme Glitch Resolved

The issue with the light background colors on dark mode has been resolved!

## Cause of the Bug
The app uses classes such as `dark:bg-gray-850`, `dark:bg-gray-850/80`, `dark:border-gray-850`, and `dark:bg-gray-850/50` on several bars and modal components. However, Tailwind CSS does not natively include a `gray-850` color shade. As a result, the browser couldn't map the classes to any color, causing them to fall back to default or transparent backgrounds which appeared light/white in dark mode.

## Fix Implemented
1. **Extended Tailwind Config**: Added a custom `gray-850` color shade (`#18202f`) to the Tailwind theme config in [tailwind.config.js](file:///Users/matthewmurphy/projects/ai-os/tailwind.config.js):
   ```javascript
   theme: {
     extend: {
       colors: {
         gray: {
           850: '#18202f',
         }
       }
     },
   }
   ```
2. **Rebuilt Production Bundle**: Ran `pnpm build` to compile the new colors into the production build styling assets and refresh `dist/index.html`.
3. **Updated Ledgers & Logs**: Logged the fix in [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md) and created an agent log in `.agent-logs/`.
