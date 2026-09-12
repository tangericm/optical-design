# Local integration receipt

The main optical-design checkout was fast-forwarded from `d130e92` through implementation
`e2a0be5` and evidence commit `07e73ba` on September 12, 2026.

- Final native/code evidence review found no release blockers.
- Integrated benchmark/adapter/worker/profile code hashes match `final-verification.json`.
- All 96 retained JSON evidence files are byte-identical to the benchmark worktree.
- The external Line-Field-OCT-Optics repository remains clean; declared source and native
  dependency hashes match the completed calculations.
- The main checkout's pre-existing untracked `docs/research/audit-2026-09-12/` is preserved.
- The benchmark worktree is retained because immutable receipts point to its owned copies
  and raw artifacts. Real prescription copies are ignored and excluded from distribution.

No remote push or package publication was performed. The local development version is
0.1.0-dev.2. See [evidence summary](evidence-summary.md) for results and physical limits.
