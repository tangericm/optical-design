# Install optical-design

[Documentation](README.md) / Install

Choose one installation route per agent. The shared skill contains the same optical
scripts and references whether installed directly or through the Claude Code plugin.

## Claude Code, Codex, Cursor, and other agents

With Node.js 22+ and npm available, run this
in your project directory:

```sh
npx optical-design install
```

The installer asks you to select an agent. To target
an agent explicitly, use one of these commands:

```sh
npx optical-design install --agent claude-code
npx optical-design install --agent codex
npx optical-design install --agent cursor
```

Project scope is the default. Add `--global` to make the skill available across your
projects. Installation copies this npm package's bundled version, records its hashes,
and preserves any existing installation by refusing to overwrite it. See the
[command reference](install.md#command-reference) for supported options and recovery behavior.

Prefer the shared ecosystem installer? `npx skills add tangericm/optical-design` remains
available for a wider range of agents. It downloads the skill from GitHub and has its
own update/remove commands. Choose one installer per agent to avoid duplicate copies.

Start a new agent conversation after installing. Ask it to use `optical-design` and
locate the installed `SKILL.md` before running its bundled scripts.

## Claude Code marketplace

Inside Claude Code, run:

```text
/plugin marketplace add tangericm/optical-design
/plugin install optical-design@optical-design
```

Or run the equivalent commands in your terminal:

```sh
claude plugin marketplace add tangericm/optical-design
claude plugin install optical-design@optical-design
```

This adds this repository's own marketplace and installs its plugin. It does not
mean the plugin is listed in Anthropic's official catalog. See
[Claude Code's marketplace guide](https://code.claude.com/docs/en/discover-plugins).

## Codex marketplace

With a current Codex CLI, run:

```sh
codex plugin marketplace add tangericm/optical-design
codex plugin add optical-design@optical-design
```

Start a new Codex task after installing. The repository marketplace is separate from
OpenAI's public curated directory. For skill-only installation, use the npm command
with `--agent codex` instead.

## Cursor plugin or direct skill

The npm command with `--agent cursor` is the direct installation route. The repository
also includes Agent Plugins and Cursor plugin manifests plus a logo. Public Cursor
Marketplace availability requires a separate submission and review; no public listing
is claimed here. Teams using a repository marketplace can follow
[Cursor's marketplace guide](https://cursor.com/docs/plugins).

## Running the optical tools

Installation gives your agent the skill files. Computation also needs:

| What you want to run | What you need |
|---|---|
| Calculators and offline review rendering | Python 3.11+ and [uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Portable lens workflows | The above; uv loads the pinned Optiland dependency |
| Native OpticStudio workflows | Windows, an installed OpticStudio with a valid API license, and the pinned native dependencies |

You do not need OpticStudio for the [quickstart](quickstart.md). Exact engine versions
and execution contracts are in [capabilities and limits](capabilities.md).

## Command reference

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

### Scope and versions

Install/update/uninstall default to the current project. Use the same `--global`
choice for subsequent operations. `update` uses the version bundled in the command
you execute; it does not separately fetch a moving GitHub branch.

For reproducibility, use `npx optical-design@1.1.0 install --agent codex` and retain
the reported version. The install receipt is `.optical-design-install.json` inside
the installed skill directory. It records the package version and exact file hashes.

### Files and recovery

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

### Diagnostics and outcomes

CLI exit 0 means success; failures return a nonzero exit code. `doctor` returns nonzero
when required local tooling is unavailable. It does not validate an OpticStudio license
or run the complete optical test suite.

The demo needs uv, an existing output parent directory, and permission to create a new
output directory. uv may download Python 3.11 and Optiland 0.6.2. The demo reports
success only after refocus improvement, saved-candidate verification, and review creation.
Partial evidence stays in place on failure. See the [quickstart](quickstart.md) to
inspect the individual optical commands and their separate exit-code contract.

## Verify your installation

From the installed `optical-design` skill directory, run:

```sh
uv run scripts/resolve.py airy --wavelength-um 0.55 --fnum 4 --json
```

Expect `airy_radius_um` of approximately **2.684** and `airy_diameter_um` of
approximately **5.368**, with the method and units in the output. For the next step,
[refocus the bundled lens and render its review](quickstart.md#refocus-a-lens).

## Manual installation and fixed releases

If you prefer a fixed release, clone the tag:

```sh
git clone --branch v1.1.0 --depth 1 https://github.com/tangericm/optical-design.git
```

Copy the **whole** `skills/optical-design` directory into your client's skill directory.
The scripts need the supporting files alongside `SKILL.md`.

| Client | Project-local destination |
|---|---|
| Claude Code | `.claude/skills/optical-design/` |
| Codex | `.agents/skills/optical-design/` |
| Cursor | `.cursor/skills/optical-design/` |
| Hermes | `.hermes/skills/optical-design/` |
| OpenCode | `.opencode/skills/optical-design/` |

The [shared installer](https://github.com/vercel-labs/skills) manages client-specific
paths for you. Manual copies stay at the copied version until you replace them.

## Update or remove

For installations managed by the optical-design npm command, use the same agent and
scope as the original installation. For example:

```sh
npx optical-design --version
npx optical-design@latest update --agent codex
npx optical-design uninstall --agent codex
```

Add `--global` to update/uninstall a global installation. Updates preserve a backup
and refuse edited installations. A fixed version can be installed with
`npx optical-design@1.1.0 install --agent codex`.

For installations made with the shared `skills` installer, use its own commands:
`npx skills update optical-design` or `npx skills remove optical-design`.

For Claude Code plugin installations, use `/plugin` to manage the installed plugin.
Refresh this repository's catalog with `/plugin marketplace update optical-design`.
For Codex plugins, use `codex plugin marketplace upgrade optical-design` to refresh
the source, then `codex plugin add optical-design@optical-design` to install the current
snapshot. Remove with `codex plugin remove optical-design@optical-design`.

## Troubleshooting

| Symptom | Next action |
|---|---|
| Installation already exists or was edited | Preserve it and follow [managed installation recovery](install.md#files-and-recovery); do not delete your edits to silence the error. |
| The agent cannot find the skill | Check the selected agent and installation scope, then start a new conversation. |
| A script path is missing | Run from the installed skill directory, or use an absolute script path. Confirm the whole skill was copied. |
| `uv` is not found | Install uv, then reopen the terminal so the updated PATH is loaded. |
| An output folder already exists | Choose a new output folder. Design jobs need a new or empty folder; review rendering needs a new one. |
| An engine is unavailable | Use the portable quickstart or check the [native prerequisites](capabilities.md). |

For optional interactive jobs, configure the [local MCP server](../skills/optical-design/references/audited/interactive.md)
with your workspace and allowed input roots. Installing the skill does not configure
or start that server automatically.
