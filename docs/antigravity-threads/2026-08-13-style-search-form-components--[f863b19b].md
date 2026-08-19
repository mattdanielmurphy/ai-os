---
title: "Style Search Form Components"
date: "2026-08-13"
conversation_id: "f863b19b-a1b4-4094-995c-f9bd98a3731a"
source: "antigravity"
---

# Style Search Form Components

## User

Fix `.search-form` and `.btn-submit` in `app/globals.css` and `app/page.tsx`:

1. Update `.search-form` in `app/globals.css` to align input field and button inline (or keep vertical on narrow mobile, but button should be normal width, e.g. `align-self: center; width: auto; padding: 0.6rem 1.5rem;` or inline search bar flex row):

```css
.search-form {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  width: 100%;
}

.input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.btn-submit {
  background: #ffffff;
  color: #000000;
  border: none;
  cursor: pointer;
  padding: 0.6rem 1.25rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  width: auto;
  align-self: stretch;
}
```

2. Make sure button text says `"Find Music"`.

Make these edits now.

---
