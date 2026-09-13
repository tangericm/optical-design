# Deployment explained

[Documentation](README.md) / Deployment

**npm distributes the package; npx runs its command; a marketplace installs a plugin
inside an agent.** These routes share the same optical skill.

## Choose an installation route

| Route | What it does | Who it is for |
|---|---|---|
| `npx optical-design install` | Copies the skill bundled with the npm package into a selected agent | Most users; one command across five supported agents |
| Claude Code marketplace | Installs the repository's plugin through Claude's plugin manager | Users who prefer native plugin management |
| Codex marketplace | Installs the repository's plugin through Codex | Users who prefer native plugin management |
| `npx skills add tangericm/optical-design` | Uses the shared skills installer to download from GitHub | Other supported agents and existing skills-installer users |
| Tagged repository checkout | Provides a fixed source revision and manual commands | Reproducible workflows and contributors |

See [Install](install.md) for exact commands. Choose one route per agent to avoid
duplicate copies; update and remove using the same tool that installed it.

## npm versus npx

`npm install` installs a package into a project, or globally with `-g`.
`npx` executes a package's command and downloads it when necessary. They use the
same registry; there is no separate “npx publication.” See the
[npm documentation](https://docs.npmjs.com/cli/v11/commands/npx/).

```text
npx optical-design install --agent codex
    └─ npm package       └─ install its bundled skill into Codex
```

With `npx optical-design@1.1.0`, the installer and installed skill come from that
specific release. `npx optical-design@latest update --agent codex` uses the current
npm release. The command does not independently fetch a newer skill from GitHub.

By contrast, `npx skills add tangericm/optical-design` runs the separate `skills`
npm package and installs the skill from the GitHub repository. Its version and update
behavior are controlled by that installer. [Skills installer](https://github.com/vercel-labs/skills).

## What is installed

| Component | Purpose |
|---|---|
| Skill | Instructions, scripts, references, and example models that an AI agent can use |
| npm command | Installation management, prerequisite checks, and a portable demonstration |
| Plugin manifest | Client-specific identity, skill discovery, and presentation metadata |
| Marketplace catalog | An installable source a client can add and browse |
| Optional MCP server | A local process exposing interactive optical job tools |

Installing the skill does not install or license OpticStudio. Calculations need Python
and uv; the portable demo loads the pinned Optiland dependency. Native analysis needs
a compatible Windows OpticStudio installation and API license.

MCP setup is optional and explicit. Define a workspace and allowed input roots before
starting the [MCP server](../skills/optical-design/references/interactive.md). A plugin
installation does not silently configure or launch it.

## Repository marketplaces and public catalogs

Claude Code and Codex support repository marketplaces. Adding this repository makes
its plugin installable through that source. It does not mean the plugin has been
accepted into Anthropic's or OpenAI's public curated catalog.
[Claude marketplace guide](https://code.claude.com/docs/en/discover-plugins) ·
[OpenAI plugin guide](https://developers.openai.com/plugins/build/plugins).

The repository includes both Agent Plugins and Cursor plugin manifests. The npm skill
installer is the direct Cursor route. A public Cursor Marketplace listing requires
separate submission and review; no accepted public listing is claimed here.
[Cursor plugin guide](https://cursor.com/docs/reference/plugins).

For Windows Git-based plugin installation errors involving long paths, use a shorter
client configuration path or the npm skill installer. The npm package excludes the
repository's historical research trees.

## Release history and verification

v1.0.0 was released on GitHub with a shared-skill installation route. It did not publish
an `optical-design` npm command. Version 1.1.0 introduces that executable and native
plugin metadata, alongside the public documentation and visual identity.

Package verification installs the actual tarball into a clean consumer, executes the
npm command, checks install/update/uninstall for every supported agent, and can run
the portable demo. Cross-platform CI checks Windows, macOS, and Linux.
[Compatibility evidence](compatibility.md) records the verified results and limits.

The live [npm package page](https://www.npmjs.com/package/optical-design) and
[GitHub releases](https://github.com/tangericm/optical-design/releases) are the publication
record. A successful local tarball test alone is not proof of registry publication.
