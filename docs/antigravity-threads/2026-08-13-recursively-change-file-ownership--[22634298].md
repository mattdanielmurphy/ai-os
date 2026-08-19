---
title: "Recursively Change File Ownership"
date: "2026-08-13"
conversation_id: "22634298-626c-566e-94c2-2e7b52be5472"
source: "antigravity"
---

# Recursively Change File Ownership

## USER_EXPLICIT (2026-08-13T18:54:09.363027)

how to set ownership of all files in a folder and folders in a folder recursively?

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-06 16:32" -->

---
## MODEL (2026-08-13T18:54:09.363029)

To change the ownership of a folder, all its files, and all its subfolders recursively in a Unix-like system (Linux/macOS), you use the `chown` command with the `-R` (recursive) flag.

Here is the standard command structure:

Bash

```
sudo chown -R username:groupname /path/to/folder

```

Breakdown of the Command

**`sudo`**: Runs the command with administrative privileges (root), which is usually required to change file ownership.

**`chown`**: The "change owner" command.

**`-R`**: The **Recursive** flag. This tells the system to apply the change to the target directory *and* everything inside it (all files, subfolders, and files within those subfolders).

**`username:groupname`**:

`username` is the new owner.

`:groupname` is the new group (optional). If you only want to change the owner and leave the group as-is, just omit the colon and group name (e.g., `sudo chown -R username /path/to/folder`).

**`/path/to/folder`**: The target directory.

Common Variations

**Change owner only (leave group alone):**

Bash

```
sudo chown -R matthew /var/www/project

```


**Change group only (leave owner alone):**
You can use `chown` with a leading colon, or use the dedicated `chgrp` command:

Bash

```
sudo chown -R :developers /var/www/project
# OR
sudo chgrp -R developers /var/www/project

```


**Match the current logged-in user dynamically:**
If you want to assign ownership to whoever is currently logged into the terminal session, you can use the `$USER` environment variable:

Bash

```
sudo chown -R $USER:$USER /path/to/folder

```


⚠️ **Important Note:** Be very careful when using the `-R` flag with `sudo`. Running an accidental typo like `sudo chown -R user:user / usr` (with an accidental space) can alter system-critical permissions and cause OS instability. Double-check your target path before hitting Enter.

<!-- /gemini-message -->

---
