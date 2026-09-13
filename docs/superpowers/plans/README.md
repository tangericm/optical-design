# Optical-design implementation roadmap

The initial six-phase spec remains design history. The audited implementation consolidated
those phases into executable copilot releases; the table below is the current status.

| Plan | Delivered scope | Status |
|---|---|---|
| `2026-09-12-plan-1-scaffold-tier0.md` | Numerical scripts and package scaffold | Complete |
| `2026-09-12-copilot-sequence.md` | Scientific corrections, core references, copied-model audit/refocus, portable/native adapters, catalog shortlist and seeded tolerancing | Complete, 0.1.0-dev.1 |
| Real-design benchmark (`docs/research/real-benchmark/`) | Native Huygens/POP reproduction on three OCT models, preserved discrepancy and evidence | Complete, 0.1.0-dev.2 |
| `2026-09-12-remaining-roadmap.md` | Explicit multivariable optimization, focus compensation, local MCP jobs and controlled optical experiments | Complete, 0.1.0-dev.3 |
| Separate validation continuation (`docs/research/validation-release/`) | Frozen requirements after optimization, baseline/candidate checks, rejected model artifacts and CLI/MCP acceptance evidence | Complete, 0.1.0-dev.4 |
| Field/spectral validation (`docs/research/field-validation/`) | Native monochromatic RMS correction, single-wavelength oracle, shipped 3×3 example and fixed-limit rejection on both engines | Complete, 0.1.0-dev.5 |

The broad original `trace.py`/`zos.py` command proposals are implemented through the narrower
validated `design.py` backend contract where supported. A generic merit editor, topology and
glass optimization, decenter/tilt or thermal tolerancing, arbitrary imported prescriptions,
live editor attachment, production manufacturing release, and MecAgent feature parity have
not been established. The package remains a development release; no remote publication is
part of this plan. New capability claims require actual engine and acceptance evidence.
