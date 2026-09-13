# Bring a real prescription

[Documentation](README.md) / Professional workflow

Use this route when you have a saved lens and engineering requirements. Start with
[supported model types](capabilities.md) and [tested engine versions](compatibility.md).
Native jobs own a standalone OpticStudio session; save GUI edits before providing a model.

## Establish the baseline

Inspect the saved prescription first. Confirm surface inventory, units, angle fields,
wavelengths, entrance-pupil diameter, material behavior, and fixed conic/asphere terms.
Retain the model hash and an unmodified source.

> Use optical-design to inspect [model path]. Check backend support, then report the
> prescription, units, field/wavelength definitions, and fixed parameters. Identify
> unsupported assumptions before computing performance or proposing changes.

## Freeze the problem

Declare hard requirements and analysis sampling. For composite merit, specify targets,
scales, and weights with explicit metric identities. Declare variables and bounds;
optimization supports up to four radius/thickness variables. Freeze extra validation
conditions before selecting the winning candidate.

[Specification contract](../skills/optical-design/references/design-workflow.md#specification-contract) ·
[Composite merit](../skills/optical-design/references/merit-functions.md) ·
[Optimization](../skills/optical-design/references/optimization.md)

## Change, verify, and assess robustness

Use expected-value edits or bounded optimization. Accept a changed model only when
the report's requirements and saved/reloaded candidate checks support acceptance.
Check extra fields/wavelengths or finer sampling using the frozen validation specification.

Sensitivity is local to its declared steps. Tolerance outcomes are conditional on the
chosen distributions, sample count, seed, and compensator; report those with the yield.

[Controlled edits](../skills/optical-design/references/model-actions.md) ·
[Separate validation](../skills/optical-design/references/validation.md) ·
[Sensitivity](../skills/optical-design/references/sensitivity.md) ·
[Tolerancing](../skills/optical-design/references/tolerancing.md)

## Hand off the evidence

Create an [offline review package](../skills/optical-design/references/review-reports.md)
and retain the job directory. Review metric identities, failed or unavailable conditions,
parameter changes, and model lineage. File hashes check artifact identity; they are not
independent optical verification or a signature of authenticity.

For native Huygens/POP intensity profiles, use the separate
[profile benchmark](../skills/optical-design/references/profile-benchmark.md).
Illumination cuts and point-image PSFs answer different questions. The
[compatibility record](compatibility.md) keeps unresolved method differences visible.
