# optical-design

An optical-design copilot skill with executable analysis, requirement-driven prescription
audits, bounded multivariable optimization, compensated tolerance evidence, an interactive
MCP interface, and native diffraction-profile benchmarks.
This pre-release includes a portable Optiland adapter and OpticStudio standalone adapters.

The job workflow copies a model, measures a baseline, searches explicit parameter bounds,
checks every hard requirement, and verifies the saved/reloaded candidate. It records engine
versions, settings, search history and file hashes. The source model stays unchanged.

| Capability | Shipped scope |
|---|---|
| Numerical optics | Resolution, Gaussian beams, Zernike/Seidel math, pupil PSF/MTF, interferometry |
| Prescription audit | Explicit fields, wavelengths, metric identities, units and hard requirements |
| Refocus | Final air gap only; bounded search; fixed prescription invariants; native save/reload verification |
| Optimization | Up to four explicit radius/thickness variables; bounded search, hard requirements and saved-candidate verification |
| Separate validation | Predeclared requirements at extra fields/wavelengths or finer sampling; saved winner checked after search; failure rejects candidate |
| Tolerance evidence | Seeded independent radius/thickness perturbations, optional bounded focus compensation, paired pass rates and Wilson intervals |
| Interactive MCP tools | Local stdio capabilities/start/status/cancel/results; owned jobs and confined input/output paths |
| Catalog shortlist | Local declared records, identity/provenance validation, unit-aware constraints and ranking |
| Native profile benchmark | Copied-model Huygens/POP central intensity cuts, explicit settings and hashes, native sampling diagnostics, optional same-method reference comparison |
| Guidance | Specifications, microscopy, OCT, interferometry, optimization, PSF/MTF and tolerancing references |

Start with [the executable workflow and specification](skills/optical-design/references/design-workflow.md).
Synthetic native/portable singlets and example specifications are included under
`skills/optical-design/assets/`.

For validation beyond the search settings, see [separate validation](skills/optical-design/references/validation.md).
For complete field/spectral requirements, run the [three-field, three-wavelength example](skills/optical-design/references/field-validation-example.md).
For interactive jobs, see [the MCP interface](skills/optical-design/references/interactive.md).
For bounded multivariable jobs, see [optimization](skills/optical-design/references/optimization.md).

For unchanged-model profile reproduction, use the [profile benchmark workflow](skills/optical-design/references/profile-benchmark.md).
The [real-design reference audit](docs/research/real-benchmark/reference-audit.md) documents
the saved OCT evidence, exact model hashes, spectrum, units and uncertainty. Its 75 saved
model/case records are reference inputs; their existence does not establish a successful
fresh native run or physical design acceptance. The completed run and later controlled
experiments are documented in [the dev.3 evidence](docs/research/next-roadmap/README.md).

## Install

Use this local checkout for the development release. Remote installation commands install
the currently published revision, which may differ:

- Agent Skills: `npx skills add tangericm/optical-design`
- Claude Code: `claude plugin marketplace add tangericm/optical-design`, then `claude plugin install optical-design@optical-design`
- npm: `npm install optical-design`; skill directory is `node_modules/optical-design/skills/optical-design`

Scripts need Python 3.11+ and uv. Tier 0 dependencies are declared in scripts.
Prescription commands use pinned optional engines; see [tiers](docs/tiers.md) and
[compatibility evidence](docs/compatibility.md).

## Current boundaries

The prescription audit/refocus/optimize/tolerance adapters support centered spherical/plane sequential
refractive systems with scalar analyses. The separate native profile backend analyzes mm,
single-configuration sequential models with complex surfaces and explicit native polarization
settings. POP currently supports a declared Gaussian-waist launch; this is not generalized
validation of arbitrary models, source fields or polarization assumptions.

Topology changes, glass selection during optimization, live GUI attachment, arbitrary portable Zemax imports,
non-sequential/stray-light analysis and manufacturing release are not shipped. The restricted
portable ZMX importer rejects unsupported directives instead of silently dropping them.
Tolerance pass rates depend on the declared perturbation model. Profile reference agreement
means same-method numerical reproduction; illumination cuts are not point-image PSFs,
integrated marginals or measured OCT performance.

See [CHANGELOG](CHANGELOG.md) for changes and [SECURITY](SECURITY.md) for execution behavior.

## License

MIT.
