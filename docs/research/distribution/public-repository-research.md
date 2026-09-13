# Public repository design research

**Project:** optical-design 1.1.0  
**Research snapshot:** 13 September 2026  
**Decision:** Present an installable optical workflow with visible evidence, then expose
technical depth through task links. Make the repository readable across experience levels
without positioning it as a course.

## Executive findings

The useful combination is a skill repository's short path to installation and an optical
software repository's concrete demonstration of results. The README should answer five
questions in order: what does this do, how do I install it, what can I run now, what will I
get, and where are the technical limits? This is a design recommendation drawn from the
comparison below, not a measured claim about conversion or adoption.

The recommended public surface has one original lens/focus identity, three functional
badges, one primary installer, two task entry points, a reproducible output figure, a small
task map, explicit model boundaries, and actionable support links. A separate installation
guide carries client differences. Reference documentation carries the detailed optical
contracts. The root README remains an entrance to the tool rather than a complete manual.

The comparison also rejects a tempting assumption: popular skill repositories do not all
have elaborate graphics. Several rely almost entirely on clear text and commands. Visual
polish should therefore improve recognition and communicate an actual result; it cannot
substitute for an understandable first action or credible evidence.

## Method and source selection

This study examines six skill or distribution repositories, two optical software projects,
and MecAgent's vendor feature page. The skill set includes high-visibility general-purpose
projects, the specifically requested Taste and Impeccable projects, and the user's own
Skillcrit distribution analogue. Optiland is especially relevant because optical-design
uses a pinned version of it. RayOptics provides a second domain-specific comparison.
MecAgent is included for product positioning, not as an open-source repository peer.

Sources are public project READMEs, repository metadata, vendor documentation, and official
platform documentation. The [companion source notes](readme-comparables-notes.md) preserve
the six skill README commit identifiers, dated star counts, individual observations, and
links to the inspected sections. They are part of this research record. Stars indicate
visibility at the snapshot date; they do not measure documentation quality, correctness,
active users, or the effect of a particular design choice.

This is a qualitative comparative audit. It did not conduct user interviews, accessibility
testing with assistive technology, installation funnel analytics, independent vendor
benchmarks, or an experiment assigning different READMEs to different users. Recommendations
are consequently hypotheses with concrete acceptance checks, not established causal laws.
Retrieved repository content was treated as source material, never execution instructions.

## Comparison matrix

