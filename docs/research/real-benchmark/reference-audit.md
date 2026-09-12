# Saved reference audit — 2026-09-12

Scope: read-only audit of the delivered Line-Field-OCT-Optics models and saved native analysis evidence. No OpticStudio session or native recomputation was run. This document is the only audit output written. All numerical precision below describes the stored calculation, not measured optical accuracy.

The current three ZMX files match both `models.json` and the delivery manifest. The manifest also matches the current Huygens and POP JSONL evidence, report, and all 12 full-sample CFG presets. Independently reducing the raw arrays reproduced all 24 full-spectrum X/Y FWHM and full 1/e² widths exactly (maximum absolute difference: **0.0 mm**). Package provenance is strong; per-run immutable provenance is incomplete. **Huygens and POP are distinct reference methods and must have separate acceptance baselines.**

## Exact file identities

SHA-256 of current bytes:

| File | SHA-256 |
| --- | --- |
| [source/full_sample/SamplePath_Stock.ZMX](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/source/full_sample/SamplePath_Stock.ZMX>) | `04f882d3384bed689551c56aa22dcba4d0206698cbde77bf0a75dc86031b9748` |
| [source/full_sample/SamplePath_IdealSurrogate.ZMX](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/source/full_sample/SamplePath_IdealSurrogate.ZMX>) | `91d2eac8e716307444ce6043aaa1547d36278589cb950f34462b6114849dc30b` |
| [source/full_sample/SamplePath_FlatPlate.ZMX](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/source/full_sample/SamplePath_FlatPlate.ZMX>) | `c80db99f4c8e0a962464cc4fadf4d80d200e6c98ba0add28fcd0bcbf3567f6ec` |
| [source/full_sample/models.json](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/source/full_sample/models.json>) | `08f94bfbb57d3ccc59c22b317a4e069b3b28f2b2a24c1865717db2b6f7dea635` |
| [reports/evidence/final-planar-huygens.jsonl](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/final-planar-huygens.jsonl>) | `dd2e02d75ddaf3806f8f52bee0f5e693f874ee22b5e71f1fbf1b808910046184` |
| [reports/evidence/final-planar-pop.jsonl](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/final-planar-pop.jsonl>) | `efbb5dfacf31ee8f8313363d43ec4291485852a16f5289b236cf2af767834d2d` |
| [reports/evidence/final-planar-summary.json](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/final-planar-summary.json>) | `605e7d0e803da5d4d20f29610bbd79587ec4a832746d2061ace326c9ce26f90f` |
| [reports/evidence/full-sample-delivery-manifest.json](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/full-sample-delivery-manifest.json>) | `02fe3b5382a6f4e55eb3abecd2cc5d47c07b84a9af00f3c1bde99760f04616a5` |
| [reports/full-sample-path-optimization.md](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/full-sample-path-optimization.md>) | `9803ae805362f2f20546827bc27373ed1be2e9b525b23d8eb1ce830914b1a7a7` |

The delivery manifest records the model hashes and raw Huygens/POP hashes. The summary is independently connected to the raw evidence by the exact width reproduction above; its hash is recorded here rather than assumed to be a manifest entry. JSONL rows themselves do not include input hashes, timestamps, engine build, or a complete settings receipt. The generator changes POP resampling settings in memory, then saves the model after its convergence/preset pass. Thus a final model hash is a package identity, not proof that every serialized analysis setting was byte-identical during every run.

## Model boundaries and active spectrum

All models use UTF-16 LE ZMX text, millimetre lens units, 29 surfaces indexed 0–28, one on-axis field, STOP at surface 2, and primary wavelength 9 = 840 nm. `FTYP` declares **18 active wavelengths**. Although 24 `WAVM` records are serialized, records 19–24 are inactive 550 nm/weight 1 placeholders and must be excluded. `HYPR 1` selects the planar reference. Header glass catalogs are `SCHOTT LIGHTPATH`.

Surface blocks 0–3 are text-identical across all three delivered models and `source/working/OriginalSample_FactoryF240APC780_HI780Gaussian_SLD.ZMX` (baseline file SHA-256 `e4e2c9519f255bac48fb35841491a6f98a6501962574bf5aca533c29f1506a1f`). This fixed HI780 fiber/F240APC-780 collimator is the source boundary. Surface 1 is POP launch, surface 4 source output, surface 11 shaper exit, and surface 28 the sample plane. These are complete source-to-sample illumination models; they are not the separate sample-to-slit collection model.

