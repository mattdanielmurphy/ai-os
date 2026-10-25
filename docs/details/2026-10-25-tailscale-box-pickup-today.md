# Tailscale box to pick up today (2026-10-25)

## 17:30 Same-day pickup in Edmonton

Matt is at his parents' in Edmonton and wanted a box he could pick up today (Sunday) from a store, maybe returning it later, or something cheap enough to keep.

---

### Stores close at 6pm and have nothing cheap

- It was about 5:25pm Sunday when I checked. Memory Express is open 11am–6pm on Sundays; Canada Computers and Best Buy keep similar Sunday hours, so in-store pickup today was down to minutes.
- **Best Buy**: nothing under $800 sold by Best Buy itself (cheap mini PCs and Pis are marketplace sellers only, no pickup).
- **Canada Computers** (two Edmonton stores, Northgate and South Park): cheapest in-stock is a Gigabyte Brix N250 barebones at $249 with no RAM or SSD; the N150 Brix is sold out; renewed Lenovo M70q is $529.99. No Raspberry Pi.
- **Memory Express**: Raspberry Pi 5 8GB $199.99 (4GB out of stock) + 27W power $24.99 + case $19.99 + a microSD card, so about $260. Mini PCs start around $700. RAM prices are extreme right now (a 32GB DDR4 laptop stick is $709.99), which is why new mini PCs are so expensive.
- Memory Express blocks headless browsers; I read it through Matt's Chrome in a background tab with a light claude-control clearance (closed afterwards).
- Not checked: Walmart and Staples in-store stock (neither normally stocks cheap mini PCs in store, and both block robots).

---

### Buy-and-return isn't worth it

Nothing in stock is cheap, so buying at $250–$700 to return later costs more hassle than waiting a day for a used box. The Pi 5 kit (~$260) is also worse value than any used Lenovo Tiny.

---

### Kijiji options for tonight or tomorrow

- **$85 Lenovo M710q** (i5-7500T, 8GB, 256GB SSD, power supply) in Clarkdale Meadows: still the best; seller hasn't replied yet. https://www.kijiji.ca/v-desktop-computers/edmonton/lenovo-tiny-pc/1744063463
- **$179.98 Lenovo M73 Tiny** (i5-4570T, 8GB, 120GB SSD, Windows 11) from an Edmonton business that delivers free and only takes voice calls (number in the listing photos/description). Older 4th-gen chip but fine for an exit node; overpriced. https://www.kijiji.ca/v-desktop-computers/edmonton/no-gst-government-surplus-lenovo-tiny-desktop-w-win-11-pro-and/1742709093
- **$100 Lenovo M73 Tiny** (i5-4570T, 8GB) posted today in Sturgeon County, but it has **no drive**, so it needs an SSD too. Skip. https://www.kijiji.ca/v-desktop-computers/edmonton/mini-pc-lenovo/1745280756
- A 4th-gen i5 still handles Tailscale fine at typical home upload speeds (estimate, untested).

---

### Free option tonight

Tailscale can run as an exit node on almost anything already at his parents' house: an old laptop or desktop (Linux, Windows or macOS), an Android phone, or an Apple TV. That works tonight for $0 while the used box is sorted out.

## 17:40 Walmart, and the one-week window

Matt's original message (which reached me after the reply above) named Walmart and said he technically has a week.

---

### Walmart needs a sign-in

Walmart.ca redirected my background Chrome tab to its login page before showing any search results, so I couldn't check its stock. I don't sign in for him. Walmart stores rarely carry cheap mini PCs on the shelf, so this probably changes nothing.

---

### A week changes the plan

With a week, there's no need to buy and return. Two clean paths:
- Wait a day or two on the $85 Kijiji M710q, then fall back to the $180 Edmonton shop listing (free delivery, phone only).
- Or order the $169 HP EliteDesk 800 G3 Mini from Amazon.ca (earlier thread), which ships free and arrives within the week.
Meanwhile, an old laptop or Android phone at his parents' can be the exit node tonight for free.
