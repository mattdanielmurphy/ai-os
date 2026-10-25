# Amazon.ca mini PC price check (2026-10-25)

## 14:45 Cheapest 6th–8th gen mini PCs, Edmonton delivery

**Asked (via coordinator):** live Amazon.ca prices for used 1L business minis (Lenovo Tiny, OptiPlex Micro, HP Mini), with 6th–8th gen i3/i5, 8GB+, adapter. List the 5 cheapest and save the method as a script.

**How:** plain curl from the Mac (desktop Chrome UA, en-CA). There was no captcha. Amazon sets the location from the home IP ("Delivering to Edmonton T6G"), so its FREE shipping quotes are real for Edmonton. 9 searches gave 297 unique ASINs. I filtered out accessories and anything 4th gen, 4GB, SFF or tower, then fetched product pages for the cheapest ~17 to confirm the buy-box price, seller and seller rating (/sp?seller=).

**Cheapest 5 (all Amazon Renewed, FREE shipping to T6G):**
1. $169.00 B0G45FZ6GD: HP EliteDesk 800 G3 Mini, "i5-6500" (probably 6500T), 8GB, 128GB SSD. AR System, 87% positive (60 ratings). Delivery Oct 28–30.
2. $169.99 B0G45F7JM7: HP ProDesk 600 G2 Mini, i5-6500T, 8GB, 256GB SSD. Ville Technologique, **60% positive** (93). Delivery Oct 29–Nov 2.
3. $179.00 B082MPZ839: HP ProDesk 600 G2 Mini, i3-6100T, 8GB, 256GB SSD. AR System 87%.
4. $194.00 B0G45D9B92: HP EliteDesk 800 G3 Mini, i5-6500T, 8GB, 256GB SSD. AR System 87%.
5. $196.00 B07J2TFW5T: HP EliteDesk 800 G2 Mini, i5-6500T, 8GB, 240GB SSD. AR System 87%.

Next up: $198 B0FX4LJ783 (ProDesk 600 G3 Mini, i5-6500, 256GB, Ville 60%) · $199.99 B07PP8SBC3 (OptiPlex 3060 Micro, i3-8100T, 8GB/128GB, TecnoCanada 88%/185) · $208 B0G45FB1H5 (800 G3 Mini, i5-7500T, 256GB, AR System) · $214.90 B07XFH6YXZ (M910q, i5-6500T, 256GB, AR System).
Requested ASINs: B0G45FVMS1 $229.99 (TecnoCanada) · B08G1XKHPB $300 (M720q, i5-8500T, 16GB, 61% seller) · **B07QQZSDLB returns 404** (delisted).

**Adapter and storage:** every listing above has storage. Amazon Renewed guarantees "accessories equivalent to those that shipped in the box when new" (power adapter, possibly non-original). Only a few listings say "power cord/supply" outright.

**Caveats:** the G2 models are 6th gen Skylake, which meets the spec but is the oldest allowed. The cheapest Lenovo Tiny is the M910q at $214.90, and the cheapest 8th gen is the OptiPlex 3060 at $199.99. Prices change hourly.

**Script:** `scripts/amazon_ca.py search "<q>"` / `product <ASIN…> --seller-rating` prints JSON. Every curl call has a 30s cap and raw HTML goes to tmp/amazon/. If Amazon ever serves a captcha, the next step is headless Playwright (not built yet).