| Surfaces | Role |
| --- | --- |
| 0–3 | Fixed fiber/collimator source |
| 5–10 | Stock: two catalog cylinders with ±90° coordinate breaks; IdealSurrogate: 2 mm N-BK7 substrate with XPOLYNOM rear surface and finite 3.3 × 4.0 mm domain; FlatPlate: 2 mm plane N-BK7 control. Ideal/Flat downstream placeholders remain air. |
| 12–15 | Y cylinder expander: reversed negative LK1836L1-B and positive LJ1477L1-B |
| 16–18 | AC254-100-B |
| 19–21 | Reversed AC254-080-B |
| 22–24 | Provisional transmitted BS014 cube: two 12.7 mm N-BK7 segments, nominal 50% internal SPLIT |
| 25–27 | AC254-080-B objective |
| 28 | Sample plane; illumination line along X, narrow dimension Y |

Active spectrum, identical in all three models. Stored wavelengths are in µm; table converts only the wavelength label to nm. Stored weight sum is approximately `0.9999999999997744`; the reference reducer normalizes these 18 weights before combining absolute irradiance.

| Native index | Wavelength nm | Stored weight |
| --- | --- | --- |
| 1 | 800 | 8.0081358047400005e-05 |
| 2 | 805 | 0.0014518265167799999 |
| 3 | 810 | 0.0137974382439 |
| 4 | 815 | 0.063860470033700004 |
| 5 | 820 | 0.107255127018 |
| 6 | 825 | 0.087790659325300002 |
| 7 | 830 | 0.073092075817000002 |
| 8 | 835 | 0.076326160809899998 |
| 9 | 840 | 0.087870698511900006 |
| 10 | 845 | 0.099905853597800007 |
| 11 | 850 | 0.107134991533 |
| 12 | 855 | 0.104151208454 |
| 13 | 860 | 0.087470181719999998 |
| 14 | 865 | 0.057081928765799997 |
| 15 | 870 | 0.0248513301449 |
| 16 | 875 | 0.0064381777734400002 |
| 17 | 880 | 0.00128161136364 |
| 18 | 885 | 0.000160179012667 |

The manifest gap map matches the current `DISZ` values at every listed index. Preserve these when comparing unchanged reference models:

| Variant | Gap indices | Thicknesses mm |
| --- | --- | --- |
| IdealSurrogate | 3, 7, 11, 13, 15, 18, 21, 24, 27 | 4.992788443928, 0.1, 5.9, 43.9075358175792, 99.9999999997294, 203.944349719342, 71.5895098008701, 71.5895098008701, 74.025 |
| Stock | 3, 7, 11, 13, 15, 18, 21, 24, 27 | 4.992788443928, 5.95, 5.9, 43.9075358175792, 99.9999999997294, 203.944349719342, 71.5895098008701, 71.5895098008701, 74.025 |
| FlatPlate | 3, 7, 11, 13, 15, 18, 21, 24, 27 | 4.992788443928, 0.1, 5.9, 42.7390066513375, 99.9999999999966, 207.611519753024, 71.5895098008701, 71.5895098008701, 74.025 |

## Saved raw cases and array semantics

Huygens arrays: [reports/evidence/final-planar-huygens.jsonl](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/final-planar-huygens.jsonl>). One-based JSONL line locators below identify exact numerical arrays under keys `x` and `y`; no curve digitization is necessary. All 15 rows have `valid=true`, `kind=Huygens`, `method=Planar`, one data series, zero grids, and finite coordinates/intensities.

| Case | Stock / Ideal / Flat line | Wavelength | Pupil | Image setting / array length | ImageDelta | Raw x interval |
| --- | --- | --- | --- | --- | --- | --- |
| Full-spectrum X | 1 / 6 / 11 | 0 = all 18 active | 512 | 128 / 129 | 6 µm | −384 to +384 µm |
| Full-spectrum Y | 2 / 7 / 12 | 0 = all 18 active | 256 | 128 / 129 | 0.5 µm | −32 to +32 µm |
| 840 nm X fine image | 3 / 8 / 13 | 9 | 512 | 256 / 257 | 3 µm | −384 to +384 µm |
| 840 nm X fine pupil | 4 / 9 / 14 | 9 | 1024 | 128 / 129 | 6 µm | −384 to +384 µm |
| Full-spectrum Y lower pupil | 5 / 10 / 15 | 0 | 128 | 128 / 129 | 0.5 µm | −32 to +32 µm |

