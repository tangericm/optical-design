# Specifications and catalog starting points

Write the acceptance contract before evaluating or changing a model. Record object and
image conjugates; field coordinates and units; wavelengths and weights; aperture/stop;
medium; detector pitch; focus position; and the exact metric and threshold at each field
and wavelength. Distinguish image-space from object-space quantities. OpticStudio's
sequential setup explicitly defines aperture, field and wavelengths; these choices are
part of the optical problem, not interchangeable display settings.
[Ansys sequential setup](https://optics.ansys.com/hc/en-us/articles/42661252179987-How-to-design-a-singlet-lens-Part-1-Setup).

For this copilot, use three separate lists: required limits, allowed variables with bounds,
and quantities held fixed. A missing required result means unverified. An improvement
objective needs direction and minimum useful gain; equivalence uses an absolute/relative
tolerance. Record the analysis settings and source/specification hashes with each result.

Zernike input additionally requires scheme, coefficient units, wavelength, normalization
circle and removed terms. Standard coefficients are RMS-normalized on their specified
pupil; do not apply full-disk orthogonality assumptions to an arbitrary measurement mask.
[Ansys Standard coefficients](https://ansyshelp.ansys.com/public/Views/Secured/Zemax/v26103/en/OpticStudio_User_Guide/OpticStudio_Help/topics/Zernike_Standard_Coefficients.html).

## Local catalog workflow

`catalog.py` validates declared metadata and filters explicit numeric constraints. It
does not fetch catalogs, verify availability, import prescriptions or predict performance.
Every entry requires `vendor`, `part`, `source`, `retrieved_on` (`YYYY-MM-DD`), `model`
(a declared model identity), and nonempty `properties`. Properties have `value` and `unit`.
The index root is `{"schema":1,"entries":[...]}`. Unknown keys, duplicate vendor/part
identities and nonfinite values are errors. `assets/catalog-example.json` is synthetic;
neither record describes a commercial part or a usable prescription.

Save this query as `query.json`:

```json
{
  "schema": 1,
  "constraints": [
    {"property":"efl","unit":"mm","min":24,"max":26,"target":25,"scale":1},
    {"property":"clear_aperture","unit":"mm","min":10}
  ]
}
```

From the skill directory:

```powershell
uv run scripts/catalog.py validate --index assets/catalog-example.json --json
uv run scripts/catalog.py match --index assets/catalog-example.json --query query.json --json
```

Each constraint requires an inclusive `min` or `max`. Optional `target` must satisfy
the bounds and requires positive `scale`; optional `weight` defaults to one. Scale uses
the constraint's unit. Supported units: `m`, `cm`, `mm`, `um`, `nm`, `rad`, `deg`, `1`.
Only dimensionally compatible units convert. Missing or incompatible properties reject
that entry. Score is the weighted mean of `abs(value-target)/scale` over targeted
properties. Lower scores rank first; ties sort by vendor then part. Without targets,
all passing entries score zero. `--limit` defaults to ten; `total_matches` reports the
untruncated count. `no_matches` is a result, never proof that a suitable part does not exist.

Inspect the retained source/date/model identities and exact index/query hashes. Independently
verify a chosen prescription, material catalog, coating band, units and allowed use before
analyzing it at the actual conjugates. Catalog proximity alone cannot approve a design.

Primary links checked 2026-09-12. Workflow and schema rules above are this project's policy.