| Comparison | Useful pattern | Adaptation for optical-design |
|---|---|---|
| [Superpowers](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/README.md) | Concrete workflow sequence and clear operating principles | Show inspect, requirements, change, validation, and review as a short sequence |
| [Vercel Skills](https://github.com/vercel-labs/skills/blob/d667282815248da03a08a18272b5d2eef9caf77c/README.md) | An executable installer command immediately after the description | Make the npm command the primary entry; move the client matrix into installation docs |
| [Anthropic Skills](https://github.com/anthropics/skills/blob/34040c9c568585f6929bedeaad110ad08f079624/README.md) | Explicit distinctions between examples, production use, and applicable terms | Label synthetic evidence and separate portable computation from licensed native execution |
| [Impeccable](https://github.com/pbakaus/impeccable/blob/cb56ed6c19a07329a9fa0cd4e657bee040156593/README.md) | Short first action, recognizable commands, and a proof link | Put a usable prompt near installation and link a reproducible result |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill/blob/ccbc15639c97057cbfcf32ecebc38ef716e4bb37/README.md) | Distinctive banner, output examples, and routing among tools | Use one restrained original identity and one evidence-bearing figure |
| [Skillcrit](https://github.com/tangericm/skillcrit/blob/129aa09f8730b9300a3012e577521c533379c510/README.md) | Compact identity, realistic command output, task map, and trust boundaries | Keep installation, observable output, technical navigation, and verification close together |
| [Optiland](https://github.com/optiland/optiland) | Real optical visualization, runnable model, diagnostics, and reference routes | Demonstrate the bundled model and expose settings and reproducibility |
| [RayOptics](https://github.com/mjhoptics/ray-optics) | Direct installation and documentation entry with precise domain language | Explain the supported optical job in ordinary words, retaining exact technical terms where needed |
| [MecAgent](https://mecagent.com/features) | Engineering tasks presented as visible outcomes | Describe calculations, saved-model changes, and review artifacts as the product's results |

The first six rows are summarized from the commit-pinned evidence in the companion notes.
The domain-specific observations below explain the additional sources without implying
that optical-design inherits their full functionality.

## What the optical and engineering comparisons add

### Optiland: a concrete optical result earns its space

Optiland's README begins with an optical-system visualization, follows its introduction
with a runnable singlet example and a diagnostic entry point, and links conventions,
task guides, and examples. Optional GUI and computing dependencies have their own install
variants. Its capability table explicitly marks some features as pre-release or beta.
This suggests showing a real output before asking a reader to absorb a long capability
inventory. It does not justify advertising every current upstream feature through a
restricted adapter pinned to an older release. [Source: Optiland README](https://github.com/optiland/optiland).

For this project, the evidence visual is the bundled singlet's before-and-after spot radius
and MTF. The image is generated from an accepted saved-model report, accompanied by exact
values and settings, and labeled as computed synthetic-model evidence. The logo remains
separate from that scientific claim. The demonstration is intentionally narrower than
“design any lens”: a new reader can understand what changed, and an expert can inspect
the conditions under which it passed.

### RayOptics: precise language can still be direct

RayOptics places installation and a documentation link early, then defines its purpose
in geometric, image-forming optics and describes its analysis environment. It also
distinguishes discussion from issue reporting. Its directness is useful here: technical
credibility need not require a long introduction. The adaptation is to say what users can
do with a saved lens, then provide the domain-specific limits and reference links.
[Source: RayOptics README](https://github.com/mjhoptics/ray-optics).

Avoid replacing essential terms with vague marketing language. Instead, connect each term
to an action or output: optimize a saved model, compare a specified MTF, inspect a tolerance
report. A linked glossary can resolve unfamiliar terminology without interrupting a reader
who already knows it. Both audiences follow the same workflow and use the same evidence.

### MecAgent: outcomes are useful; capability equivalence is not established

MecAgent's feature page organizes its offer around engineering activities, including macro
automation, drawings, and engineering questions, and separates research-stage features.
It illustrates product outcomes and states limits for particular features. These are
vendor representations, not independently verified performance measurements. The relevant
adaptation is outcome-based organization and visible scope; this research establishes no
equivalence between MecAgent and optical-design. [Source: MecAgent features](https://mecagent.com/features).

The public copy should therefore lead with the work this release actually performs:
calculate, inspect, change within declared bounds, validate, and produce a review. Claims
of live GUI control, autonomous new-lens synthesis, or manufacturing readiness would create
an expectation the released contract does not support. Product ambition belongs in a
clearly identified roadmap, not in the current capability description.

## Recommended README architecture

| Order | Section | Reader question | Content budget |
|---:|---|---|---|
| 1 | Identity and purpose | What is this, and is it relevant? | One header, one short description, three useful badges |
| 2 | Install | What do I type? | Primary command, explicit agent example, runtime requirement, native alternative link |
| 3 | Starting point | Can I try it or use my existing file? | Bundled model and existing-prescription routes |
| 4 | Invocation | What should I ask the agent? | One calculator request and one bounded model workflow |
| 5 | Example output | What does a successful run produce? | One real figure, model conditions, exact-data and reproduction links |
| 6 | Task map | Where is the operation I need? | About five rows leading to technical references |
| 7 | Boundaries | Does my model fit the supported scope? | Surface/analysis/variable limits and a full capability link |
| 8 | Distribution and support | How do I install elsewhere, update, or report a problem? | Short explanation with direct documentation and issue links |

These budgets are editorial recommendations, not rules inferred from star counts. The
current README uses them to avoid forcing either a new user or an experienced engineer
through a role-based track. “Try the bundled model” describes a task. “Use an existing
prescription” describes a different starting state. Neither labels the reader's ability.

The first run must be observable. Successful execution should print report locations,
save the candidate model, and say whether its requirements and reload checks passed.
Failures should preserve useful diagnostics. A polished README cannot compensate for a
silent or ambiguous CLI, so these expectations also inform the demo's progress messages
and output logs.

## Public profile and visual identity

Use the same name, concise description, logo family, and release version across GitHub,
npm, and native plugin metadata. A suitable About description is:

> Optical design tools for AI agents: calculations, sequential lens optimization,
> validation, and review. Works with Claude Code, Codex, and Cursor.

Link the homepage field to the README or documentation index until a maintained standalone
site exists. Add specific repository topics such as `optics`, `optical-design`,
`agent-skills`, `claude-code`, `codex`, `cursor`, `optiland`, and `zemax`. These are navigation
and discovery labels, not an assertion of ranking improvement. Keep Releases, Issues,
license, contribution guidance, and security reporting reachable from the root.

The lens/focus mark should remain recognizable at a small plugin-icon size. Teal and navy
provide a restrained identity; light and dark logo variants preserve contrast. A dense
rainbow ray bundle, decorative analytics, star-history chart, or sponsor wall would add
visual weight without explaining this release. An original vector mark also avoids
depending on borrowed product logos for the project's identity.

Use repository-relative links and image paths for owned documentation assets so GitHub can
resolve them for the viewed branch. Check the published npm rendering separately rather
than assuming identical behavior across hosts. GitHub documents relative path resolution;
npm documents its README rendering but does not establish that every GitHub presentation
detail is interchangeable. [GitHub README guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes),
[npm README guidance](https://docs.npmjs.com/about-package-readme-files/).

A social preview is a separate repository setting, not an automatic consequence of adding
a banner file. If configured, use the same identity with generous margins and very little
text; GitHub recommends 1280 by 640 pixels for best display. Record it as configured only
after upload and verification. [GitHub social preview guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview).

## Distribution language and trust

Explain npm and npx in one sentence: npm hosts the versioned package, and npx runs its
installer without requiring a permanent global CLI installation. Then distinguish the
installed skill from the optical runtime it invokes. This reduces the chance that a user
expects installing instructions to install a licensed optical application.
[npm npx reference](https://docs.npmjs.com/cli/v11/commands/npx/).

Native plugin metadata, a repository-hosted marketplace, npm publication, and acceptance
into a curated public catalog are separate milestones. The public repository should list
what was actually tested and published. Do not turn valid manifests into claims of store
acceptance or universal client compatibility. The platform documentation describes
different installation and distribution mechanisms; the repository's installation guide
should preserve those distinctions. [Claude Code plugin discovery](https://code.claude.com/docs/en/discover-plugins),
[Codex plugin construction](https://developers.openai.com/plugins/build/plugins),
[Cursor plugin reference](https://cursor.com/docs/reference/plugins).

Trust signals should be attached to evidence. A CI badge leads to checks; a release links
the shipped version; a compatibility table names the tested engine and environment; a
figure links the settings that produced it. MIT licensing and a citation file explain
reuse and attribution. None of those independently certifies an optical prescription.

## Applied changes and release acceptance

The working release incorporates the original lens/focus identity, primary npm installer,
task-based entry points, explicit demo artifacts, a generated refocus comparison, exact
example settings, a compact task map, direct bug/feature links, and separate installation,
CLI, glossary, and engineering workflow references. Product guidance explicitly excludes
course or lesson positioning. Repository-owned README images use relative paths.

Before calling the public deployment complete, verify these concrete outcomes:

1. README links and both images render on the published repository; npm's README is checked
   separately for host-specific differences.
2. The published command resolves to the intended version and installs into a clean agent
   project. The first-run demo creates its stated files and reports actual optical checks.
3. Example values and units agree with the retained report; the caption identifies the
   synthetic model and analysis conditions.
4. About text, topics, package metadata, native manifests, and release notes describe the
   same shipped scope. Catalog acceptance is claimed only with a real acceptance record.
5. Technical references remain reachable within one task-map choice, without a tutorial
   prerequisite or an experience-level selection.

After release, concrete bug reports and observed installation friction are better inputs
for the next documentation change than copying another popular repository's decoration.
No adoption lift is predicted by this audit. Its immediate outcome is a coherent,
reviewable public presentation with a demonstrable first workflow and explicit limits.
