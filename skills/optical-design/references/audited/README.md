# Audited mode

The audited mode is the original job runner: `scripts/design.py`, `scripts/review.py`,
`scripts/server.py` (MCP), `scripts/zos.py` and `scripts/benchmark.py`. Use it when a team
needs a hash-verified receipt for a bounded change to a saved prescription: every job works
on a copy, records source and artifact hashes, re-measures the saved candidate after reload,
and refuses to accept a change that fails a declared requirement.

It is deliberately narrow. Portable jobs handle centered spherical and plane systems;
native OpticStudio jobs add fixed conics and even aspheres. Variables are radius and
thickness only, at most four for `optimize`. Metrics are EFL, F-number, total track, image
distance, RMS spot radius and FFT MTF at one frequency. For everything else, write Optiland
code from the [recipes](../optiland-recipes.md) and follow the discipline in `SKILL.md`.

| Page | Covers |
|---|---|
| [design-workflow](design-workflow.md) | Commands, output files, specification contract, adapter boundaries |
| [model-actions](model-actions.md) | `inspect` and expected-value `edit` |
| [optimization](optimization.md) | Bounded `refocus` and `optimize`, acceptance rules |
| [sensitivity](sensitivity.md) | Central-difference sensitivity at declared steps |
| [validation](validation.md) | Predeclared validation of the search winner |
| [review-reports](review-reports.md) | Receipt rendering with `review.py` |
| [interactive](interactive.md) | The MCP job server |
| [specifications](specifications.md) | Requirement lists and the local catalog matcher |
| [field-validation-example](field-validation-example.md) | Three-field, three-wavelength worked example |
| [profile-benchmark](profile-benchmark.md) | Native Huygens and POP intensity-profile reproduction |

The composite merit contract shared with these jobs is in
[merit-functions](../merit-functions.md#audited-mode-composite-merit-designpy).
