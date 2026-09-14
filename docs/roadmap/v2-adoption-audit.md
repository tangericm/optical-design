# Optical Design Skill: Adoption, Experience, and Utility Audit

## Assessment

**Keep the v2 architecture, but repair the complete user journey before expanding distribution.** A short skill that teaches an agent to use a real optical engine, backed by deterministic checks and an optional audited workflow, is a sound foundation. The strongest opportunity is to make optical reasoning and useful visual results accessible to people who cannot yet write an Optiland script or interpret an aberration plot.

The current release has substantial capabilities: calculators, fourteen executable recipes, eleven starting forms, visual reporting, portable computation, and licensed OpticStudio support within a documented scope. It also has defects at the boundaries between those components. The published review recipe does not satisfy the renderer's schema. Running a calculator can make a managed installation impossible to update. Some first-order labels and acceptance checks can mislead an agent even when the code executes successfully.

For a broad audience, these defects matter more than additional engines, more plugin manifests, or a larger collection of prescriptions. Beginners need a reliable first result and an explanation they can understand. Practitioners need confidence that units, model fidelity, metric definitions, and acceptance checks remain correct when they move beyond the examples.

The recommended order is **correctness and workflow repairs → guided first use → stronger evidence → targeted discovery**. Position the project around a concrete promise: *Understand a lens, improve it against stated requirements, and share the evidence.* Avoid treating every generated review as a verified design.

## Scope and evidence

This assessment concerns **v2.0.0**, repository commit `398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d`. Public repository statistics and documentation were checked on **14 September 2026**. The audience includes beginners, students, researchers, and practicing optical engineers. The earlier adoption review concerned v1.1.0; its recommendations for recipes, forms, figures, and shorter instructions have largely shipped and should not be repeated as missing functionality.[^1]

Coverage includes the public README and onboarding, skill instructions and references, plugin metadata, npm installation lifecycle, first-order and inspection tools, review generation, representative optical calculations, evaluation design, and CI boundaries. Targeted reproductions used the previously downloaded public npm v2.0.0 package in an isolated consumer directory, with Python 3.11.13 and Optiland 0.6.2. Source inspection and reproduced behavior are distinguished below. This is a product and engineering audit, not a certification of every formula, optical prescription, or supported agent host. No new live OpticStudio validation or controlled agent benchmark is claimed.

| Area | Assessment | Evidence and implication |
|---|---|---|
| Skill structure | Strong foundation | `SKILL.md` is about 694 whitespace-delimited words and 90 lines; detailed knowledge is already outside the entry point. |
| Useful optical capability | Substantial | Fourteen recipes and eleven forms cover much more than a refocus wrapper. The product should demonstrate this breadth through selected tasks. |
| First-use experience | Needs repair | Repository-relative prompts, installation/output directory confusion, and a disconnected review contract interrupt the journey. |
| Numerical meaning and acceptance | Needs repair | Reproduced unit, BFL-label, and gate-validation problems affect interpretation and trust. |
| Audited workflow | Worth preserving | Copying, hashing, reload checks, explicit requirements, and bounded mutations provide valuable engineering discipline. |
| Evaluation evidence | Encouraging but preliminary | Five paired scenario summaries exist, with disclosed leakage and budget limitations; general effectiveness is not established. |
| Distribution and maintenance | Good base, lifecycle defect | Several installation channels and cross-platform CI exist; ordinary use can block managed updates. |
| Beginner learning | Underdeveloped | References explain optics, but initial prompts assume familiarity with prescription files, pupils, Seidel terms, and optimization. |

The repository contains 128 tracked files under the skill and 44 tracked files under `tests`. File count is not a context-window cost: only material actually loaded into a conversation incurs that cost. Further cleanup should target redundant knowledge and generated outputs, not remove useful dormant references solely to make these counts smaller.

## Comparison with adopted skills and plugins

The following are selected comparators, not a universal ranking. Stars measure public interest, not active users, successful tasks, scientific validity, or the quality of an individual skill. Large general-purpose collections address a much larger audience than optical design. Counts are an observed snapshot of GitHub's repository metadata.[^2]

