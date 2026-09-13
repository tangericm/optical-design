# Command reference

[Documentation](README.md) / CLI

Run with `npx optical-design`, or use `optical-design` after an explicit global npm
installation. Node.js 22+ is required. Add `--json` for structured output.

| Command | Purpose |
|---|---|
| `npx optical-design install --agent codex` | Copy this package's skill into the current project |
| `npx optical-design install --agent cursor --global` | Install into your user-level Cursor skills directory |
| `npx optical-design doctor` | Check Node and uv readiness; describe native prerequisites |
| `npx optical-design demo --out my-first-lens` | Run the portable example and generate a review in a new directory |
| `npx optical-design@latest update --agent codex` | Replace an intact managed install with the fetched package version; keep a backup |
| `npx optical-design uninstall --agent codex` | Remove an intact installation managed by this installer |
| `npx optical-design --version` | Print the package version being executed |
| `npx optical-design --help` | Show supported commands and options |

Supported agent names: `claude-code`, `codex`, `cursor`, `opencode`, `hermes`.
Use one agent per invocation. Run `install` without `--agent` in an interactive
terminal to choose one. Noninteractive runs require `--agent`.

## Scope and versions

Install/update/uninstall default to the current project. Use the same `--global`
choice for subsequent operations. `update` uses the version bundled in the command
you execute; it does not separately fetch a moving GitHub branch.

For reproducibility, use `npx optical-design@1.1.0 install --agent codex` and retain
the reported version. The install receipt is `.optical-design-install.json` inside
the installed skill directory. It records the package version and exact file hashes.

## Files and recovery

The installer refuses an existing unmanaged skill, symlinked paths, or a managed
installation whose files or directory structure changed. There is no force-overwrite
flag. Keep design outputs outside the installed skill directory.

Normal Python execution can create `__pycache__` files. The demo prevents those writes;
other script invocations may create them. Extra files trigger the same conservative
update/uninstall refusal as edits. Inspect and back up changes first. To recover from
a modified install without deleting anything, move the whole skill folder outside
the client's skills directory, then install a fresh copy and reconcile changes manually.

An update reports a sibling `.optical-design.backup-*` folder holding the previous
installation. Keep it until you have verified the replacement. An interrupted uninstall
may leave a `.optical-design.remove-*` recovery folder; errors identify it.

If `.optical-design.lock` remains after interruption, confirm no installer process is
running before removing the empty lock directory. Never remove an active operation's lock.

## Diagnostics and outcomes

CLI exit 0 means success; failures return a nonzero exit code. `doctor` returns nonzero
when required local tooling is unavailable. It does not validate an OpticStudio license
or run the complete optical test suite.

The demo needs uv, an existing output parent directory, and permission to create a new
output directory. uv may download Python 3.11 and Optiland 0.6.2. The demo reports
success only after refocus improvement, saved-candidate verification, and review creation.
Partial evidence stays in place on failure. See the [manual quickstart](quickstart.md)
to inspect the individual optical commands and their separate exit-code contract.
