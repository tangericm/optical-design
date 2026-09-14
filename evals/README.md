# Evaluating optical-design

Evaluation materials live at repository level and are excluded from installed skills
and npm artifacts. They are for a grader, not runtime instructions for the agent.

## Development tasks and held-out evaluation

`evals.json` contains eleven public development scenarios: five optical tasks and six
beginner, missing-input, import, native-capability, failed-requirement and lifecycle cases.
Supply only the query and required files to a run. Asset paths are relative to
`skills/optical-design`; copy them into the agent's project without changing their bytes.
The non-mm scenario specifies a synthetic fixture that the grader prepares first.

A public scenario is not a secret holdout. For release comparisons, prepare additional
unpublished input prescriptions and assertions before running either condition. Keep
rubrics, this directory, expected values and previous results inaccessible to the agent
through its filesystem, tools and browser. Merely moving a file does not enforce that
boundary: configure the execution sandbox or evaluation harness accordingly.

## Paired-run protocol

1. Freeze the query, input hashes, field/wavelength definitions, assertions, numeric
   tolerances, solver budget and wall limit before either run. Choose a seed where
   applicable. Do not intervene mid-run to change budgets or make a task easier.
2. Run the same exact model and reasoning setting with the installed skill and without
   it. Both conditions receive the same optical engine, inputs, tools and cache state.
   The without-skill condition must not read the skill's scripts or references.
3. Use the budgets in each scenario. Optimization queries separately cap optimizer work;
   overall wall limits include agent reasoning. Log downloads separately from warm work.
   Repeat each high-value scenario at least three times; alternate condition order.
4. Record exact provider/model identifier, host version, skill commit, package version,
   Python and engine distribution versions, seed, timing, tokens when available,
   termination reason and artifacts using `run-record-template.json`.
5. Give anonymized transcripts and output artifacts to an independent grader. Check
   numerical assertions against compatible definitions, not prose confidence. Record
   pass/fail/partial plus the supporting artifact for each assertion.
6. Compare per-task correctness, missed requirements, source preservation, time to a
   useful result and report interpretability. Report variance and failures. A budget
   limit is not convergence; a rendered review is not optical acceptance.

Before claiming cross-model benefits, run the protocol with an economical model and a
more capable model. The expensive comparison belongs at release checkpoints; unit,
integration and package lifecycle regressions should run in CI. A small opt-in pilot
with beginners and practitioners can assess comprehension, but has not been conducted
by these automated checks.

## Reference values

From the repository root:

```sh
uv run --python 3.11 --with optiland==0.6.2 evals/check_first_order.py skills/optical-design/assets/forms/cemented-achromat-doublet.zmx
```

The checker uses the same Optiland engine, so agreement is not independent physical
validation. Back focal length comes from a parallel-ray intersection measured from the
last optical vertex; image distance is reported separately. Its regression test anchors
this against the thick-lens power formula on a defocused singlet. Use validated mm
inputs. Assess unsupported import features before comparing numerical outputs.

Compare EFL, back focal length and pupil quantities with stated relative tolerances.
For angles near zero, use an absolute tolerance (the public tasks allow 0.001 degree)
instead of dividing by a vanishing value. The checker reports a real-ray chief-ray angle;
the skill's paraxial angle must not be graded as if it were the identical quantity.
EFL spread across wavelength and best-focus spread are distinct measures.

## Historical results

`results/` retains the original five paired v2.0.0 summaries unchanged. They disclose
rubric exposure, mid-run optimization caps and lack of convergence in two scenarios.
Their BFL convention was the final air gap; do not reuse those values as corrected BFL
ground truth. The reported 30/30 versus 26/30 assertions and timing differences are
preliminary observations, not a current general performance guarantee.

No new multi-model benchmark or participant study is implied by this protocol.

## Audited workflow regression

The deterministic job-runner exercise is separate from agent reasoning evaluation:

```powershell
pwsh -NoProfile -File evals/run-portable-workflow.ps1 -OutputRoot <new-absolute-directory>
```

The default skill root is the repository's `skills/optical-design`. Pass `-SkillRoot`
to test an installed copy instead. Keep output outside both the skill and this directory.
This checks receipts, requirements and saved-candidate lineage; it does not grade
diagnosis or teaching quality.
