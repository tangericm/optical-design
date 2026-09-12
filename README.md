# optical-design

Agent skill for optical design review, analysis and optimization. Gives a coding agent
(Claude Code, Codex, Cursor, Hermes, OpenCode, Copilot) senior-designer guidance plus
deterministic scripts for resolution, PSF/MTF, wavefront error, Zernike and Seidel
aberrations, Strehl, tolerancing and merit-function design. Works without any ray tracer;
uses optiland for prescriptions and Zemax OpticStudio through ZOS-API when present.

Status: pre-release. See `docs/tiers.md` for what each compute tier needs.

## Install

- Any Agent Skills client: `npx skills add tangericm/optical-design`
- Claude Code: `claude plugin marketplace add tangericm/optical-design` then `claude plugin install optical-design@optical-design`
- npm: `npm install optical-design` and point your client at `node_modules/optical-design/skills/optical-design`

Scripts need Python 3.11+ and `uv`; dependencies install on first run.

## License

MIT.
