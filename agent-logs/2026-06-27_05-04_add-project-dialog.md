## Goal
Support adding new projects through the interface. Clicking the `+` button in the projects list should prompt to open an existing project (using native file/folder picker) or start a new one. Starting a new project should ask for the project name, generate a git repository name (customizable by user), create the project in `~/projects`, initialize the local git repository, commit a default README.md, create a private GitHub repository using `gh` CLI, and link/push to it.

## Changes Made
1. **`src-tauri/Cargo.toml`**: Enabled the `"dialog"` feature for `tauri` dependency to enable native folder selection dialogs.
2. **`src-tauri/src/main.rs`**:
   - Added `select_directory` command using `tauri::api::dialog::blocking::FileDialogBuilder` to pick folders natively on macOS.
   - Added `create_new_project` command to create project folders under `~/projects`, initialize a local git repo, create a private repository using `gh repo create --private --source=. --remote=origin --push`, and push the initial commit.
   - Registered the two new commands in `tauri::generate_handler!`.
3. **`index.html`**:
   - Added a beautiful Tailwind CSS-styled modal overlay for adding projects.
   - Divided the modal into two clear choices: "Open Existing" and "Start New Project".
   - Created input fields for "Project Name" and "GitHub Repo Name" inside the starting form.
4. **`src/main.ts`**:
   - Wired up the custom interactive modal transitions (opacity and scale transitions).
   - Hooked up `btnChoiceExisting` to trigger Rust's `select_directory` command and append selected folders.
   - Added an event listener to the "Project Name" input that auto-generates a kebab-cased Git repository name in real-time as the user types.
   - Hooked up `btnSubmitNewProject` to invoke the `create_new_project` Rust backend, handle button disabled/loading states, and update the global project list state.
5. **`FEATURES.md`**:
   - Documented the new interactive add project flow and dialog features.

## What Worked
- Native directory picking using blocking dialog builders in Tauri worked seamlessly.
- Non-interactive creation of private GitHub repositories using the authenticating user via `gh repo create --private --source=. --remote=origin --push` worked correctly because the user is already authenticated with `gh`.
- Real-time kebab-case transformation in TypeScript correctly generates matching repository names from human-entered project names.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The blocking `FileDialogBuilder::new().pick_folder()` is executed inside the command which pauses the thread executing the Tauri command. This matches client expectations for modal selections.
- Using `gh repo create` with the `--push` flag handles both linking the remote and pushing the initial commit in a single atomic step after the repository is created.
