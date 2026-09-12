# OCT sample-arm audits

Separate axial coherence gating from transverse focusing. The familiar Gaussian-spectrum
axial estimate in air is `Δz = (2 ln 2 / π) λ0² / Δλ`, with an explicitly stated spectral
FWHM and depth convention; the wavelength-bandwidth expression is an approximation to
the frequency/wavenumber description. It is not an arbitrary-spectrum PSF simulator.
[Primary OCT study, Scientific Reports (2021)](https://www.nature.com/articles/s41598-021-90837-9).

OCT optical delay must be converted to physical depth using the appropriate group index;
phase index controls refraction and should not silently substitute for group index.
State whether the coordinate represents one-way depth or round-trip delay.
[Primary study on OCT refraction and path-length correction (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9484446/).

Collect source spectrum and bandwidth definition, center wavelength, immersion/sample
medium, beam-diameter convention, scan field, desired depth range, working distance and
return-path geometry. The following commands provide limited analytic starting points:

```powershell
uv run scripts/resolve.py oct-axial --center-wavelength-um 0.84 --bandwidth-nm 50 --json
uv run scripts/resolve.py oct-lateral --wavelength-um 0.84 --focal-mm 36 --beam-diameter-mm 3 --json
```

Audit the sample-arm prescription over scan position and source band, then check focus
position, lateral width, clipping and available working distance. Preserve beam and
aperture conventions when comparing candidates. A sequential image-quality calculation
does not itself verify interference contrast, sensitivity, tissue scattering or a measured
axial PSF. These are explicit outside-model requirements.

For a system acceptance test, retain the measured spectrum, reconstruction/window settings,
axial PSF definition, reference/sample-arm dispersion assumptions and spatial sampling.
State which evidence is measured, calculated or unavailable. Evaluate the actual processed
axial response when a Gaussian-bandwidth approximation is insufficient.

Primary links checked 2026-09-12. The checklist is project workflow guidance, not a clinical claim.
