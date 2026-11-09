# Airframe materials, hardware and reference airframes

Parts research for the lift + cruise VTOL (MTOW 8–15 kg, span 2–3 m, breaks
down to fit in a car). All pages were checked live on **2026-10-13** unless a row
says otherwise. "—" means the value was not on the page. Unit conversions and
derived values are marked *(calc)* and show their formula. Vendor property data
is reference only: Rock West labels its values Classical Lamination Theory (CLT)
estimates, "not guaranteed". Carbon Fiber Tube Shop says its table is "not for
design purposes".

Conversions used: 1 in = 25.4 mm; 1 lb = 453.6 g; 1 lb/ft = 1488 g/m;
1 Msi = 6.895 GPa; 1 ksi = 6.895 MPa. Rock West does not label the units on its
weight or property fields. Its weights check out as lb: for P/N 45593,
π/4·(0.882²−0.810²)·72 in³ × 0.055 lb/in³ = 0.379 lb, which matches the listed
0.379. Its property values are taken as psi because the page is set to Imperial.

---

## Recommendation (summary)

| Role | Part | Size (OD / ID / L) | Mass | Price | Properties (vendor) | Why |
|---|---|---|---|---|---|---|
| **Lift booms** | Carbon Fiber Tube Shop **ME9972F** (roll-wrapped, fabric cello) | 0.995 in (25.3 mm) / 0.875 in (22.2 mm) / 72 in (1829 mm); wall 0.060 in (1.5 mm) | 0.110 lb/ft → 164 g/m *(calc)* | $123.45 per 72 in tube (one tube gives two booms of about 0.9 m) | Generic carbon/epoxy composite: 17 Msi (117 GPa) tensile modulus, 275 ksi (1.9 GPa) tensile strength (vendor says "general comparison only") | Roll-wrapped, US stock (Utah), close to the 25 mm clamp standard (Tarot 25 mm mounts). The same tube is the spar joiner below, so you can buy common stock. |
| **Wing spar (outer panels)** | Carbon Fiber Tube Shop **ME1172F** | 1.120 in (28.4 mm) / 1.000 in (25.4 mm) / 72 in; wall 0.060 in | 0.130 lb/ft → 193 g/m *(calc)* | $151.54 | Same generic table as above | Its ID of 1.000 in takes the ME9972F (OD 0.995 in) as a full-length **joiner** with about 0.005 in diametral clearance *(calc: 1.000 − 0.995)*. That gives a 3-piece wing with a plug-in center joiner. |
| Alternative with better published data | Rock West **45593** (3k twill, roll-wrapped) | 0.882 in (22.4 mm) / 0.810 in (20.6 mm) / 72 in; wall 0.036 in (0.9 mm) | 0.379 lb → 172 g/tube → 94 g/m *(calc)* | $94.99 (1–9) | CLT: EX 8.337×10⁶ psi = 57.5 GPa; X tensile 62,780 psi = 433 MPa; X compressive 68,680 psi = 474 MPa *(calc)* | 71 in stock, ships next business day. The thin wall makes it light, but 22.4 mm doesn't match the standard 22 or 25 mm clamps. Check the fit. |

---

## 1. Carbon fiber tubes (OD 16–30 mm)

### 1a. US vendors

