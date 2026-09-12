# optical-design

An optical-design copilot skill with executable analysis, requirement-driven prescription
audits, bounded refocus, and tolerance evidence. This pre-release includes a portable
Optiland adapter and an OpticStudio standalone adapter.

The job workflow copies a model, measures a baseline, searches an explicit final-gap range,
checks every hard requirement, and verifies the saved/reloaded candidate. It records engine
versions, settings, search history and file hashes. The source model stays unchanged.

| Capability | Shipped scope |
|---|---|
| Numerical optics | Resolution, Gaussian beams, Zernike/Seidel math, pupil PSF/MTF, interferometry |
| Prescription audit | Explicit fields, wavelengths, metric identities, units and hard requirements |
| Refocus | Final air gap only; bounded search; fixed prescription invariants; native save/reload verification |
| Tolerance evidence | Seeded independent radius/thickness perturbations, sensitivity, failed trials, Wilson interval; no compensators |
| Catalog shortlist | Local declared records, identity/provenance validation, unit-aware constraints and ranking |
| Guidance | Specifications, microscopy, OCT, interferometry, optimization, PSF/MTF and tolerancing references |

Start with [the executable workflow and specification](skills/optical-design/references/design-workflow.md).
Synthetic native/portable singlets and example specifications are included under
`skills/optical-design/assets/`.

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

The adapters support centered spherical/plane sequential refractive systems. General
multi-variable redesign, live GUI attachment, aspheres, arbitrary Zemax imports,
polarization, non-sequential/stray-light analysis and manufacturing release are not shipped.
The restricted portable ZMX importer rejects unsupported directives instead of silently
dropping them. Tolerance pass rates depend on the declared perturbation model.

See [CHANGELOG](CHANGELOG.md) for changes and [SECURITY](SECURITY.md) for execution behavior.

## License

MIT.
