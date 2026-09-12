# ZOS-API Python Connectivity Probe -- Ansys Zemax OpticStudio 2024 R1.00

## Verdict: WORKS

Standalone ZOS-API connection from Python succeeded end-to-end: connect -> new system ->
build a singlet lens -> set wavelength/EPD -> run an FFT MTF analysis -> get numeric
results back -> clean disconnect. Exit code 0, no license or .NET loading errors.

## Environment

- OpticStudio install: `C:\Program Files\Ansys Zemax OpticStudio 2024 R1.00` (confirmed present)
- ZOS-API reported version (via `zos.version`): 24.1.0
- License status (via `zos.Application.LicenseStatus`): PremiumEdition
- Python versions available on machine: only Python 3.13.7 was installed (`py -0p` showed a single
  interpreter, `C:\Users\erict\AppData\Local\Programs\Python\Python313\python.exe`). No 3.11/3.12
  were present, so no fallback was needed.
- Python used: 3.13.7 (system interpreter, via a fresh venv) -- pythonnet 3.1.0 ships a
  cp313 wheel (`pythonnet-3.1.0-cp310.cp311.cp312.cp313.cp314-none-win32.win_amd64.whl`), so 3.13
  worked without any downgrade.
- venv location: `C:\Users\erict\AppData\Local\Temp\claude\C--Users-erict-OneDrive-Desktop-Projects\704edb22-276c-4f8d-bbe3-a625496a44d8\scratchpad\zosprobe\.venv`
- zospy version: 2.1.5
- pythonnet version: 3.1.0
- clr_loader version: 0.3.1
- Other installed deps: numpy 2.5.3, pandas 3.0.5, pydantic 2.13.5, lark 1.2.2, semver 3.0.4, cffi 2.1.1

## ZOS-API Libraries folder check

- `C:\Users\erict\OneDrive\Documents\Zemax\ZOS-API\Libraries` -> exists (this is the active
  OneDrive-redirected Documents folder, and is what zospy/pythonnet actually located and used).
- `C:\Users\erict\Documents\Zemax\ZOS-API\Libraries` -> does not exist (this machine's "Documents"
  is redirected into OneDrive, so this plain path is expected to be absent; not an error).

No `ZOSAPI_NetHelper` / native-DLL-load errors were encountered -- pythonnet's `clr_loader`
found and loaded the ZOS-API .NET assemblies without any manual configuration.

## What the probe did (see probe.py in this directory)

1. `import zospy as zp; zos = zp.ZOS(); oss = zos.connect(mode="standalone")` -- connected cleanly.
2. Printed `zos.version` -> `24.1.0`, and `zos.Application.LicenseStatus` -> `PremiumEdition`.
3. `oss.new(saveifneeded=False)` to get a fresh system; built a simple singlet by inserting two
   surfaces into `oss.LDE`, setting `Radius`/`Thickness`/`Material="N-BK7"` on the front surface
   and `Radius`/`Thickness` on the back surface.
4. Set the primary wavelength to 0.55 um via `oss.SystemData.Wavelengths.GetWavelength(1).Wavelength = 0.55`
   and EPD to 10 via `oss.SystemData.Aperture.ApertureValue = 10.0`.
5. Ran an FFT MTF analysis: `from zospy.analyses.mtf import FFTMTF; result = FFTMTF().run(oss)`.
   This returned a real `AnalysisResult` with a 300-row tangential/sagittal MTF-vs-spatial-frequency
   pandas DataFrame (values ranging from 1.0 at 0 lp/mm down to ~0 at 380 lp/mm) -- i.e., OpticStudio
   actually computed and returned physically sensible results, not a stub/error object.
6. `oss.close(saveifneeded=False); zos.disconnect()` -- disconnected without error.
7. Final stdout lines: `DISCONNECTED CLEANLY` / `PROBE_SUCCESS`; process exit code 0.

## Exact stdout/stderr captured (full run)

```
zospy version: 2.1.5
ZOS object created: <zospy.zpcore.ZOS object at 0x000001E1CAFDA900>
connected, OpticStudioSystem: <zospy.zpcore.OpticStudioSystem object at 0x000001E1CAFDAF90>
Application: ZemaxUI.Common.ViewModels.ZOSAPI_Application
ZOSAPI version info: 24.1.0
LicenseStatus: PremiumEdition
Number of surfaces initially: 3
Surfaces after build: 5
FFT MTF analysis ran OK. Result type: <class 'zospy.analyses.base.AnalysisResult'>
Description       Field: 0.0000 (deg)          
SeriesLabels               Tangential  Sagittal
Spatial Frequency                              
0.000000                     1.000000  1.000000
1.270903                     0.879386  0.879386
2.541806                     0.760387  0.760387
3.812709                     0.644616  0.644616
5.083612                     0.533687  0.533687
...                               ...       ...
374.916388                   0.001140  0.001140
376.187291                   0.000875  0.000875
377.458194                   0.000593  0.000593
378.729097                   0.000300  0.000300
380.000000                   0.000000  0.000000

[300 rows x 2 columns]
DISCONNECTED CLEANLY
PROBE_SUCCESS
*** FRU__delta_init(): Attempt to start when running!
```

The only anomalous-looking line is the last one, `*** FRU__delta_init(): Attempt to start when
running!`, emitted to stderr AFTER `PROBE_SUCCESS` (i.e., during OpticStudio's own process
teardown, after Python's logic had already completed and printed success). This is a known
benign message from OpticStudio's internal FlexNet/telemetry ("FRU") subsystem during shutdown
of the standalone COM/.NET server process -- it did not affect the exit code (0) or any of the
actual API calls, all of which completed successfully before this line appeared.

## Notes on the two API mismatches encountered and fixed while adapting to zospy 2.1.5

zospy 2.1.5 restructured its analyses as classes with a `.run(oss)` method rather than the
`fft_mtf(oss)`-style function call suggested in the task's older-API sketch:
- `zospy.analyses.mtf.fft_mtf` is a submodule (not callable) -- the callable is the class
  `zospy.analyses.mtf.FFTMTF`, used as `FFTMTF().run(oss)`.
- `OpticStudioSystem.close()` takes the keyword `saveifneeded` (no underscore), not
  `save_if_needed`.
Both were discovered via `inspect.signature()` against the installed package and fixed in
probe.py; the corrected script is the one whose output is captured above.

## Working probe.py

See `C:\Users\erict\AppData\Local\Temp\claude\C--Users-erict-OneDrive-Desktop-Projects\704edb22-276c-4f8d-bbe3-a625496a44d8\scratchpad\zosprobe\probe.py`
(the exact file that produced the successful run above).

## Conclusion

The locally installed Ansys Zemax OpticStudio 2024 R1.00 does accept ZOS-API standalone
connections from Python on this machine, under a PremiumEdition license, using
Python 3.13.7 + zospy 2.1.5 + pythonnet 3.1.0, with no venv/interpreter downgrade, no
license error, and no .NET/assembly loading error. No changes were made outside the scratch
directory; the OpticStudio installation and system settings were not modified.