| Vendor / P/N | Construction | OD | ID | Wall | Length | Weight | Price | Properties listed | In stock | Ships from | Lead time | URL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Rock West 45593 | Roll-wrapped, 3k 2×2 twill, std modulus, Tenax UTS50 / Eporite EHM32 | 0.882 in (22.4 mm) | 0.810 in (20.6 mm) | 0.036 in | 72 in | 0.379 lb (172 g) *(calc)* | $94.99 (1–9), $84.79 (10–49) | EX 8.337e6 psi (57.5 GPa), X tens 62,780 psi (433 MPa), X comp 68,680 psi, Y tens 40,820 psi, GXY 987,000 psi; Tg 225–249 °F | y (71) | US (West Jordan, UT, will-call address) | Next business day; >71 pcs ≥4 wk | https://www.rockwestcomposites.com/45593.html |
| Rock West 45001 INFINITubeTW Size 1 | Roll-wrapped, 3k twill | 0.935 in (23.7 mm) | 0.875 in (22.2 mm) | 0.030 in | 72 in | 0.338 lb (153 g) → 84 g/m *(calc)* | $89.99 (1–9) | EX 9.96e6 psi (68.7 GPa), X tens 78,460 psi (541 MPa); also a "lengthwise ultimate 100 ksi" | y (51) | US (UT) | Next business day; >51 ≥4 wk | https://www.rockwestcomposites.com/45001.html |
| Rock West 45002 INFINITubeTW Size 2 | Roll-wrapped, 3k twill | 1.055 in (26.8 mm) | 0.983 in (25.0 mm) | 0.036 in | 72 in | 0.456 lb (207 g) → 113 g/m *(calc)* | $99.99 (1–9) | EX 1.107e7 psi (76.3 GPa), X tens 82,090 psi (566 MPa), X comp 87,590 psi | y (11) | US (UT) | Next business day; >11 ≥4 wk | https://www.rockwestcomposites.com/45002.html |
| Rock West 46642 | Roll-wrapped, 3k twill outer, uni core | 1.000 in (25.4 mm) | 0.625 in (15.9 mm) | 0.188 in | 72 in | 1.895 lb (860 g) → 470 g/m *(calc)* | $518.99 (1) | EX 1.328e7 psi (91.6 GPa), X tens 86,470 psi (596 MPa), X comp 108,800 psi | n (backorder) | US (UT) | ≥4 wk | https://www.rockwestcomposites.com/46642.html |
| Rock West 45167 | Unidirectional, std modulus | 0.625 in (15.9 mm) | 0.553 in | 0.036 in | 72 in | — | $66.99 | — (not fetched) | y (2) | US (UT) | — | https://www.rockwestcomposites.com/45167.html |
| Rock West PBRT-1618 | Pull-braided, sanded smooth (clearance) | 18 mm | 16 mm | 0.0395 in (1.0 mm) | 2000 mm | 0.37 lb (168 g) → 84 g/m *(calc)* | $84.49 (was $168.99); no returns | — (tab did not load) | y (19) | US (UT) | Next business day | https://www.rockwestcomposites.com/pbrt-1618.html |
| Carbon Fiber Tube Shop ME8272F | Roll-wrapped, fabric, cello | 0.825 in (21.0 mm) | 0.750 in (19.1 mm) | 0.037 in | 72 in | 0.062 lb/ft → 92 g/m *(calc)* | $79.96 | Generic table only (see 1c) | — (not stated) | US (West Jordan, UT) | Sanded versions ship in 2–3 days | http://www.carbonfibertubeshop.com/medium%20tubing.html |
| CFTS ME8772F | Roll-wrapped, fabric | 0.870 in (22.1 mm) | 0.750 in | 0.060 in | 72 in | 0.100 lb/ft → 149 g/m | $105.41 | Generic | — | US (UT) | — | same |
| **CFTS ME9972F** | Roll-wrapped, fabric | 0.995 in (25.3 mm) | 0.875 in (22.2 mm) | 0.060 in | 72 in | 0.110 lb/ft → 164 g/m | $123.45 (uni version ME9972U $117.07) | Generic | — | US (UT) | — | same |
| CFTS ME9972TWF | Roll-wrapped, fabric, heavy wall | 0.994 in (25.2 mm) | 0.750 in | 0.122 in | 72 in | 0.224 lb/ft → 333 g/m | $210.56 | Generic | — | US (UT) | — | same |
| **CFTS ME1172F** | Roll-wrapped, fabric | 1.120 in (28.4 mm) | 1.000 in (25.4 mm) | 0.060 in | 72 in | 0.130 lb/ft → 193 g/m | $151.54 (uni ME1172U $140.50) | Generic | — | US (UT) | — | same |
| CFTS ME1272F | Roll-wrapped, fabric | 1.245 in (31.6 mm, just over range) | 1.125 in | 0.060 in | 72 in | 0.150 lb/ft → 223 g/m | $158.85 | Generic | — | US (UT) | — | same |
| DragonPlate FDPT.625×.75×24 | Roll-wrapped twill, gloss | 0.75 in (19.1 mm) (from SKU) | 0.625 in | 0.0625 in | 24 in | — | from $38.10 | Fiber 33 Msi std modulus (fiber, not laminate) | — | US (DragonPlate, NY; phone 315-252-2559) | "Standard sizes typically in stock" | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-0625-id-x-24-gloss-finish |
| DragonPlate 0.625 ID × 72 | Roll-wrapped twill | 0.75 in | 0.625 in | 0.0625 in | 72 in | — | $106.22 | Fiber 33 Msi | — | US | — | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-0625-id-x-72-gloss-finish |
| DragonPlate FDPT.875×1.0×24 | Roll-wrapped twill | 1.0 in (25.4 mm) (from SKU) | 0.875 in | 0.0625 in | 24 in | — | from $45.33 | Fiber 33 Msi | — | US | — | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-0875-id-x-24-gloss-finish |
| DragonPlate FDPT1.125×1.25×24 | Roll-wrapped twill, woven 0/90 + UD 0 | 1.25 in (31.8 mm, just over range) | 1.125 in | 0.0625 in | 24 in | 0.322 lb (146 g) | $66.39 (1), $63.73 (6+) | Fiber 33 Msi, fiber UTS 700 ksi; density 0.057 lb/in³; max 250 °F | — | US | "Large quantities need additional time" | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-1125-id-x-24-gloss-finish |
| Gator-RC GC1002 wing tube + sleeve | Carbon tube with a 25.4 mm sleeve | 25 mm | — (wall 0.85 mm) | 0.85 mm | 850 mm | Tube 93 g; tube + sleeve 277 g | $79.95 | — | y | US (Algonquin, IL address; origin not stated) | — | https://gator-rc.com/gator-25mm-carbon-fiber-wing-tube-and-sleeve-gc1002 |

