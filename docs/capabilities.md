# Capabilities and limits

[Documentation](README.md) / Capabilities

## Shipped capabilities

| Capability | Shipped scope |
|---|---|
| Numerical optics | Resolution, Gaussian beams, Zernike/Seidel math, pupil PSF/MTF, interferometry |
| Inspection and edits | Physical prescription inspection; explicit radius/thickness edits with expected-value checks, fixed-state verification and saved reload |
| Prescription audit | Explicit fields, wavelengths, metric identities, units and hard requirements |
| Refocus | Final air gap only; bounded search; fixed prescription invariants; native save/reload verification |
| Optimization | Up to four explicit radius/thickness variables; bounded search, hard requirements and saved-candidate verification |
| Composite merit | Dimensionless weighted RMS across explicit metrics, fields and wavelengths; target, scale, weight and residual evidence for each term |
| Local sensitivity | Central differences at declared radius/thickness steps; derivatives, finite-step effects and nonlinearity; rankings within a metric and unit |
| Separate validation | Predeclared requirements at extra fields/wavelengths or finer sampling; saved winner checked after search; failure rejects candidate |
| Tolerance evidence | Seeded independent radius/thickness perturbations, optional bounded focus compensation, paired pass rates and Wilson intervals |
| Review package | Standalone HTML and Markdown; verified artifact hashes, metric comparisons, parameter changes, sampled charts and an axial vertex schematic |
| Interactive MCP tools | Local stdio capabilities/start/status/cancel/results/review; owned jobs and confined input/output paths |
| Catalog shortlist | Local declared records, identity/provenance validation, unit-aware constraints and ranking |
| Native profile benchmark | Copied-model Huygens/POP central intensity cuts, explicit settings and hashes, native sampling diagnostics, optional same-method reference comparison |
| Guidance | Specifications, microscopy, OCT, interferometry, optimization, PSF/MTF and tolerancing references |

## Supported models and analysis limits

The native prescription adapter supports centered Standard conic and EvenAspheric
sequential refractive systems in mm with angle fields and entrance-pupil diameter.
Conics and all eight even-asphere coefficients remain fixed during edits and optimization.
The portable adapter supports its documented spherical/plane contract. Analyses are scalar.
Coatings, coordinate breaks, multiple configurations and unsupported surface types reject.
The separate native profile backend analyzes mm,
single-configuration sequential models with complex surfaces and explicit native polarization
settings. POP currently supports a declared Gaussian-waist launch; this is not generalized
validation of arbitrary models, source fields or polarization assumptions.

Topology changes, glass selection during optimization, live GUI attachment, arbitrary portable Zemax imports,
non-sequential/stray-light analysis and manufacturing release are not shipped. The restricted
portable ZMX importer rejects unsupported directives instead of silently dropping them.
Tolerance pass rates depend on the declared perturbation model. Profile reference agreement
means same-method numerical reproduction; illumination cuts are not point-image PSFs,
integrated marginals or measured OCT performance.

## Research evidence

The [real-design reference audit](https://github.com/tangericm/optical-design/blob/v1.1.0/docs/research/real-benchmark/reference-audit.md) records saved OCT inputs, model hashes, spectrum, units and uncertainty. Its 75 model/case records are reference inputs, not proof of fresh native execution or physical acceptance.

See [controlled profile experiments](https://github.com/tangericm/optical-design/blob/v1.1.0/docs/research/next-roadmap/README.md) and [release compatibility evidence](compatibility.md) for completed runs and unresolved method differences.
