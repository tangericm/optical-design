# Adoption review: making optical-design the lens-design skill people reach for

Date: 2026-09-14. Reviewed at commit `7887a30` (v1.1.0).

## Summary

The project has an unusually strong engineering spine and an unusually narrow optical
window. Provenance, verification, cross-platform CI, packaging and distribution are
better than almost any community skill. But the thing a lens designer actually wants to
do with a `.zmx` file, look at it, understand its aberrations, change glass or shape,
optimize it with a real merit function, and see spot diagrams and MTF curves, is mostly
outside the shipped scope. The bundled OpticStudio export cannot even be opened by the
portable backend. The prose that wraps the tools is written as a liability policy rather
than as a colleague explaining optics.

To become widely adopted the skill needs three shifts, in this order:

1. **Open the window.** Expose the analyses and optimizer that Optiland already provides
   (layouts, spot diagrams, ray and OPD fans, field curvature, distortion, Seidel sums,
   through-focus MTF, damped least squares, glass and asphere variables, real ZMX import).
2. **Change the voice.** Cut SKILL.md and the references to roughly a third of their
   current length, replace repeated disclaimers with one clear "evidence limits" section,
   and add the concise principles and formulae the project goal calls for.
3. **Make the output legible.** A review should open with a layout, a spot diagram, an MTF
   curve and a two-sentence plain-language verdict, with the receipt details below.

The rest of this document gives the evidence for each finding and a prioritized plan.

## What is already strong and should be kept

- **Bounded, verified mutation.** Every job works on a copy, records hashes, reloads the
  saved candidate and re-measures it. This is rare and valuable; it is what will let
  professionals trust an agent touching their prescriptions.
- **Explicit requirements as hard gates**, separate from the merit function. Correct and
  well-explained in the merit reference.
- **Tier 0 calculators.** Fast (0.3 s), JSON envelopes carry inputs, results, units,
  method text and provenance. This is the right output contract for an agent tool.
- **CI matrix and tests.** 404 Python tests and 17 Node tests across Linux, macOS and
  Windows with Python 3.11 and 3.13, plus a portable-engine job and a package
  verification step.
- **Distribution.** One npm command for five agents, a Claude plugin marketplace, Codex
  and Cursor metadata, and the `npx skills add` route. Nothing to change here.
- **Two-engine design.** Optional licensed OpticStudio through ZOSPy with a portable
  Optiland fallback is exactly the split practitioners need.

## Findings

### 1. The capability window is far smaller than the engine underneath

Measured against Optiland 0.6.2, which the skill already pins:

| Area | Optiland provides | Skill exposes |
|---|---|---|
| Analyses | SpotDiagram, RayFan, PupilAberration (OPD), FieldCurvature, Distortion, GridDistortion, EncircledEnergy, ThroughFocusMTF, MTFvsField, RmsSpotSizeVsField, RmsWavefrontErrorVsField, YYbar, IncoherentIrradiance | six scalar metrics: EFL, F-number, total track, image distance, RMS spot radius, FFT MTF at one frequency |
| Aberration theory | Seidel sums and third-order coefficients (spherical, coma, astigmatism, Petzval, distortion, axial and lateral color) | none |
| First-order | EFL, BFL, pupils, cardinal points, magnification, Lagrange invariant, marginal and chief ray trace | EFL, F-number |
| Optimization | LeastSquares (damped least squares), OrthogonalDescent, DifferentialEvolution, CMA-ES, SHGO, particle swarm, dual annealing, basin hopping, torch Adam and SGD; ray, paraxial and aberration operands | custom coordinate and pattern search, 7 to 201 evaluations |
| Variables | radius, thickness, conic, even and odd asphere coefficients, polynomial and Chebyshev coefficients, refractive index with GlassExpert catalog substitution | radius and thickness only, at most four |
| Surfaces | Standard, EvenAsphere, OddAsphere, Forbes Q, Zernike, Chebyshev, toroidal, biconic, grid sag, gratings | spherical and plane; conics and aspheres only on the licensed native backend, and then fixed |
| Materials | catalog glasses through refractiveindex.info data, Abbe-number models | exact catalog lookup, no substitution |
| Tolerancing | Tolerancing and SensitivityAnalysis with distribution and range samplers | own radius and thickness Monte Carlo with one focus compensator |
| Starting points | sample library: Cooke triplet, double Gauss, Petzval, Tessar, Heliar, telephoto, wide angle, Microscope20x, Objective60x, eyepieces, telescopes | one synthetic singlet |
| Plots | `Optic.draw()` layout, every analysis has a `.view()` | vertex-only schematic in the review |

