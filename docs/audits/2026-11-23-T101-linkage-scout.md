# T-101 S1 scout: elevon linkage options (rod, clevis, horn bushing, PETG allowable)

Role: scout. Records options and evidence only; picks nothing. All URLs below were opened in this run on 2026-11-23 (date checked).
"—" = not found / not shown on the page. Arithmetic marked "calc" is mine from cited inputs, not a source figure.

## Problem (from the brief and repo files)

- Concept A elevon linkage, `redesign/qp/A/cad/amodel/electrical.py` ~640-700: 1.2 mm rod (RMRC linkage set), Z-bend leg in a 1.3 mm hole in the EMAX ES3054HV arm at 6.86 mm radius, 1.0 mm clevis pin through a 2.0 mm PETG horn blade (1.1 mm reamed hole), printed PETG keeper MEC-008.
- After the chord increase, rod force is 30.44 N (hold) and 63.25 N (stall) (`redesign/qp/A/mechanism/out/T101_data/chord/U5_mechanism.md`, quoted in the brief, not re-opened).
- Failing rows: Z-bend leg needs 1727 MPa yield vs 1680 MPa (A228, "recalled"); horn-hole bearing 32.8 MPa factored vs 20 MPa (PETG EST); shear-out at stall 13.8 vs 11.55 MPa; keeper bridge utilisation 1.69.
- Repo allowables (read in `redesign/qp/A/mechanism/linkage_loads_check.py` lines 15-26, 68): rod bending allowable = 0.78 S_ut with S_ut = 2211 / d^0.145 (d in mm), "Shigley Tables 10-4/10-6, RECALLED, NOT re-read: VERIFY"; curved-wire K = 1.625 at bend radius = d; PETG 20 MPa in-layer and bearing, EST. Hold factor 2.156 (calc check: 30.44 x 2.156 / (1.0 x 2.0) = 32.8 MPa, so the bearing row is hold-governed).
- `redesign/team/F5/RC-LINK.md` has no clevis or RMRC-clevis notes (grep for clevis/slot/RMRC: no match). No RMRC clevis dimensions in the repo files I searched.

## Item 1. Music-wire diameters above 1.2 mm, vendors, strength

### 1a. A228 minimum tensile (ksi, from a mill datasheet reproducing the A228 table; MPa = calc, 1 ksi = 6.895 MPa)

Source: Gibbs Interwire, Type Corrostan Music Wire datasheet, https://www.gibbswire.com/wp-content/uploads/2025/08/Gibbs-Datasheet-Wire-10-Type-Corrostan-Music-Wire.pdf (opened 2026-11-23). Its table header says "ASTM-A-313" while the body says chemistry "Per ASTM-A-228"; the page also says the charts are "for reference only. It is not intended for engineering or design." The values match the A228 min/max pairs quoted in a web search summary of the ASTM A228 PDFs, but those ASTM PDFs would not open (404 / error page), so the ASTM text itself was NOT read. Treat as vendor-reported A228-equivalent.

| Diameter (in) | mm | Tensile min (ksi) | Tensile min (MPa, calc) | Tensile max (ksi) | Note |
|---|---|---|---|---|---|
| 0.048 | 1.22 | 306 | 2110 | 339 | nearest listed row to the current 1.2 mm (0.047 in not listed) |
| 0.055 | 1.40 | 300 | 2068 | 331 | |
| 0.059 | 1.50 | 296 | 2041 | 327 | |
| 0.063 | 1.60 | 293 | 2020 | 324 | 1/16 in = 0.0625 in sits between 0.059 and 0.063 rows |
| 0.067 | 1.70 | 290 | 2000 | 321 | |
| 0.072 | 1.83 | 287 | 1979 | 317 | |

Repo formula check (calc): 0.78 x 2211 / d^0.145 gives 1680 MPa at 1.2 mm, 1644 at 1.4 mm, 1626 at 1.5 mm, 1618 at 1.6 mm. So the repo allowable falls about 3.7% from 1.2 to 1.5 mm while the table minimum falls about 3.3%; both fall slowly with d, as the brief said.

Yield/tensile basis for bending of wire: "none found" in any page I opened. The only basis in hand is the repo's recalled 0.78 S_ut (Shigley), still unverified. The RS datasheet below confirms only the general A228 range (245-455 ksi).