| Repository | Stars | Relevant structure or behavior | Useful lesson for optical-design |
|---|---:|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | 286,627 | Task-specific skills, tests, host integrations, and an explicit workflow | Make transitions between stages clear; do not copy an entire software-development methodology into a lens task. |
| [anthropics/skills](https://github.com/anthropics/skills) | 176,299 | Individual skill folders, references/scripts, a template, and skill-creation evaluation guidance | Keep the entry point focused; test the behavior added by the skill. |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 44,914 | Scientific skills, example research workflows, repository checks, contribution and citation material | Connect scientific tools to complete research outcomes and make the software citable. |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | 37,104 | A focused tool service with explicit discussion of CLI plus skills versus MCP | Choose the interface by the task; a large MCP surface is not inherently better. |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | 31,621 | Shared discovery and installation infrastructure | Participate in existing distribution infrastructure instead of creating another registry. |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 31,191 | Focused capabilities, recognizable trigger examples, and categorized guidance | Describe jobs people recognize and organize supporting knowledge by the question it answers. |
| [openai/skills](https://github.com/openai/skills) | 27,179 | A catalog of discrete skills | Preserve a portable skill core while keeping host-specific presentation outside it. |
| [tangericm/optical-design](https://github.com/tangericm/optical-design) | 1 | One specialized skill with an installer, recipes, tools, and engineering evidence | This is an early adoption stage; a small set of successful external users is more informative than more packaging features. |

Three distinctions are especially useful.

**Progressive disclosure is already substantially implemented.** The Agent Skills specification supports a small entry file with optional scripts, references, and assets. It recommends loading additional material only when needed and keeping references shallow. The current skill follows that basic structure; there is no evidence that splitting it into many separately installed skills would improve it.[^3] The next improvement is routing precision: tell the agent exactly where scripts live and which reference section answers the current question.

**Specificity should depend on fragility.** Anthropic's authoring guidance distinguishes flexible reasoning from operations that need precise instructions.[^4] Optical diagnosis and choice of design strategy benefit from flexibility. Unit conversion, acceptance predicates, file ownership, and report serialization need deterministic behavior. The current release puts some fragile work into prose while hard-coding some decisions that should depend on the problem.

**A plugin is distribution and integration, not evidence of utility.** Superpowers' repository combines a clear workflow with host integration.[^5] Vercel's examples make the intended task easy to recognize.[^6] K-Dense demonstrates multi-step scientific outcomes and supplies citation guidance; its own headline usage claims are not independently validated here.[^7] These are useful design patterns, not proof that copying their scale or promotional language will cause adoption.

Playwright's own repository explicitly describes situations suited to CLI plus skills and others suited to persistent MCP state.[^8] Optical-design should similarly keep short calculations and portable analysis easy to invoke, while retaining its existing job interface for long operations, cancellation, and owned native sessions. More tools should follow demonstrated friction, not precede it.

## Comparison with optical tools

Optical software has a smaller public audience than general coding tools. Several maintained projects serve complementary purposes, so the previous review's sweeping characterization of other tools as dormant or mere paper artifacts should not guide future positioning.

| Project | Stars | Relevant strength | Recommended relationship |
|---|---:|---|---|
| [Optiland](https://github.com/optiland/optiland) | 969 | Sequential optical design, analysis, optimization, examples, and differentiable computation | Keep as the portable default; maintain an explicit tested-version boundary. |
| [DeepLens](https://github.com/vccimaging/DeepLens) | 730 | Differentiable simulation and computational-imaging workflows | Treat as a specialized research alternative and possible later integration, not a default dependency. |
| [RayOptics](https://github.com/mjhoptics/ray-optics) | 404 | Paraxial layout diagrams, geometric analysis, file import, notebooks and GUI | Learn from its visual explanation of system layout; consider selected independent reference comparisons. |
| [prysm](https://github.com/brandondube/prysm) | 356 | Physical optics, wavefront analysis, image simulation, and metrology | Useful reference and potential cross-check for carefully matched scalar calculations. |
| [DCC-Lab/RayTracing](https://github.com/DCC-Lab/RayTracing) | 344 | ABCD-matrix paths, stops, imaging and Gaussian-beam teaching | A strong model for accessible relay and microscopy explanations; not an aberration-design replacement. |
| [ZOSPy](https://github.com/MREYE-LUMC/ZOSPy) | 118 | Python access to OpticStudio analyses, solvers and API features | Preserve native interoperability and learn from its explicit examples and compatibility documentation. |

All six repositories were unarchived at the snapshot. Their latest recorded pushes ranged from July to September 2026; that is evidence of repository activity, not equal maintenance depth or validation quality.[^2]

Optiland's current documentation routes readers into beginner, practitioner, researcher, and contributor paths. It places conventions near the beginning and offers both a quickstart and task-oriented navigation.[^9] Its public documentation currently describes a development build beyond 0.6.2; examples from that site must be checked against the version the skill actually installs. Link to upstream conceptual material, but test local executable recipes against the pinned distribution.

RayOptics illustrates how paraxial diagrams and prescription views can explain a system before optimization.[^10] DCC-Lab's documentation explicitly limits its ABCD approach to analysis without spherical or chromatic aberrations; this clarity is a useful model for beginner-facing scope statements.[^11] Prysm's composable numerical tools suggest targeted physical-optics comparisons without requiring a wholesale backend rewrite.[^12]

DeepLens explicitly invites agent-driven simulation and directs automated lens-design work toward its AutoLens project. That makes it a meaningful adjacent competitor for computational imaging, rather than something to dismiss.[^13] ZOSPy exposes a different API and native-session model; having the same optical goal does not make an Optiland code recipe executable through ZOSPy.[^14]

The defensible differentiation is therefore **a well-taught, reproducible path from a question to an optical result and a readable explanation**. It is not exclusivity over Python optics, agent-written simulation, or open-source lens design.

## Findings and recommended repairs

Priorities below are recommended release priorities. **P0** means repair before promoting v2 more widely because a normal workflow fails or a result can be materially misleading. **P1** improves successful use and confidence. **P2** expands reach after those foundations work. These are product priorities, not security vulnerability ratings.

### F1 — P0: The published review recipe cannot feed the published renderer

**Reproduced.** Recipe 14 executed and produced its figures and `summary.json`, but `validate_summary()` rejected the result because `engine` was missing. Adding that field exposed a second mismatch: first-order values were scalars while the renderer requires objects containing `value`. Normalizing those values exposed a third mismatch: metric rows lacked `name` and `value`.[^15]

There is also a semantic problem. The recipe extracts `spot.rms_spot_radius()[0]`, which is the first field's wavelength series, and creates several rows labeled `0,0` without wavelength labels. In the reproduction those values were approximately 3.79, 4.29, and 6.20 µm. The figures cover additional fields, but the metric table does not. The verdict is a literal example string rather than a conclusion calculated from thresholds.

**Recommendation:** define one versioned summary contract and make the recipe produce it directly. Enumerate both field and wavelength, attach units, record the actual engine distribution version, and distinguish source-file hashes from hashes of an in-memory representation. Generate verdict language from measured requirements or mark it as an authored interpretation.

**Acceptance:** the exact published recipe runs in a clean consumer directory, renders without editing JSON, and produces tables whose field/wavelength pairs agree with the plotted data. Add one integration test connecting recipe output to the renderer. The existing recipe tests prove snippets execute; the renderer tests use separately constructed fixtures, so both can pass while this journey fails.

### F2 — P0: Ordinary use contaminates managed installations

**Reproduced from the published npm package.** A clean project-scoped Codex installation succeeded. Running the documented Airy calculator succeeded and created `scripts/_lib/__pycache__`. An immediate update then failed with the managed-installation-changed error. No source file had been edited. The installer compares both file hashes and the exact directory tree.[^16]

The step-by-step quickstart compounds this: it tells readers to run inside the installed skill directory and writes `quickstart-focus` and `quickstart-review` there. Those outputs also violate the exact-tree ownership check. Meanwhile, the README's first example names `skills/optical-design/assets/forms/cooke-triplet.zmx`, which is absent in a normal project installation at `.agents/skills/optical-design`.[^17]

**Recommendation:** make the skill directory read-only in normal use. Resolve scripts and assets from the location of the loaded `SKILL.md`, and put all user work into one named directory in the user's project. Prevent bytecode generation consistently at supported entry points, and define conservative recovery for recognized generated caches. Preserve the protection for genuinely edited source files. Do not solve this by blindly allowing arbitrary added files during uninstall.

Update backups also need a visible, bounded lifecycle: report their location, explain retention, and provide an ownership-aware cleanup route. Avoid accumulating a new hidden backup for every uneventful update indefinitely.

**Acceptance:** install → calculator → example → update → uninstall works without manual cleanup on Windows, macOS, and Linux. User outputs and edited files survive. The exact README prompt works from an empty consumer project, without a repository checkout.

### F3 — P0: Import fidelity is too easy to confuse with successful parsing

**Reproduced.** A synthetic copy of the bundled triplet with `UNIT IN` retained the same numeric prescription values. Inspection warned that the reader did not convert non-millimetre units, but still returned `units: "mm"`. The separate first-order tool returned an EFL labeled millimetres, approximately 50.0004, with no warning. This fixture tests unit interpretation; it is not intended as a realistic inch-scale lens.[^18]

The inspection classifier also collapses unrecognized directives into the ignored category. Documentation repeatedly calls ignored directives cosmetic, although the code includes ray-aiming, polarization, aperture-related and vignetting entries in that area. A parameter being ignored by an importer does not establish that it was optically irrelevant in the source program.

**Recommendation:** share an import assessment between inspection, first-order analysis, and reporting. Distinguish *preserved*, *display metadata*, *unsupported with possible optical effect*, and *unknown*. Normalize supported units or stop numerical acceptance with a precise conversion requirement. Keep partial inspection available, with a visible fidelity status. Avoid an unrestricted claim that any real OpticStudio export is represented faithfully.

**Acceptance:** a non-mm file cannot acquire a passing mm-based gate without conversion. Unknown model-affecting content remains visible in the summary and review. Add representative fixtures for aperture clipping, vignetting, coordinate breaks, and multiple configurations, with documented expectations rather than a blanket promise of support.

### F4 — P0: Back focal length is mislabeled, and related metrics need clearer definitions

**Reproduced.** `first_order.compute()` assigns the distance from the last optical surface to the current image surface to `bfl_mm`. For the bundled triplet it returned 42.20778 mm. Moving only the image surface 10 mm farther away changed the reported BFL to 52.20778 mm while EFL stayed unchanged. The last-vertex-to-paraxial-back-focus distance, calculated using Optiland's documented image-relative focal-point convention, remained 42.41549 mm.[^19][^20]

This is an image-distance measurement, not a general back-focal-length measurement. The evaluation checker repeats the same final-gap definition, so agreement with that checker does not independently establish correctness. The issue already exists for a model whose image plane differs slightly from paraxial focus; it is not limited to the shifted fixture.

**Recommendation:** expose separate `image_distance_mm` and `back_focal_length_mm` quantities, with reference planes and conjugates stated. Give each a definition-based regression case. Similarly, label `na_image` as a paraxial estimate where it is computed from `1/(2 F/#)`, and distinguish the first-order tool's paraxial chief-ray angle from the evaluation checker's real-ray angle. EFL spread over wavelength should be named explicitly rather than silently equated with a best-focus shift.

**Acceptance:** moving a detector without changing the optics changes image distance, not the back focal length. A high-NA or reverse-traced objective does not receive an unqualified real-NA claim from a paraxial estimate. Evaluation tolerances compare the same physical quantity and reference convention.

### F5 — P0: A gate can pass without imposing a valid requirement

**Reproduced.** `evaluate_gate()` accepted all of the following for an EFL of 50 mm: a rule containing only `tol_pct: 1`, a NaN maximum, a NaN target, and a boolean minimum. The first rule evaluates no constraint; NaN comparisons fail to reject it. Python's default JSON decoder also accepts non-standard NaN constants, so this is not restricted to internal Python calls.[^19]

A separate reference issue affects optimization: `merit-functions.md` describes operand `min_val`/`max_val` as hard constraints. In the pinned Optiland operand implementation, violating those bounds contributes a weighted residual. That differs from a post-optimization acceptance gate and from bounds on optimization variables.[^21]

**Recommendation:** require at least one actual bound or target; reject non-finite values and booleans; require a target when a percentage tolerance is supplied; validate nonnegative tolerances and consistent bounds. Keep hard acceptance separate from optimizer penalties, and demonstrate that distinction in the direct-code workflow as well as audited mode.

**Acceptance:** invalid specifications fail before optical work. A candidate with a better merit value but a failed hard requirement is reported as rejected. Tests exercise malformed and contradictory specifications, not only sensible passing and failing examples.

### F6 — P0: The teaching references need a focused scientific correction pass

**Source inspection.** The diagnosis example calls a steep, odd-symmetric linear tangential fan evidence of coma. The aberration table also calls the coma fan odd, while its own formula states transverse coma is quadratic in pupil coordinate. In the pure tangential case, differentiating the cubic coma wavefront produces an even quadratic ray term; a linear fan is associated with a focus-like contribution and may reflect astigmatic focus differences.[^22]

The Petzval section uses `sum(phi/n)` for both thin elements and individual refracting surfaces. Those are different formulations: the general surface expression includes both adjoining refractive indices, with an overall sign depending on the convention. Sasián's published surface term makes that distinction explicit.[^23] Several other statements are too categorical, including interpreting a geometric spot near an Airy radius as a reason to stop, and treating EFL, magnification, and track as universally over-constrained rather than checking the actual system and degrees of freedom.

**Recommendation:** correct these examples before using them as a beginner curriculum or benchmark rubric. Pair each diagnostic claim with a plotted controlled example and a brief statement of applicability. Treat Seidel terms as useful low-order evidence, then confirm the diagnosis with the actual fans, wavefront, and field dependence. Geometric spot comparisons should motivate diffraction analysis, not replace a specified MTF or wavefront criterion.

**Acceptance:** a small set of independently checked spherical, coma, astigmatism, defocus, distortion, and chromatic examples reproduces the stated signatures. Formula sources identify a section or equation and a convention. The grader must not reward repeating an incorrect diagnosis from the skill.

### F7 — P1: Acceptance sampling and report status need to survive the flexible workflow

The skill and optimization recipe repeatedly prescribe fields at 0, 0.5, 0.8, and 0.9 of full field. Recipe 9 includes an edge chief-ray operand, but does not evaluate edge RMS spot in that list. Those are illustrative optimization samples, not adequate proof of an edge-of-field requirement. Final validation should include the actual requirement boundary, declared wavelengths, and sufficient sampling.[^24]

**Reproduced boundary:** the renderer accepted a supplied metric of 99 µm against a maximum of 1 µm with `pass: true`, and counted it as passing. This is consistent with its documented role as a renderer rather than an optical engine; it becomes a UX problem if the page presents supplied status as independently verified evidence.

**Recommendation:** preserve separate states for *rendered*, *measured*, *checked against requirements*, and *saved candidate reloaded and verified*. Validate simple numerical consistency in the report contract, or visibly mark statuses as supplied by the analysis. A rendering success must never be the sole basis for optical success language. Direct-code and audited paths can share these definitions without being forced into one optimizer framework.

**Acceptance:** a full-field requirement is tested at full field; a contradictory supplied pass flag is rejected or prominently identified. Reports state what was checked, what was not, and whether values belong to the source, an in-memory candidate, or the reloaded candidate.

### F8 — P1: Native support and installation instructions overstate interchangeability

The README and capabilities table say the same recipes run through licensed OpticStudio. The fourteen executable recipes import Optiland classes, while the native reference mainly documents prerequisites and the bounded audited adapter. The first-order and inspection scripts accept `.zmx` and Optiland JSON, not `.zos`. The general workflow is transferable, but these snippets are not drop-in ZOSPy recipes.[^25]

**Recommendation:** publish a small capability matrix by file format, engine, and execution path. Route `.zos` directly to the licensed path, with a useful alternative when it is unavailable. Either provide tested native equivalents for the core inspect/analyze/save workflow or describe native support more narrowly. Use the same capability wording in npm metadata, the README, and plugin listings.

There are smaller documentation inconsistencies to repair alongside this: the thin renderer creates HTML, while one capabilities entry promises HTML/Markdown; a quickstart example uses `--out review`, although that option is an HTML file path. Five installation commands in one block should be clearly labeled as alternatives, so a beginner does not run all five.

**Acceptance:** every advertised file type has a working first action or an actionable capability explanation. Client installation is distinguished from engine readiness and end-to-end host validation. A richer doctor command should report those separately; it should not claim to have tested a license or engine that it only found on a path.

### F9 — P1: The evaluations show promise, not a general adoption claim

The release includes paired summaries for five scenarios. They report 30 of 30 assertions with the skill versus 26 of 30 without, and median wall clocks of 10.0 versus 14.2 minutes. The records also acknowledge that a with-skill agent read the shipped evaluation rubric, optimization budgets were capped through mid-run instructions, and the two optimization cases did not establish convergence. Optimization runs with the skill were slower in those examples.[^26]

The first-order checker shares some definitions with the implementation, including the BFL problem above. A single pair per task, imprecisely identified model versions, no measured between-run variance, and task-specific intervention make the aggregate unsuitable as a general speed or correctness guarantee. The existing transparency is a strength; preserve it.

**Recommendation:** move test rubrics and results outside the installed skill across every distribution method, while retaining public evaluation transparency in the repository. Hold back a separate set of inputs and assertions from the agent. Predetermine budgets, compare equivalent inputs and environments, record exact model/settings/package versions, and grade independently. Anthropic's skill-creation materials provide useful patterns for baselines, artifact-based grading, and inspection of weak assertions.[^27]

Add beginner and failure cases: an ambiguous camera-sampling question, a request with no file, a non-mm prescription, an unsupported `.zos` path, interrupted downloads, update after normal use, and a failed design that still deserves a useful report. A skill that gives a fast correct limit or a useful explanation of an unsupported file is succeeding, even when it does not optimize anything.

**Acceptance:** publish per-task outcomes and failures, not only an aggregate pass rate. Compare at least one economical and one capable model for claimed cross-model utility. Repeat high-value held-out scenarios before advertising uplift; run the full expensive comparison at release checkpoints rather than on every documentation change.

## Experience design for a broad audience

### One product, three starting points

Keep one installed skill. Offer three recognizable entry choices in the README, documentation, and plugin starter prompts:

| Starting point | Example prompt | First useful result |
|---|---|---|
| Learn with an example | “Show me how a lens forms an image using the bundled doublet. Explain the picture without assuming I know optical design.” | A labeled layout, one blur plot, and a short explanation. |
| Answer a practical question | “Will 6.5 µm camera pixels sample my microscope adequately? Help me find the information you need.” | Known inputs, the one or two missing quantities that matter, then a numerical answer with assumptions. |
| Work on my design | “Inspect this lens, explain what limits it, and suggest the smallest useful change.” | Import-fidelity status, first-order summary, evidence-based diagnosis, and a bounded next action. |

The first option should not require the user to know where a bundled asset was installed. The agent should resolve that location and copy a validated example into a user-owned output directory. The calculator result already provides a good teaching anchor: at 550 nm and f/4, the reproduced Airy first-zero radius was 2.684 µm. Explain what that number means before introducing more metrics.

Use optional explanatory depth rather than a separate beginner implementation. A beginner needs “the point spreads into a small patch,” followed by “RMS spot radius” when it becomes relevant. An engineer may prefer the metric table immediately. Both should receive the same computations, assumptions, and acceptance criteria.

### Ask only when the answer changes the work

The instruction to stop whenever first-order quantities disagree with the request is too broad for a design assistant. A mismatch is often the reason someone wants help. Distinguish an unknown requirement from a known target that the existing lens fails. For an unknown that changes the physical problem, ask a concise question. For a clear requested change, explain the mismatch and proceed with an appropriate candidate strategy.

When no prescription exists, infer a reasonable educational starting point and label it. Do not turn a learning request into an exhaustive requirements interview. Conversely, do not infer a real microscope manufacturer's tube-lens convention from a name such as “20x” or “60x” alone. Present the missing convention as a specific assumption or question.

### Make the first demonstration representative

The existing one-command demo is valuable as an installation and audited-refocus smoke test. Retain it for that purpose. Add one flagship walkthrough that demonstrates the v2 promise end to end: load a bundled model, explain an actual limitation, make one bounded improvement, reload the saved candidate, and render the result. It should exercise the same recipe/report path that users will follow afterward.

Prefer a simple doublet or a carefully chosen triplet task. The OCT form is deliberately unbalanced, and the microscope forms use a reverse-trace convention; those are useful intermediate exercises but poor unqualified defaults for a newcomer. Label each starting form as an educational reference, corrected example, deliberately unbalanced exercise, or validated starting point for a stated envelope. A form's familiar name is not a catalog specification.

Give the walkthrough a measured expected duration, separating cold dependency downloads from warm optical computation. During longer work, report useful stages and the current outcome. An optimizer stopping at its evaluation budget should say so and return the best measured candidate with its limitations, rather than imply convergence.

### Make the report answer a human question

The default report should open with the user's objective, a short result, and the next action. Then show the lens layout and a matched before/after comparison. Follow that with a compact requirements table: metric, field, wavelength, before, after, limit, and status. Put settings, source/candidate hashes, sampling, and engine versions in a secondary evidence section.

Use the same plot scales for before/after comparisons, label axes and units, and explain the meaning of the Airy reference. Add useful captions that describe the conclusion rather than only “Spot diagram.” Distinguish absent data from a pass. Preserve readable tables for people who cannot interpret the figures or cannot distinguish colors. The renderer already has HTML escaping, bounded figure-path handling, figure captions, and a provenance section; improve those foundations instead of replacing the reporting system.

Offer plain-language explanation alongside technical detail: “The center improved, but the outer field still misses the target” is more useful than a lower merit value alone. A physically unsuccessful optimization can still produce a successful review if the user understands why it failed and what to try next.

## Structure and utility recommendations

### Preserve a small, portable core

Keep `skills/optical-design/SKILL.md` as the single router, with scripts, assets, and references beneath it. Add an explicit skill-root rule and a default output-location rule. Keep host-specific icons, starter prompts, and installation metadata in the existing manifests. Do not move general optical instructions into one host's configuration.

The 24 KB recipes file is useful but large enough that loading it for one small operation can be wasteful. Start by adding precise task-to-section links and measuring how much agents read. If they repeatedly ingest the whole document, split it into a few cohesive sections such as analysis, optimization, and tolerancing/reporting. Avoid fourteen tiny skills or a deep reference hierarchy.

Put evaluation prompts, rubrics, transcripts, and results at repository level so installers do not expose the test material as normal skill knowledge. Keep runtime example assets under the skill. Store large benchmark outputs as versioned release evidence rather than restoring large generated trees to the main repository.

Add a small shared summary builder and import/metric validation layer where it eliminates the demonstrated inconsistencies. Do not create a new generalized workflow language or replace the existing audited runner. Direct Python should remain easy to adapt, with a small number of deterministic checks at the important boundaries.

### Prioritize useful optical jobs over engine breadth

After the P0 repairs, prioritize these tasks:

1. **File triage and explanation:** what the file contains, what was represented faithfully, whether its first-order values make sense, and which analysis answers the user's question.
2. **Camera and microscope matching:** pixel sampling, magnification conventions, pupil matching, working distance, and the distinction between object and image space.
3. **A bounded improvement:** a visible before/after with explicit requirements and reproducible saved output.
4. **Review and comparison:** compare two designs or measurements under the same metric definitions and sampling.
5. **Buildability:** sensitivity and tolerance studies with explicit perturbation models, compensation, sample count, and uncertainty.

These jobs are accessible to students and useful to professionals. A broader catalog search, sensor-image simulation, glass-cost optimization, or differentiable design integration can follow demonstrated demand. Do not add a GPU dependency to answer questions already solved by the calculators or portable engine.

## Adoption and maintenance

Use the existing installation choices, but present one recommended route per selected client. Keep a separate short distinction between installing a skill, running the optical engine, and enabling licensed native features. A standalone calculator or demo should not require understanding plugin marketplaces.

Make the repository searchable through concrete use cases: lens design, Zemax file analysis, optical simulation, camera sampling, microscopy, and Optiland. Align npm and plugin descriptions with the v2 promise. Add a concise demonstration with actual before/after numbers and one reusable example report. A citation file, clear upstream acknowledgements for adapted forms, and an issue template that requests a synthetic reproduction make participation easier. Verify the provenance and redistribution notices of adapted example data instead of assuming a top-level repository license explains every source.

Participate in existing discovery channels after the journey works. Skills.sh documents installation-based ranking and an available badge; that is evidence of installations through its CLI, not successful optical work or repeat use.[^28] Verify the actual listing before displaying counts, and describe any curated marketplace acceptance only after it occurs. Submit a small worked optics example to relevant communities or upstream documentation when maintainers invite that contribution; do not begin with unsupported superiority claims.

Measure first-use completion, time to a correct result, number of clarification turns, successful update after use, ability to interpret the report, and repeat use on another problem. Downloads, stars, and installs are secondary reach indicators. Start with an opt-in pilot of roughly 8–12 people spanning beginners and practitioners; this is enough to reveal friction, not to estimate population-wide success precisely. Avoid collecting private prescriptions as routine telemetry.

## Suggested delivery sequence

Effort bands describe relative implementation scope, not calendar commitments. “Small” is a focused documentation or localized code change; “medium” crosses component boundaries; “larger” includes optical review, several fixtures, or user evaluation.

| Stage | Changes | Effort | Exit evidence |
|---|---|---|---|
| Correctness patch | F1 report contract; F3 import units/fidelity; F4 metric definitions; F5 gate validity; F6 teaching corrections | Larger overall, separable into focused changes | Recipe-to-report integration passes; non-mm and invalid specs fail correctly; independently defined BFL and aberration examples agree. |
| Lifecycle patch | F2 installed paths, generated caches, output placement, backup lifecycle | Medium | Clean consumer install/use/update/uninstall succeeds without losing user work. |
| First-use release | Three entry prompts, one representative walkthrough, form status labels, accurate native matrix, clearer doctor output | Medium | Beginners complete the documented first result without knowing repository layout; advertised paths are exercised. |
| Evidence release | F7 acceptance/report states; F9 held-out tasks, fixed budgets, repeat runs, versioned artifacts | Larger | Measured benefit and limitations are reported per task and model; failed outcomes remain understandable. |
| Discovery pass | Consistent metadata, short demo, citation/provenance material, verified listings, focused community examples | Small to medium | New users reach the working walkthrough and can report issues with actionable evidence. |

For the first-use pilot, a reasonable **proposed target** is at least 80% unassisted completion of the basic example and correct identification of its main limitation. Record cold and warm timings separately rather than promising a five-minute setup on every machine. For engineering acceptance, require all explicitly declared hard checks to pass; a percentage-based marketing success metric must not weaken that contract.

Do not prioritize a new desktop application, a broad backend abstraction, dozens of additional MCP tools, more separately installed skills, or a much larger form library now. The current release already has enough scope to earn adoption. Its next advantage should be that the documented path works, the numbers mean what they say, and the explanation helps someone make a better optical decision.

## Reproduction record

The following summarizes targeted checks against the public package. It preserves the evidence without committing generated lenses, caches, plots, or temporary environments into the repository.

| Check | Observed result |
|---|---|
| Project-scoped Codex install into a clean consumer directory | Succeeded; installed version 2.0.0. |
| Run `resolve.py airy --wavelength-um 0.55 --fnum 4 --json` using `uv run --python 3.11` | Succeeded; radius 2.684 µm, diameter 5.368 µm; generated `_lib/__pycache__`. |
| Update the otherwise unedited installation | Refused because the managed tree had additional files. |
| Locate the README's repository-relative form path in that consumer project | Absent; installed asset existed beneath `.agents/skills/optical-design`. |
| Execute the published recipe 14 | Produced layout, spot, MTF, and JSON outputs. |
| Validate its JSON against the published renderer | Failed successively for missing engine, scalar first-order rows, and incompatible metric rows. |
| Inspect and compute first-order values for a synthetic `UNIT IN` variant | Inspection warned but still labeled mm; first-order emitted an approximately 50 mm EFL with no warning. |
| Move only the image plane 10 mm in a triplet copy | Reported BFL increased by 10 mm; physical last-vertex-to-paraxial-focus distance remained 42.41549 mm. |
| Gate with only percentage tolerance or a NaN bound/target | Returned pass; boolean bound also accepted. |
| Render a supplied 99 µm metric against a 1 µm maximum with `pass: true` | Rendered and counted as one passing metric; no independent acceptance check. |

Existing CI separately covers Python checks across three operating systems and two Python versions, portable-engine jobs on Windows and Linux, and installer/package jobs across three operating systems. Those checks are valuable, but execution and packaging success do not by themselves validate physical meanings or the consistency between independently tested components.[^29]

## Sources

Public pages and repository metadata below were accessed on 14 September 2026. Local implementation citations pin the audited commit. External living documentation describes the state visible on that date; it is not a promise that the pinned runtime implements every currently documented upstream feature.

[^1]: Eric Tang, [optical-design v2.0.0 source](https://github.com/tangericm/optical-design/tree/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d), especially README, SKILL.md, capabilities, compatibility, and the historical adoption review under `docs/roadmap`.
[^2]: GitHub, repository metadata (`stargazers_count`, `archived`, and `pushed_at`) for each linked repository in the comparison tables, retrieved through the public repository API. Example endpoints: [optical-design](https://api.github.com/repos/tangericm/optical-design), [Superpowers](https://api.github.com/repos/obra/superpowers), and [Optiland](https://api.github.com/repos/optiland/optiland). Counts in the tables preserve the observed snapshot; live endpoints change.
[^3]: Agent Skills, [Specification](https://agentskills.io/specification), especially directory structure, progressive disclosure, and file references.
[^4]: Anthropic, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), especially appropriate degrees of freedom, concision, and model-dependent testing.
[^5]: Jesse Vincent and contributors, [Superpowers README](https://github.com/obra/superpowers), workflow and repository structure.
[^6]: Vercel, [Agent Skills README](https://github.com/vercel-labs/agent-skills), capability descriptions, usage examples, and installation.
[^7]: K-Dense, [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills), quick examples, contribution material, and software/skill citation guidance.
[^8]: Microsoft, [Playwright MCP README](https://github.com/microsoft/playwright-mcp#playwright-mcp-vs-playwright-cli), interface tradeoffs described by the project maintainers.
[^9]: Optiland, [Start Here](https://www.optiland.org/docs/start_here.html), [Conventions](https://www.optiland.org/docs/conventions.html), and [Quickstart](https://www.optiland.org/docs/quickstart.html). These pages displayed a 0.6.2 development-build version, rather than the exact installed 0.6.2 distribution.
[^10]: Michael J. Hayford and contributors, [RayOptics documentation](https://ray-optics.readthedocs.io/en/latest/), overview, paraxial layouts, supported import paths, and examples.
[^11]: DCC-Lab, [RayTracing documentation](https://raytracing.readthedocs.io/en/master/), ABCD approach and stated aberration limitations; includes the project's microscopy tutorial citation.
[^12]: Brandon Dube and contributors, [prysm README](https://github.com/brandondube/prysm), composable numerical optics, propagation, metrology, and optional dependencies. Performance superlatives in that README were not independently benchmarked or adopted here.
[^13]: VCC Imaging, [DeepLens README](https://github.com/vccimaging/DeepLens), computational imaging, agent-scriptable simulation, and the automated-design handoff to AutoLens.
[^14]: MREYE-LUMC, [ZOSPy README](https://github.com/MREYE-LUMC/ZOSPy), API scope, runnable native example, compatibility links, and citation.
[^15]: Eric Tang, [recipe 14](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/references/optiland-recipes.md#L305), [summary validator](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/scripts/_lib/review_render.py#L39), and [recipe execution tests](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/tests/python/test_recipes.py).
[^16]: Eric Tang, [managed installer](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/lib/installer.mjs#L18), exact-tree checks and update backup behavior.
[^17]: Eric Tang, [quickstart](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/docs/quickstart.md#L50) and [README](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/README.md), working-directory instructions, output paths, and starter prompts.
[^18]: Eric Tang, [inspection implementation](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/scripts/inspect_zmx.py), especially directive classification, non-mm warnings, and output unit labels.
[^19]: Eric Tang, [first-order implementation](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/scripts/_lib/first_order.py#L103), metric definitions and gate validation; [evaluation checker](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/evals/check_first_order.py).
[^20]: Optiland, [Paraxial API documentation](https://optiland.readthedocs.io/en/latest/api/paraxial/paraxial.html), reference planes for focal points; [0.6.2 paraxial source](https://github.com/optiland/optiland/blob/v0.6.2/optiland/paraxial.py). Numerical reproduction used the installed 0.6.2 runtime.
[^21]: Eric Tang, [merit-functions reference](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/references/merit-functions.md#L59); Optiland, [0.6.2 operand implementation](https://github.com/optiland/optiland/blob/v0.6.2/optiland/optimization/operand/operand.py), `delta_ineq()` and `fun()`, and [optimization problem](https://github.com/optiland/optiland/blob/v0.6.2/optiland/optimization/problem.py).
[^22]: Eric Tang, [diagnosis example](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/references/diagnosis.md#L12) and [aberration table](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/references/aberrations.md#L63). The parity check follows directly by differentiating the stated wavefront polynomial; Ansys, [Ray Aberration documentation](https://ansyshelp.ansys.com/public/Views/Secured/Zemax/v251/en/OpticStudio_User_Guide/OpticStudio_Help/topics/Ray_Aberration_rays_and_spots.html), describes the ray-fan coordinates and reference.
[^23]: José Sasián, [Theory of sixth-order wave aberrations](https://wp.optics.arizona.edu/jsasian/wp-content/uploads/sites/33/2016/03/published-six-order-theory.pdf), Applied Optics 49(16), 2010, Table 3, Petzval surface term. Compared with the skill's [Petzval section](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/references/aberrations.md#L74).
[^24]: Eric Tang, [SKILL.md workflow](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/SKILL.md#L43) and [optimization recipe](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/references/optiland-recipes.md#L171).
[^25]: Eric Tang, [capabilities](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/docs/capabilities.md), [OpticStudio reference](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/references/opticstudio.md), and the executable Optiland recipes.
[^26]: Eric Tang, [v2 evaluation records](https://github.com/tangericm/optical-design/tree/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/evals/results), scenario summaries and disclosed methodological limitations; [evaluation instructions](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/skills/optical-design/evals/README.md).
[^27]: Anthropic, [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) and [grader instructions](https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/grader.md), baseline comparisons, artifact/transcript grading, and critique of evaluation assertions.
[^28]: Vercel, [Skills documentation](https://www.skills.sh/docs), installation-based ranking, scope of telemetry, and installation-count badge.
[^29]: Eric Tang, [CI workflow](https://github.com/tangericm/optical-design/blob/398beac7a8b2f98f6d1bbeafe9c5c364ccc3431d/.github/workflows/ci.yml), job matrices and validation commands.
