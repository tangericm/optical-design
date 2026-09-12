# Optical design review

Outcome: **improved**.

Source: `C:\Users\erict\OneDrive\Desktop\Projects\optical-design-copilot\skills\optical-design\assets\defocused-singlet.zmx`

Source SHA-256: `ec1fb8245314d8373aab2dc81d29b17bfb6c14e2d630a0ddf5bd46ea6d8ccbf7`

Only the final image-space gap may change during refocus. All declared requirements are hard constraints.

## Baseline

Image distance: 60 mm.

| Requirement | Status | Value | Unit |
|---|---|---|---|
| focal-length | pass | 49.05139286997028 | mm |
| track | pass | 65.0 | mm |
| contrast | fail | 0.00047605320821753137 | 1 |
| spot | fail | 989.5399128858029 | um |

## Candidate

Image distance: 46.819143 mm.

| Requirement | Status | Value | Unit |
|---|---|---|---|
| focal-length | pass | 49.05139286997028 | mm |
| track | pass | 51.81914 | mm |
| contrast | pass | 0.46085078939858726 | 1 |
| spot | pass | 14.814946459697966 | um |

## Evidence

Evaluations: 24. Source unchanged: True.

Full metrics, analysis settings, engine version, search history, and artifact hashes are in report.json.

The time budget is checked between native analysis calls. A blocking engine call can exceed it.

Refocus searches one bounded gap; it does not perform a general lens redesign or certify manufacturing yield.
