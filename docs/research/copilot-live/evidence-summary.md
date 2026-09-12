# Optical copilot development evidence — 2026-09-12

The first bounded copilot workflow is implemented: explicit specification → copied model →
baseline audit → constrained refocus → saved/reloaded candidate → tolerance evidence.
It retains the numerical calculators and adds the local catalog/reference layer. This is
a development release, not general autonomous optical design or MecAgent feature parity.

## Live refocus result

Matching synthetic prescriptions: N-BK7 singlet, radii +50/−50 mm, glass thickness 5 mm,
entrance pupil diameter 10 mm, on-axis field, wavelength 0.55 µm, initial image gap 60 mm.
The allowed refocus range was 44–51 mm. Objective: minimum geometric centroid RMS spot;
hard constraints included EFL 48–51 mm, track ≤65 mm, RMS spot ≤30 µm and tangential MTF
at 20 cycles/mm ≥0.3. Sampling setting 128; 25-evaluation cap; 300-second cooperative deadline.

| Metric | OpticStudio baseline | OpticStudio candidate | Optiland baseline | Optiland candidate |
|---|---:|---:|---:|---:|
| EFL (mm) | 49.05139287 | 49.05139287 | 49.05139287 | 49.05139287 |
| Image gap (mm) | 60 | 46.81914251 | 60 | 46.81914251 |
| RMS spot radius (µm) | 989.539913 | 14.814946 | 973.842028 | 14.271819 |
| Tangential MTF, 20 cycles/mm | 0.000476 | 0.460851 | 0.002490 | 0.470689 |

Both jobs used 24 evaluations, passed every declared candidate requirement, preserved the
source hash and fixed prescription invariants, and verified native save/reload. The native
RMS reduction is approximately 98.50%. This demonstration specification is not a user lens
requirement or a production qualification.

Engine sampling differs: native StandardSpot ray density 16 versus Optiland's documented
pupil sampling. These geometric RMS/MTF values are therefore not strict cross-engine
equivalence claims. Separately, matched hexapolar spot sampling in direct adapter checks
agreed at approximately 989.54 µm for the defocused singlet. The first-order EFL matches.

- [Native refocus report](zos-final/report.json), [native review](zos-final/report.md), [candidate](zos-final/candidate-model.zmx).
- [Portable refocus report](optiland-final/report.json), [portable review](optiland-final/report.md), [candidate](optiland-final/candidate-model.json).

## Live tolerance result

Each saved candidate was subjected to 20 seeded independent trials (seed 20260912):
surface 1 radius uniform ±0.05 mm, thickness Gaussian σ=0.01 mm. Six signed sensitivity
trials and one separate nominal analysis accompanied the Monte Carlo samples. No compensator
was applied. Both engines reported 20/20 passing samples, zero analysis failures, verified
parameter readback and baseline restoration. The 95% Wilson interval is **83.887–100%**.
This interval quantifies finite-sample uncertainty under the specified simulation model;
it does not establish production yield.

- [Native raw tolerance evidence](zos-tolerance-final/report.json).
- [Portable raw tolerance evidence](optiland-tolerance-final/report.json).

Source and baseline/candidate artifact hashes in all four reports were checked against the
files after execution. Absolute paths in raw evidence identify the original execution
worktree; that worktree is retained. Adjacent artifacts provide the portable copies.

## Verification and boundaries

- Full default suite: 336 passing tests and 34 optional-engine skips. Optional engine coverage was
  separately executed in the pinned live environments.
- Pinned Optiland suite: 44 live tests; native suite: 10 live tests, including valid CLI JSON
  despite native shutdown output. Additional job/tolerance tests use analytic engine fixtures.
- Seven npm tests, skillcrit (zero errors/warnings), tarball install verification and local
  Markdown link checks pass. Python Ruff and Git whitespace checks pass.
- Independent numerical/import/recovery review findings and behavioral retest:
  [implementation review](implementation-review.md).

The older bundled skill-creator validator rejects the existing `compatibility` frontmatter
key. It was retained because the current [Agent Skills specification](https://agentskills.io/specification)
explicitly supports it; the repository's specification tests and skillcrit pass. No claim is
made that the incompatible auxiliary validator passed.

The engine scope is centered spherical/plane sequential refraction, with explicit restrictions
on fields, apertures and glass lookup. General redesign, compensators, polarization, aspheres,
full ZMX import, GUI integration and manufacturing release remain future work. See the
[shipped workflow](../../../skills/optical-design/references/design-workflow.md).
