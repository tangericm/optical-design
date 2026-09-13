# Production distribution and public repository design

User authorization: implement a polished repository readable across optics experience levels,
native plugin installation, and publish to npm. Retain the released optical scope.

## Product contract

- Release 1.1.0 adds distribution and onboarding without changing optical algorithms.
- One bundled skill is the source of truth for npm, Claude Code, Codex, and Cursor.
- Node >=22; dependency-free JavaScript installer, no install lifecycle scripts.
- `optical-design install --agent <claude-code|codex|cursor|opencode|hermes>` installs
  to the current project. `--global` explicitly chooses user scope. Interactive install
  asks for an agent; noninteractive execution requires an explicit agent.
- Install copies the shipped version, never a moving remote branch. It records file
  hashes and version. Existing unmanaged or edited installations must not be overwritten.
- `update` replaces only intact managed installs, retains a recoverable backup, and
  reports the bundled version; users fetch a newer installer with `npx optical-design@latest`.
- `uninstall` removes only intact managed installs. Refuse symlinks and unsafe paths.
- `doctor` reports Node/uv readiness and reminds users that native OpticStudio requires
  Windows and an API license. No account secrets, model uploads, or silent dependency setup.
- `demo --out <new-directory>` runs the bundled calculator, portable refocus, and review
  using uv. Report success only after saved candidate verification and optical acceptance.
- `--help`, `--version`, and structured `--json` output support repeatable use.
- Claude and Codex repository marketplaces must be validated with real client CLIs in
  temporary client configurations. Cursor manifest validation is distinguished from UI
  installation. Public catalog submission/acceptance is a separate recorded milestone.

## Public experience

Original lens/focus geometric logo, SVG source and PNG exports; readable in light and
dark modes and at icon sizes. Teal accent, high-contrast neutral lettering. No fake
ray-trace or measured-performance imagery. Logo is an identity mark, not optical evidence.
README leads with install, then routes by task: try the bundled model or use an existing
prescription. This is a working toolkit, not a course. Include a reference glossary,
runnable example, engineering task links, troubleshooting, support/issue templates,
license, security, compatibility and a clear distribution status.

## Release acceptance

Unit tests cover installer ownership, traversal/symlink rejection, conflict preservation,
update/uninstall, CLI parsing and meaningful diagnostic failures. Clean packed-package
tests execute the bin and install into all supported client paths, then run the demo.
All platform CI jobs must pass. Validate manifests and cross-version metadata. Publish
only from the verified release commit; verify npm registry version/integrity and a fresh
public npx installation afterward. Record external login/review blockers honestly.
