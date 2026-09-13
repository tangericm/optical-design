# Installed workflow evaluation

Run these scenarios against the installed skill directory. They are evaluation inputs
and executable acceptance checks, not claims that a particular release, engine or client
has passed. Preserve generated output directories to keep artifact paths reproducible.

`full-workflow.json` contains two prompts and observable grading criteria. Give one prompt
at a time to the engineering agent, along with the installed skill path and a new output
root. Grade evidence produced by tools; prose claims without receipts do not satisfy a
criterion. Record the model/effort, installed revision, engine versions, exact inputs,
outputs and unmet criteria with each run. Do not replace numeric results with expected
values from this document.

## Portable executable check

From the installed skill directory, with PowerShell 7 and `uv` available:

```powershell
pwsh -NoProfile -File evals/run-portable-workflow.ps1 -OutputRoot C:/Optical/evals/new-workflow
```

The runner uses Python 3.11 and Optiland 0.6.2, copies no secrets, and launches no native
engine. It exercises inspect → expected-value edit with composite merit → sensitivity →
separate original/candidate audits → review. It also checks stale expected values, an
invalid sensitivity step, missing action configuration and an intentionally rejected edit.
Every CLI call retains stdout/stderr separately. The runner emits one JSON summary only
after its assertions pass; failure throws and leaves existing evidence intact. A failed
original audit is expected and retained; the edited candidate must pass the supplied
synthetic requirements and its separate audit for this scenario to pass.

The script is a deterministic workflow check. The agent prompt additionally evaluates
whether the agent interprets the optical evidence and limitations correctly. Neither
constitutes independent physical validation or a native-engine test.

## MCP full-field check

Launch the server using the pinned commands in [interactive.md](../references/interactive.md),
with this installed skill's `assets` directory under a declared input root. Use a new
workspace. Apply the second JSON prompt through the actual installed MCP client.

1. Hash model/spec/variables/validation bytes immediately before `start`. Inspect first
   without spec fields, then start optimization with all matching path/hash pairs.
2. Wait through `status`, then obtain `results`. Record the final state and acceptance,
   and every failing field/wavelength/axis. Do not require optimization to succeed as the
   evaluation's expected outcome; require the agent to preserve the actual outcome.
3. Call `review` with the returned job ID. Verify the rendered package agrees with the
   receipt and remains unaccepted when validation fails.
4. Submit a separate start request with an intentionally wrong 64-digit model hash.
   Require rejection before job creation. Keep the source model bytes unchanged.

For a native adaptation, an operator must launch the pinned licensed Windows server and
use the corresponding `assets/field-validation/native.zmx`. Run serially. Native conic
and EvenAspheric shape coverage requires its own saved prescriptions and shape invariants;
the spherical fixture here does not establish that coverage. Never infer native success
from this portable scenario.