**Huygens `x` is a coordinate array in micrometres**, including for the Y cross-section; `y` is intensity. The reducer explicitly divides coordinates by 1000 to obtain millimetres, consistent with native `ImageDelta` and observed spacing. Never treat Huygens `x` as millimetres or confuse the JSON key `y` with a physical Y coordinate.

Generator settings: HuygensPsfCrossSection, planar method, field 1, X_Linear/Y_Linear, Normalize=true, UseCentroid=false, UsePolarization=true, wavelength as above. Current saved CFG readback shows RowCol=0 (central). The worker does not explicitly assign RowCol on each raw analysis call, so central-row identity is supported by the saved configuration/readback rather than embedded in each raw row. The raw evidence has no complex field or two-dimensional Huygens grid. A separate 512×512, 1.5 µm 2D preset exists but does not turn these cross-section rows into 2D reference evidence.

POP arrays: [reports/evidence/final-planar-pop.jsonl](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/final-planar-pop.jsonl>). All 60 rows have finite central/local arrays and empty `messages`. Each variant has 18 spectral rows followed by two monochromatic convergence rows:

| Variant | SLD_POP 1024 lines | 840 nm 2048 line | 840 nm 4096 line |
| --- | --- | --- | --- |
| Stock | 1–18 | 19 | 20 |
| IdealSurrogate | 21–38 | 39 | 40 |
| FlatPlate | 41–58 | 59 | 60 |

For each POP row, `x` and `y` are **irradiance arrays**, not coordinates. Reconstruct X coordinates in mm as `x0 + i*dx` and Y as `y0 + i*dy`. Each central cut length equals `n` (1024, 2048 or 4096). The `ycuts` list retains five Y irradiance cuts requested at X = −0.3, −0.15, 0, +0.15, +0.3 mm; use each `actual_x` to document the nearest native grid location. `requested_x` is not proof of exact sampling at that position.

POP recipe: field 1, launch surface 1, end surface 28, GaussianWaist, surface-to-beam distance 0, TotalPower=1 with UseTotalPower=true, UsePolarization=true, SeparateXY=true, Irradiance output. Circular launch waist radius in mm is `(4.6 + (wavelength_um - 0.780)*0.4/0.070)*0.001/2`; at 840 nm this is `0.002471428571428571`. Full-spectrum rows use wavelength indices 1–18 separately, 1024×1024 sampling and initial X/Y window 0.4 mm. The 840 nm convergence rows use 2048×2048 or 4096×4096, initial window 0.8 mm. ResampleAfterRefraction is cleared downstream and enabled at S4 (width 8 mm), S15 (64 mm), S24 (64 mm), with the requested n and AutoResample=false.

The launch window is not the final-plane coordinate extent. The interactive saved POP preset uses 2048/840 nm/0.8 mm and must not be substituted for the 18-wave 1024/0.4 mm reference recipe. `power` is the recorded full-grid irradiance sum times dx·dy relative to unit launched power. Only this integrated value and selected cuts survive; the full 2D grid and complex field were not retained.

Native 840 nm sample pitches illustrate the resolution limit; these numbers are mm and are taken directly from the indicated raw rows:

| Variant | n | JSONL line | dx mm | dy mm |
| --- | --- | --- | --- | --- |
| Stock | 1024 | 9 | 0.01724707717427945 | 0.0010537699679451923 |
| Stock | 2048 | 19 | 0.008623368484724257 | 0.0010538127714924312 |
| Stock | 4096 | 20 | 0.0043116256276044505 | 0.0010538409901067892 |
| IdealSurrogate | 1024 | 29 | 0.025050491180513952 | 0.0010536263126613339 |
| IdealSurrogate | 2048 | 39 | 0.012524215033250756 | 0.0010536690759595205 |
| IdealSurrogate | 4096 | 40 | 0.00626177196047285 | 0.0010536972241876443 |
| FlatPlate | 1024 | 49 | 0.027950474452745514 | 0.0010536903116032947 |
| FlatPlate | 2048 | 59 | 0.013975193965099112 | 0.001053733114817712 |
| FlatPlate | 4096 | 60 | 0.006987514787148661 | 0.0010537612930487938 |

## Exact full-spectrum scalar baselines

All widths in this table are **full widths in mm**. Values come from the saved summary and were independently reconstructed from the raw arrays. For µm multiply by 1000. Match the same method, variant, axis, wavelength treatment, settings and metric definition before applying a comparison tolerance.

