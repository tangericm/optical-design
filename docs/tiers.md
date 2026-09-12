# Compute tiers

| Tier | Needs | Scripts | Status |
|---|---|---|---|
| 0 | Python 3.11+, uv; declared numerical dependencies | resolve, zernike, wavefront, interfero, compare, catalog | shipped |
| 1 | Optiland 0.6.2 through `uv run --with optiland==0.6.2` | design audit/refocus/tolerance --backend optiland | bounded sequential subset |
| 2 | Windows, valid OpticStudio API license; ZOSPy 2.1.5, pythonnet 3.1.0 | zos check; design audit/refocus/tolerance --backend zos | owned standalone session |

Tier 0 calculator envelopes include inputs, results, units, method, warnings and provenance.
Design/tolerance reports use a separate schema with explicit requirement assessment,
inspection, raw metrics, artifacts and source-preservation evidence. See
[the full contract](../skills/optical-design/references/design-workflow.md).

Exit codes: 0 successful/completed, 1 comparison mismatch/unmet requirements/no acceptable
refocus improvement, 2 usage, 3 missing dependency/engine, 4 analysis failure.
A completed tolerance job may contain failed trials; inspect its yield and errors.

Dependency download happens through uv. The adapters do not send optical models to a remote
service. OpticStudio's own licensing behavior and third-party library behavior remain external.
