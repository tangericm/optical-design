# Bounded optimization and refocus

An optimizer improves its specified merit function. A local minimum is not a proof of
global optimality or compliance with requirements absent from that function. OpticStudio's
sequential tutorial demonstrates choosing variables, building a merit function and then
evaluating the resulting system.
[Ansys singlet optimization](https://optics.ansys.com/hc/en-us/articles/42661700528275-How-to-design-a-singlet-lens-Part-3-Optimization).

Use this project's conservative sequence:

1. Preserve the original model. Snapshot prescription, fields, wavelengths, apertures,
   materials, configurations and analysis settings; hash the source and specification.
2. Evaluate the unchanged baseline. Stop if required metrics are unavailable or the
   selected backend cannot represent the model.
3. Declare one objective, its direction, minimum useful gain and all hard constraints.
   Give every adjustable variable a physical interval and set an evaluation/time budget.
4. Start with bounded focus travel when appropriate. A focus adjustment must not silently
   change conjugates, field definitions, aperture, wavelength weights or required magnification.
5. Compare candidate and baseline with identical settings. Check hard constraints
   independently of the aggregate score; include all specified fields and wavelengths.
6. Save the best valid candidate separately, reload it and re-evaluate. Report budget
   exhaustion, restoration failures and no-improvement outcomes explicitly.

These are workflow requirements, not a guarantee that every backend supports each operation.
Inspect the runtime capability result and the saved job evidence before claiming execution.
Do not reuse historical connectivity as proof of a current licensed session.

Distinguish equivalence from improvement. A favorable large change can fail an equivalence
test; conversely, numerical agreement with a baseline does not prove a useful improvement.
Use independent validation metrics or held-out field/wavelength samples where the model
supports them, and compare the observed gain with numerical convergence variation.

After nominal improvement, run the declared manufacturing/assembly model rather than
assuming nominal merit-function gain establishes yield. See [tolerance evidence](tolerancing.md).

Primary link checked 2026-09-12. The bounded search and acceptance rules are project policy.
