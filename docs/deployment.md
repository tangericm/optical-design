# Deployment explained

[Documentation](README.md) / Deployment

**A GitHub release, an npm package, and a marketplace listing are separate distribution
channels.** The optical tools can be shared across them, but publishing one does not
automatically publish the others.

## npm and npx

| Term | What it does | Example |
|---|---|---|
| npm registry | Hosts versioned packages | The published `skillcrit` package |
| `npm install` | Installs a package into a project, or globally with `-g` | `npm install --save-dev skillcrit` |
| `npx` | Runs a package's command, fetching it when necessary | `npx skillcrit --help` |
| `npm publish` | Publishes a package version to the registry | A maintainer release action |

`npx` is convenient for a tool you want to run without managing a global installation.
It is not another registry or a separate publication target. See the
[npm npx documentation](https://docs.npmjs.com/cli/v11/commands/npx/).

Our current command has three parts:

```text
npx skills add tangericm/optical-design
│   │          └─ GitHub repository containing the optical skill
│   └─ npm package whose installer command is being run
└─ run that command
```

The [skills installer](https://github.com/vercel-labs/skills) places the skill where
your selected agent can discover it. It does not publish optical-design to npm or
register it in a native plugin marketplace.

## Skill, plugin, and MCP server

| Component | What the user gets |
|---|---|
| Skill | `SKILL.md`, optical scripts, reference guides, and example models/specifications |
| Plugin | A client-recognized package that can bundle skills and other integrations |
| Marketplace | A catalog through which a client discovers and installs plugins |
| MCP server | An optional running process that exposes interactive job tools to a client |

Installing this skill makes its workflow available to the agent. Running calculations
still needs Python/uv, and native analysis still needs a licensed OpticStudio installation.
The [MCP server](../skills/optical-design/references/interactive.md) requires explicit
workspace/input-root configuration; it is not started automatically by skill installation.

## Current distribution status

Verified for the v1.0.0 release on September 13, 2026:

| Channel | Status | Installation path |
|---|---|---|
| GitHub release | Published | [v1.0.0](https://github.com/tangericm/optical-design/releases/tag/v1.0.0) |
| Cross-agent skill | Available from GitHub | `npx skills add tangericm/optical-design` |
| Claude Code repository marketplace | Manifests shipped | Add this repository's marketplace, then install its plugin |
| Cursor Agent Plugins format | Root `plugin.json` shipped | Direct skill installation is the documented quick path; a public listing is not established |
| Codex | Direct skill installation available | A Codex-specific plugin manifest and marketplace distribution still need work |
| npm `optical-design` | Not published | No `npx optical-design` executable yet |

The repository has `package.json` and tarball checks, but it has no `bin` command entry.
Simply publishing that package would place files in npm without creating a dedicated
cross-agent installer. A successful package test is not proof of registry publication.

## Recommended distribution path

Keep one shared optical skill and offer several ways to get it:

1. **Keep the current cross-agent installer.** It already provides a short command
   for Claude Code, Codex, Cursor, and other supported clients.
2. **Complete native plugin distribution.** Validate each target client's plugin
   packaging and install/update/remove flow, then document its marketplace route.
3. **Add a dedicated npm command if desired.** Implement and test a small installer
   with client/scope selection, version reporting, and setup diagnostics; publish a
   versioned npm package after testing it from a clean environment.
4. **Submit public marketplace listings separately.** Packaging compatibility and
   catalog approval are different milestones. Claim availability only after a listing
   is actually accepted and installable.

A command such as `npx optical-design install` would be a possible future interface,
not a command supported by v1.0.0.

Claude Code supports repository-hosted marketplaces; adding one registers its catalog
before you install a plugin. [Claude Code installation guide](https://code.claude.com/docs/en/discover-plugins).
Codex has marketplace sources and a plugin browser. [OpenAI plugin documentation](https://learn.chatgpt.com/docs/plugins).
Cursor accepts the Agent Plugins format, while its public marketplace uses a review
process. [Cursor plugin documentation](https://cursor.com/docs/plugins).

For working installation commands today, return to [Install](install.md).
