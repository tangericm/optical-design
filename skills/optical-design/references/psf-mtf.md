# PSF and MTF validity

Choose the image-formation model before reading a transfer curve. The Tier 0 wavefront
tool uses scalar Fraunhofer diffraction with uniform amplitude on a binary pupil and
incoherent MTF from the PSF. It does not model vector polarization, apodization or a
general nonplanar image surface. FFT and Huygens analyses have different validity and
sampling requirements; check the engine's analysis documentation for high-NA, tilted
or strongly distorted pupils.
[Ansys PSF analysis](https://optics.ansys.com/hc/en-us/articles/42661723066515-What-is-a-Point-Spread-Function).

For coefficient input, `--npix` sets the pupil grid; map input uses its actual square
canvas without resampling. `--pad` must be at least two and changes focal-plane sampling,
not the amount of measured pupil information. Explicit map normalization uses
`--pupil-center-px row,col --pupil-radius-px R`. Without it the adapter assumes a complete
symmetric rim. NaNs are opaque aperture, not unmeasured transmissive pixels. Repair or
separately model missing measurements before running a physical prediction.

The reported Strehl compares the sampled peak with the same pupil at zero phase.
Record focus and tilt handling; map input removes fitted piston and tilts. The exponential
variance estimate is approximate and cannot diagnose a convention error by itself.
Mahajan compares the approximation behavior for primary aberrations.
[Mahajan, JOSA 73, 860–861 (1983)](https://opg.optica.org/josa/abstract.cfm?uri=josa-73-6-860).

For a fixed pupil amplitude, the triangle inequality applied to its autocorrelation
gives the phase-free pupil as an MTF bound. This is a derivation under the scalar
incoherent model. An annular pupil can exceed the clear-circle curve at some frequencies;
use `ideal_x`/`ideal_y` and `curve_ideal_mtf_*`. The legacy `diffraction_limit` field is
only the clear-circle reference. Keep frequency units and x/y orientation fixed.

Verification procedure: check a zero-phase pupil, compare analytic clear-disk results,
translate the pupil without changing its normalization diameter, and increase pupil
sampling and FFT padding separately. Require the requested metric to converge below its
acceptance tolerance. Finite pupil sampling, sampled peaks and width interpolation remain
numerical approximations. Q below two flags possible aliasing under the stated incoherent
cutoff; actual aliased content depends on the scene.

Primary links checked 2026-09-12. CLI behavior is documented from the local implementation.