Supplementary: RS Components / "Precision Brand Music Wire" datasheet, https://docs.rs-online.com/d240/A700000009631396.pdf (opened 2026-11-23): C1085 carbon steel, "Meets ASTM-A-228", tensile 245,000-455,000 psi overall; only the 0.029 in row shown (333-363 ksi). No row above 0.029 in.

### 1b. Required-yield scaling with diameter (calc, estimate)

Bending stress ~ 1/d^3 at fixed force and moment arm. With the repo's 1727 MPa at d = 1.2 mm and ignoring the small growth of the arm (d/2 + t_arm/2) term and any change in bend radius: d^-3 factor gives 1.4 mm about 1088 MPa, 1.5 mm about 884 MPa, 1.6 mm about 729 MPa. The (d + t_arm) arm term is unquantified here because t_arm is not in the sources I opened ("—"); including a 1 mm arm would raise the 1.5 mm figure to about 1004 MPa (illustrative). Any larger rod also needs a bigger hole in the servo arm and a bigger clevis jaw; those are not checked here.

### 1c. Vendors / listings (straight lengths or pushrod wire)

| Option | Source URL | Date | Dimension | Strength | Price | Vendor | Fit note |
|---|---|---|---|---|---|---|---|
| K&S 503 music wire 0.055 in (1.4 mm) x 36 in, pack of 3 | https://www.sunwardhobbies.ca/055-pack-of-3-music-wire-36-long-ks-engineering-503/ | 2026-11-23 | 0.055 in x 36 in | A228 table row 300 ksi min (not stated on the page) | $5.49 CAD, 1 in stock | Sunward Hobbies (Canada) | Shipping: extra "long metals" fee, amount not shown on page. Canadian vendor; duty/currency to us unknown |
| K&S 504 music wire 0.062 in x 36 in, pack of 3 | https://sunwardhobbies.ca/062-pack-of-3-music-wire-36-long-ks-engineering-504 | 2026-11-23 | 0.062 in (1.57 mm) x 36 in | — (page; table 0.063 row 293 ksi) | $5.49 CAD, out of stock | Sunward Hobbies | Same shipping note |
| K+S Metals music wire 0.062 in x 36 in, pack of 15 (KSM504) | https://store.hobbyetc.com/parts/view/172747 | 2026-11-23 | 0.062 in x 36 in, 15 pcs | — | $13.81 sale ($14.54 list), not in stock | Hobby Etc | Shipping not shown |
| RMRC piano wire 0.059 in (1.5 mm) x 12 in, 6 pcs | https://www.readymaderc.com/products/details/-059-piano-wire-6-pcs-with-z-bends | 2026-11-23 | 1.5 mm x 300 mm | — | $5.49, in stock (collection page https://www.readymaderc.com/collections/airplanes/build-and-repair-parts/control-horns-hinges-linkages, same price) | Ready Made RC (Ohio) | Z-bends not confirmed on the listing (URL slug says "with-z-bends"); shipping cost not shown (shipping weight 0.057, units not stated); "A228" not stated |
| Du-Bro .062 in x 12 in music-wire pushrod (DUB976) | https://motionrc.com/products/du-bro-pushrod-062-x-12-dub976 | 2026-11-23 | 0.062 in x 305 mm, ~19 mm thread one end | — | price shown garbled ("$089") | Motion RC | Threaded end is not a Z-bend; cannot use as is |
| Sullivan SUL515 1/16 in cable pushrod with clevis (2) | https://www.amainhobbies.com/sullivan-pushrods-36-cable-1-16-w-clevis-sul515/p105741 | 2026-11-23 | 0.063 in zinc-plated aircraft cable, 30-36 in, 2-56 thread | — | $10.92, back order | AMain Hobbies | Cable (not music wire), semi-flexible; not a stiff linkage |

Not opened (so no figures used): K&S 8125 / dkhardware, Zoro, OnlineMetals pages (403), ASTM A228 iteh PDFs (404/not a PDF), Scribd (410).

Cost to us (item 1), calc: steel at ~7.85 g/cm3 (recalled density, not sourced) is about 0.89 g per 100 mm at 1.2 mm and 1.39 g per 100 mm at 1.5 mm (+0.50 g per 100 mm); the rod length (L_ROD) is in the repo, not read here. Part count unchanged (one rod per linkage, same Z-bend and clevis count). $ about 5.5 per pack of 3 to 6 straight rods (CAD or USD as stated above) plus shipping not shown. Fit: needs a larger arm hole (currently 1.3 mm) and a clevis for the bigger wire (item 2); Z-bends must be made by the team (pliers; Model Aviation notes Z-bend pliers work up to .062 in / 2-56 wire, the Du-Bro E/Z Bender to .093 in, see item 5 source).

