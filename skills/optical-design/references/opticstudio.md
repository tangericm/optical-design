# Licensed OpticStudio for native optical design

The portable inspection and first-order scripts accept `.zmx` and Optiland JSON only.
A `.zos` file requires this licensed native path, or an export to supported `.zmx` in
OpticStudio. The optical workflow is similar, but Optiland snippets are not executable
ZOSPy recipes. Native support here is the bounded audited adapter below.

## Requirements

- Windows operating system.
- OpticStudio with valid ZOS-API license (Professional or Premium tier).
- ZOSPy 2.1.5 and pythonnet 3.1.0, installed via uv.
- Python 3.11 (the verified Windows runtime).

Run commands with this exact prefix:

```powershell
uv run --python 3.11 --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/zos.py ...
uv run --python 3.11 --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/design.py ...
```

## Checking the license

Before starting design work, verify your installation:

```powershell
uv run scripts/zos.py check --json
```

Exit 0 means the license is valid and ready; exit 3 means unavailable (check your installation,
license server and trusted host environment).

## Standalone sessions

Scripts own a standalone OpticStudio session; they never attach to an open editor. Standalone
sessions isolate optical analysis from GUI edits and allow controlled teardown after each job.
The editor remains free for other work. This is operator launch configuration: the verified
native client explicitly passes the trusted host environment to inherit licensing.

## Native surface types and actions

Native prescription adapter accepts centered refractive systems with air object/image spaces,
angle fields and entrance pupil diameter. Supported surfaces: Standard spheres, planes and conics;
EvenAspheric with even-order coefficients A2 through A16 (all fixed, not optimization variables).

Supported design.py actions: `inspect`, `audit`, `edit`, `refocus`, `optimize`, `sensitivity`,
`tolerance`. All run the same validation contract: units mm, radius and thickness solves fixed,
field normalization radial, no explicit apertures or decenters/tilts, no multi-configuration or
coordinate breaks.

## Native profile benchmark

`scripts/benchmark.py` reproduces Huygens or POP profiles on unchanged models. Huygens and POP
use different methods and sampling; first-order and spot agreement is cross-validation useful
evidence. Same-method reproduction does not establish design acceptance.

## Known pitfalls

- Session ownership: scripts own the session; do not run two simultaneously or attach editor.
- Save GUI edits first: scripts open prescription copy, changes do not affect your editor model.
- Native calls can block past deadline: cancellation checks occur between calls only.
- Units must be mm; radius/thickness solves must be fixed; no explicit apertures/decenters/tilts.
- Coordinate breaks, multi-configuration prescriptions, coatings and polarization unsupported.
- Native 17-ray pupil validation catches gross failures, not every clipping event.

## Compatibility record

Version 2.0.0 keeps the audited-mode algorithms of 1.0.0 unchanged. Verify supported scope at
[release evidence](https://github.com/tangericm/optical-design/tree/v1.1.0/docs/research):
OpticStudio 2024 R1 with API 24.1.0, ZOSPy 2.1.5, pythonnet 3.1.0 on Windows. Native audit,
refocus, optimize and compensated tolerance passed on synthetic N-BK7 singlet models with
saved-model reload and source hash verification. Profile benchmark (75 Huygens/POP cases)
demonstrates same-method reproduction, not independent physical validation. Portability to other
OpticStudio versions and API versions requires explicit verification. Pin your adapter versions
and rerun capability checks when moving to another machine.
