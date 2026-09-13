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

The release installs through GitHub with `npx skills add`; no `optical-design` npm registry
package or `npx optical-design` executable is published. Local npm tarballs are packaging
verification artifacts. Use the release tag in a Git checkout for a fixed revision.

Verify: `uv run <skill-dir>/scripts/resolve.py airy --wavelength-um 0.55 --fnum 4`

Optional interactive transport: follow [the local MCP setup](../skills/optical-design/references/interactive.md).
Declare a workspace and the input roots before starting the server.