Rock West's metric pull-braided tubes (PBRT-2025, -2225, -2325, -2528, -2830; 25–30 mm OD × 2 m) show up in search but their product pages returned 404 on 2026-10-13. Treat them as unavailable.

### 1b. Non-US / marketplace

| Vendor | OD / ID / L | Weight | Price | Properties | In stock | Ships from | URL |
|---|---|---|---|---|---|---|---|
| Easy Composites (UK) roll-wrapped 25 mm | 25 / 22 mm (1.5 mm wall) / 1000 or 2000 mm | 178 g/m | £29.20 ex VAT (1 m); £25.20 (5–19) | UD 0° plus 90° hoop plies, epoxy; max 80 °C; no modulus or strength listed; "not designed for torsional loads" | y (>50) | UK (US site exists; its page failed with an SSL error on 2026-10-13) | https://www.easycomposites.co.uk/25mm-roll-wrapped-carbon-fibre-tube-metric |
| Flying Tech (UK) 3K 16 mm boom | 16 / 14 mm / 333 or 440 mm | 24 g / 30 g | £11.50 / £14.90 | — | conflicting (page says sold out) | UK | https://www.flyingtech.co.uk/product/3k-16mm-carbon-fibre-tube-multicopter-boom/ |
| eBay / AliExpress (China) | 20–30 mm OD × 1000 mm | — | — | — | — | China | eBay returned 403 and AliExpress was not reachable. **No live price recorded.** |
| Amazon | — | — | — | — | — | — | Amazon search returned 503. **No live price recorded.** |

### 1c. Published laminate and fiber properties

| Source | Value | URL |
|---|---|---|
| Carbon Fiber Tube Shop "tube properties" | Carbon/epoxy composite: tensile modulus 17 Msi (117 GPa), tensile strength 275 ksi (1.90 GPa), density 0.056 lb/in³ (1.55 g/cm³ *(calc ×27.68)*). Fiber alone: 33 Msi, 580 ksi. "Not for design purposes." | http://www.carbonfibertubeshop.com/tube%20properties.html |
| DragonPlate weights/specs | Fiber data only (e.g. T700S 33.4 Msi / 711 ksi; HR40 57 Msi). Does not map fibers to tubes. | https://dragonplate.com/dragonplate-weights-specs |
| Rock West | Per-tube CLT values (see table 1a). Twill tubes come out at 57–92 GPa axial and 433–596 MPa axial tensile. | per-product URLs above |