| Variant | Method | Axis | FWHM mm | Full 1/e² mm |
| --- | --- | --- | --- | --- |
| IdealSurrogate | Huygens | X | 0.5527616703921798 | 0.6096042824757449 |
| IdealSurrogate | Huygens | Y | 0.007588630177740743 | 0.013885136771344255 |
| IdealSurrogate | POP | X | 0.553997384404399 | 0.6074928092885262 |
| IdealSurrogate | POP | Y | 0.008341441703333084 | 0.015027317290024347 |
| Stock | Huygens | X | 0.5681549255243716 | 0.6078047331593057 |
| Stock | Huygens | Y | 0.007411477145383498 | 0.013129715461932258 |
| Stock | POP | X | 0.6642616486472988 | 0.7414818062153821 |
| Stock | POP | Y | 0.00783588488338067 | 0.013848199746636324 |
| FlatPlate | Huygens | X | 0.35165929778164307 | 0.5961722045033251 |
| FlatPlate | Huygens | Y | 0.007597092276031501 | 0.013541795174997907 |
| FlatPlate | POP | X | 0.36388131332373397 | 0.6194005418164128 |
| FlatPlate | POP | Y | 0.007981333560186807 | 0.014137381276351838 |

| Variant | Huygens X CV, central 0.42 mm | POP X CV, central 0.42 mm | POP spectrum-weighted power fraction |
| --- | --- | --- | --- |
| IdealSurrogate | 0.009918645321832582 | 0.02137390957276759 | 0.408542792959358 |
| Stock | 0.10105796167568389 | 0.06008323322535442 | 0.4041201015787037 |
| FlatPlate | 0.27160415853063835 | 0.2490156515541729 | 0.3755623835000181 |

CV is dimensionless; multiply by 100 for percent. The measured simple bench target of approximately 0.6 mm refers to **full 1/e² width**, not FWHM. The source report gives measured X FWHM 0.527 mm, full 1/e² 0.609 mm and central 0.42 mm CV 4.75%; these are contextual bench measurements, not matched immutable native reference arrays.

## Reduction contract and checks

1. Normalize the 18 stored spectral weights. For POP, interpolate each **absolute irradiance** cut, multiply by its weight, then sum. Do not peak-normalize each wavelength before summation. X comparison grid is `linspace(-0.6,0.6,6001)` mm; Y is `linspace(-0.05,0.05,5001)` mm, with zero outside each native domain. Full-spectrum POP power is the weighted sum of raw `power`.
2. For Huygens, select wavelength=0 and the exact baseline pupil/image combination. Divide raw coordinate arrays by 1000. Huygens spectral combination is native analysis behavior, not an external sum of the two 840 nm convergence rows.
3. FWHM uses 0.5 times the global peak; full 1/e² uses exp(−2) times the peak. Find the first and last samples above threshold and linearly interpolate both adjacent crossings. These are **outermost threshold spans**, including across disconnected peaks. A threshold touching the array boundary returns an invalid/NaN width, not a clipped width.
4. Central X flatness CV is population standard deviation divided by mean for |X|≤0.21 mm. The same generic reducer also writes a CV for Y, but its 0.42 mm region is not a useful Y flatness requirement. Do not use it as such.
5. The saved `cut_energy_fraction_within_18um` integrates one cut within ±0.009 mm divided by its retained cut integral. It is not 2D encircled energy or total system throughput. Secondary-peak metrics depend on the documented prominence/valley heuristic; they are not a zero-sidelobe proof.
6. Local spectral Y cuts are combined by their matching `requested_x`; retained `actual_x` values vary with wavelength/grid. A future comparison requiring a physically identical X position must account for that difference.

The independent audit used standalone NumPy arithmetic, read the raw JSONL and current model weights, and did not import or execute the project reporting/worker modules. All 24 full-spectrum width differences against the summary were exactly 0.0 mm. Array finiteness and empty POP message lists were checked. This verifies the saved reduction, not fresh native execution.

## Existing convergence evidence and limits

