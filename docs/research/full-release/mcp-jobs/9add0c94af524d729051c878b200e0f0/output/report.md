# Optical design review

Outcome: **improved**.

Source: `C:\Users\erict\OneDrive\Desktop\Projects\optical-design-v1\docs\research\full-release\mcp-jobs\9add0c94af524d729051c878b200e0f0\inputs\model.zmx`

Source SHA-256: `4fe32615eac8c57b2d80c6745c99f0e3235f7586a2917e62dffe0aba2b9f7cf8`

Only the final image-space gap may change during refocus. All declared requirements are hard constraints.

## Baseline

Image distance: 60 mm.

| Requirement | Status | Value | Unit |
|---|---|---|---|
| focal-length | pass | 49.05139286997028 | mm |
| track | pass | 65.0 | mm |
| contrast | fail | 0.00040010977242531186 | 1 |
| spot | fail | 993.4228136201618 | um |

## Candidate

Image distance: 46.769475 mm.

| Requirement | Status | Value | Unit |
|---|---|---|---|
| focal-length | pass | 49.05139286997028 | mm |
| track | pass | 51.76947 | mm |
| contrast | pass | 0.3985805096694023 | 1 |
| spot | pass | 15.841366208313875 | um |

## Evidence

Evaluations: 24. Source unchanged: True.

Full metrics, analysis settings, engine version, search history, and artifact hashes are in report.json.

The time budget is checked between native analysis calls. A blocking engine call can exceed it.

Refocus searches one bounded gap; it does not perform a general lens redesign or certify manufacturing yield.
