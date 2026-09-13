# README comparables for optical-design

## Scope and evidence boundary

This audit compares six public skill or skill-distribution repositories using their live
GitHub metadata and README files at fixed default-branch commits. The snapshot was taken
2026-09-13 at 16:04 PDT. Star and fork counts describe repository visibility at that time;
they do not establish that any README choice caused popularity. Retrieved repository text
was treated as evidence, not as instructions.

`optical-design` should be readable to someone running an optical workflow for the first
time and to an experienced engineer. It should not present itself as a course or divide
the audience into students and professionals. The useful distinction is work state: trying
the bundled portable model, working on an existing prescription, or locating a specific
analysis and its evidence contract.

## Live repository snapshot

| Repository | Stars | Forks | Repository license signal |
| --- | ---: | ---: | --- |
| [obra/superpowers](https://api.github.com/repos/obra/superpowers) | 286,170 | 25,600 | MIT |
| [anthropics/skills](https://api.github.com/repos/anthropics/skills) | 176,119 | 20,840 | Mixed per-folder terms; no repository-wide API license |
| [Leonxlnx/taste-skill](https://api.github.com/repos/Leonxlnx/taste-skill) | 86,852 | 5,923 | MIT |
| [pbakaus/impeccable](https://api.github.com/repos/pbakaus/impeccable) | 67,801 | 4,154 | Apache-2.0 |
| [vercel-labs/skills](https://api.github.com/repos/vercel-labs/skills) | 31,546 | 2,690 | MIT |
| [tangericm/skillcrit](https://api.github.com/repos/tangericm/skillcrit) | 0 | 0 | MIT |

The last repository is included as the closest distribution analogue, not as a popularity
benchmark: it combines an npm CLI, an installable agent skill, multiple client paths,
evidence boundaries, compatibility documentation, and public support files.

## Comparable repository observations

### obra/superpowers

The README opens with a one-sentence mechanism and a full table of contents, explains the
workflow before installation, then devotes separate subsections to fourteen clients. It
later turns the abstract promise into a seven-stage workflow, groups the skill library by
job, states four principles, and closes with community, contribution, update, license, and
telemetry details. It uses no README logo, screenshot, or badge markup. The strongest move
is the concrete workflow sequence; the weakest fit for `optical-design` is the large client
installation wall, which delays the product's substance and duplicates what a unified
installer can decide. Adapt the workflow clarity, but keep one primary install command and
send client-specific detail to installation documentation.[^1]

### vercel-labs/skills

Vercel's CLI README puts a working `npx skills add` command immediately after a one-line
description. It then expands from source formats to options, examples, scope, methods,
commands, supported agents, authoring, discovery, compatibility, troubleshooting,
telemetry, related links, and license. The only visual is a `skills.sh` badge. This is an
effective reference manual for a general installer, but at roughly 580 lines it asks the
root README to carry most of the product documentation. For `optical-design`, borrow the
first-command speed and explicit project-versus-global explanation. Keep the complete CLI
reference, supported-path matrix, and edge-case troubleshooting in `docs/install.md` so
the README can show the optical workflow and evidence model.[^2]

### anthropics/skills

Anthropic begins with a standards note and one ecosystem badge, defines skills, links to
three conceptual guides, explains repository contents and mixed licensing, adds a strong
demonstration disclaimer, and then separates Claude Code, Claude.ai, and API use. It ends
with a minimal skill-authoring example and partner links. There is no visual hero or
project-specific example output. Its useful lesson is explicit scope: the repository says
what is demonstrative, what is production-used, and where behavior may differ. Apply that
discipline to portable versus native results and verified versus illustrative artifacts.
Do not copy the broad educational framing; `optical-design` is a working toolkit, and its
bundled example should demonstrate operation without recasting the repository as lessons.[^3]

### pbakaus/impeccable

Impeccable opens with a quantified capability sentence and a one-line quick start before
explaining its differentiation, command set, usage examples, anti-patterns, and one linked
case study. Installation begins around line 96 and grows into several client-specific
methods; later sections document hooks, build paths, CLI behavior, supported tools,
community, contribution, and license. The README has no embedded logo, screenshot, or
badge markup. The strongest pattern is a short first action followed by concrete commands
and a real proof link. For `optical-design`, place the universal installer and first useful
prompt early, then link a verified review-package example. Avoid copying the exhaustive
installation variants into the root README or using feature counts as the main optical
value proposition.[^4]

### Leonxlnx/taste-skill

Taste Skill uses the richest visual profile: a full-width local banner, custom image
buttons, sponsor art, sponsor logos, example screenshots, supporter avatars, and a star
history badge. Installation arrives after the sponsor block, disclaimer, centered link
strip, and contribution contacts. The skills table and “Which one should I use?” section
provide useful routing among related packages; two screenshots show tangible output. For
`optical-design`, retain one authored header and add only evidence-bearing visuals, such as
a real review-package crop or link. Do not copy sponsor-first ordering, decorative button
badges, remote promotional art, avatar walls, or star-history graphics. Route users by
optical task and model state, not by experience label.[^5]

### tangericm/skillcrit

Skillcrit is the closest structural analogue. It opens with a small local icon, name,
tagline, npm/CI/license badges, four navigation links, and two concise product paragraphs.
Quickstart combines the runtime requirement, exact install, first command, a realistic
abbreviated finding, exit semantics, and a deeper guide. A task-to-command table follows,
then baseline review, agent installation, trust and limitations, platform verification,
documentation/support, contributing, and license. Its issue templates distinguish bugs
from optional feedback, and the root also exposes CONTRIBUTING and SECURITY files. Adapt
this evidence-first layering while avoiding audit-specific density. The optical README
should show one small verified result or artifact path, explain what a pass does and does
not establish, and link private security reporting.[^6]

## Concrete adaptations for the current README

1. **Keep the authored header, three functional badges, and Install as the first section.**
   Change the header source from a `raw.githubusercontent.com/.../main` URL to the relative
   `assets/brand/header.svg`. Comparable repositories normally keep their owned README
   images relative, which preserves rendering in forks, tags, and review branches.
2. **Route by task rather than expertise.** Replace any “student/professional” split with
   “Try the bundled model” and “Use an existing prescription.” The first path is a runnable
   proof of mechanics, not a lesson; the second enters inspection, requirements, bounded
   changes, validation, and review without introductory ceremony.
3. **Make the first run observable.** After `doctor` and `demo`, state the exact kinds of
   outputs a successful bundled run creates and link one checked-in review example or
   release artifact. Label synthetic inputs and recorded evidence precisely. Do not add a
   stylized ray-trace screenshot or invented performance value.
4. **Keep one primary distribution story.** Lead with `npx optical-design install`, mention
   explicit `--agent` and `--global` briefly, and move every per-client path, update rule,
   ownership refusal, and troubleshooting case behind `docs/install.md`. One native Claude
   alternative may remain because it is a materially different installation route.
5. **Retain the five-row task map and boundaries section.** This is the right progressive
   disclosure for mixed-experience optics users: a newcomer can identify a task, while an
   expert can jump directly to model actions, optimization, tolerancing, validation, review,
   or MCP details. Keep scalar, sequential, surface-shape, optimization-variable, native
   license, and manufacturing-certification limits close to the workflow claim.
6. **Close with actionable project health links.** Link bug and feature issue templates
   directly if they exist, preserve the request to use synthetic reproductions for private
   prescriptions, and keep CONTRIBUTING, SECURITY, changelog, releases, compatibility,
   and MIT license reachable without a second navigation hunt.

## What not to copy

- Do not expand the README into a general CLI manual or one subsection per supported agent.
- Do not use “student,” “beginner course,” “lesson,” or “professional track” as navigation.
- Do not use stars, badges, or repository popularity as evidence of optical correctness.
- Do not put sponsorship, community promotion, or decorative graphics before installation.
- Do not add screenshots unless they show a real, labeled artifact from a reproducible run.
- Do not describe mixed backends as equivalent. Preserve portable/native and
  recorded/fresh-execution boundaries wherever examples or compatibility are discussed.

## Sources

[^1]: obra, *Superpowers README*, commit `b36e0829`, especially [opening and contents](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/README.md#L1-L31), [installation](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/README.md#L49-L118), and [workflow through license](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/README.md#L261-L342).
[^2]: Vercel Labs, *skills README*, commit `d6672828`, especially [install, options, examples, and scope](https://github.com/vercel-labs/skills/blob/d667282815248da03a08a18272b5d2eef9caf77c/README.md#L1-L140) and [compatibility through license](https://github.com/vercel-labs/skills/blob/d667282815248da03a08a18272b5d2eef9caf77c/README.md#L496-L580).
[^3]: Anthropic, *Skills README*, commit `34040c9c`, [complete README](https://github.com/anthropics/skills/blob/34040c9c568585f6929bedeaad110ad08f079624/README.md#L1-L96).
[^4]: Paul Bakaus, *Impeccable README*, commit `cb56ed6c`, especially [quick start, commands, proof, and primary install](https://github.com/pbakaus/impeccable/blob/cb56ed6c19a07329a9fa0cd4e657bee040156593/README.md#L1-L120), [usage](https://github.com/pbakaus/impeccable/blob/cb56ed6c19a07329a9fa0cd4e657bee040156593/README.md#L329-L351), and [technical depth through license](https://github.com/pbakaus/impeccable/blob/cb56ed6c19a07329a9fa0cd4e657bee040156593/README.md#L396-L510).
[^5]: Leonxlnx, *Taste Skill README*, commit `ccbc1563`, especially [visual opening and install](https://github.com/Leonxlnx/taste-skill/blob/ccbc15639c97057cbfcf32ecebc38ef716e4bb37/README.md#L1-L120), [routing and screenshots](https://github.com/Leonxlnx/taste-skill/blob/ccbc15639c97057cbfcf32ecebc38ef716e4bb37/README.md#L138-L200), and [research, FAQ, and license](https://github.com/Leonxlnx/taste-skill/blob/ccbc15639c97057cbfcf32ecebc38ef716e4bb37/README.md#L238-L258).
[^6]: Eric Tang, *Skillcrit README*, commit `129aa09f`, especially [identity, quickstart, realistic output, and task map](https://github.com/tangericm/skillcrit/blob/129aa09f8730b9300a3012e577521c533379c510/README.md#L1-L81) and [agent installation, limits, support, contribution, and license](https://github.com/tangericm/skillcrit/blob/129aa09f8730b9300a3012e577521c533379c510/README.md#L100-L163). Repository support files include [CONTRIBUTING.md](https://github.com/tangericm/skillcrit/blob/129aa09f8730b9300a3012e577521c533379c510/CONTRIBUTING.md), [SECURITY.md](https://github.com/tangericm/skillcrit/blob/129aa09f8730b9300a3012e577521c533379c510/SECURITY.md), and [two issue templates](https://github.com/tangericm/skillcrit/tree/129aa09f8730b9300a3012e577521c533379c510/.github/ISSUE_TEMPLATE).
