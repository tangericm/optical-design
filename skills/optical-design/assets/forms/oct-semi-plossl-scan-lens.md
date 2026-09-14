# OCT semi-Plössl scan lens

Two identical cemented achromats (the `cemented-achromat-doublet` cell, scaled and
mirrored so their flint sides face each other), stop 27.6 mm in front of the first
element at the galvo pivot, 1.6 mm air gap between the pair, 36.00 mm system EFL,
4 mm entrance pupil (f/9), +/-6 degree scan, 800/840/900 nm — an LSM03-class envelope.
Placing the stop at the system's front focal point makes the exit pupil land at
infinity, which is what makes the image-side chief ray parallel to the axis
(telecentric) regardless of scan angle; that is the whole point of the semi-Plössl
topology for a scanned sample arm.

**This form is not yet a good lens — that is deliberate.** It hits EFL, pupil and
telecentricity (chief-ray angle 0.000 at 840 nm, +/-6 degrees) exactly, because those
were the only optimization targets used to build it. On-axis RMS spot is 102 um
against a 9.2 um Airy radius at 840 nm/f9 — spherochromatism from the two cemented
interfaces, uncorrected because nothing asked the optimizer to correct it, dominates.
Telecentricity error away from 840 nm has not been checked at all. Rebalancing this
exact file across 800-900 nm is eval scenario 3 in `evals/evals.json`.

Variables to release, roughly in this order: the four element curvatures (they were
never varied — only stop distance, group separation and back focus were), then the
inter-group air gap, then, if still short, allow the two elements to stop being
mirror-identical and let them differ.

The semi-Plössl scan-lens form, *Appl. Opt.* 55, 646 (2016); Thorlabs LSM03 scan lens
datasheet for the target envelope this form approximates.
