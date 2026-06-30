# Added "Open in Finder" Button

I have updated the project sidebar to include a new "Open in Finder" button next to each project.

- A folder icon (📁) now appears when hovering over a project in the left sidebar.
- Clicking this button will open the project's folder using Tauri's native `open()` integration.
- The root project (which normally hides the delete button) will also display the folder button so you can open it in Finder as well.

The UI changes are implemented in [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts). You can run the app using `pnpm tauri dev` or `npm run dev` to test the new functionality!
