# Interactive optical jobs over MCP

`scripts/server.py` exposes `capabilities`, `start`, `status`, `cancel`, `results`, and `review`
through the official MCP Python SDK over stdio. It dispatches the existing `design.py`
CLI in an owned subprocess. All optical requirements, budgets, native isolation, and
saved-candidate verification remain in the CLI implementation.

The verified SDK pin is `mcp==2.2.0` (PyPI release September 7, 2026). The implementation
uses `mcp.server.MCPServer`, its tool decorators and lifespan, `run(transport='stdio')`,
and the official `mcp.Client` with `StdioServerParameters` for verification. This is
the SDK v2 API; v1 FastMCP examples are not interchangeable. Sources checked September
12, 2026: [official SDK](https://github.com/modelcontextprotocol/python-sdk),
[versioned distribution](https://pypi.org/project/mcp/2.2.0/).

## Launch with an explicit workspace and read roots

Portable engine, from the installed skill directory:

```powershell
uv run --python 3.11 --with optiland==0.6.2 scripts/server.py --workspace C:/Optical/jobs --input-root C:/Optical/models --input-root C:/Optical/specs
```

Licensed native engine on Windows:

```powershell
uv run --python 3.11 --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/server.py --workspace C:/Optical/jobs --input-root C:/Optical/models --input-root C:/Optical/specs
```

The script's PEP 723 metadata installs the SDK and NumPy. The `--with` options put
the optional engine in the **same interpreter** inherited by its CLI children.
Include both sets of optional dependencies if one server must run both backends.
`capabilities` reports installed package versions, not a licensed-engine health check.
Missing dependencies or unavailable licenses produce a failed job with diagnostic logs.
MCP clients may deliberately start stdio servers with a restricted environment. The
verified native client explicitly inherits the trusted local host environment with
`StdioServerParameters(..., env=dict(os.environ))`, matching an ordinary local CLI
launch. Forwarding only the two Ansys licensing variables and a short Windows-variable
list was insufficient on the verified host; the exact omitted prerequisite was not
isolated. Host inheritance restored native startup while retaining process ownership.
This is operator launch configuration, never a tool argument. Do not serialize the
environment or embed license-server values in checked-in configuration or evidence
logs. A Python environment containing ZOSPy alone does not supply native licensing.
The tool does not accept a command, executable, argument list, environment override,
output path, or GUI attachment. Only the host launching the server chooses the roots.

## Tool calls

Compute SHA256 of every input immediately before starting. `Get-FileHash` returns
uppercase text; convert it with `.Hash.ToLowerInvariant()`. The `start` tool takes
one strict `request` object:

```json
{
  "request": {
    "action": "audit",
    "backend": "optiland",
    "model": "C:/Optical/models/lens.json",
    "model_sha256": "<64 lowercase hexadecimal characters>",
    "spec": "C:/Optical/specs/audit.json",
    "spec_sha256": "<64 lowercase hexadecimal characters>"
  }
}
```

Actions are `inspect`, `audit`, `edit`, `refocus`, `tolerance`, `optimize`, and `sensitivity`;
backends are `optiland` and `zos`. `inspect` requires only model identity: omit both
`spec` and `spec_sha256`. All other actions require that pair.

| Action | Additional input path/hash pair |
|---|---|
| `edit` | `changes`, `changes_sha256` |
| `sensitivity` | `perturbations`, `perturbations_sha256` |
| `tolerance` | `tolerances`, `tolerances_sha256` |
| `optimize` | `variables`, `variables_sha256` |

Each pair is required only for its corresponding action; partial or unrelated pairs
reject. Changes use schema 1 `changes` rows with `surface`, `parameter`, `expected_mm`,
`value_mm`. Perturbations use schema 1 `parameters` rows with `surface`, `parameter`,
positive `step_mm`. These are declarative data files, not code or native commands.
For optional post-search validation on `optimize`, add
`validation_spec` and `validation_spec_sha256`; both are required together and undergo the
same root, hash, snapshot and stale-input checks. Each file must resolve beneath a declared input root.
A changed hash is rejected before creating a job. The exact verified bytes are copied
to an owned input snapshot; the optical CLI runs on that copy.

`start` returns `job_id`. Pass `{"job_id":"..."}` to `status`, `cancel`, or `results`.
Identities belong only to the current server session. Restarting the server does not
resume old jobs or make old workspace folders executable. Outputs use generated UUID
directories and never overwrite an earlier job. Jobs are serialized within this
server; use one server for a licensed execution queue.

For a completed job, `review({"job_id":"..."})` rechecks the owned receipt and renders
a fresh owned review directory. It accepts no arbitrary report/output path and runs no
optical engine. The return is `{job_id, directory, manifest}`; `directory` is an absolute
local path. The manifest records schema, tool, action, optical status, acceptance,
receipt hash, artifact verification, and SHA-256/byte counts for `report.html` and
`report.md`. Link those files for the engineer; rendering does not change acceptance.
Recheck `results` for optical status instead of treating a rendered package as a pass.

Each job directory contains `inputs/`, `output/`, `temp/`, `stdout.log`, and `stderr.log`.
Native startup and teardown output remains in diagnostic logs, keeping MCP stdout
reserved for protocol messages. Native worker temporary receipts use the owned `temp/`
directory. Optical-engine libraries may have their own installation-level caches;
this wrapper does not sandbox the installed engine.

## Completion and acceptance

`state` is `running`, `completed`, `failed`, or `cancelled`. `optical_accepted` is true
only for a fully checked `requirements_met`, `improved`, or explicit-edit `applied`
result. An applied edit meets its requirements but need not improve merit. A completed audit
that misses requirements and a completed refocus/optimization without an acceptable
improvement, or whose separate validation fails (`validation_failed`), have `optical_accepted: false`; their exit code 1 is an expected optical
outcome. Inspection and sensitivity completion are evidence collection, with
`optical_accepted: false`. Tolerance completion is evidence collection, so it also has
`optical_accepted: false`; inspect the conditional tolerance statistics in `report`.

`results.report` remains null while running and for failed/cancelled jobs. Before
exposing a report, the manager checks action/schema, exit/status agreement, exact
stdout/report receipt agreement, source and input snapshot hashes, restoration
evidence, confined model artifact paths and hashes, and saved-candidate verification
for improvements. A `failure.json` invalidates any partial report. Reads recheck the
original inputs and artifacts: changes after completion invalidate acceptance.
Diagnostic file paths remain available on failure; a raw partial report on disk is
never an accepted result.

Cancellation kills the owned process tree. Windows uses a kernel Job Object with
kill-on-close and a gated child, assigned before the CLI can spawn descendants.
POSIX uses a new process session/group. The manager never enumerates processes by
name, attaches to an editor, or kills an unrelated PID. Normal stdio disconnect and
server shutdown cancel active jobs. Hard POSIX termination that prevents cleanup is
outside the graceful shutdown guarantee. Cancellation preserves diagnostic files and
does not claim the interrupted copy was restored; the original input is never the
CLI's working model.

Keep declared roots and workspace private from untrusted local writers. Canonical
path checks reject root escapes, but this tool boundary is not a filesystem sandbox
against another local process racing directory replacement or a malicious installed
backend. Use trusted optical model files and engine installations.

## Verification

```powershell
uv run --with mcp==2.2.0 pytest tests/python/test_tool_jobs.py tests/python/test_mcp_server.py -q
```

The subprocess tests cover allowlists, stale hashes, root confinement, unknown IDs,
one active job under concurrent starts, receipt/exit disagreement, artifact tampering,
cancel/shutdown cleanup, and owned child termination while an unrelated process stays
alive. The SDK stdio tests exercise the registered tools, reject unknown
request fields/stale hashes, dispatch the real CLI, and confirm an invalid optical
spec fails without acceptance. A symbolic-link test skips where Windows cannot create
links. Real optical acceptance is a separate engine-enabled integration check, not
inferred from this transport test.

Use [the workflow verification protocol](https://github.com/tangericm/optical-design/tree/main/evals) to collect current installed-client
evidence for inspection, edits, composite merit, sensitivity and review. The scenarios
include stale expected values, stale input hashes, and rejected designs; a test
description is not a claim that a specific engine/client run passed.

For chained calls, preserve the preceding job ID, accepted saved-model path and SHA-256.
The next model path must still lie under a declared input root. Copy a reviewed accepted
artifact into an authorized model root when needed, then hash the copied bytes. Never
weaken root confinement or silently swap in a rejected file. Define all next-step inputs
before `start`; report the exact returned evidence rather than predicting an optimum.

When validation is requested, the manager also checks the frozen specification and its
snapshot hash, reassesses both validation measurements, and links their parameter vectors
to the original and saved/rejected models. A successful search cannot conceal a missing
or failed validation. See [separate validation](validation.md).
