# Marketplace mini PCs (2026-10-25)

## 15:40 Marketplace search for a Tailscale exit-node mini PC

Asked (coordinator brief, then Matt: "did you check Marketplace?"): search Facebook Marketplace Edmonton for used Lenovo Tiny / OptiPlex Micro / HP Mini, i5 6th gen+, 8GB+, storage + adapter; cheapest 5 vs the Kijiji M710q $85.

---

### Method that works

- Plain curl gets HTTP 400. Headless Chrome (`--headless=new --dump-dom`, throwaway profile in `tmp/marketplace/profile`) renders the public search with no login, and the page embeds listing JSON (id, price, city, title, creation_time).
- Saved as `scripts/marketplace.py search <queries...> [--max-price N] [--details N] [--near any]`. Filters to Edmonton-area cities by default.
- `&sortBy=price_ascend` breaks it when logged out (returns ~0 results). Removed.
- Never used Matt's visible Chrome, so no claude-control ask was needed. Read only; no sellers contacted.
- Descriptions read from item pages (`redacted_description`).

---

### Cheapest five that meet spec

| Price | Listing | CPU | RAM | Storage | Adapter | Area | Listed |
|---|---|---|---|---|---|---|---|
| $129 | [HP EliteDesk 800 G2 Mini](https://www.facebook.com/marketplace/item/998462592730144/) (dealer, 3-mo warranty) | i5 (G2 = 6th gen, model unstated) | 8GB | 128GB SSD | not mentioned | Edmonton | 2026-05-17 |
| $150 | [HP ProDesk 400 G3 Mini](https://www.facebook.com/marketplace/item/1286410736811282/) (Uniway, Sherwood Park store) | i5 7th gen | 8GB | 256GB SSD | not mentioned | Edmonton/Sherwood Park | 2026-06-21 |
| $155 | [Lenovo M910q](https://www.facebook.com/marketplace/item/1507841997776009/) | i5-6500T (4-core) | 16GB | 256GB SSD | yes, Lenovo 65W | Edmonton northside | 2026-09-01 |
| $165 | [Lenovo M910q](https://www.facebook.com/marketplace/item/1023341490516805/) | i5-6500T (4-core) | 16GB | 256GB SSD | yes, Lenovo 65W | Edmonton | 2026-08-10 |
| $170 | [HP ProDesk 600 G3 Mini](https://www.facebook.com/marketplace/item/1514230740434509/) | i5-6500T (4-core) | 16GB | 256GB | not mentioned | Edmonton | 2026-06-27 |

Next: $175 [M710q i5 7th gen 8GB 256GB](https://www.facebook.com/marketplace/item/1422498479729327/) (2026-09-01).

Rejected: $99 HP EliteDesk (i5-4590T, 4th gen), $150 Lenovo Tiny Spruce Grove (Pentium G3220), $169 Lenovo Tiny (i5-3470T), $90 ThinkCentre Mini (i3), $99 "Tiny/Mini/Micro in stock" (dealer ad, no specific unit).

---

### Verdict versus Kijiji

Kijiji M710q i5-7500T 8GB 256GB + PSU at $85 (Sherwood Park) stays the best: $44+ cheaper than anything here that meets spec. Best Marketplace pick if Kijiji falls through: the $155 M910q (16GB, adapter confirmed). Older listings (May/June) may be gone.

Untested: whether listings are still live beyond the "not sold/pending" flags; dealer ads may be stale.
