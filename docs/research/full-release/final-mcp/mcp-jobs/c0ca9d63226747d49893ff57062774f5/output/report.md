# Optical design review

Outcome: **improved**.

Source: `C:\Users\erict\OneDrive\Desktop\Projects\optical-design-v1\docs\research\full-release\final-mcp\mcp-jobs\c0ca9d63226747d49893ff57062774f5\inputs\model.json`

Source SHA-256: `73d813dea1ad75db10d87d5023b3608740c652a6ccc38b999eec38599aa803ca`

Only the final image-space gap may change during refocus. All declared requirements are hard constraints.

## Baseline

Image distance: 60 mm.

| Requirement | Status | Value | Unit |
|---|---|---|---|
| focal-length | pass | 49.05139286997028 | mm |
| track | pass | 65.0 | mm |
| contrast | fail | 0.002489848452484078 | 1 |
| spot | fail | 973.842027568571 | um |

## Candidate

Image distance: 46.819143 mm.

| Requirement | Status | Value | Unit |
|---|---|---|---|
| focal-length | pass | 49.05139286997028 | mm |
| track | pass | 51.8191425091652 | mm |
| contrast | pass | 0.4706893577206028 | 1 |
| spot | pass | 14.271818695450222 | um |

## Evidence

Evaluations: 24. Source unchanged: True.

Full metrics, analysis settings, engine version, search history, and artifact hashes are in report.json.

The time budget is checked between native analysis calls. A blocking engine call can exceed it.

Refocus searches one bounded gap; it does not perform a general lens redesign or certify manufacturing yield.
