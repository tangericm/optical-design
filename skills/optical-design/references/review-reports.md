# Offline design-review packages

Create a standalone review from a recorded sequential-imaging job:

```powershell
uv run scripts/review.py --report C:/work/design-job/report.json --out C:/work/design-review --json
```

The output directory must be new. Exit 0 means the review was rendered, including when
the recorded optical outcome failed requirements. Exit 4 means the input or output was
invalid or inaccessible. `--json` prints the manifest; without it, the CLI prints the
HTML location and recorded outcome. No optical engine, browser, network access, or
third-party Python dependency is needed.

Python API: `_lib.review_report.render_review(report_path, out) -> dict`. It returns
the same manifest written to disk. Outputs are:

- `report.html`: standalone, responsive review with measurement tables, recorded MTF
  and RMS spot samples, labeled axial schematic, and expandable structured evidence.
- `report.md`: readable Markdown with exact values and structured evidence.
- `manifest.json`: input receipt SHA-256, verified local artifact hashes, recorded
  action/status, candidate acceptance flag, and SHA-256/byte counts for both reports.

`validate_review_receipt(report_path) -> dict` performs the same receipt validation
without writing output. It returns `action`, `status`, `accepted_candidate`,
`receipt_sha256`, and `verified_local_artifacts`. Job ownership and original process
exit/stdout checks remain the responsibility of the caller.

Identical receipt and artifact bytes produce identical output bytes in any new output
directory. No timestamp, random identifier, remote asset, or JavaScript is injected.
All untrusted content is escaped, including Markdown markup and HTML attributes.

## Accepted receipts and evidence checks

Schema 1 reports support `audit`, `refocus`, `optimize`, `tolerance`, `sensitivity`,
`inspect`, and `edit`. Source preservation and baseline restoration must be recorded
for completed reports. The renderer checks baseline/candidate/rejected artifact hashes,
source-snapshot identity where supplied, specification/configuration snapshots, metric
identities, duplicate measurements, recomputed requirement assessments and claimed
objective evidence. Separate validation is reassessed using its own specification and
bound to the matching parameter vector. Sensitivity derivatives and within-metric
rankings are recomputed from the declared symmetric trial pair.

Artifact paths must resolve inside the receipt's directory. Traversal, remote paths,
alternate data streams, escaping symlinks, and mismatched hashes are rejected. Paths in
`source` are displayed only: the renderer never reopens the original source file. Keep
recorded artifact paths valid when moving receipts; relative paths inside the receipt
directory are supported. A manifest verifies local bytes and internal consistency;
it is not an authenticated signature, independent ray-trace verification, or proof
that the original optical engine behaved correctly.

`improved` and `applied` require a saved, verified, passing candidate. Rejected edits
and independent-validation failures retain their rejection status and cannot appear
as an accepted candidate. Audits retain failed and unavailable requirements. Inspection
needs no invented specification. Sensitivity/tolerance completion implies no accepted
changed model. Missing physical coordinates, metrics, validation, or prescription
data are labeled unavailable or not recorded.

For interrupted jobs, pass `failure.json` to render a diagnostic review. Legacy minimal
failure receipts are supported. A successful `report.json` alongside `failure.json` is
rejected, since a later teardown failure can invalidate apparent success. Diagnostic
reviews preserve failure text and never claim accepted optical performance. Where a
failure receipt includes artifacts or assessments, supplied evidence still must be
internally consistent. Failures before a usable receipt exists cannot be rendered.

## Visual and scientific limits

Charts plot only recorded MTF or RMS spot metric samples, with exact identities and
values in adjacent tables. Field indices remain discrete selections, not physical
distances. Physical coordinates and wavelengths come from recorded analysis/settings
or the model inventory. No fabricated spot-intercept diagram, fitted MTF curve, or
unmeasured spectral/field coverage is implied.

The axial schematic places surface vertices at recorded axial positions, or accumulates
recorded thicknesses relative to the first real surface. Its label states the coordinate
convention. It does not draw lens sag, clear aperture, traced rays, or aspheric profiles.
The prescription diff and inventory retain recorded radii, thicknesses, conics, and
asphere coefficients as data. Missing axial positions/thicknesses suppress the schematic.

Local sensitivity is not manufacturing yield. Tolerance yield is reported only from
the recorded tolerance job. No review certifies a global optimization result, removes
a failed requirement, or resolves disagreement between physical analysis methods.

For other offline acceptance boundaries, `validate_sensitivity_evidence(report, spec)`
recomputes sensitivity and rankings only; callers must separately validate snapshots,
hashes, recorded assessments, action/status, and job ownership.