A seasoned engineer opening the skill will notice within minutes that it cannot draw a
layout, cannot show a ray fan, and cannot vary a glass. A beginner will not learn
anything about aberrations from it, because it never names one.

### 2. The ZMX door is locked

The portable importer keeps a hand-written allowlist of 20 directives and raises on the
first unknown one. Running the bundled native example through it:

```
$ uv run --with optiland==0.6.2 scripts/design.py inspect --backend optiland \
    --model assets/defocused-singlet.zmx --out inspect-zmx --json
ValueError: unsupported Zemax directive: AUTH
```

Optiland's own `load_zemax_file` reads the same file without complaint and reports the
correct four-surface N-BK7 singlet. Every real OpticStudio export carries `AUTH`, `ENVD`,
`RAIM`, `POLS`, `GSTD`, `NSCD` and dozens of other header lines, so the documented caveat
"a normal full OpticStudio export can be rejected" is in practice "every normal export is
rejected". For a project whose stated goal is optimizing `.zmx` files, this is the first
thing to fix. Reject only what changes the optical model and cannot be traced, and record
ignored cosmetic directives as warnings. Optiland's reader already handles coordinate
breaks, toroids and Zemax paraxial surfaces and can write `.zmx` back out (since 0.6.0),
so the portable backend could round-trip a real file today.

### 3. The voice reads as a liability policy

Counts across SKILL.md and the 17 reference files:

| Measure | Value |
|---|---|
| SKILL.md | 160 lines, about 3,000 tokens, 1,484 words |
| References | about 21,700 tokens |
| Sentences | 859 |
| `not`, `never`, `cannot`, `reject` | 221 |
| "does not establish / prove / imply / certify" | 9 |
| "not a manufacturing / clinical" | 3 |

Every reference ends with "Primary links checked 2026-09-12. ... is project policy."
The review package opens with "This review runs no optical analyses. ... Artifact hashes
verify local bytes, not optical performance." before it shows any result.

Some of this caution is right and should stay, once, in a clearly labelled place. Repeated
on every page it has three costs: it consumes context the agent needs for the user's
problem, it trains the agent to hedge instead of answering, and it tells a newcomer the
tool does not trust itself. Anthropic's skill-authoring guidance is explicit that a skill
should explain why a rule exists rather than pile up prohibitions, and that SKILL.md
should stay well under its budget so the agent can load references when needed.

The vocabulary is also internal. "Receipt", "owned job", "expected-value edit",
"fixed-state verification", "holdout", "copied-model Huygens/POP central intensity cuts"
appear in user-facing docs without definition. Optical engineers have their own words:
prescription, layout, merit function, operand, variable, pickup, solve, tolerance,
compensator, yield.

### 4. Onboarding is spread across five overlapping entry points

README, `docs/first-lens.md`, `docs/quickstart.md`, `docs/professional-workflow.md` and
`docs/README.md` all describe the same singlet refocus from slightly different angles. A
first-time visitor should meet one path: install, run the demo, see one picture, then one
"bring your own lens" page. The rest can be reference.

The demo itself proves the plumbing but not the value. Refocusing a singlet from 974 µm
RMS to 14 µm is not a result anyone doubts; it does not show what an agent adds. The
example that would sell the tool is one that people actually struggle with: take a stock
achromat pair as an OCT scan lens, show the chromatic focal shift across 800 to 900 nm,
and let the agent rebalance it while explaining the Seidel changes.

### 5. The review is a ledger, not a review

The rendered `report.md` and `report.html` show values unrounded
(`49.05139286997028`), show constraints as HTML-escaped JSON blobs, include a row
`error: unavailable`, and draw a vertex-only schematic. There is no layout, no spot
diagram, no ray fan, no MTF curve, and no sentence saying what changed and why it is
better or worse. Lens designers read pictures first. A review page that a project lead
would forward should open with:

