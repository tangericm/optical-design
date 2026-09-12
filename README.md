# optical-design

Agent skill for optical design analysis. Gives a coding agent (Claude Code, Codex, Cursor,
Hermes, OpenCode, Copilot) senior-designer guidance plus deterministic scripts for
resolution limits, PSF/MTF, wavefront error, Zernike and Seidel aberrations, Strehl, depth
of focus, Gaussian beams and interferometry — numbers come from code, and every formula
names its source.

Status: pre-release. **This release ships Tier 0 only**: closed-form calculators and
wavefront analysis that need nothing but numpy (plus scikit-image for phase unwrapping).
No ray tracer and no optical design suite is involved.

## Planned, not in this release

- **Tier 1 — prescriptions.** Sequential ray tracing of `.zmx`/`.seq`/`.len` files and typed
  surfaces through [optiland](https://pypi.org/project/optiland/): paraxial and Seidel
  summaries, spot diagrams and ray fans, wavefront and Zernike, PSF/MTF, surface edits,
  optimization and export.
- **Tier 2 — Ansys Zemax OpticStudio.** Driving a standalone or live OpticStudio session
  over ZOS-API (through ZOSPy) for the same analyses plus merit-function building and
  optimization. Needs Windows and a Professional/Premium licence.
- **Tolerancing** (sensitivity and Monte Carlo, compensators, budgets) and
  **merit-function design** help: both need Tier 1 or Tier 2 to say anything useful.
- The design-guidance layer — audit a lens, rank its limitations with evidence, suggest and
  apply corrections, find comparable published or stock designs — and the reference library
  behind it.

See `docs/tiers.md` for what each tier needs and returns, and `CHANGELOG.md` for what has
landed so far.

## Install

- Any Agent Skills client: `npx skills add tangericm/optical-design`
- Claude Code: `claude plugin marketplace add tangericm/optical-design` then `claude plugin install optical-design@optical-design`
- npm: `npm install optical-design` and point your client at `node_modules/optical-design/skills/optical-design`

Scripts need Python 3.11+ and `uv`; dependencies install on first run.

## License

MIT.
