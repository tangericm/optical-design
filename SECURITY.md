# Security

Scripts under `skills/optical-design/scripts/` read the files you name on the command line,
compute, and write to stdout or to an output path you pass. They make no network requests
and send no telemetry. Dependency installation happens through `uv` on first run and
downloads packages from PyPI; pin versions in the PEP 723 headers.

Tier 2 (`zos.py`, later release) launches or attaches to Ansys Zemax OpticStudio through
ZOS-API. It is read-only unless `--write` is passed.

Report vulnerabilities through GitHub security advisories on this repository.
