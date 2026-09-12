# Install

Prerequisite for the scripts: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

| Client | Command or path |
|---|---|
| Any Agent Skills client | `npx skills add tangericm/optical-design` |
| Claude Code | `claude plugin marketplace add tangericm/optical-design` then `claude plugin install optical-design@optical-design` |
| Codex | copy `skills/optical-design` into `.agents/skills/` (project) or `~/.agents/skills/` |
| Cursor | copy into `.cursor/skills/` or install as a local plugin from `plugin.json` |
| Hermes | copy into `.hermes/skills/` or `~/.hermes/skills/` |
| OpenCode | copy into `.opencode/skills/` |
| npm | `npm install optical-design`; skill lives at `node_modules/optical-design/skills/optical-design` |

Verify: `uv run <skill-dir>/scripts/resolve.py airy --wavelength-um 0.55 --fnum 4`
