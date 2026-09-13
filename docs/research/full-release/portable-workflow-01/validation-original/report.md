# Optical design review

Outcome: **requirements_not_met**.

Source: `C:\Users\erict\OneDrive\Desktop\Projects\optical-design-v1\skills\optical-design\assets\portable-singlet.json`

Source SHA-256: `73d813dea1ad75db10d87d5023b3608740c652a6ccc38b999eec38599aa803ca`

Only the final image-space gap may change during refocus. All declared requirements are hard constraints.

## Baseline

Image distance: 60 mm.

| Requirement | Status | Value | Unit |
|---|---|---|---|
| focal-length | pass | 49.05139286997028 | mm |
| track | pass | 65.0 | mm |
| contrast | fail | 0.0013321355840192194 | 1 |
| spot | fail | 965.7974573583507 | um |

## Evidence

Evaluations: 1. Source unchanged: True.

Full metrics, analysis settings, engine version, search history, and artifact hashes are in report.json.

The time budget is checked between native analysis calls. A blocking engine call can exceed it.

Refocus searches one bounded gap; it does not perform a general lens redesign or certify manufacturing yield.
