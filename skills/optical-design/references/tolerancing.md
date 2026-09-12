# Tolerance evidence

The shipped command is `design.py tolerance`; see [the executable workflow](design-workflow.md).
Its JSON configuration uses `schema: "1"`, explicit integer `seed`, `samples` from 1 to 1000,
and `perturbations`: `{surface, parameter, distribution, half_width_mm}` for uniform draws,
or `{surface, parameter, distribution, sigma_mm}` for Gaussian draws. Supported parameters
are `radius_mm` and `thickness_mm`, indexed as native surfaces excluding object/image.
Sensitivity uses scale factors `[-1, 0, 1]` by default. The implementation uses independent
draws and defaults to **no compensation**. Optional explicit final-air-gap compensation
uses the strict `compensator` object described below; unsupported correlation keys and
other compensator types are rejected.
Every trial restores the baseline and verifies edit readback. Analysis failures count
against the sampled pass fraction. This bounded implementation does not model a complete
manufacturing or alignment process.

## Explicit bounded focus compensation

Add this object to the tolerance JSON, substituting the actual final physical surface
index and absolute permitted image-space air gap in millimeters:

```json
"compensator": {
  "surface": 2,
  "parameter": "thickness_mm",
  "min_mm": 45,
  "max_mm": 50,
  "max_evaluations": 21
}
```

All five fields are required; extra fields are rejected. Bounds must be finite and satisfy
`0 < min_mm < max_mm`; `max_evaluations` is an integer from 3 through 201. The surface must
be immediately before the image, within a supported backend's validated air image space.
The design specification must declare an objective. The compensator must not also appear
among the perturbed parameters. Bounds are absolute gaps, not signed travel relative to
nominal focus. No compensator is inferred from a design specification's `focus` field.

The nominal model, every sensitivity point, and every Monte Carlo draw retain their original
uncompensated measurements, assessment and status. Each row adds `compensated`, containing
the actual search settings, history, candidate attempts, additional analysis calls,
analysis/readback failure count, and best verified feasible result. The search first tries
up to seven evenly spaced positions including both endpoints, then applies bounded golden
interval refinement near the best coarse objective. It retains the best candidate meeting
**all** requirements. A passing uncompensated result within the bounds may seed that best
candidate. One evaluation slot is reserved for independently restoring and reproducing the
best candidate. This is a finite local search and may miss a narrow feasible interval or a
different local optimum. A no-feasible-candidate outcome retains its failed search evidence.

`max_evaluations` limits additional analysis calls **per row**, including final verification;
candidate attempts are also capped at that value, including setter/readback failures.
The global `timeout_s` remains cooperative between engine calls. `report.evaluations` counts
all uncompensated and compensated analysis calls, including calls that raise or exceed the
elapsed-time budget. Configurations with no `compensator` preserve the previous accounting.

Every candidate restores and verifies the native baseline, reapplies the same original
perturbations, and checks the resulting complete inspection against the trial baseline.
Before and after analysis, it verifies focus bounds and readback, all applied perturbations,
and fixed optical invariants. Where the adapter exposes axial positions, only the image
position may shift, by exactly the commanded gap change. Uncompensated analysis must itself
preserve its input inspection. Ignored edits, coupling and invalid analyses are rejected;
baseline-reset failures stop the job. Cleanup restores the nominal baseline even after an
elapsed-time failure, and `failure.json` retains the active partial compensation history.

`report.yield` continues to describe uncompensated draws. `report.paired_yield` adds
`uncompensated`, `compensated`, `recovered`, `lost`, `both_pass` and `both_fail`, using the
same attempted Monte Carlo draws. Each marginal fraction and Wilson 95% interval includes
analysis failures as failures; incomplete draws remain in the active failure evidence and
are not silently counted as completed pairs. Intervals are conditional on the declared
independent perturbation model, engine and bounded adjustment rule. Incomplete runs may
have informative stopping. These are sampled pass fractions, not manufacturing guarantees,
and the two marginal intervals do not constitute a confidence interval for improvement.

Tolerance analysis needs a manufacturing model and compensators. Its performance criterion
can differ from the optimization merit function; compensator choices determine which
errors are adjustable during assembly. Declare the permitted travel and adjustment rule.
[Ansys sequential tolerancing](https://optics.ansys.com/hc/en-us/articles/42661666289043-How-to-perform-a-sequential-tolerance-analysis).

Before a run, record nominal values, perturbation identities and units, distribution and
parameter meaning, truncation, correlations, compensator bounds, random seed, sample count,
acceptance limits and engine settings. Unsupported perturbations must be rejected; they
cannot silently contribute zero sensitivity.

Start with a signed one-at-a-time sensitivity check. Re-evaluate the nominal model after
restoration and inspect asymmetric changes or failures. Sensitivity ranking is local and
does not include interactions unless they are explicitly evaluated. A focus-only experiment
must be described as focus sensitivity, not a general manufacturing-yield analysis.

For Monte Carlo evidence, keep every draw's outcome and compensator result. Report the
number attempted, completed, passing and failed, the denominator used for the pass fraction,
and how execution failures are treated. Never drop unfavorable or failed draws to improve
the reported fraction. Keep source preservation and reproducibility evidence with the result.

Give a confidence interval for a binomial pass proportion when draws support that model.
The Wilson method avoids treating an observed all-pass finite sample as certainty.
It quantifies sampling uncertainty, not uncertainty in an incorrect manufacturing model.
[NIST proportion confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

A diffraction-limited nominal design does not automatically fail tolerancing. The decision
is whether predicted as-built metrics satisfy the actual specification under the declared
tolerance and compensation model. Confirm model realism with measured manufacturing and
assembly data before describing a simulation result as production yield.

Primary links checked 2026-09-12. Run accounting and acceptance rules are project policy.