**Takeaway for design:** for twill roll-wrapped tubes, use the per-tube Rock West CLT numbers (EX ≈ 57–76 GPa, σx ≈ 430–570 MPa). The 117 GPa / 1.9 GPa generic figure is a UD best case and would make stiffness look better than it is.

### 1d. Joiners, sleeves and ferrules for wing breakdown

| Item | Fits | Dimensions | Price | In stock | URL |
|---|---|---|---|---|---|
| **CFTS ME9972F used as joiner** | Inside ME1172F (ID 1.000 in) | OD 0.995 in, cut to length | $123.45 / 72 in | — | http://www.carbonfibertubeshop.com/medium%20tubing.html |
| CFTS ME990FER ferrule | Inside ID 1.000 in tubes (ME1172) | OD 0.990 / ID 0.875 in × 6 in, uni plus glass veil | $15.65 (includes First Class shipping) | — | same |
| CFTS ME865FER | Inside ID 0.875 in tubes (ME9972) | OD 0.865 × 6 in | $15.36 | — | same |
| CFTS ME740FER | Inside ID 0.750 in tubes (ME8272/8772) | OD 0.740 × 5 in | $11.63 | — | same |
| CFTS ME111FER | Inside ID 1.125 in tubes (ME1272) | OD 1.115 × 6 in | $16.17 | — | same |
| Rock West 45626-F5-5 ferrule | ID 0.865 in or larger | OD 0.865 / ID 0.750 × 5.5 in | $15.99 | y (2) | https://www.rockwestcomposites.com/45626-f5-5.html |
| Rock West INFINITube Size 1 in Size 2 | 45001 (OD 0.935) inside 45002 (ID 0.983) | 1.2 mm diametral gap *(calc: (0.983 − 0.935)·25.4)*. Rock West recommends low-friction tape as a spacer, so it is loose without shimming. | $89.99 + $99.99 | y | URLs in 1a |
| Gator-RC GC1002 | Ready-made 25 mm tube + 25.4 mm sleeve set, 850 mm | see 1a | $79.95 | y | see 1a |
| DragonPlate telescoping tube clamps | FDPCK-TC-125 (1.125 to 0.875 ID) $12.75; TC-150 $13.00; TC-1 $12.50 | — | — | — | https://dragonplate.com/carbon-fiber-roll-wrapped-twill-tube-1125-id-x-24-gloss-finish |

A 6 in (152 mm) ferrule is short for a wing-root joiner that carries bending. A full-length tube joiner (ME9972F in ME1172F) is the stronger choice. Size the joiner length with the spar bending analysis.

---

## 2. Wing and fuselage materials

### 2a. Foam

| Product | Size | Density | Properties | Price | In stock | Ships from | URL |
|---|---|---|---|---|---|---|---|
| Aircraft Spruce Styrofoam (small cell, blue), hot-wire friendly | 1 × 24 × 48 in (01-09700) | 2 lb/ft³ (32 kg/m³ *(calc ×16.02)*) | — | $17.95 | — | US (Aircraft Spruce) | https://www.aircraftspruce.com/catalog/cmpages/styrofoam.php |
| same | 2 × 24 × 48 in (01-10000) | 2 lb/ft³ | — | $42.50 | — | US | same |
| same | 4 × 24 × 48 in (01-10200) | 2 lb/ft³ | — | $66.75 | — | US | same |
| same | 2 × 24 × 96 in (01-10100) | 2 lb/ft³ | — | $84.85 | — | US | same |
| Owens Corning FOAMULAR 150 XPS (home-center insulation) | 2 in × 4 × 8 ft (model 45W) | — (not in the extracted datasheet text) | ASTM C578 Type X; flexural strength 60 psi (414 kPa) min, ASTM C203; water absorption ≤0.10 % vol | — (Home Depot returned 403) | — | US retail | datasheet: https://images.thdstatic.com/catalog/pdfImages/42/42a0ae07-0b4c-4678-bfee-da8123394cf8.pdf ; listing https://www.homedepot.com/p/100320352 |
| STRIX flat EPP sheets (ReadyMadeRC) | 10 mm × 1.0 × 0.6 m, 10-pack | 1.9 lb/ft³ (≈30 g/L) | — | $99.99 | y | US (Ohio) | https://www.readymaderc.com/products/details/86190-strix-flat-epp-foam-10mm-thick-1m-x-0-6m-10-pack |
| Hobby Lobby white foam board (paper-faced) | 20 × 30 in × 3/16 in | — | — | $1.99 | — | US retail | https://www.hobbylobby.com/art-supplies/project-supplies/poster-projects/white---foam-board---20-x-30/p/101651 |
| Depron (3 / 6 mm) | — | — | — | — (no live US listing found) | — | — | — |