1. Layout with rays, before and after if a change was made.
2. Spot diagram grid by field and wavelength, with the Airy disk drawn.
3. Ray fan and OPD fan, or at least RMS wavefront versus field.
4. MTF versus frequency with the diffraction limit.
5. A three-line plain-language verdict: what moved, what improved, what still fails.
6. Then the requirements table, then provenance and hashes.

### 6. Microscopy and OCT guidance is thin

The two references are 37 and 34 lines and mostly audit checklists. For the stated goal
they need the design content practitioners look for:

- Microscopy: objective classes and correction (achromat, plan, fluor, apo), NA versus
  working distance versus field, tube-lens conventions (Nikon 200, Olympus 180, Zeiss
  165, Leica 200 mm), infinity-corrected relays and the 4f condition, pupil matching to a
  scanner or SLM, cover glass and immersion, Nyquist sampling, Petzval sum and field
  flatness, telecentricity for quantitative imaging.
- OCT: sample-arm forms (telecentric f-theta scan lens, Plössl-type pairs of stock
  achromats, Keplerian relay to a galvo), lateral resolution versus depth of focus
  trade-off through the confocal parameter, chromatic focal shift and dispersion over a
  broadband source, group versus phase index, reference-arm dispersion matching, back
  reflections and ghost focus, beam clipping at the galvo, telecentricity error and its
  effect on flattening a B-scan.

Each of these is one or two formulae and a paragraph. The skill already computes the
easy scalar numbers; it needs to connect them to design decisions.

### 7. The repository carries process and evidence weight that new visitors do not need

`docs/research/` is 98 MB of committed logs, JSON evidence and stdout captures, and
`docs/superpowers/` holds internal planning specs. These are valuable to the maintainer
but they make the clone heavy, clutter search results, and signal "internal project"
rather than "community tool". Move release evidence to GitHub Releases assets or a
separate `optical-design-evidence` repository, keep a short `docs/verification.md` that
links to it, and drop the plans from the published tree.

### 8. Triggering

The description is 231 characters and reads well, but it omits the words a user actually
types: `.zmx`, Zemax, lens design, optimize a lens, achromat, objective, scan lens, spot
diagram, ray fan, Seidel, glass. Description text is how the agent decides to load the
skill at all.

## Recommendations

Priority 0 items unblock the stated goal. Priority 1 items drive adoption. Priority 2
items are polish.

### P0. Import real ZMX files (portable backend)

- Replace the allowlist with a deny-list of directives that change the optical model and
  are unsupported: `COORDBRK`, `NSC*`, `MOFF`/`MNUM` (multi-config), `PPAR`/`PZUP` pickups
  when they cannot be resolved, surface `TYPE` values Optiland cannot trace. Everything
  else passes through Optiland's reader; ignored directives are listed in the inspect
  report under `ignored_directives`.
- Accept `UNIT` in inches and centimetres by converting to mm, with the conversion recorded.
- Resolve `GLAS` names against Optiland's catalog; on a miss, fall back to the `GLAS`
  line's own nd and Vd values with an Abbe model and a warning, instead of aborting.
- Keep `.zos` and `.zar` on the native backend only, but say so in one line.

### P0. Expose the standard analysis set

Add `design.py analyze --model lens.zmx --out dir [--plots]` that writes one JSON file
per analysis and one PNG each, using Optiland's existing classes:

layout, spot diagram, ray fan, OPD fan, field curvature and distortion, through-focus
MTF, MTF versus field, RMS spot and RMS wavefront versus field, encircled energy, Seidel
and third-order table, first-order summary (EFL, BFL, pupils, cardinal points, Lagrange
invariant, working F-number at each field).

Return a compact `summary.json` the agent can read in one call and a folder of images for
the review. This one command turns the skill from a job runner into something a designer
uses every day.

### P0. Use a real optimizer and real variables

