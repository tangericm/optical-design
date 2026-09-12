# Separate validation after optimization

Optimization finds a candidate under the search specification. Optional separate
validation checks the saved winner against additional, predeclared requirements.
Use it for extra existing fields/wavelengths, additional metrics, finer sampling, or
stricter acceptance limits. It does not expand the backend's supported model scope.

```powershell
uv run --with optiland==0.6.2 scripts/design.py optimize --backend optiland --model assets/portable-singlet.json --spec assets/optimization-spec.json --variables assets/variables-example.json --validation-spec assets/validation-spec.json --out checked-optimization --json
```

Run from the installed skill directory, or substitute absolute paths. Native execution
uses `--with zospy==2.1.5 --with pythonnet==3.1.0`, `--backend zos` and the supported
native model. The flag is optional and accepted only for `optimize`. Without it,
existing optimization behavior and budgets are unchanged.

## Specification and execution

The validation file uses the same strict schema as the search specification, with
`fields`, `wavelengths`, `requirements`, optional frequencies, analysis settings and
budget. Omit `objective` and `focus`; they are rejected because this stage performs
no optimization or compensation. Indices must already exist in the unchanged model.
The bundled example repeats the requirements at sampling 256 after searching at 64.

The validation specification is copied and hashed before opening the backend. The
optimizer uses only the search specification for ranking and selecting its winner.
After the winner passes its search-specification save/reload checks, the runner loads
the original baseline for one validation analysis, then reloads the saved candidate
for another. Parameter and fixed-geometry readbacks bracket each analysis. A backend
change to the frozen validation specification invalidates the job.

The baseline validation provides comparison evidence. It may fail requirements while
the candidate passes; only the candidate must meet every validation requirement.
These measurements never feed back into search or select another candidate during
this job. If no improved search winner exists, validation is explicitly not run.

Every analysis counts against the **search specification's total evaluation budget**:
four slots are reserved for two search-specification verification calls and the two
validation calls. The total job timeout continues to apply. The validation budget's
timeout additionally limits its two-call stage; its evaluation cap is also respected
because this stage performs exactly two analyses (the shared schema minimum is seven).
The minimum shared budget of seven permits only two search samples. Use a larger
budget for useful exploration. Cooperative deadlines reject late results but cannot
interrupt a synchronous native call; mandatory restoration is outside those deadlines.

## Outcomes and artifacts

| Result | CLI exit | Acceptance |
|---|---:|---|
| `improved`, validation `passed` | 0 | Search improvement, saved reload and separate requirements all pass |
| `validation_failed`, validation `requirements_not_met` | 1 | Search winner rejected; `candidate` is null and `saved_candidate_verified` is false |
| `no_acceptable_improvement`, validation `not_run_no_candidate` | 1 | No candidate available for validation |
| Analysis, timeout, interruption, restoration or teardown failure | 4 | Failure receipt; no accepted result |

Completed requirement failures retain `rejected_candidate` measurements and a hashed
`rejected-candidate-model.*` artifact. There is no `candidate_model` artifact in that
receipt. Execution failures retain diagnostic files and `failure.json`; any surviving
model is unaccepted regardless of its filename. Missing or incomparable validation
metrics fail requirement assessment.

`report.validation` includes the frozen specification and hash, original/candidate
measurements and assessments, actual validation-call count, and differences in the
declared field/wavelength/frequency/analysis settings. `history` labels the validation
calls separately. MCP returns completed requirement rejection with
`optical_accepted: false`; it independently checks the validation evidence and its
linkage to the original and saved candidate parameter vectors.

## Meaning of validation

This is a **separate-specification numerical acceptance check**. It is not an
independent physical measurement or a guarantee of convergence. Identical settings
remain a repeated numerical check, even if their file or requirement names differ.
Finer sampling alone does not establish convergence. Additional field/wavelength
requirements can expose gaps in what the search objective rewarded.

If the designer repeatedly changes the model or constraints after seeing these
results, the validation conditions become part of design iteration. Do not call
them an untouched holdout, and do not change an acceptance threshold merely to obtain
a pass. Preserve the failed result and define a subsequent authorized design job.

Ansys's singlet tutorial separately evaluates the final optical system after merit
optimization. This project's frozen-specification gate, budgets and quarantine are
implementation policy, not features attributed to that tutorial.
[Ansys: singlet optimization and final evaluation](https://optics.ansys.com/hc/en-us/articles/42661700528275-How-to-design-a-singlet-lens-Part-3-Optimization)
(checked September 12, 2026).
