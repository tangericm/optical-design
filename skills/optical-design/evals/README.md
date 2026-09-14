# Evals

`evals.json` holds five scenarios that exercise the skill on real problems: read a
`.zmx` and diagnose it, match a microscope objective to a camera through a relay,
rebalance a scan lens across a wavelength band, run a real optimizer on a triplet, and
tolerance a doublet. Each entry has a `query`, the `assets/forms/` files it needs, and
an `expected_behavior` list of checkable assertions — units stated, wavelength named
for every number, the original file left unmodified, numeric before/after values
rather than qualitative claims. These are not pass/fail unit tests; grade them by
reading the transcript and any files the agent wrote against `expected_behavior`.

## Running a with-skill / without-skill pair

The comparison is the point: run the same `query` twice, once with an agent that has
the optical-design skill installed and once with a bare agent that only has Optiland
(or ZOSPy) and general knowledge, then compare the two transcripts against
`expected_behavior`. In practice: spawn two sessions on the same model and effort
level, give each the identical `query` text from `evals.json` and the same starting
`files`, let both run to completion, then grade independently. `expected_behavior`
describes what the skill should add over the bare agent — an agent with genuine optics
knowledge can pass some assertions without the skill; the skill should raise the pass
rate and the quality of the reasoning shown (named aberrations, stated assumptions,
correct conventions), not just get numbers approximately right.

## Grading with check_first_order.py

`check_first_order.py` is the ground truth for every first-order number an eval asks
for: EFL, BFL, F/#, EPD, total track, per-wavelength EFL (chromatic focal shift), and
the real-ray image-space chief-ray angle at the largest declared field (telecentricity
error). Run it against the same `.zmx`/`.json` the agent was given, and against
whatever file the agent produced, and compare:

```bash
uv run --python 3.11 --with optiland==0.6.2 evals/check_first_order.py \
  assets/forms/cemented-achromat-doublet.zmx
```

It exits 3 with a clear message if Optiland is not installed, 2 on a bad path or
extension, and prints one JSON object to stdout otherwise. Treat any agent-reported
first-order number more than 1% off this script's value as a failed assertion.

## Legacy audited-mode check

`run-portable-workflow.ps1` and `full-workflow.json` predate this eval set and exercise
the older wrapper-based job pipeline (`design.py inspect/optimize/sensitivity/review`
with explicit hashing and acceptance receipts) rather than open-ended agent reasoning.
Keep running it as a regression check on that pipeline — `pwsh -NoProfile -File
evals/run-portable-workflow.ps1 -OutputRoot <new-dir>` — but treat it as the audited,
deterministic-workflow counterpart to `evals.json`, not a replacement for it: it never
asks an agent to name an aberration, choose a tube-lens convention, or explain a
tradeoff, which is exactly what the five scenarios above are for.
