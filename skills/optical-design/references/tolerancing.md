# Tolerance evidence

The shipped command is `design.py tolerance`; see [the executable workflow](design-workflow.md).
Its JSON configuration uses `schema: "1"`, explicit integer `seed`, `samples` from 1 to 1000,
and `perturbations`: `{surface, parameter, distribution, half_width_mm}` for uniform draws,
or `{surface, parameter, distribution, sigma_mm}` for Gaussian draws. Supported parameters
are `radius_mm` and `thickness_mm`, indexed as native surfaces excluding object/image.
Sensitivity uses scale factors `[-1, 0, 1]` by default. The implementation uses independent
draws and **no compensators**; unsupported correlation/compensation keys are rejected.
Every trial restores the baseline and verifies edit readback. Analysis failures count
against the sampled pass fraction. This bounded implementation does not model a complete
manufacturing or alignment process.

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