### 2b. Fiberglass cloth

| Product | Weight | Weave | Width | Thickness | Price / yd | URL |
|---|---|---|---|---|---|---|
| US Composites style 120 (FG-C0338) | 3 oz E-glass | 4HS satin | 38 in | 0.0046 in | $8.70 (1–9 yd) | https://uscomposites.com/cloth.html |
| US Composites 1522 (FG-C0430) | 4 oz E-glass | plain | 30 in | 0.0059 in | $4.40 | same |
| US Composites 1522 (FG-C0450) | 4 oz E-glass | plain | 50 in | 0.0059 in | $6.70 | same |
| US Composites FG-C0638 | 6 oz E-glass | plain | 38 in | 0.0093 in | $5.90 | same |
| US Composites FG-C0627S (6533 S2) | 6 oz S-glass | plain | 27 in | 0.0089 in | $9.95 | same |
| Fibre Glast style 3733 (SKU 259) | 5.5–5.8 oz | plain | 38 in | 0.008–0.010 in | $7.90/yd cut (10 yd min); 1 yd pack $12.14; 5 yd pack $40.26 | https://www.fibreglast.com/product/6_oz_Fabric_38_inch_wide_259 |
| 2 oz class | — | — | — | — | No live 2 oz listing found at US Composites or Fibre Glast. The nearest light cloth is the 3 oz style 120 above. | — |

Stock was not shown on either vendor page. Both ship from the US.

### 2c. Laminating epoxy

| Product | Size | Price | Mix ratio | Mixed viscosity | Cured properties (neat resin) | URL |
|---|---|---|---|---|---|---|
| WEST SYSTEM 105 resin + 205 fast hardener | 105-B 0.98 gal + 205-B 0.86 qt | $131.42 + $81.13 = $212.55 list *(calc)*; prices effective 2026-06-22 | 5:1 by volume | 975 cps | SG 1.18; tensile 7,900 psi (54.5 MPa *(calc)*); tensile modulus 4.08×10⁵ (psi implied) = 2.81 GPa; flexural 14,100 psi; flex modulus 4.61×10⁵; compression yield 11,400 psi; pot life 9–12 min | price https://westsystem.com/?p=419 ; TDS https://www.westsystem.com/app/uploads/2022/09/105_205-207-Combined.pdf |
| WEST 105 + 206 slow | 105-B + 206-B | $131.42 + $74.38 = $205.80 *(calc)* | 5:1 | 725 cps | SG 1.18; tensile 7,300 psi; modulus 4.60×10⁵ psi; flexural 11,800 psi; pot life 20–25 min | same |
| WEST 105-A + 205-A (small) | 0.25 gal + 0.44 pt | $59.51 + $38.95 = $98.46 *(calc)* | 5:1 | — | same as 105/205 | same |
| US Composites 635 thin epoxy, 3:1 medium | 1 gal + 42.6 oz kit | $92.75 | 3:1 | 600 cps | — (not listed) | https://www.uscomposites.com/epoxy.html |
| US Composites 635, 2:1 slow | 1/2 gal + 32 oz | $53.45 | 2:1 | 600 cps | — | same |
| TotalBoat High Performance | — | — (no live US first-party page reached; product page 404) | 2:1 | — | — | — |
| ProMarine | — | — (not searched to a live page) | — | — | — | — |

### 2d. 3D-printing filament

