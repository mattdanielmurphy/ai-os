---
title: "Implement Client-Side Form Submission"
date: "2026-08-12"
conversation_id: "c86477ab-46e6-4834-8820-b048cac4a093"
source: "antigravity"
---

# Implement Client-Side Form Submission

## User

Modify `app/page.tsx` to handle client-side form submission.
When the user submits the search form with a pasted URL or text input:
- Prevent default form submission.
- Extract the input value. If trimmed value is non-empty, navigate via router or window.location (`window.location.href = '/' + encodeURIComponent(trimmed)` or `router.push('/' + encodeURIComponent(trimmed))`).

Target file: /Users/matt/projects/music-cross-linker/app/page.tsx

---

## Assistant

The requested modifications have been applied to `/Users/matt/projects/music-cross-linker/app/page.tsx`.

- Added `"use client"` directive.
- Integrated `useRouter` hook and `FormEvent` type.
- Implemented `handleSubmit` function:
    - Prevents default form submission.
    - Extracts input via `FormData`.
    - Navigates to `/<encoded-input>` if the input is non-empty after trimming.
- Updated the form to call `handleSubmit` and added `name="search"` to the input element.

---
