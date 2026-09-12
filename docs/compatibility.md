# Compatibility

Development evidence recorded September 12, 2026.

| Surface | Evidence | Boundary |
|---|---|---|
| Windows, Python 3.11 | Full pytest suite, CLI examples, npm package checks | Other configured CI platforms were not rerun locally |
| OpticStudio 2024 R1, API 24.1.0, Premium | Fresh standalone connection; real audit/refocus/tolerance; saved-model reload and source hashes | No live GUI attachment or broad prescription coverage |
| ZOSPy 2.1.5 / pythonnet 3.1.0 | Installed API calls exercised | Different suite/API versions need validation |
| Native profile benchmark | 75 Huygens/POP cases across three real OCT models; 135 profiles; two final-CLI smoke cases | Same-method reproduction, not independent physical acceptance or unrestricted model coverage |
| Optiland 0.6.2 | Native JSON, restricted ZMX regression fixtures, real audit/refocus/tolerance | Full OpticStudio exports can be rejected; import is deliberately narrow |
| Agent skill entrypoint | Independent before/after behavioral scenarios for defocus, annular MTF, refocus and yield | Not an autonomous-design benchmark |
| npm tarball | Local pack/install verification | No registry publication in this development change |

The synthetic N-BK7 singlets are independently constructed from matching prescriptions.
Shared first-order and geometric spot checks are evidence; FFT MTF uses different pupil
sampling implementations. Numerical results from the current run are in the local
`docs/research/copilot-live/` evidence directory, which is excluded from distribution.

Any Agent Skills client can read the portable frontmatter. End-to-end installations in
every named client have not been tested. Pin the adapter versions and rerun capability
checks when moving to another machine.

The 0.1.0-dev.2 profile workflow retains reference comparisons, native setting readback,
source/dependency hashes and raw profiles in local `docs/research/real-benchmark/` evidence.
Its Stock model still shows about 22% disagreement between Huygens and POP X full 1/e²
widths. The benchmark preserves that discrepancy. It does not relax the original spherical
optimization adapter or declare the design physically validated. The final software check
record is 451 Python tests passed (34 optional tests skipped), seven package tests passed,
and successful lint/package-install checks.