| Product | Spool | Price | Density | Mechanical (vendor TDS) | In stock | Ships from | URL |
|---|---|---|---|---|---|---|---|
| Polymaker PolyLite LW-PLA (pre-foamed) | 800 g | $29.69 (sale; reg $32.99) at West3D | 0.9 g/cm³ (TDS v7.0, ISO 1183). West3D page says 0.8 g/cm³. | E 1689 MPa (XY) / 1726 MPa (Z); σt 24.4 MPa (XY) / 20.8 MPa (Z); bending 50.2 MPa, bending modulus 1959 MPa; HDT 50 °C at 1.8 MPa | — | US (West3D, Beaverton OR address) | https://west3d.com/products/polymaker-polylite-lw-pla-lightweight-pla-800g ; TDS https://polymaker.com/wp-content/uploads/TDS_PolyLite_LW-PLA_v7.0_2026-04-09.pdf |
| colorFabb LW-PLA (active foaming) | — (spool weight not listed) | €26.49 sale (from €32.05) | Unfoamed 1.21–1.43 g/cm³; max foamed 0.403–0.476 g/cm³; foaming starts at about 230 °C; "up to 65 %" lighter | — | y | Netherlands (EU) | https://colorfabb.com/lw-pla-natural |
| Polymaker Fiberon PA6-CF20 | 500 g | $39.99 at West3D | 1.17 g/cm³ | Dry (first TDS table): E 8637 MPa XY / 3760 MPa Z; σt 109.3 / 54.0 MPa; bending 161.0 MPa, bending modulus 7038 MPa; HDT 173 °C at 1.8 MPa. A second TDS table (presumably conditioned) gives σt 54.7 MPa XY. | — | US (West3D) | https://west3d.com/products/polymaker-fiberon-engineering-filament-pa6-cf20 ; TDS https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PA6-CF20_V1.1_EN.pdf |
| PETG (Ambrosia, West3D) | 1 kg | $20.99 (sale) | — | — | — | US | https://west3d.com/products/ambrosia-petg-filament-of-the-gods-1kg-bambu-ams-friendly-cardboard-spools-premium-3d-printing-filament |
| Bambu PETG HF / PAHT-CF (US store) | — | — (US store returned 402) | — | — | — | — | — |

### 2e. Plywood and balsa

| Product | Size | Plies | Weight | Price | Spec | URL |
|---|---|---|---|---|---|---|
| Aircraft Spruce domestic birch ply 1/8 in (3.2 mm), 90° | 2 × 4 ft (02-24530) | 3 | 15 lb per 4×8 sheet → 0.47 lb/ft² *(calc 15/32)*; density ≈ 0.47 / (0.125/12) = 45 lb/ft³ ≈ 721 kg/m³ *(calc)* | $36.50 | MIL-P-6070 "structural aircraft-grade" | https://www.aircraftspruce.com/catalog/wppages/domplywood2.php |
| same, 1/8 in | 1 × 4 ft (02-24550) | 3 | same | $18.85 | same | same |
| same, 1/8 in | 4 × 8 ft (02-24580) | 3 | 15 lb | $144.75 | same | same |
| same, 1/16 in | 2 × 4 ft (02-24330) | 3 | 7 lb per 4×8 | $34.95 | same | same |
| Aircraft Spruce Lite-Ply 1/8 in (3 mm) | 4 × 8 (02-00115) | — | — | $71.75 | — | same |
| Balsa 1/8 × 4 × 36 in (Bud Nosen, 15-pack, Walmart) | 15 sheets | — | — | $78.54 (out of stock); from a search snippet, not opened live | — | https://www.walmart.com/ip/352244652 |
| National Balsa | — | — | — | — (category page 404) | — | — |

Stock was not stated on the Aircraft Spruce pages. Aircraft Spruce ships from the US.

---

## 3. Hardware

### 3a. Boom clamps and motor mounts