| Variant | POP 840 nm X FWHM 2048 → 4096, mm | Relative X change | POP 840 nm Y FWHM 2048 → 4096, mm | Relative Y change |
| --- | --- | --- | --- | --- |
| IdealSurrogate | 0.5503412288708044 → 0.5503812264065493 | 7.267770184493649e-05 | 0.008492197185810142 → 0.008502852728275119 | 0.0012547450597097942 |
| Stock | 0.6681001477621524 → 0.669978083568461 | 0.00281085973801809 | 0.0075759977356652615 → 0.0075760787801145285 | 1.0697528179726135e-05 |
| FlatPlate | 0.3647838684606416 → 0.3644321595879696 | -0.0009641568695353264 | 0.007807511143906662 → 0.00780245300050387 | -0.0006478560593204952 |

These small changes are practical checks of this saved recipe, not a general error bound. Full-spectrum POP uses 1024 sampling, whereas the convergence pair is monochromatic 2048/4096. Its native X pitch near 840 nm is about 17–28 µm at 1024; interpolating it onto a 0.2 µm reporting grid adds no spatial information. At 2048→4096 the final Y pitch remains approximately 1.054 µm while the Y window expands. Thus tiny Y width changes do not certify convergence under finer Y sampling.

Huygens 840 nm X changes both pupil sampling (512→1024) and image sampling (256→128, spacing 3→6 µm); it is not a one-variable convergence sweep. The retained full-spectrum Y cases do isolate pupil 128→256 with the same 0.5 µm image spacing. Their lower-pupil FWHM values are:

| Variant | P128 Y FWHM mm | P256 Y FWHM mm |
| --- | --- | --- |
| IdealSurrogate | 0.007589825764077984 | 0.007588630177740743 |
| Stock | 0.007411166329448606 | 0.007411477145383498 |
| FlatPlate | 0.007598329861075756 | 0.007597092276031501 |

## Missing evidence and acceptable benchmark claims

- **Cross-method equivalence is not established.** Stock X is 0.5681549255 mm Huygens FWHM versus 0.6642616486 mm POP, and 0.6078047332 versus 0.7414818062 mm full 1/e². The delivered report explicitly preserves stock ripple and method-dependent width limits. The manifest marks strict zero-sidelobe Ayase equivalence false. Reproducing either method does not resolve their disagreement or prove physical truth.
- Raw rows lack model hash per run, timestamps, exact live OpticStudio build and comprehensive readback. The report/worker identify OpticStudio 2024 R1 / installation path `Ansys Zemax OpticStudio 2024 R1.00`; actual runtime build is not recorded per result. A fresh benchmark should capture model SHA-256, engine version/build, active spectrum and primary index, field, polarization, planar choice, complete analysis settings and output-grid metadata in each receipt.
- Current retained evidence does not contain the Huygens text-export headers requested by the generator, a full 2D irradiance reference grid or complex pupil/field arrays. It cannot support a new 2D or phase-derived metric solely from these cuts. MTF, Strehl, RMS spot and axial OCT metrics are not interchangeable with these illumination widths.
- Fixed-source prediction (~1.74 mm full 1/e² output diameter) differs from measured source output (~1.54 mm). The fiber Gaussian waist remains uncalibrated against that measurement. No uncertainty interval here covers actual source mode, assembly, glass/coating data, tolerances or manufacturing.
- Downstream nominal `I.995` coatings and the provisional 50% cube do not model the actual diagonal coating, polarization response, ghosting or missing ND/reference/detection-arm optics. The ideal shaper is a mathematical surrogate, not an as-built/catalog Ayase prescription.
- `final-planar-point.jsonl` concerns the separate collection path. Do not merge its point-imaging fields with full-sample illumination axes or use this audit to claim OCT SNR, axial resolution, global optimum, or measured prototype improvement.

A defensible first benchmark is: unchanged copied model, same native analysis method and explicit recipe, same spectrum and units, fresh widths and retained arrays compared against these saved references. Numerical tolerances need a declared purpose and convergence evidence; the existing evidence does not justify inventing a universal sub-percent physical-accuracy tolerance.

## Source pointers

- [tools/final_planar_validation.py](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/tools/final_planar_validation.py>)
- [tools/full_sample_worker.ps1](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/tools/full_sample_worker.ps1>)
- [tools/report_planar_final.py](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/tools/report_planar_final.py>)
- [tools/optical_support.py](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/tools/optical_support.py>)
- [reports/evidence/full-sample-config-readback.json](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/full-sample-config-readback.json>)
- [reports/evidence/full-sample-delivery-manifest.json](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/evidence/full-sample-delivery-manifest.json>)
- [reports/full-sample-path-optimization.md](<C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics/reports/full-sample-path-optimization.md>)
