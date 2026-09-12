# Real-design benchmark implementation

The user approved the next sequence, beginning with a real-design benchmark. Inspection found
the current Line-Field-OCT-Optics models and their saved native evidence. The existing spherical
FFT adapter cannot represent this validation: the models use source NA/Gaussian apodization,
cylinders, coordinate breaks, a polynomial surrogate, polarization and 18 wavelengths.

## Architecture and boundaries

Add a separate read-only native profile-analysis backend and benchmark runner. Preserve the
existing optimization adapter's restrictions. Benchmark copied models through explicitly set
Huygens and POP settings, retain raw curves and exact setting readback, and compare against
the existing project's raw evidence. A comparison pass establishes reproduction, not suitability
as an Ayase replacement or manufacturing acceptance. Do not apply optimization based on a
known unresolved method discrepancy or transplant test-bench targets to the sample plane.

Original project inputs, reference evidence and analysis configurations remain untouched.
Any API changes to POP computational resampling affect only an owned in-memory copy; restore
the saved baseline after each analysis. Do not run the older builder/validation entrypoints,
which can save over original models and presets. Do not redistribute user optical prescriptions
inside the installable skill package. Benchmark manifests reference external model paths/hashes.

## Tasks

- [x] Audit three current source hashes, spectral weights and retained raw reference identities.
- [x] Add tested 1D cut metrics: interpolated threshold widths, ROI CV, support/edge diagnostics,
  multimodal topology, and absolute-irradiance spectral combination.
- [x] Add strict benchmark manifest parsing and a copied-model runner with source/catalog/
  reference hashes, explicit settings, incremental raw results, failure evidence and restoration.
- [x] Implement native Huygens cross-section and Gaussian-waist POP profiles; verify actual
  installed API settings, coordinate units, field identity and polarization settings live.
- [x] Run the previous spherical audit on a copied real model to record its honest capability
  boundary, then execute matching three-model Huygens/POP cases and compare reference metrics.
- [x] Evaluate convergence/control cases sufficient to distinguish reproduction from physical
  agreement; do not accept an optimization from an unresolved profile disagreement.
- [x] Add documentation and behavioral routing for illumination profiles versus point-image
  PSFs. Run meaningful unit/native/package checks and independent review.
- [ ] Integrate verified changes into the original optical-design checkout locally; preserve
  original OCT models/evidence and the earlier untracked audit directory.

## Initial live cases

For each of Stock, IdealSurrogate and FlatPlate: Huygens X all wavelengths, pupil512/image128,
delta6um; Huygens Y all wavelengths, pupil256/image128, delta0.5um; Force Planar, polarization
enabled, field1, normalized central cuts. POP: wave indices1..18, 1024², 0.4mm launch window,
Gaussian waist from the documented MFD law, startS1/endS28, 1W input, polarization and SeparateXY,
resample S4 at8mm and S15/S24 at64mm. Sum absolute spectral irradiance using model weights.
Use fresh output directories and native worker subprocess ownership.
