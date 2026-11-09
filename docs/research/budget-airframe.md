# Budget airframe: booms, spar, joiner, skin, foam, hardware, filament

Parts research to cut the airframe from about $1,000 (carbon tube + glass/epoxy)
to a low-cost build. Baseline in the brief: MTOW 5–7.5 kg, 2.4 m span foam wing
(two 1.2 m halves), twin booms (~1.2 m front + ~0.6 m rear stub each), H-tail,
plug-in wing joiner tube, printed clamps. **Note:** the 5–7.5 kg MTOW in the
brief is below CLAUDE.md's 8–15 kg target. Tube and skin choices here hold
either way, but the mass fractions below are worked at 5–7.5 kg.

All prices were read live on **2026-10-13** from the URL in each row. "—" means
the value was not on the page. Derived values are marked *(calc)* with the
formula. Amazon prices come from search-result pages (delivery to Berkeley
94704). Those pages do not show the seller or ships-from, so ships-from is "—"
for Amazon rows. Amazon and marketplace prices change daily, so re-check them
before ordering.

Formulas used:

- Tube cross-section area: A = π/4 · (OD² − ID²), with OD and ID in mm.
- Mass per metre: m′ = ρ · A. With ρ in g/cm³ and A in mm², m′ [g/m] = ρ · A
  (1 mm² × 1 m = 1 cm³). Aluminium ρ = 2.70 g/cm³ (brief; also
  https://en.wikipedia.org/wiki/6061_aluminium_alloy, checked 2026-10-13).
- Second moment of area: I = π/64 · (OD⁴ − ID⁴). Bending stiffness is E·I.
  6061: E = 69 GPa (same Wikipedia page, which says it applies to all tempers).
- Carbon estimates use ρ = 1.55 g/cm³ (Carbon Fiber Tube Shop table,
  docs/research/airframe-materials.md §1c). Goodwinds' listed weights give
  1.553 g/cm³ *(calc, below)*, which confirms it.
- Unit conversions: 1 in = 25.4 mm, 1 oz = 28.35 g, 1 lb = 453.6 g,
  1 ft² = 0.0929 m².
- Sales tax: Berkeley, CA **10.25 %**, effective 2026-10-01
  (https://www.cdtfa.ca.gov/taxes-and-fees/rates.aspx, checked 2026-10-13).

---

## Verdict (summary)

| Item | Cheapest credible pick | Price (pre-tax) | Mass |
|---|---|---|---|
| Booms (2 × 1.83 m) | OnlineMetals 6061-T6 1.000 × 0.035 in, 2 × 72 in | $52.40 | 185 g/m *(calc)* → 677 g for both |
| Wing spar sockets (2 × 1.2 m) | OnlineMetals 6061-T6 1.000 × 0.058 in, 1 × 96 in, cut in half | $53.97 | 299 g/m *(calc)* → 729 g for both |
| Wing joiner | OnlineMetals 6061-T6 0.875 × 0.058 in, 36 in (cut to about 0.6 m, estimate) | $18.45 | 259 g/m *(calc)* → about 155 g at 0.6 m |
| **Tube set** | One OnlineMetals order | **$124.82** (+ UPS, priced at checkout: —) | **about 1.56 kg** |
| Wing skin | Scotch Heavy Duty packing tape, 6 rolls (14.3 m² raw) | $19.98 | — (weigh a sample, M2) |
| Wing foam | Owens Corning FOAMULAR NGX F-250, 2 in × 4 × 8 ft (Home Depot) | $59.97 | — |
| Tail/fuselage foam | FOAMULAR NGX F-150, 1 in × 4 × 8 ft (Home Depot) | $30.97 | — |
| Hardware kit (minimum) | 13 Amazon lines, §3 | **$124.01** (+tax $136.72) | — |
| Hardware kit (with spares) | 18 Amazon lines, §3 | $184.44 (+tax $203.35) | — |

Airframe materials + minimum kit: $124.82 + $59.97 + $30.97 + $19.98 + $124.01
= **$359.75** pre-tax, **$396.62** with 10.25 % tax *(calc)*, plus metal
shipping (—). That is about 40 % of the previous ~$1,000 airframe, before
filament (§5).

**Joiner fit.** A 0.875 in OD joiner in a 1.000 × 0.058 in socket
(ID 0.884 in) leaves 0.009 in (0.23 mm) diametral clearance *(calc:
0.884 − 0.875)*. That is a normal telescoping slip fit for 0.058 in wall. It
does **not** work in the boom tube 1.000 × 0.035 in (ID 0.930 in, 0.055 in
gap), so the spar sockets have to use the 0.058 in wall.

**Mass penalty.** The all-aluminium set weighs about 1.56 kg, which is
21–31 % of a 5–7.5 kg MTOW *(calc: 1.56/7.5, 1.56/5)*. Per gram, aluminium is
less stiff than carbon. The 1.000 × 0.035 in boom gives EI = 355 N·m² at
185 g/m. The Goodwinds 0.875 in wrapped carbon tube gives EI = 452–603 N·m²
at 173 g/m *(calc, with E = 57–76 GPa twill CLT from
docs/research/airframe-materials.md §1c)*. A mixed set is also possible:
aluminium booms (cheap, stiffness adequate), with carbon only for the spar
sockets (§1d option B).

---

## 1. Booms, spar and joiner

### 1a. 6061-T6 aluminium round tube (US vendors)

m′ and EI are *(calc)* from the formulas above. Vendor weights are converted
as a cross-check.

| Vendor / P/N | OD × wall (in) | ID (in) | Length options and price | m′ (g/m) | EI (N·m²) | Vendor weight check | Stock | Ships from | URL |
|---|---|---|---|---|---|---|---|---|---|
| OnlineMetals 1211 | 1.000 × 0.035 | 0.930 | 12 in $7.14 · 24 in $13.91 · 36 in $19.02 · 48 in $23.74 · **72 in $26.20** · 96 in $41.89 · 144 in $52.41 | **185** | 355 | 0.13 lb/ft → 193 g/m | Add to Cart shown | Nearest of 6 OnlineMetals warehouses (FAQ) | https://www.onlinemetals.com/en/buy/aluminum/1-od-x-0-035-wall-x-0-93-id-aluminum-round-tube-6061-t6-drawn/pid/1211 |
| OnlineMetals 4341 | 1.000 × 0.049 | 0.902 | 12 in $9.50 · 36 in $25.33 · 48 in $31.61 · 72 in $34.90 · 96 in $55.77 | 255 | 477 | 0.18 lb/ft | Add to Cart | same | https://www.onlinemetals.com/en/buy/aluminum/1-od-x-0-049-wall-x-0-902-id-aluminum-round-tube-6061-t6-drawn/pid/4341 |
| OnlineMetals 4342 | 1.000 × 0.058 | 0.884 | 12 in $9.20 · 36 in $24.49 · 48 in $30.60 · 72 in $33.76 · **96 in $53.97** · 144 in $67.53 | **299** | 549 | 0.21 lb/ft | Add to Cart | same | https://www.onlinemetals.com/en/buy/aluminum/1-od-x-0-058-wall-x-0-884-id-aluminum-round-tube-6061-t6-drawn/pid/4342 |
| OnlineMetals 1212 | 1.000 × 0.065 | 0.870 | 12 in $12.10 · 72 in $44.31 · 96 in $70.84 | 333 | 602 | 0.23 lb/ft | Add to Cart | same | https://www.onlinemetals.com/en/buy/aluminum/1-od-x-0-065-wall-x-0-87-id-aluminum-round-tube-6061-t6-drawn/pid/1212 |
| OnlineMetals 20531 | 0.875 × 0.035 | 0.805 | 12 in $6.03 · 36 in $16.09 · 72 in $22.17 · 96 in $35.42 | 161 | 234 | 0.11 lb/ft | Add to Cart | same | https://www.onlinemetals.com/en/buy/aluminum/0-875-od-x-0-035-wall-x-0-805-id-aluminum-round-tube-6061-t6-drawn/pid/20531 |
| OnlineMetals 6891 | 0.875 × 0.058 | 0.759 | 12 in $6.94 · 24 in $13.48 · **36 in $18.45** · 48 in $23.02 · 72 in $25.42 | **259** | 359 | 0.18 lb/ft | Add to Cart | same | https://www.onlinemetals.com/en/buy/aluminum/0-875-od-x-0-058-wall-x-0-759-id-aluminum-round-tube-6061-t6-drawn/pid/6891 |
| OnlineMetals 6982 | 0.875 × 0.065 | 0.745 | 12 in $9.95 · 36 in $27.80 · 72 in $44.14 | 288 | 392 | 0.20 lb/ft | Add to Cart | same | https://www.onlinemetals.com/en/buy/aluminum/0-875-od-x-0-065-wall-x-0-745-id-aluminum-round-tube-6061-t6-drawn/pid/6982 |
| OnlineMetals 6996 | 1.125 × 0.058 | 1.009 | 12 in $11.09 · 36 in $29.51 · 72 in $40.66 · 96 in $65.01 | 339 | 797 | 0.23 lb/ft | Add to Cart | same | https://www.onlinemetals.com/en/buy/aluminum/1-125-od-x-0-058-wall-x-1-009-id-aluminum-round-tube-6061-t6-drawn/pid/6996 |
| Aircraft Spruce 03-36600 | 1.000 × 0.035 | 0.930 *(calc)* | **$4.35/ft**; lengths 1, 3, 6, 12 ft → 6 ft = $26.10 *(calc)* | 185 | 355 | — | — | — | https://www.aircraftspruce.com/catalog/mepages/alumtube_6061t6.php |
| Aircraft Spruce 03-36610 | 1.000 × 0.049 | 0.902 | $4.80/ft | 255 | 477 | — | — | — | same |
| Aircraft Spruce 03-36700 | 1.000 × 0.058 | 0.884 | $5.35/ft | 299 | 549 | — | — | — | same |
| Aircraft Spruce 03-36800 | 1.000 × 0.065 | 0.870 | $12.95/ft | 333 | 602 | — | — | — | same |
| Aircraft Spruce 03-36375 | 0.875 × 0.035 | 0.805 | $6.50/ft | 161 | 234 | — | — | — | same |
| Aircraft Spruce 03-36380 | 0.875 × 0.049 | 0.777 | **$4.99/ft** → 3 ft = $14.97 *(calc)* | 221 | 313 | — | — | — | same |
| Aircraft Spruce 03-36400 | 0.875 × 0.058 | 0.759 | $9.90/ft | 259 | 359 | — | — | — | same |
| Aircraft Spruce 03-36450 | 0.875 × 0.065 | 0.745 | $10.85/ft | 288 | 392 | — | — | — | same |
| Speedy Metals p-4585 | 1.000 × 0.035 | 0.930 | $0.58/in cut; 12 in $10.40 · 36 in $20.80 · 48 in $24.96 · 72 in $31.20 | 185 | 355 | 0.0104 lb/in → 186 g/m | — | — (UPS to 90 in) | https://speedymetals.com/p-4585-1-od-x-035-wall-tube-6061-t6-aluminum.aspx |
| Speedy Metals p-4587 | 1.000 × 0.058 | 0.884 | $0.93/in cut; 12 in $16.80 · 48 in $40.32 · 72 in $50.40 | 299 | 549 | 0.2016 lb/12 in → 300 g/m | — | — | https://speedymetals.com/p-4587-1-od-x-058-wall-tube-6061-t6-aluminum.aspx |
| Speedy Metals p-4568 | 0.875 × 0.049 | 0.777 | $0.69/in cut; 12 in $12.50 · 36 in $25.00 · 72 in $37.50 | 221 | 313 | 0.0125 lb/in → 223 g/m | — | — | https://speedymetals.com/p-4568-78-od-x-0049-wall-tube-6061-t6-aluminum.aspx |
| Metals Depot | 0.875 × 0.065 and 1.000 × 0.065 are the thinnest walls listed in this OD range | 0.745 / 0.870 | Price appears only after choosing a size: — | 288 / 333 | — | 0.25 / 0.22 lb/ft | — | Winchester, KY (corporate address) | https://www.metalsdepot.com/aluminum-products/aluminum-round-tube |
| McMaster-Carr | — | — | Not fetched (JavaScript catalog) | — | — | — | — | — | https://www.mcmaster.com/tubing/fabrication~cold-drawn |
| Amazon (HPS AST-2F-100) | 1.000 × 0.065, 6061-T6, 2 ft | 0.870 | $23.14 | 333 | 602 | — | — | — | https://www.amazon.com/s?k=6061+aluminum+round+tube+1+inch+OD |
| Amazon | 1.000 × 0.0625, 6061-T6, 47 in | 0.875 | $49.99 | 321 *(calc)* | — | — | — | — | same search |
| Amazon (4 × 36 in) | 1.000 × 0.04, **alloy not stated** | 0.920 | $34.99 for 4 (3.66 m) → $9.56/m *(calc)* | 210 *(calc)* | 400 | — | Prime | — | same search |
| Amazon (OnlineMetals listing) | 1.000 × 0.083, 24 in | 0.834 | $59.23 | — | — | — | — | — | same search |
| Home Depot Everbilt 6718 | 1 in × 6 ft, **wall and alloy not shown** | — | $43.22 | — | — | — | Ship to store | — | https://www.homedepot.com/s/aluminum%20round%20tube%201%20in |
| Home Depot 50-A100ID/6 | 1 in IPS Sch. 40 pipe, 6 ft (OD about 1.315 in, far too heavy) | — | $28.14 | — | — | — | Ship to store | — | same |

Price per metre for the main candidates *(calc, price ÷ length)*:
OnlineMetals 1.000 × 0.035 at 72 in = $14.33/m. Aircraft Spruce 1.000 × 0.035 =
$14.27/m. Speedy 1.000 × 0.035 at 72 in = $17.06/m. OnlineMetals
1.000 × 0.058 at 96 in = $22.13/m. OnlineMetals 0.875 × 0.058 at 36 in =
$20.18/m.

Notes:
- Search snippets quoted different Speedy Metals prices ($0.69/in and
  $1.12/in) from the live pages ($0.58/in and $0.93/in). Only the live
  values are used.
- OnlineMetals ships UPS and calculates the charge at checkout step 3. The
  longest piece it can ship by UPS is 96 in. Six fulfillment centers, no
  minimum order (https://www.onlinemetals.com/en/faq).
- Aircraft Spruce's tube page notes that 13 ft lengths go by UPS Freight. Free
  shipping does not apply to pieces over 48 in long (see §4).

### 1b. Telescoping and joiner fits *(calc)*

Diametral clearance = socket ID − joiner OD.

| Joiner (OD) | Socket (ID) | Clearance | Verdict |
|---|---|---|---|
| Al 0.875 in (any wall) | Al 1.000 × 0.058 (0.884) | 0.009 in / 0.23 mm | **Slip fit. Recommended.** |
| Al 0.875 in | Al 1.000 × 0.049 (0.902) | 0.027 in / 0.69 mm | Loose. Needs a shim or printed bushings. |
| Al 0.875 in | Al 1.000 × 0.035 (0.930) | 0.055 in / 1.40 mm | Too loose |
| Al 0.875 in | Al 1.000 × 0.065 (0.870) | −0.005 in | Does not fit |
| Al 1.000 in | Al 1.125 × 0.058 (1.009) | 0.009 in | Slip fit, but heavier (339 g/m socket) |
| Al 0.875 in | Goodwinds 0.875 in carbon (ID 0.880) | 0.005 in | Close fit. Mixed option B. |
| Goodwinds 0.750 in carbon (OD 0.872) | Goodwinds 0.875 in carbon (ID 0.880) | 0.008 in | All-carbon slip fit |
| Amazon CF 22 × 20 mm (OD 22.0) | Amazon CF 25 × 22 mm (ID 22.0) | 0 nominal (tolerance —) | Not credible without measuring |
| Gator-RC GC1006 tube | Matching sleeve (supplied) | Set | Turnkey, but $73 |

### 1c. Carbon tubes 20–25 mm (US)

| Vendor / item | OD × ID × L | Listed weight | m′ (g/m) | Price | $/m *(calc)* | Stock / shipping | URL |
|---|---|---|---|---|---|---|---|
| Goodwinds WCT875060 (wrapped, std modulus 33 Msi prepreg) | 0.997 × 0.880 in × 60 in (25.3 × 22.4 mm × 1.524 m) | 9.290 oz | 172.8 *(calc: 9.290×28.35/1.524)*; implied ρ = 1.553 g/cm³ | $83.84 (6+: $75.62) | $55.01 | ADD TO CART shown; FedEx/USPS at actual cost + handling | https://goodwinds.com/product-category/carbon-fiberglass/carbon/wrapped/cylindrical-tubes/ |
| Goodwinds WCT750060 | 0.872 × 0.755 in × 60 in (22.1 × 19.2 mm) | 8.090 oz | 150.5 *(calc)* | $67.50 | $44.29 | same | same |
| Goodwinds WCT875060Twill | 1.007 × 0.880 in × 60 in | 9.861 oz | 183.4 *(calc)* | $93.10 | $61.09 | same | same |
| Gator-RC GC1006 1 in wing tube + sleeve | 25.4 mm OD, 1.2 mm wall × 914 mm | 303 g (tube + sleeve) | — (set) | $73.00 | — | In stock; free US shipping over $99 | https://www.gator-rc.com/products/gator-rc-one-inch-carbon-fiber-wing-tube |
| Amazon, "High Strength 3K" 22 × 20 × 1000 matte twill | 22 × 20 mm × 1 m | — | 102 *(calc, ρ 1.55, estimate)* | $28.32 | $28.32 | $13 delivery, Oct 28 – Nov 12 (overseas lead time, estimate) | https://www.amazon.com/s?k=carbon+fiber+tube+22mm+1000mm |
| Amazon, same seller, 22 × 18 × 1000 | 22 × 18 mm × 1 m | — | 195 *(calc, estimate)* | $35.99 | $35.99 | $13 delivery | same |
| Amazon, 1 pc 22 × 20 × 1000 glossy twill | 22 × 20 mm × 1 m | — | 102 *(calc, estimate)* | $34.99 | $34.99 | $6 delivery, Oct 26 – Nov 4 | same |
| Amazon, 1 pc 25 × 22 × 1000 matte twill | 25 × 22 mm × 1 m | — | 172 *(calc, estimate)* | $40.99 | $40.99 | $6 delivery | same |
| Amazon, pultruded 25 × 22 × 1000 (small business) | 25 × 22 mm × 1 m | — | 172 *(calc, estimate)* | $38.94 | $38.94 | $4.52 delivery, Oct 22 | same |
| Amazon, 2 pc 22 × 20 × 420 (best seller) | 22 × 20 mm × 0.42 m | — | 102 *(calc, estimate)* | $23.95 (2) | $28.51 | Prime, tomorrow; "Only 18 left" | same |
| Amazon, uxcell 2 pc 22 × 20 × 420 | 22 × 20 mm × 0.42 m | — | 102 *(calc, estimate)* | $19.79 (2) | $23.56 | Prime; "Only 8 left" | same |
| HobbyKing US | — | — | — | — | — | Returned 403 | https://hobbyking.com/en_us/catalogsearch/result/?q=carbon+tube+22mm |
| CST (cstsales.com) | — | — | — | — | — | Product page returned 404 | https://www.cstsales.com/carbon_tube.html |

The cheapest carbon on a per-metre basis is the Amazon 22 × 20 mm tube
($23.56–28.32/m, about 102 g/m estimate). Its laminate, wall tolerance and
real modulus are not listed (—). A 22 mm OD tube also does not match a 25 mm
clamp. The cheapest US carbon with a published weight is Goodwinds 0.750 in
at $44.29/m and 150.5 g/m. For reference, the earlier pick in
docs/research/airframe-materials.md (CFTS ME9972F) cost $123.45 per 72 in,
which is $67.50/m.

### 1d. Option sets *(calc)*

All lengths are estimates from the brief: booms 2 × 1.83 m (one 72 in tube
each), spar sockets 2 × 1.2 m, joiner 0.6 m.

| Option | Booms | Spar sockets | Joiner | Price | Mass |
|---|---|---|---|---|---|
| **A. All 6061 (OnlineMetals)** | 2 × 1.000 × 0.035 × 72 in, $52.40 | 1 × 1.000 × 0.058 × 96 in, $53.97 | 0.875 × 0.058 × 36 in, $18.45 | **$124.82** | 677 + 729 + 155 = **1,561 g** |
| A′. Same, Aircraft Spruce booms and joiner | 2 × 6 ft 03-36600 = $52.20 | OnlineMetals 96 in, $53.97 | 3 ft 03-36380 (0.875 × 0.049) = $14.97 | $121.14 (two vendors, two shipments) | 677 + 729 + 133 = 1,539 g |
| B. Al booms, carbon sockets | $52.40 | Goodwinds WCT875060 cut into 2 × 0.76 m root sockets, $83.84 | Al 0.875 × 0.035 × 36 in, $16.09 | $152.33 | 677 + 263 + 97 = 1,037 g (but only 0.76 m of carbon per half) |
| C. All carbon (Goodwinds) | 60 in tubes are shorter than a 1.83 m boom: 3 × WCT875060 with a splice, $251.52 | 2 × WCT875060 cut to 1.2 m, $167.68 | WCT750060, $67.50 | $486.70 | about 632 + 415 + 90 = 1,137 g |
| D. Cheapest-possible carbon (Amazon 22 × 20) | 4 × 1 m, $113.28 | 3 × 1 m, $84.96 | none matched (see §1b) | > $198 + no joiner | about 102 g/m |

Option A is the cheapest *credible* set: published 6061-T6 drawn tube, one
vendor, a known slip fit. Its cost is the mass. Weigh the stock on arrival
(M1) and decide in the mass budget whether 1.56 kg fits at the target MTOW.

### 1e. Wood spar options (relevant only for spar caps or a wood-cored spar)

| Item | Size | Price | Shipping | Density | URL |
|---|---|---|---|---|---|
| Spruce strip (Amazon, 7 pcs) 5558 | 1/4 × 1/2 × 36 in | $30.60 | $12.49 delivery, Oct 26 | — | https://www.amazon.com/dp/B00YV707V0 |
| Spruce strip (10 pcs) | 1/8 × 1/4 × 36 in | $14.00 | $12.49 | — | https://www.amazon.com/dp/B00YV6Y2MG |
| Basswood (12 pcs) 3455 | 1/4 × 1/4 × 24 in | $16.15 | $10.07 | — | https://www.amazon.com/dp/B01N2131ZG |
| Basswood (8 pcs) 3458 | 1/4 × 1/2 × 24 in | $14.88 | $10.04 | — | https://www.amazon.com/dp/B01NBTEXOF |
| Oak dowel (Cindoco), 1 pc | 3/4 in × 36 in | $6.99 | $7.99 delivery | — | https://www.amazon.com/dp/B003FHR2QK |
| Poplar dowels, 10 pcs | 3/4 in × 36 in | $32.99 | Prime | — | https://www.amazon.com/dp/B0GSHH21LC |

A 36 in strip does not span a 1.2 m half, so wood caps would need scarf
joints. Wood is not recommended as the main spar for a plug-in joiner.

---

## 2. Wing skin and foam

### 2a. Skin options

Coverage is the raw roll area: width × length *(calc)*. A taped skin needs
overlap. At 25 % overlap (estimate), the effective coverage is 0.75 × raw.

**Skin area estimate (not from repo).** Chord is not defined in the repo (—).
At an assumed 0.30 m chord: wing 2.4 × 0.30 × 2 sides × 1.05 wrap = 1.5 m²,
plus about 1 m² for tail and fuselage, so about **2.5 m²** total.

| Option | Product | Roll size | Raw coverage | Price | $/m² raw *(calc)* | Rolls for 2.5 m² | Prime / shipping | URL |
|---|---|---|---|---|---|---|---|---|
| **Packing tape (cheapest)** | Scotch Heavy Duty Shipping Packing Tape, 6 rolls (B000087KUA) | 1.88 in × 54.6 yd | 2.384 m²/roll; 14.3 m²/pack | **$19.98** ($3.33/roll) | $1.40 | 1.4 at 75 % → one 6-pack with spares | Prime; free $35+ non-Prime | https://www.amazon.com/dp/B000087KUA |
| Packing tape (3850, 3.0 mil) | Scotch 3850, 2 rolls (B0GPZ6WR48) | 1.88 in × 54.6 yd | 4.77 m² | $15.09 | $3.16 | 2 rolls | Prime | https://www.amazon.com/dp/B0GPZ6WR48 |
| Packing tape (3850, 12 rolls) | B0GPZYQK94 | same | 28.6 m² | $58.99 | $2.06 | — | Prime | https://www.amazon.com/dp/B0GPZYQK94 |
| Packing tape (1 roll) | Scotch Heavy Duty refill (B000J05FJW) | same | 2.384 m² | $5.97 | $2.50 | 2 rolls | Prime | https://www.amazon.com/dp/B000J05FJW |
| Hot laminating film | EXTRIC thermal laminating film, 2 rolls, 1.5 mil, 1 in core (B0B15KTV8F) | 25 in × 500 ft each | 96.8 m²/roll; 193.5 m² total | $50.14 | $0.26 | fraction of one roll | Prime | https://www.amazon.com/dp/B0B15KTV8F |
| Hot laminating film (narrow) | Matte, 28 µm, 1 in core (B0DQ5S3T6Z) | 12.6 in × 656 ft | 64.0 m² | $35.99 | $0.56 | fraction | Prime | https://www.amazon.com/dp/B0DQ5S3T6Z |
| UltraCote (Hangar 9) | HANU874 black, Amazon | 23.5 in × 78 in (from Adrenaline RC listing for the same 6.5 ft roll) | 1.18 m² | $19.99 | $16.90 | 2–3 rolls ($40–60) | Prime | https://www.amazon.com/dp/B0006N6MFI ; size: https://www.adrenalinercracing.com/collections/airplane-parts/products/hangar-9-ultracote-bright-yellow-6-5 |
| UltraCote 10 m roll | HANU87010 white | 10 m (width — on the page) | — | $89.99 | — | — | Prime | https://www.amazon.com/dp/B0006O31M4 |
| Generic iron-on film | Viloga 60 × 500 cm white (B07QWS4VM8) | 0.6 × 5 m | 3.0 m² | $42.99 | $14.33 | 1 roll | Prime | https://www.amazon.com/dp/B07QWS4VM8 |
| Monokote | Top Flite Monokote not listed on Amazon for this search. The listed "Oracover Monokote Ultracote" film is 60 × 100 cm for $16.89 | 0.6 m² | | $16.89 | $28.15 | 4–5 | $8 delivery | https://www.amazon.com/dp/B07S6DQ3XN |
| Gorilla tape | Gorilla Crystal Clear, 1 pack (B0783SG446) | 1.88 in × 18 yd | 0.786 m² | $9.49 | $12.07 | 4–5 rolls (~$40) | Prime | https://www.amazon.com/dp/B0783SG446 |
| Paper skin: paper | DIY Crew kraft, 30 in × 150 ft (B01N6584SD) | 0.762 × 45.7 m | 34.8 m² | $24.99 | $0.72 | fraction | Prime | https://www.amazon.com/dp/B01N6584SD |
| Paper skin: paper (cheaper/m²) | 36 in × 100 ft kraft (B07KKP6D3Z) | 0.914 × 30.5 m | 27.9 m² | $22.99 | $0.82 | fraction | Prime | https://www.amazon.com/dp/B07KKP6D3Z |
| Paper skin: glue | Titebond II, 16 oz (B0000223UR) | — | — | $7.57 | — | 1 | Prime | https://www.amazon.com/dp/B0000223UR |
| Paper skin: glue (bulk) | Elmer's Glue-All, 1 gal (B0038DZZJC) | — | — | $19.99 | — | 1 | Prime | https://www.amazon.com/dp/B0038DZZJC |
| Paper skin: sealer | Minwax Polycrylic satin, 1 qt (B000BZYYH4) | — | — | $23.48 | — | 1 | Prime | https://www.amazon.com/dp/B000BZYYH4 |

Mass per area is not listed for the tapes, laminating film or kraft paper
(—). UltraCote is 0.30 oz/ft², which is 92 g/m² *(calc: 0.30×28.35/0.0929)*
(Adrenaline RC listing). The only kraft weights shown were 70 gsm (PerkHomy,
B0CZ74KWLT, 30 in × 200 ft, $39.99) and 80 gsm (B0DCGCF1DH, 36 in × 150 ft,
$27.99). That is before glue.

**Cheapest skin by cash outlay:** Scotch Heavy Duty packing tape, 6 rolls,
**$19.98**. It needs no iron and no extra glue. **Cheapest per m²:** hot
laminating film at $0.26–0.56/m². It needs a covering iron or a clothes iron
(not priced here), and a $36–50 roll is far more film than one aircraft uses.
Paper skin costs $22.99 paper + $7.57 Titebond + $23.48 sealer = $54.04
*(calc)*, so it is not cheaper.

### 2b. XPS / EPS foam board (home centers, 94547 / Berkeley area)

| Product | Size | Price | Stock (store) | Delivery | URL |
|---|---|---|---|---|---|
| **Owens Corning FOAMULAR NGX F-250, Home Depot 52DDNGX** | 2 in × 4 × 8 ft (2.97 m² *(calc)*) | **$59.97** (32+: $50.97) | 44 at El Cerrito | Tomorrow | https://www.homedepot.com/s/foamular%20150 |
| Owens Corning FOAMULAR NGX F-250, Lowe's | 2 in × 4 × 8 ft | $59.98 | Pickup today, 34 available | Tomorrow | https://www.lowes.com/search?searchTerm=foamular%20xps%202%20in |
| Owens Corning FOAMULAR NGX F-150, Home Depot 20WENGX | 1 in × 4 × 8 ft | **$30.97** (32+: $26.32) | 5 at El Cerrito | Tomorrow | https://www.homedepot.com/s/foamular%20150 |
| Owens Corning FOAMULAR NGX F-150, Lowe's | 1.5 in × 4 × 8 ft | $42.67 | 31 at Concord | Thu Oct 15 | https://www.lowes.com/search?searchTerm=foamular%20xps%202%20in |
| FOAMULAR NGX 2 × 2 ft project panel, Home Depot 9WE | 1 in × 2 × 2 ft | $9.97 | 22 at Hercules | Free with $25 of eligible items | https://www.homedepot.com/s/foamular%20150 |
| FOAMULAR NGX project wall panel, Home Depot 36WENGX | 1.5 in × 14.25 in × 4 ft | $14.98 | 63 at Hercules | Free with $25 | same |
| FOAMULAR F-150 **2 in** | — | Not listed at either store (only F-250 in 2 in) | — | — | — |
| RMAX R-Matte Plus-3 (polyiso, foil faced; not for hot wire) | 2 in × 4 × 8 ft | $55.97 | 44 at Hercules | Tomorrow | https://www.homedepot.com/s/foamular%202%20in%20x%204%20ft%20x%208%20ft |
| Henry EPS 320825 | 2 in × 4 × 8 ft | $39.97 | 9 at Martinez | Tomorrow | same |
| Henry EPS 320817 | 1.5 in × 4 × 8 ft | $20.97 | 28 at Hercules | Tomorrow | same |
| Henry EPS 320810 | 0.5 in × 4 × 8 ft | $12.97 | 70 at Hercules | Tomorrow | same |
| Kingspan / Dow equivalents | — | Not shown in these searches | — | — | — |
| Dollar Tree Readi-Board foam board | 20 × 30 × 3/16 in (0.387 m² *(calc)*) | "$1.25, 25 ct" on Instacart-run same-day page (unclear whether per board or per case); dollartree.com returned "Service Unavailable" | — | Same-day | https://sameday.dollartree.com/store/dollar-tree/products/22660723-readi-board-20-x-30-x-3-16-white-foam-board-25-ct |
| UCreate foam board (Amazon), 10 sheets | 20 × 30 in | $35.92 ($3.59/sheet) | — | Free Oct 15 | https://www.amazon.com/dp/B074QZMLQF |
| Office Depot foam board (Amazon), 3-pack | 20 × 30 in | $19.52 | "Only 3 left" | Free Oct 15–16 | https://www.amazon.com/dp/B011BQW9Y6 |
| Adams foam board | — | Not found on a live page (—) | — | — | — |

One 2 in × 4 × 8 ft sheet holds both 1.2 m wing halves end to end along the
8 ft length, for any chord up to 1.2 m. A 2 in (50.8 mm) core suits a
section up to about 50 mm thick, which is a 12 % airfoil at about 0.42 m
chord *(calc: 50.8/0.12)*.

---

## 3. Wiring and hardware kit (replaces the $120 allowance)

All lines are Amazon, delivery to 94704, checked 2026-10-13. Every line
showed "Join Prime to get FREE delivery" (Prime-eligible). Non-members get
free delivery on $35+ of items shipped by Amazon. Ships-from / seller is not
shown on search pages (—). The XT90S line suits a 6S pack. Check against the
battery chosen in docs/research/pusher-battery-servo.md.

### 3a. Minimum realistic kit

| # | Item | Pack | Price | ASIN / URL |
|---|---|---|---|---|
| 1 | FLY RC Amass XT90S anti-spark connectors | 5 pairs | $13.99 | https://www.amazon.com/dp/B0893CGLP7 |
| 2 | 10 AWG silicone wire, tinned (main battery leads) | 5 ft red + 5 ft black | $8.98 | https://www.amazon.com/dp/B0D968WN4W |
| 3 | BNTECHGO 12 AWG silicone wire (ESC branches) | 10 ft red + 10 ft black | $14.98 | https://www.amazon.com/dp/B01ABOPMEI |
| 4 | 300 mm servo extension leads | 10 pcs | $6.99 | https://www.amazon.com/dp/B0FYCJLY1V |
| 5 | Mywish 304 SS M2/M3/M4/M5 button and socket screws, nuts, washers | 1290 pcs | $17.99 | https://www.amazon.com/dp/B0CQWYFTXC |
| 6 | M3 brass heat-set inserts (for printed clamps) | 100 pcs | $5.99 | https://www.amazon.com/dp/B0BVMMBG2N |
| 7 | Nylon control horns, 4-hole, with M2 screws | 12 sets | $8.98 | https://www.amazon.com/dp/B0B58ZSC8J |
| 8 | Du-Bro 230 Mini Nylon Kwik-Link on 12 in 2-56 rod | 5 pushrods | $12.48 | https://www.amazon.com/dp/B0006O8TAI |
| 9 | Andibro hinge tape 1 in × 10 yd | 2 rolls | $6.69 | https://www.amazon.com/dp/B0H7J994N4 |
| 10 | Heat-shrink tubing kit 2:1 | 900 pcs | $6.99 | https://www.amazon.com/dp/B0BG6V4HV4 |
| 11 | Zip ties 4/6/8/12 in | 200 pcs | $3.99 | https://www.amazon.com/dp/B0CSXGZXM8 |
| 12 | ZORZA UBEC 5 V 5 A, 2–7S input | 2 pcs | $9.99 | https://www.amazon.com/dp/B0CQ1R55BV |
| 13 | Gorilla 2-part epoxy, 5 min, 0.85 oz | 1 | $5.97 | https://www.amazon.com/dp/B001Z3C3AG |
| | **Total** | | **$124.01** | +10.25 % tax = **$136.72** *(calc)*; shipping $0 (over $35 / Prime) |

Line 9 can be dropped if the packing tape from §2a doubles as hinge tape,
which brings the total to $117.32 *(calc)*.

### 3b. Add-ons (recommended spares and convenience)

| Item | Pack | Price | URL |
|---|---|---|---|
| Second Du-Bro 230 pushrod 5-pack (spares) | 5 | $12.48 | https://www.amazon.com/dp/B0006O8TAI |
| XT60H connectors (lift ESC breakout, if used) | 12 pairs | $6.99 | https://www.amazon.com/dp/B0DPBP1N59 |
| 14 AWG silicone wire (pusher ESC / BEC feeds) | 10 ft + 10 ft | $9.99 | https://www.amazon.com/dp/B0C5QY73WC |
| Nylon M2–M6 hex screws, nuts, washers (breakaway wing bolts) | 500 pcs | $9.99 | https://www.amazon.com/dp/B0FMDSM1VG |
| ShareGoo LiPo battery straps 20 × 250 mm | 10 | $7.99 | https://www.amazon.com/dp/B0FG8CV6KP |
| Foam-safe glue 4 oz with brush cap | 1 | $12.99 | https://www.amazon.com/dp/B0FRM9N2CS |
| **Min kit + all add-ons** | | **$184.44** | +tax $203.35 *(calc)* |

### 3c. Alternatives seen (same date, same search pages)

| Item | Price | URL |
|---|---|---|
| TMH XT90, 10 pairs with heat shrink (sponsored) | $14.89 | https://www.amazon.com/dp/B0F5HC24VM |
| Amass XT90 10 pairs (sponsored) | $16.99 | https://www.amazon.com/dp/B06ZY34369 |
| BNTECHGO 10 AWG, 10 ft + 10 ft | $19.98 | https://www.amazon.com/dp/B01ABOPO2S |
| BNTECHGO 14 AWG, 10 ft + 10 ft | $11.98 | https://www.amazon.com/dp/B017TFR6SM |
| M3 socket-head kit, 1120 pcs | $9.99 | https://www.amazon.com/dp/B0FGV5FCBN |
| M3–M6 304 SS socket-head kit, 1220 pcs | $22.99 | https://www.amazon.com/dp/B0FG2964F5 |
| Du-Bro T-style nylon control horns (2) | $5.81 | https://www.amazon.com/dp/B000BOG8MY |
| Du-Bro 801 2-56 × 12 in threaded rods (6), "Only 12 left" | $10.74 | https://www.amazon.com/dp/B0043XATSI |
| Du-Bro 600 2-56 Kwik-Link clevis (12) | $14.38 | https://www.amazon.com/dp/B0006O8TY4 |
| Du-Bro 109 2-56 Kwik-Link (2) | $6.58 | https://www.amazon.com/dp/B0006O4FWO |
| ZTW UBEC 6 A (10 A peak), 5.0/5.5/6.0 V adjustable | $19.99 | https://www.amazon.com/dp/B071CHGWRM |
| 8 A UBEC 5 V/6 V, 2–6S | $18.98 | https://www.amazon.com/dp/B07DD9L6P6 |
| UHU Por 50 ml (free on $35) | $13.00 | https://www.amazon.com/dp/B004GHJ9NW |
| 3M Super 77 spray, 13.44 oz (not sold in CA per title) | $14.99 | https://www.amazon.com/dp/B01MFA2EEE |

---

## 4. Shipping terms at the vendors used

| Vendor | Free shipping / rate | Source |
|---|---|---|
| Amazon | Prime: free delivery (next day, Oct 14, on most rows). Non-Prime: free on $35+ of items shipped by Amazon. Some third-party rows charge delivery ($4.52–$13 on carbon tubes; $7.99–12.49 on wood). | Search-result pages cited per row |
| OnlineMetals | No free-shipping threshold stated. UPS charge calculated at checkout step 3. Max UPS length 96 in. Ships from the nearest of 6 facilities. No minimum order. | https://www.onlinemetals.com/en/faq |
| Aircraft Spruce | Free UPS ground on in-stock orders over $350 (USA). Excludes "specially cut materials" and packages over 48 in long, per the exclusions the search tool quoted from aircraftspruce.com (the shipping page itself was not fetched). A 6 ft tube is therefore not free-ship. | https://www.aircraftspruce.com/catalog/mepages/alumtube_6061t6.php (page banner); exclusions per search of aircraftspruce.com, 2026-10-13 |
| Speedy Metals | No minimum order. Shipping rate not shown (—). UPS up to 90 in. | Product pages above |
| Goodwinds | Actual FedEx/USPS cost + insurance + handling fee. No free threshold. | https://goodwinds.com/shipping/ |
| Gator-RC | Free US shipping over $99 (planes excluded) | https://www.gator-rc.com/products/gator-rc-one-inch-carbon-fiber-wing-tube |
| Home Depot | Foam sheets: store pickup or "Delivery: Tomorrow" (fee not shown). Small items: free delivery with $25 of eligible items. Ship-to-store free. | Search pages above |
| Lowe's | Pickup today (Hercules area). Delivery date shown, fee — | Search page above |
| Metals Depot | — (shipping page not fetched) | — |

Plan: one OnlineMetals order (tubes), one Amazon order over $35 (kit, tape,
filament), and pick up foam at Home Depot El Cerrito or Hercules (no
freight).

---

## 5. Filament

| Product | Type | Price (1 kg unless noted) | $/kg *(calc)* | Prime | URL |
|---|---|---|---|---|---|
| ELEGOO PETG black, 1.75 mm | PETG | **$12.99** | 12.99 | Yes | https://www.amazon.com/dp/B0D41Y3WWZ |
| SUNLU PETG black, 1.75 mm | PETG | $13.99 | 13.99 | Yes | https://www.amazon.com/dp/B0DJS3PJVX |
| SUNLU PETG 4 kg (4 × black) | PETG | $39.99 | **10.00** | Yes | https://www.amazon.com/dp/B0D1KC72YP |
| SUNLU PLA black, 1.75 mm | PLA | **$13.99** | 13.99 | Yes | https://www.amazon.com/dp/B07XG3RM58 |
| Creality PLA 2 kg (black + white) | PLA | $23.99 | **12.00** | Yes | https://www.amazon.com/dp/B0C4TNQZYY |
| ANYCUBIC PLA 4 kg multicolor | PLA | $39.99 | 10.00 | Yes | https://www.amazon.com/dp/B0D53ZNHSV |

### Is PETG reasonable near motors?

| Material | HDT 0.45 MPa | HDT 1.80 MPa | Method | Source |
|---|---|---|---|---|
| Prusament PETG | **68 °C** | 68 °C | ISO 75 | Prusament PETG technical datasheet v1.1, last update 16-02-2022 (PDF hosted by 3dprintergear.com.au, text extracted 2026-10-13): https://www.3dprintergear.com.au/assets/files/technical-data-sheet%20(1).pdf |
| Prusament PLA | **55 °C** | 55 °C | ISO 75 | Prusament PLA technical datasheet v1.1, last update 27-07-2022 (via MatterHackers): https://www.matterhackers.com/r/xFvGl8 |
| Bambu Lab PETG Basic | 69 °C (load not stated) | — | — | MatterHackers listing: https://matterhackers.com/store/l/bambu-lab-petg-basic-filament-175mm-1kg/sk/MEQ3G60P |

PETG's HDT is about 13 °C higher than PLA's (68 vs 55 °C). That makes PETG
the better default for clamps and mounts. It is reasonable for boom clamps
and wing joiner saddles, which sit away from heat. At motor mounts it is
**reasonable only if the motor case stays well below 68 °C.** Motor case
temperature in hover is not known (—), so measure it (M3). If it exceeds
about 60 °C, the margin is gone: use the aluminium motor mounts listed in
docs/research/airframe-materials.md, or a higher-HDT filament (not priced
here). PLA is not recommended for anything that touches a motor or ESC, or
that sits in the sun (dark parts in the sun can exceed 55 °C; no measured
value here, —).

---

## What the team must measure

- **M1 – Delivered tube mass.** Weigh each tube on a kitchen scale against
  the m′ values above (185 / 299 / 259 g/m). If the airframe tube set exceeds
  1.6 kg, or the tube set exceeds 25 % of MTOW at the final MTOW, go to
  option B (carbon sockets).
- **M2 – Skin areal mass.** Tape a 0.25 m × 0.25 m foam test panel with
  packing tape at 25 % overlap. Weigh it bare and skinned. If the tape adds
  more than about 150 g/m² (assumed threshold, —), compare against a
  laminating-film panel.
- **M3 – Motor case temperature.** Run a lift motor at hover throttle for
  2 min plus your reserve time on the bench. Read the case with an IR
  thermometer. Above about 60 °C, PETG mounts fail the 68 °C HDT margin.
- **M4 – Joiner fit and play.** Slide the 0.875 in joiner into the 1.000 ×
  0.058 in socket. Measure wingtip vertical play with a ruler at 1.2 m.
  More than about 5 mm (assumed threshold) calls for a printed bushing or a
  tape shim.
- **M5 – Boom tip deflection.** Clamp a 1.83 m boom at the wing. Hang one
  lift-motor thrust equivalent at the motor station with a luggage scale.
  Measure deflection and compare with EI = 355 N·m² for 1.000 × 0.035 in.
