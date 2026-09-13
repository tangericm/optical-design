# Contributing

- Every formula carries a cited source and a test that pins a textbook value.
- Scripts follow the contract in [compute tiers](docs/tiers.md): `--help`, `--json`, exit codes 0/1/2/3/4.
- Run `uv sync` then `uv run pytest`; `npm ci` then `npm test`.
- Commits are authored by the human contributor; no AI co-author trailers.
