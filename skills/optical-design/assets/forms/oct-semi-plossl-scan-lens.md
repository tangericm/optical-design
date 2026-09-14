# OCT semi-Plössl scan lens

Two identical cemented achromats (the `cemented-achromat-doublet` cell, scaled and
mirrored so their flint sides face each other), stop 27.6 mm in front of the first
element at the galvo pivot, 1.6 mm gap between the pair, 36.00 mm system EFL, 4 mm
entrance pupil (f/9), +/-6 degree scan, 800/840/900 nm — an LSM03-class envelope.
Stop at the system's front focal point puts the exit pupil at infinity, so the
image-side chief ray stays parallel to the axis at any scan angle — the whole point of
the semi-Plössl topology in a scanned sample arm.

**Not yet a good lens, deliberately.** It hits EFL, pupil and telecentricity
(0.000 deg at 840 nm, +/-6 deg) exactly — the only things asked of the optimizer.
On-axis RMS spot is 102 um against a 9.2 um Airy radius at 840 nm/f9;
spherochromatism from the two cemented interfaces was never corrected. Telecentricity
away from 840 nm has not been checked. Rebalancing this file across 800-900 nm is
a band-rebalancing learning exercise.

Release the four element curvatures first (never varied — only stop distance, group
separation and back focus were), then the inter-group air gap, then let the two
elements stop being mirror-identical if still short.

The semi-Plössl scan-lens form, *Appl. Opt.* 55, 646 (2016); Thorlabs LSM03 scan lens
datasheet for the target envelope.