| Item | Tube size | Material | Weight | Price | In stock | Ships from | URL |
|---|---|---|---|---|---|---|---|
| Tarot TL25A3 25 mm aluminium motor mount (2-piece clamp) | 25 mm | 6061-T6 | 58 g | £31.90 inc VAT | y (next ship 13/10/2026) | UK (Flying Tech) | https://www.flyingtech.co.uk/product/tarot-25mm-aluminium-motor-mount-tl25a3/ |
| Tarot TL68B52 25 mm motor mount | 25 mm | Magnesium alloy | 26 g | £13.50 inc VAT | y | UK | https://www.flyingtech.co.uk/product/tarot-ultra-lightweight-magnesium-alloy-motor-mount-25mm-tl68b52/ (motor pattern M3 Ø18/20/25 mm) |
| RCDrone CNC aluminium folding arm joint | 25/28/30/35/40 mm | Al alloy | 61 g (25 mm) | $25.00 | **n (sold out)** | China (Shenzhen) | https://rcdrone.top/sw/products/rcdrone-cnc-aluminum-folding-arm-joint-25mm-28mm-30mm-35mm-40mm-carbon-fiber-tube-clamp-for-agricultural-drone-uav-frame |
| RCDrone multi-size Al tube clamp 16–30 mm | 16/18/20/22/25/30 | Al | — | — (page 403) | — | China | — |
| Getfpv Tarot 25 mm Al mount | 25 mm | Al | — | — (page 403) | — | US | — |
| DragonPlate telescoping tube clamps | inch IDs | — | — | $12.50–13.00 | — | US | see 1d |
| 3D-printed clamps (PA6-CF or PETG) | any | see 2d | — | material cost only | — | in-house | — |

No US-stocked metric 22/25 mm aluminium clamp with a live price turned up. The cheapest stocked path is UK Tarot parts, or printed PA6-CF clamps.

### 3b. Wing bolts

| Item | Size | Qty | Price | Stock | URL |
|---|---|---|---|---|---|
| Du-Bro DUB993 nylon wing bolt XL | 1/4-20 × 3 in | 4 | $3.55 (sale) | — | https://store.hobbyetc.com/parts/view/68829 |
| Secraft M6 aluminium wing bolts + nuts + studs | M6 | 2 sets | $8.91 (sale) | y (only 3 left) | https://www.gator-rc.com/products/secraft-6mm-wing-bolts |

### 3c. Landing gear

| Item | Construction | Weight | Price | Stock | Ships from | URL |
|---|---|---|---|---|---|---|
| Tarot TL8X028 25 to 16 mm quick-release landing gear (one leg; need 2) | Ø25×Ø23×305 mm carbon down-tube, Ø16×Ø14×333 mm skid, metal tee | 170 g each | £33.90 each | y | UK | https://www.flyingtech.co.uk/product/tarot-25-to-16mm-landing-gear-with-quick-release-tl8x028/ |
| Freefly Carbon Tube 25 × 250 mm kit (2 tubes) | 25 mm carbon | 85 g/pair | $40.00 | y, "ships within 1 business day" | US (Freefly) | https://store.freeflysystems.com/products/carbon-tube-25-x-250mm-kit-for-cargo-landing-gear |
| DIY skid from boom offcuts | Leftover CFTS/Rock West tube plus printed tees | — | ≈$0 marginal | — | — | — |

---

## 4. Reference airframes (for scale and mass checks only, not to buy)

