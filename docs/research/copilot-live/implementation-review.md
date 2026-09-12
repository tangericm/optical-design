# Implementation review and behavioral evaluation

## Corrections driven by reproduced failures

The original audit reproductions cover displaced/annular pupil scale, false equivalence
with disjoint metrics, invalid physical inputs and an overbroad Maréchal diagnostic.
Regression tests now enforce explicit pupil geometry, matched-pupil MTF, finite physical
arguments, strict coverage/units/identity and explicit interferometric quantity conversion.

Independent implementation reviews found and verified corrections for:

| Finding | Resolution and regression evidence |
|---|---|
| Saved candidate could lose tiny gain or leave focus bounds within reload tolerance | Recheck minimum gain and allowed gap after reload; design job tests |
| Setup or teardown failure lacked a failed receipt | Failure artifacts and success invalidation; disk/close-failure fixtures |
| Unknown nested requirement keys were silently ignored | Reject unknown keys; typo and boolean-index regressions |
| Nearby MTF frequencies collided after six-digit formatting | Round-trip numeric identity; close-frequency regression |
| JSON-native baseline model collided with analysis evidence | Separate `baseline-model.*` artifact name; imported-extension regression |
| Negative glass thickness or Standard-surface tilt escaped native scope guard | Positive glass gaps and explicit transform/aperture guards |
| Portable ZMX ingestion metadata changed after JSON reload | Retain original ingestion identity; live audit/tolerance reload regressions |
| Portable import accepted but dropped `DIAM` clear aperture | Reject unsupported aperture directive before conversion |
| Catalog material lookup could choose an approximate glass | Require exact catalog/name; verify index at every active wavelength |
| Tolerance setter could report edits that never happened | Verify all parameter readbacks after all setters; no-op/coupled setter regressions |
| Tolerance load could silently fail to restore between trials | Compare restored optical inspection before each trial |
| OpticStudio shutdown text corrupted CLI JSON | Owned native worker with result-file payload; native live CLI JSON test |
| Native process could crash after writing a success payload | Require consistent exit/result; suppress success and invalidate matching receipt; crash fixture |
| Malformed native payload escaped CLI error handling | Return analysis-failure status; truncated JSON fixture |

The direct adapter interfaces and the CLI worker have different ownership layers: engine
adapters own native systems, while the CLI waits for process shutdown before accepting its
payload. Deadlines remain cooperative between engine calls.

## Skill instruction evaluation

An independent evaluator read the old entrypoint before its replacement, then repeated the
same requests with the revised skill and relevant references:

| Scenario | Old instruction-driven decision | Revised decision |
|---|---|---|
| Pure defocus RMS 0.1 waves, FFT Strehl 0.66255 | Wrong scheme/normalization inferred from truncated Maréchal disagreement | Approximation alone does not diagnose convention; check exact defocus/convergence |
| Annular pupil MTF above clear-circle reference | Flag as a violated universal MTF bound | Compare the same pupil amplitude/support with phase removed |
| Authorized 44–51 mm refocus of supplied model/spec | No runnable prescription workflow advertised | Execute bounded copied-model refocus and verify saved/reloaded constraints/gain |
| 20/20 Monte Carlo samples pass | Not exercised in old capability set | Report sampled fraction and 83.89–100% Wilson interval, not certified yield |

These are focused behavioral checks, not a broad agent benchmark. Numerical/backend tests
exercise the underlying operations independently of the instruction wording.

## Verification record

Verified: 336 default Python tests pass (34 optional skips); 44 portable backend tests and
10 native tests pass in their pinned environments; seven npm tests, Ruff, skillcrit and
local-link checks pass. Tarball install verification passes after line-ending normalization. The original main
checkout also passes 336 tests and tarball install verification after local integration.
No remote publication or registry release is part of this change. The version is 0.1.0-dev.1.
