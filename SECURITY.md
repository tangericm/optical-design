# Security

## Installation and prerequisites

The npm command copies the bundled skill only to an explicitly selected agent and
scope. It does not modify agent credentials, install optical engines in the background,
or enable an MCP server. It records file hashes for managed installations and refuses
to overwrite unmanaged or changed files. An explicit update retains the previous
installation as a sibling backup; review that backup before removing it manually.

The demo starts uv with fixed arguments for the bundled synthetic model. uv may download
Python and pinned optical dependencies. The installer and demo are local tools, not
an isolation boundary against other processes that can modify the same directories.

## Optical execution

Tier 0 and catalog scripts read named files and emit results. Design jobs copy a named optical
model into a new/empty output directory, open the copy, and save baseline/candidate artifacts.
They never overwrite the named source model or attach to an open OpticStudio editor session.

The native adapter owns one standalone ZOS-API session and closes it after the job. Refocus
changes only the final air gap. Optimization changes only explicit bounded radius/thickness
variables and verifies the remaining geometry. Tolerance jobs change explicitly declared radius/thickness
parameters on the copy, read them back and restore the baseline between trials. Optional
focus compensation repeats the identical perturbations for each bounded focus candidate. No arbitrary
generated Python, macros, shell commands, purchases or external messages are executed by the
design specification.

Native calls are synchronous. In-process CLI budgets and cooperative cancellation are
checked between calls and cannot interrupt a blocked engine call. MCP force-cancellation
terminates the owned process tree; it cannot claim the interrupted copy was restored.
Failure reports record available restoration evidence.
A candidate file left by a failed run is not an accepted candidate.

The skill scripts do not upload prescriptions or send telemetry. uv downloads dependencies;
OpticStudio may use its own licensing/network facilities. Backend libraries and native model
loaders are trusted dependencies, not a sandbox for hostile files. Open only models you intend
to process. Logs/reports retain local paths, design data, vendor identities and hashes.

Report vulnerabilities through GitHub security advisories on this repository.

The optional MCP stdio server exposes typed job operations. It confines outputs to its
declared workspace and input reads to declared roots, verifies supplied hashes, and runs
allowlisted CLI argument lists. It owns job processes and cancellation. Transport completion
is separate from optical acceptance; partial or mismatched receipts cannot accept a model.

Every action binds normalized specifications/configurations to the requested input snapshots.
Optical acceptance requires consistent measurements and hard-requirement assessments.
Hashes are pinned when evidence files are created and checked after engine teardown.
Explicit edits require expected original cell values. Local review packages escape text,
validate confined artifact paths and recalculate recorded numerical evidence; they do not
authenticate external engine claims or rerun optics. The host must keep declared job
directories private from untrusted local writers; this is an API boundary, not an OS sandbox.
