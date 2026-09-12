# Compute tiers

| Tier | Needs | Scripts | Status |
|---|---|---|---|
| 0 | Python 3.11+, uv (numpy/scipy/scikit-image auto-installed) | resolve, zernike, wavefront, interfero, compare | shipped |
| 1 | optiland (auto-installed on first run) | trace | planned |
| 2 | Windows, Ansys Zemax OpticStudio Professional/Premium, ZOSPy | zos | planned |

## Script contract

- `uv run scripts/<name>.py <subcommand> [args] [--json]`
- JSON envelope: `{schema, tool, subcommand, tier, inputs, results, units, method, warnings}`
- Exit codes: 0 ok, 1 comparison failed (`compare.py` only), 2 usage, 3 missing tier dependency, 4 analysis failed
- No network calls at runtime; dependency download happens through uv on first run.