| Airframe | Span | Empty wt | MTOW | Battery | Endurance | Cruise | Lift motors | Tail | URL |
|---|---|---|---|---|---|---|---|---|---|
| **DeltaQuad Evo** | 2.69 m | 4.8 kg | 10 kg | 6S 22 Ah semi-solid Li-ion; ≈2.0 kg each *(calc: 6.8 kg with 1 battery − 4.8 kg empty)*; 1 or 2 batteries | 272 min (dual battery, 90 % usage, low wind) | 16.54 m/s | — (not listed) | Flying wing | https://docs.deltaquad.com/evo/vehicle-specifications ; https://www.deltaquad.com/resources/technical-specifications |
| **Foxtech Baby Shark 260** | 2.5 m | 5.5 kg without battery (frame alone 2.68 kg) | 12 kg | 2× 6S 5000 mAh LiPo (lift) + 30–40 Ah Li-ion (cruise); mass — | up to 2.5 h | — (max 100 km/h; stall 15–16 m/s) | 4 (T-Motor MN505 KV260) | — | https://www.suasnews.com/2019/01/foxtech-baby-shark-260-vtol/ (Jan 2019 article quoting the Foxtech spec) |
| Makeflyeasy Fighter VTOL (奋斗者VTOL) | 2.43 m | — | 13.5 kg | — | — | 19–20 m/s (recommended) | — | — | https://www.makeflyeasy.com/index.php/%e5%a5%8b%e6%96%97%e8%80%85vtol/ |
| Makeflyeasy Fighter mini VTOL | 2.1 m | — | 7.5 kg | — | — | 18–21 m/s | — (744 mm VTOL booms) | — | https://www.makeflyeasy.com/index.php/%e5%a5%8b%e6%96%97%e8%80%85mini-vtol/ |
| Foxtech Loong 2160 VTOL (PX4 docs) | 2.16 m | — | ≈7 kg excluding payload | 12S 22 Ah recommended (page inconsistent: link is a 6S 22 Ah pack) | up to 1 h 30 min | ≈17 m/s | 4 (inferred from the actuator list) | V-tail | https://docs.px4.io/v1.17/ko/frames_vtol/vtol_quadplane_foxtech_loong_2160 |
| JOUAV CW-007 | 2.2 m | — | 6.8 kg | — | 55 min | 61.2 km/h (17 m/s) | — | — | https://www.jouav.com/products/cw-007.html |
| Mugin-2 Pro / GV293 (out of class, gasoline cruise) | 2.93 m | — | 23 kg | gasoline + electric VTOL | up to 5 h | 21–23 m/s | — | H-tail | https://www.muginuav.com/product/mugin-2-pro/ |

The Freeman 2300 (rcdrone.top), Foxtech Great Shark 330 (foxtechfpv.com) and T-Drones VA25 pages all returned 403, so their numbers are not used here.

### Mass fractions *(calc)*

| Airframe | Empty / MTOW | Battery / MTOW | Structure-only / MTOW | Notes |
|---|---|---|---|---|
| DeltaQuad Evo | 4.8 / 10 = **0.48** | 1 battery: 2.0 / 10 = 0.20; 2 batteries: 4.0 / 10 = **0.40** | — | Check: 4.8 + 4.0 + 1.0 kg payload (dual-battery payload) = 9.8 kg ≈ MTOW |
| Foxtech Baby Shark 260 | 5.5 / 12 = **0.46** | ≤ (12 − 5.5 − 1.5 camera) / 12 = **≤0.42** (estimate; battery mass not published) | 2.68 / 12 = **0.22** | "Empty" includes motors and ESCs, without battery |
| Makeflyeasy Fighter VTOL | — | — | — | (empty + battery) ≤ (13.5 − 2.5 payload) / 13.5 = 0.81 |
| JOUAV CW-007 | — | — | — | (empty + battery) ≤ (6.8 − 1.0) / 6.8 = 0.85 |

**Sanity band for the 8–15 kg design (estimate from two data points):** empty
(no battery) ≈ 0.46–0.48 of MTOW, battery ≈ 0.40 of MTOW, payload ≈ 0.10–0.12,
bare airframe structure ≈ 0.22 (Baby Shark only). At 12 kg MTOW that gives about
5.6 kg empty, 4.8 kg battery and 2.6 kg structure *(calc: 12 × 0.47, 12 × 0.40,
12 × 0.22)*.

---

## What the team must measure

- **M1. Boom tube bending stiffness.** Cantilever a 0.5 m offcut of the chosen
  boom tube and hang known weights (kitchen scale plus a water jug). Back out EI
  from δ = PL³/3EI. If the measured EX comes in under 50 GPa (below Rock West's
  57.5 GPa CLT figure for 45593), boom tip deflection and the rotor-arm natural
  frequency need rechecking.
- **M2. Joiner fit.** Check that ME9972F slides into ME1172F with no measurable
  play (feeler gauge or tape shim). A diametral gap over 0.2 mm means the joint
  needs shimming or bonded sleeves.
- **M3. Linear mass.** Weigh every tube on arrival (kitchen scale) and compare
  with the listed lb/ft. Over +10 % means updating the mass roll-up.
- **M4. LW-PLA as printed.** Print a 50 mm test cube at the chosen temperature
  and weigh it to get the real density. colorFabb lists 0.40–0.48 g/cm³ foamed;
  Polymaker lists 0.9 g/cm³.
