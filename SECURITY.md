# Security

Tier 0 and catalog scripts read named files and emit results. Design jobs copy a named optical
model into a new/empty output directory, open the copy, and save baseline/candidate artifacts.
They never overwrite the named source model or attach to an open OpticStudio editor session.

The native adapter owns one standalone ZOS-API session and closes it after the job. Refocus
changes only the final air gap. Tolerance jobs change explicitly declared radius/thickness
parameters on the copy, read them back and restore the baseline between trials. No arbitrary
generated Python, macros, shell commands, purchases or external messages are executed by the
design specification.

Native calls are synchronous. Budgets/cancellation are checked between calls and cannot
forcibly interrupt a blocked engine call. Failure reports record restoration evidence.
A candidate file left by a failed run is not an accepted candidate.

The skill scripts do not upload prescriptions or send telemetry. uv downloads dependencies;
OpticStudio may use its own licensing/network facilities. Backend libraries and native model
loaders are trusted dependencies, not a sandbox for hostile files. Open only models you intend
to process. Logs/reports retain local paths, design data, vendor identities and hashes.

Report vulnerabilities through GitHub security advisories on this repository.