- Add `optimizer: least_squares` (Optiland's damped least squares) as the default for
  `optimize`, keep the current bounded pattern search as `optimizer: pattern` for the
  cases where its budget accounting is wanted, and add `optimizer: global` for
  differential evolution with a wall-clock budget.
- Variables: radius, thickness, conic, asphere coefficients, and glass (via GlassExpert
  or a declared candidate list). Lift the four-variable cap; keep the bounds contract.
- Operands: keep the current metrics and add RMS wavefront error, Seidel terms, chief-ray
  height and angle (for telecentricity and distortion), paraxial EFL and magnification,
  edge and center thickness, and total track. These are the operands every merit function
  in practice uses.
- Keep the acceptance rules exactly as they are: hard requirements gate, saved candidate
  reloads and re-measures, source untouched. That discipline is the differentiator; the
  optimizer underneath it should be the standard one.

### P0. Add a first-order gate and a plain-language aberration diagnosis

Two habits separate an expert from a novice, and both are cheap to automate:

- **First-order gate before any optimization.** EFL, back focal distance, F-number or NA,
  magnification, stop position, entrance and exit pupil, total track, and for scan lenses
  chief-ray angle at the image (telecentricity). Report them against the specification
  and refuse to optimize when they are inconsistent (EFL, magnification and track length
  are coupled; users routinely over-constrain all three). The OptiAgent study found
  frontier language models producing focal lengths 35 to 55 percent off when they
  reasoned without a paraxial check ([arXiv 2602.23761](https://arxiv.org/abs/2602.23761));
  this gate is where an agent tool earns trust.
- **Aberration diagnosis after every analysis.** From the Seidel table, field curvature
  and distortion curves and the ray fans, state in two sentences which aberration
  dominates at which field and wavelength, and which variable class usually controls it
  (bending, stop shift, glass pair, splitting, a field flattener). In Zemax community
  threads the recurring failure is misdiagnosis, for example calling field curvature
  "spherical aberration" ([example thread](https://community.zemax.com/got-a-question-7/removing-spherical-aberration-from-optimization-2027)).
  Nobody asks for "explain what the optimizer did" by name; they ask why the optimizer
  is stuck, and this is the answer.

Encode the practitioner merit-function recipe as the default path in the optimization
reference: first-order operands first, then RMS spot, then OPD or wavefront, then MTF
at the required frequencies; freeze glasses early; sample fields at 0, 0.5, 0.8 and 0.9
of the full field rather than uniformly; add custom operands only after a baseline
merit exists ([Zemax community guidance](https://community.zemax.com/got-a-question-7/generic-optimization-mf-for-lens-design-problem-solving-4733)).

### P0. Rewrite SKILL.md

Target 60 to 80 lines and under 1,500 tokens. Suggested shape:

```
---
name: optical-design
description: >
  Use when the user has a lens or optical system to analyze, optimize, tolerance or
  review: .zmx/.zos/Optiland prescriptions, achromats, objectives, relays, scan lenses,
  microscopy or OCT optics, or asks about resolution, PSF, MTF, Zernike, wavefront or
  interferometry results. Also use for lens-design questions even without a file.
---

# optical-design

One paragraph: what the skill does and the two engines.

## Start here (a 6-row table: user intent -> command -> reference)

## How to work a design problem (8 numbered lines: inspect, first-order check, freeze
requirements, choose variables and merit, optimize, look at the pictures, tolerance,
review). Each line names the command and the one reference to read.

## Explaining results (6 bullets: always give the number with its unit and the condition
it was measured at; name the dominant aberration from the Seidel table; say what the
optimizer traded; compare to the diffraction limit; state the model limit in one clause,
not a paragraph.)

## Evidence limits (one short section, the only place the disclaimers live)

## Reference index (one line each)
```

Move the rest of the current text into `references/policy.md` for people who want the
detailed acceptance semantics. The current SKILL.md is a good document; it is just not
the right first page.

### P1. Make the review a review

Reorder and extend `review.py` output as listed in finding 5. Round values to
significant figures appropriate to the unit (three for µm and mm, two for MTF). Render
constraints as "20 cyc/mm tangential MTF ≥ 0.30" instead of JSON. Put the verification
paragraph in a collapsible "Provenance" section at the end. Embed PNGs from `analyze`.

### P1. Add a design-forms library with commentary

Ship `assets/forms/` with ten to fifteen starting points in Optiland JSON and `.zmx`
(cemented and air-spaced achromats, Cooke triplet, Tessar, double Gauss, Petzval, Plössl
scan-lens pair, telecentric f-theta scan lens, infinity-corrected 10x and 20x microscope
objectives, tube lens, 4f relay). Each form gets a 15-line `.md` beside it: what it is
good for, its typical NA and field limits, which aberration it fails on first, and which
variables to release first. Optiland's sample library covers half of these already; the
commentary is what people cannot get elsewhere. Public prescription sources to draw on
and cite: [lens-designs.com](https://www.lens-designs.com/) (over 1,000 `.zmx` files,
including 109 microscope objectives), [LensLibrary](https://github.com/nzhagen/LensLibrary),
and Zhang and Gross's three-part "Systematic design of microscope objectives" with its
29 lens modules ([Part I](https://www.degruyterbrill.com/document/doi/10.1515/aot-2019-0002/html)).
Key the index by form, F-number, half field and NA so an agent can pick a start from
a specification, the way Johantgen's starting-point method does by hand
([opticalensdesign.com](https://www.opticalensdesign.com/post/lens-design-process-with-zemax-selection-of-a-starting-point-part-ii)).

### P1. Deepen the microscopy and OCT references

Rewrite both to about 120 lines each with the topics in finding 6. Keep the formula
density high and the audit checklists short. Add two worked examples that run end to
end: a 4f relay with tube-lens matching, and an OCT scan lens showing chromatic focal
shift across the source band before and after optimization. For the OCT example use the
published semi-Plössl form, two stock achromats face to face, which reaches near
diffraction-limited spots to about 6 degrees of scan against 2 degrees for a single
doublet ([Appl. Opt. 55, 646](https://opg.optica.org/ao/abstract.cfm?uri=ao-55-4-646)),
and compare it with a commercial telecentric scan lens envelope such as the Thorlabs
LSM03 (36 mm EFL, 4 mm pupil). Show lateral resolution, confocal parameter, chromatic
focal shift across 800 to 900 nm and telecentricity error side by side.

### P1. Add a principles primer

One reference, `references/aberrations.md`, of about 150 lines: the five Seidel
aberrations plus axial and lateral color, what each looks like in a spot diagram, ray
fan and OPD fan, the sign conventions, which variables control each (bending, stop
shift, glass choice, splitting), the Petzval sum, Maréchal and Rayleigh quarter-wave
criteria, Strehl approximations, and the diffraction-limited spot and MTF cutoff. This is
the "robust and concise explanation of principles and quantitative formulae" the goal
asks for, and it is what makes the skill useful to beginners without slowing experts.

### P1. Fix the description and add near-miss guards

Use the description drafted above. Add three lines of "do not use for" in the body:
non-sequential and stray light, thin-film coating design, illumination and non-imaging
optics. This protects triggering precision without a wall of exclusions.

### P2. Slim the repository

- Move `docs/research/` to release assets or a sibling evidence repository; keep a short
  `docs/verification.md` with links and the compatibility table.
- Move `docs/superpowers/` out of the published tree.
- Merge `first-lens.md` and `quickstart.md`; fold `professional-workflow.md` into the
  rewritten SKILL.md workflow section and a single `docs/your-own-lens.md`.
- Replace the vertex schematic in the README with a real layout and spot diagram from
  `analyze`.

### P2. Make the MCP server optics-shaped

The six job-runner tools are fine for long jobs. Add stateless tools `inspect`,
`analyze`, `first_order` and `seidel` that return in seconds, so an agent in Claude
Desktop or Cursor can converse about a lens without spinning up a job.

### P2. Housekeeping

- The `pip` package of Optiland 0.6.2 reports `__version__` 0.6.1; pin by distribution
  version in provenance and note the discrepancy.
- `docs/glossary.md` should use the field's own words alongside the project's.
- `CONTRIBUTING.md` asks for a cited source and a pinned test per formula. Keep this, it
  is a real differentiator, and say it in the README.

## Suggested sequence

| Milestone | Contents | Why first |
|---|---|---|
| 1.2 "Open the file" | Real ZMX import, `analyze` with plots, SKILL.md rewrite, description fix | Unblocks every real user; largest visible change for the least risk to the verified job core |
| 1.3 "Design, not just refocus" | Least-squares optimizer, conic/asphere/glass variables, wavefront and Seidel operands, review redesign | Turns the tool into something that can improve a real lens |
| 1.4 "Teach" | Aberration primer, forms library with commentary, microscopy and OCT rewrites, two worked examples | The content that earns word-of-mouth in the optics community |
| 1.5 "Lighten" | Evidence moved out, docs merged, optics-shaped MCP tools | Lower barrier for contributors and forks |

Each milestone keeps the current tests green and keeps the acceptance semantics
unchanged; the new analysis and optimizer paths should carry the same hash and reload
verification the existing ones do.

## Evidence from the skill ecosystem

What the most-installed skills have in common, and what the community complains about,
supports the changes above. Sources are linked.

**Official guidance sets hard budgets.** Anthropic's
[skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
say to keep the SKILL.md body under 500 lines, and the
[open specification](https://agentskills.io/specification) recommends under 5,000 tokens
for instructions. The current SKILL.md is within that budget on length but not on
density: the guidance's core principle is "the context window is a public good... only
add context Claude doesn't already have", and it names verbosity, too many options and
inconsistent terminology as anti-patterns. The
[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) adds:
"If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid
structures, that's a yellow flag; if possible, reframe and explain the reasoning."

**Descriptions must be pushy and noun-heavy.** The same skill-creator recommends making
descriptions "a little bit pushy", for example "use this skill whenever the user mentions
... even if they don't explicitly ask". A 650-trial study found directive descriptions
activated 100 percent of the time against 37 percent for passive ones
([Seleznov, Medium](https://medium.com/@ivan.seleznov1/why-claude-code-skills-dont-activate-and-how-to-fix-it-86f679409af1)).
Claude Code also has a listing budget of roughly 8,000 characters across all installed
skill descriptions; when it is exceeded, descriptions are silently dropped and the agent
sees only names ([claude-code issue 64606](https://github.com/anthropics/claude-code/issues/64606)).
A short description packed with the nouns users type is therefore both a triggering and
a survival strategy.

**Top skills are small and single-purpose.** On the
[skills.sh leaderboard](https://skills.sh/) the most-installed community skill,
grill-me, has an 11-line SKILL.md that delegates to a 47-line primitive. Superpowers,
the most-starred skill collection, budgets "frequently loaded skills under 200 words,
other skills under 500 words" in its own writing-skills guide, and its v6 release notes
report removing "recap sections, social proof, and benefits-selling prose" for almost
50 percent fewer tokens ([release notes](https://github.com/obra/superpowers/blob/main/RELEASE-NOTES.md)).
Simon Willison's endorsement singled out that "the core of it is VERY token light"
([simonwillison.net](https://simonwillison.net/2025/Oct/10/superpowers/)).

**Scientific skills that work ship scripts and worked examples.** The K-Dense scientific
collection, the closest analogue to this project, pairs each SKILL.md with a `scripts/`
folder ("run these instead of hand-writing code"), a README with four end-to-end
workflows and a video, and repository-wide validation on every pull request. Vercel's
react-best-practices skill is an index into 57 one-page rules, each with a why, an
incorrect example and a correct example. Firecrawl's review of the field puts it as
"lean SKILL.md, fat reference.md" and "three worked examples beat twenty bullet-pointed
constraints" ([firecrawl](https://www.firecrawl.dev/blog/best-claude-code-skills)).

**Complaints cluster on bloat and lecturing.** "A 20k-token skill file is 10 percent of a
200k window gone before a single line" ([ksred](https://www.ksred.com/best-claude-code-skills-which-ones-are-actually-worth-installing/));
Mintlify's guidance that a skill "is a cheat sheet, not a replacement for docs"
([mintlify](https://www.mintlify.com/blog/skill-md)); and on the heaviest collections,
"I do not think the current models need as much harness"
([mcp.directory](https://mcp.directory/blog/superpowers-skill-worth-it-2026)). The
current references total about 21,700 tokens; an agent that reads three of them to answer
one question has spent a third of a small context window on policy.

**Adoption drivers are legible promises and install one-liners.** Every top repository
lists one install line per agent at the top of the README, then two or three example
prompts, then a numbered workflow. The promise is one sentence: "grill me", "brainstorm
before code", "65 percent fewer tokens". For this project the equivalent sentence is
"Open a .zmx, see what is wrong with it, fix it with a verified change, and get a review
you can forward." The current README's opening line, "From your first lens to an
engineering review", is close; the demo underneath it does not yet deliver the middle
two clauses.

## Evidence from the optical-design ecosystem

**Optiland is the right engine, and it is moving fast.** About 970 stars, MIT licensed,
a release every one to two months (0.6.2 on 14 July 2026), and it is the only open
tool that combines `.zmx` read and write, CODE V and OSLO import, aspheres and freeforms,
coordinate breaks, catalog glasses, local, global and categorical (GlassExpert)
optimization, tolerancing, PSF and MTF, and a PyTorch backend
([releases](https://github.com/optiland/optiland/releases),
[docs](https://optiland.readthedocs.io/en/latest/)). The skill pins it and then uses a
small fraction of it. Pinning is right; the fraction is the problem.
[ray-optics](https://github.com/mjhoptics/ray-optics) (about 400 stars, 0.9.10 in
September 2026) is the natural complement for y-ybar first-order layout and is worth
citing in the primer even if it is not a dependency.

**Everything else is dormant or a paper artifact.** rayopt last committed in 2023,
Goptical in 2012, OpticSim.jl was archived by Microsoft in 2022, KDP-2 survives as Koko
with 33 stars, pyrate and OpenRayTrace are abandoned. The differentiable tracers
(DeepLens, dO, Torch Lens Maker) are research vehicles. There is no maintained
open-source rival to Optiland for sequential design, which means an agent skill built on
it has no competition for the "portable" tier.

**The Zemax MCP servers are the competition for the native tier, and they are thin.**
Four appeared in 2025 and 2026, all Windows only, from 31 to 143 tools, one to 56 stars,
with README notes like "may not work correctly in all cases" and no user reviews found
([jaruiz6363](https://github.com/jaruiz6363/OpticStudioMCPServer),
[webworn](https://github.com/webworn/zemax-mcp-server),
[YonggangG](https://github.com/YonggangG/Zemax_MCP_Server)). Ansys's own Engineering
Copilot is a chat assistant, not a designer. None of them offers a license-free path,
verified mutation, or explanation. That combination is this project's opening, provided
it can actually open the file and draw the picture.

**Research confirms where language models fail at optics.** The OptiAgent paper measured
frontier models producing focal lengths 35 to 55 percent off and initial RMS spots from
127 to 5,847 µm when designing from text alone; a paraxial engine in the loop brought
that to 1 percent and 41 µm ([arXiv 2602.23761](https://arxiv.org/abs/2602.23761)).
Flexcompute's account of agentic photonics design lists the practices that worked:
design-rule checks before simulation, hypothesis journaling, state exposed in readable
form, and a human formulating the problem
([arXiv 2606.00915](https://arxiv.org/html/2606.00915v1)). The skill's receipt discipline
already covers the last two; the first-order gate covers the first.

**What practitioners ask for.** Across Zemax community threads, the Hacker News
discussion of Torch Lens Maker and lens-design blogs, the same requests recur: paraxial
quantities and principal planes first, a rich operand set with explicit constraints,
stock-lens matching, starting-point libraries chosen by field and F-number, and help
diagnosing which aberration is limiting a design
([HN](https://news.ycombinator.com/item?id=43435438),
[Zemax forum](https://community.zemax.com/got-a-question-7/design-a-camera-lens-optics-studio-4524),
[Pencil of Rays](https://www.pencilofrays.com/lens-design-forms/)). The canonical texts
to cite in the primer are Kidger, Smith's Modern Lens Design, Shannon, Geary, Sasián and
the Gross Handbook, volume 4 for microscope optics.

**Microscopy and OCT specifics worth encoding.** Tube-lens focal lengths (Nikon, Leica
and Mitutoyo 200 mm, Olympus 180 mm, Zeiss 164.5 mm) and the stop-size and ray-aiming
conventions for modelling an objective from its NA and magnification
([Zemax forum](https://community.zemax.com/got-a-question-7/aperture-settings-for-microscope-objective-simulation-1764));
the OCT resolution set (axial from bandwidth, lateral from NA, depth of focus from the
confocal parameter, imaging range from spectrometer sampling) with the reminder that
axial and lateral resolution are independent
([NCBI OCT chapter](https://www.ncbi.nlm.nih.gov/books/NBK554044/)); telecentric scan-lens
requirements and their cost ([Thorlabs](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_ID=10343));
and the relay-conjugation requirement between galvo mirrors for true telecentric scanning.

## What this review did not change

No code, SKILL.md text or reference file was modified. The numbers above come from
running the shipped commands on this branch and from reading the sources linked. The
recommendations are a plan, not an implementation; each milestone can ship as its own
pull request against the current test suite.