## Item 2. Clevises / Z-bend practice

| Option | Source URL | Date | Dimension | Strength | Price | Vendor | Fit note |
|---|---|---|---|---|---|---|---|
| RMRC 10-piece pushrod/linkage set: 10 Z-bend rods 1.2 mm (.047 in) x 200 mm, 10 clevises, 10 horns (20 mm), 10 connectors | https://www.readymaderc.com/products/details/rmrc-10pc-pushrod-linkage-set-control-horn | 2026-11-23 | rod 1.2 mm x 200 mm; clevis slot width, pin diameter: not published on the page | — | $8.99 | Ready Made RC | Current baseline. Clevis jaw/pin dimensions "—"; the repo's 1.0 mm pin and any slot width must be measured on the delivered part |
| Du-Bro Long Arm Micro Clevis 1.2 mm (.047 in), 2 pack (DUB974) | https://motionrc.com/eu/products/du-bro-long-arm-micro-clevis-1-2mm-047-black-2-pack-dub974 | 2026-11-23 | throat depth 0.6 in (15.2 mm); snap-fit with silicone safety band; weight 0.04 g each; pin size and slot width "—" | — | EUR 319 shown (looks like a price-display error; unreliable) | Motion RC | Wire size is the baseline 1.2 mm; no help for bigger wire |
| Freewing clevises for 1.5 mm pushrod, 8 pack (N213), with 100 mm silicone tube | https://motionrc.com/products/freewing-1-5mm-clevises-8-pack-n213 | 2026-11-23 | slot width, pin, length, material: "—" | — | "$399" shown (display error likely; unreliable) | Motion RC | Exists for 1.5 mm wire; pin and jaw not published, so cannot tell whether the pin is 1.0-1.5 mm |
| Du-Bro Kwik-Link clevises (2-56 spring steel #109 $2.15; 2-56 solder #112 $1.95; 4-40 #304 $2.70; 4-40 solder #305 $2.70), sized by thread | https://www.readymaderc.com/collections/airplanes/build-and-repair-parts/control-horns-hinges-linkages | 2026-11-23 | 2-56 = .062 in (Model Aviation source); jaw and pin "—" | — | as listed | Ready Made RC | 2-56 threaded wire is about 1.6 mm; solder types attach to plain wire; pin sizes unpublished |
| Sullivan Gold-N-Clevis (steel, welded pin, retaining clip) on 1/16 in cable | https://www.amainhobbies.com/sullivan-pushrods-36-cable-1-16-w-clevis-sul515/p105741 | 2026-11-23 | page lists 2-56 thread only; pin diameter not listed | — | $10.92 for rod + 2 clevises | AMain | A search summary said the welded-pin design had no loose pin; that statement was NOT on a page I opened, so unconfirmed |

Finding: published clevis slot widths and pin diameters for 1.2-1.6 mm wire were not found on any page opened. The only dimensions shown are the DUB974 throat depth 15.2 mm and its 0.04 g mass. The Z-bend practice is already direct-in-arm in the repo; a bigger-wire swap would need the clevis pin and slot measured from a bought sample ("—" here).

Cost to us (item 2): a clevis change is a purchase of 2-8 clevises (about $2 to $9, the Freewing price is unreliable); part count unchanged; the printed horn jaw width and pin hole (1.1 mm reamed) must be re-derived from a measured clevis; build time: measure + redesign horn CAD.

## Item 3. Brass tube / eyelets for the horn hole

| Option | Source URL | Date | Dimension | Strength | Price | Vendor | Fit note |
|---|---|---|---|---|---|---|---|
| K&S 1143 round brass tube 1/16 in OD x 0.014 in wall x 36 in | https://www.sunwardhobbies.ca/1-16-pack-of-1-round-brass-tube-0-14-wall-36-long-ks-engineering-1143/ | 2026-11-23 | OD 1/16 in = 1.588 mm, wall 0.014 in = 0.356 mm, ID = 0.875 mm (calc) | — (page); brass allowables below | $5.99 CAD | Sunward Hobbies (Canada) | ID 0.875 mm is smaller than the 1.0 mm pin: does not fit that pin; would suit a 0.8 mm pin. Shipping: extra long-metal fee, amount not shown |
| Larger K&S tube (e.g. 5/64 in, 3/32 in OD, 0.014 in wall) for a 1.0 mm pin | — | — | — | — | — | — | not opened; "—" |
| Miniature brass eyelets | — | — | — | — | — | — | none opened; "—" (not found) |

Brass allowable (rod/bar, ASTM B927/B927M-23, C26000, from the Wieland Concast reference): https://www.concast.com/files/C26000.pdf (opened 2026-11-23; PDF text extracted locally).

| Temper (rod under 1/2 in) | Tensile min | Yield (0.5% ext.) min |
|---|---|---|
| H01 quarter hard | 50 ksi (345 MPa) | 30 ksi (205 MPa) |
| H02 half hard | 57 ksi (395 MPa) | 35 ksi (241 MPa) |

H04 (hard) is listed in the same file; I did not read its under-1/2-in row. These are rod values; tube temper and strength for K&S tube are "—" (not published on the opened pages; K&S tube is commonly half hard, not sourced here).

Calc (brass vs PETG bearing): bearing stress on the printed hole = F_factored / (contact width x 2.0 mm). Current: 65.6 N / (1.0 mm pin x 2.0 mm) = 32.8 MPa (hold). If a bonded bushing of OD 2.0 mm were pressed in (full blade thickness unchanged), PETG bearing becomes 65.6 / (2.0 x 2.0) = 16.4 MPa, under the repo's 20 MPa; a 1.6 mm OD gives 20.5 MPa. The brass-pin bearing is then metal on metal (brass yield 205-241 MPa vs 32.8 MPa). The cost is a ligament reduction: the horn hole grows from 1.1 mm to the bushing OD, so shear-out, already failing at stall (13.8 vs 11.55 MPa), must be recomputed (not done here).

Cost to us (item 3): brass tube about 0.01 g per mm of 1.588 mm OD tube order of magnitude (calc, density 8.5 g/cm3 recalled), negligible; one new small part per horn (bushing) plus bonding step; $ about $6 CAD per 36 in tube plus shipping; fit: needs a tube with ID at or above the pin and OD at or below blade space; no matching size verified.

## Item 4. PETG bearing / compressive strength

Source: Prusament PETG technical data sheet v1.1, https://www.3dprintergear.com.au/assets/files/technical-data-sheet%20(1).pdf (opened 2026-11-23; text extracted locally; column alignment is imperfect in the extracted text).

| Property (printed specimens, 0.20 mm FAST, 250 C, Prusa MK3) | Horizontal | Method |
|---|---|---|
| Tensile yield strength | 47 +/- 2 MPa | ISO 527-1 |
| Tensile modulus | 1.5 +/- 0.1 GPa (text-extraction value; repo uses E_PETG 2.1 GPa EST) | ISO 178 as printed in table |
| Elongation at yield | 5.1 +/- 0.1 % | ISO 178 (as printed) |
| Flexural strength | 66 +/- 2 MPa | ISO 179-1 (as printed) |
| Vertical (xz) column | garbled in extraction (tensile yield shown as 1.6 +/- 0.1, clearly misaligned); not used | |
| Filament tensile yield | 74 MPa | |

Compressive strength: not found on this datasheet (no compressive row). Bearing strength: not found. The sheet states values "are significantly dependent on print settings, operator experiences, and surrounding conditions."

Comparison: repo EST 20 MPa is about 43% of the horizontal printed tensile yield 47 MPa. The factored bearing demand of 32.8 MPa is above that EST but below the printed tensile yield; whether a bearing allowable above 20 MPa is defensible needs a bench test of printed hole (the T-101 test plan owns that); I did not find a datasheet allowable for bearing.

Cost to us (item 4): $0 and no mass; changes only the allowable. Risk: a datasheet tensile value is not a bearing or creep allowable.

## Item 5. How others size horns/pushrods; brass in horn holes

- Model Aviation "Control Linkage Roundup", https://www.modelaviation.com/node/1891 (opened 2026-11-23): states there "does not seem to be any standard sizing" for these linkage interfaces; oversize holes create lash, undersize holes bind; recommends pin vise, mini drills, calipers to .001 in; Z-bend pliers (Great Planes, Hangar 9) handle .062 in (2-56) and smaller; Du-Bro E/Z Bender up to .093 in (4-40). No brass tube or bushing in the article; no hinge-moment sizing.
- FlyRC, https://flyrc.com/?p=1324 (opened 2026-11-23): one interviewed modeler suggests "drilling the hole slightly oversize and epoxying a short section of brass tubing" into the control surface (for horn screw holes) to strengthen it. No dimensions or sizing method given.
- Hinge-moment-based sizing of horns/pushrods with bushings: none found in pages opened (a search summary mentioned forum threads on horn placement; those threads were not opened, so not cited).

Cost to us (item 5): none directly; supports the brass-tube bushing concept (item 3) as hobby practice, but not as an engineered sizing method.

## Cost-to-us summary per option (calc and sources above; mass is estimate)

| Option | Mass | $ | Part count | Fit / build effort | Evidence gap |
|---|---|---|---|---|---|
| A. 1.4-1.6 mm A228 rod (K&S 503/504, RMRC .059 piano wire) | about +0.5 g per 100 mm (1.5 vs 1.2 mm) | about $5.5 per pack (CAD or USD as listed) + shipping not shown | same | bigger arm hole, bigger clevis, new Z-bend by hand | clevis jaw/pin for that wire not published; A228 table read via mill sheet, ASTM PDF not opened |
| B. 1.5 mm clevis (Freewing N213) or 2-56 Kwik-Link | negligible | price display unreliable ($399 shown) / $1.95-$2.70 per 2 | same | horn jaw and pin must be re-measured | pin and slot dimensions unpublished |
| C. Brass bushing in horn hole (K&S tube) | negligible | $5.99 CAD per 36 in tube | +1 small part per horn | OD/ID not verified (1/16 in tube ID 0.875 mm < 1.0 mm pin); shear-out must be recomputed | no verified tube size, no tube yield |
| D. Raise PETG allowable from 20 MPa via datasheet | 0 | 0 | 0 | none | datasheet gives tensile yield 47 MPa only; no bearing or compressive value |
| E. Keep 1.2 mm rod and redesign loads (out of scope for this scout) | — | — | — | — | not researched |

## Sources opened (2026-11-23)

1. https://www.gibbswire.com/wp-content/uploads/2025/08/Gibbs-Datasheet-Wire-10-Type-Corrostan-Music-Wire.pdf (A228-labelled tensile table, text extracted locally)
2. https://docs.rs-online.com/d240/A700000009631396.pdf (music wire datasheet, A228 range)
3. https://www.concast.com/files/C26000.pdf (C26000 rod tensile/yield by temper)
4. https://www.3dprintergear.com.au/assets/files/technical-data-sheet%20(1).pdf (Prusament PETG TDS)
5. https://www.sunwardhobbies.ca/055-pack-of-3-music-wire-36-long-ks-engineering-503/
6. https://sunwardhobbies.ca/062-pack-of-3-music-wire-36-long-ks-engineering-504
7. https://www.sunwardhobbies.ca/1-16-pack-of-1-round-brass-tube-0-14-wall-36-long-ks-engineering-1143/
8. https://store.hobbyetc.com/parts/view/172747
9. https://www.readymaderc.com/products/details/-059-piano-wire-6-pcs-with-z-bends
10. https://www.readymaderc.com/products/details/rmrc-10pc-pushrod-linkage-set-control-horn
11. https://www.readymaderc.com/collections/airplanes/build-and-repair-parts/control-horns-hinges-linkages
12. https://motionrc.com/products/du-bro-pushrod-062-x-12-dub976
13. https://motionrc.com/eu/products/du-bro-long-arm-micro-clevis-1-2mm-047-black-2-pack-dub974
14. https://motionrc.com/products/freewing-1-5mm-clevises-8-pack-n213
15. https://www.amainhobbies.com/sullivan-pushrods-36-cable-1-16-w-clevis-sul515/p105741
16. https://www.modelaviation.com/node/1891
17. https://flyrc.com/?p=1324

Repo files read: `docs/reference/agent-standard/LOCAL.md`, `redesign/qp/A/mechanism/linkage_loads_check.py` (lines 15-26 and grep hits), `redesign/team/F5/RC-LINK.md` (grep only). `electrical.py`, `U5_mechanism.md` and AR-004 not opened; their values are quoted from the brief.

Blocked / failed to open (not cited for facts): ASTM A228 PDFs at cdn.standards.iteh.ai (404 or error page), Scribd A228 (410), dkhardware, Zoro, makeitfrom (403), onlinemetals (403), racedawgrc (429).
