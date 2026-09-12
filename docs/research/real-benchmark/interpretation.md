# Interpreting the saved real-design benchmark

This note interprets existing evidence and proposes controlled follow-up work. It makes no
claim that a fresh native benchmark has completed or passed.

## Reproduction is one gate in a trustworthy engineering loop

A MecAgent-like optical-design loop needs distinct gates: reproduce an unchanged baseline,
establish that its physical model answers the intended question, then evaluate authorized
changes against measured requirements. Matching saved arrays tests execution, identity,
units and numerical repeatability. It cannot establish source fidelity, adequate sampling,
manufacturability or OCT performance. A repeatable bias remains a bias. The
[benchmark contract](../../../skills/optical-design/references/profile-benchmark.md) therefore
separates completion, reference comparison and sampling diagnostics from physical acceptance.

Keep the fixed fiber/collimator surface blocks **0–3 unchanged** in all reference and
downstream design comparisons. They are identical across the three delivered models and
the fixed-source baseline. Source-calibration experiments need separately identified copies
and receipts; silently retuning the source would change the comparison boundary.
[Model identities and boundaries](reference-audit.md#model-boundaries-and-active-spectrum).

## What remains unresolved

For Stock, the saved full-spectrum X full 1/e² width is **0.6078047331593057 mm** in
Huygens and **0.7414818062153821 mm** in POP: POP is approximately **22% wider relative
to Huygens**. These are different methods' baseline values, not a reference tolerance.
The cause remains undetermined. Method approximations, effective launch/pupil weighting,
intermediate diffraction or truncation, and numerical sampling are hypotheses to test,
not diagnoses. [Exact saved baselines](reference-audit.md#exact-full-spectrum-scalar-baselines).

Ansys describes ray-derived diffraction PSFs as propagating a ray-reconstructed exit-pupil
field to the image in one diffraction step. Intermediate foci, truncation and long nearly
collimated propagation can make neglected diffraction relevant. POP instead propagates a
sampled field through the optical path, but its own sampling limits still matter. This makes
a method-dependent difference plausible; it does not prove POP is correct for this model.
[Ansys: About Physical Optics Propagation](https://ansyshelp.ansys.com/public/Views/Secured/Zemax/v251/en/OpticStudio_User_Guide/OpticStudio_Help/topics/About_Physical_Optics_Propagation.html).

## Prioritized controlled checks

1. **Separate Huygens pupil and image controls at one wavelength.** Start with 840 nm,
   one model/axis and unchanged planar, polarization, pupil illumination and observation
   settings. First vary pupil sampling while holding the image grid fixed. Then vary image
   spacing at fixed pupil sampling, keeping the physical observation window fixed where
   possible; test window expansion separately. Retain raw curves, outer crossings and
   native settings readback. The existing X pair changes pupil 512→1024 **and** image
   256→128 with spacing 3→6 µm, so it is not a controlled convergence demonstration.
   Repeat over additional wavelengths before extending a conclusion to the 18-wave mean.
   [Saved convergence cases](reference-audit.md#existing-convergence-evidence-and-limits).

2. **Test POP physical pitch and guard bands separately, including intermediate planes.**
   Record actual Dx/Dy, array extent, power and edge intensity at launch, shaper exit,
   resampling planes, intermediate foci and the sample. Inspect intensity and phase where
   available. At 840 nm, the saved 2048→4096 runs leave final Y pitch approximately
   **1.054 µm** while expanding the Y window; their small Y-width change does not prove
   convergence under finer Y sampling. Adjust propagation/resampling controls to improve
   actual spatial resolution, then vary window margins independently. Recheck upstream
   planes after every change. Ansys documents both undersampling artifacts and inadequate
   guard bands, and shows why changing a preceding grid width can alter downstream pitch.
   [Native pitches](reference-audit.md#saved-raw-cases-and-array-semantics);
   [Ansys POP sampling guidance](https://optics.ansys.com/hc/en-us/articles/42661979347731-Using-Physical-Optics-Propagation-POP-Part-2-Inspecting-the-beam-intensities).

3. **Match effective Gaussian source, spectral weights and coherence assumptions.** Compare
   the declared POP waist and phase at launch with the ray-derived pupil amplitude used
   for Huygens; enabling polarization in both is insufficient to establish identical
   illumination. OpticStudio Gaussian apodization varies **amplitude across the pupil**;
   distinguish it from intensity weighting and from a Gaussian waist specified at another
   plane. [Ansys apodization definition](https://optics.ansys.com/hc/en-us/articles/42661779181203-What-does-the-term-apodization-mean).
   Use only the 18 active wavelengths and declared weights. For an incoherent spectral
   mean, normalize weights and sum absolute monochromatic irradiances before peak scaling.
   Do not sum individually normalized profiles or substitute a point-image PSF or integrated
   marginal for an illumination cut. Preserve native pitch through interpolation and require
   full flatness-ROI coverage. [Reduction and units](reference-audit.md#reduction-contract-and-checks).

4. **Tie acceptance to matched measured profiles and the provisional cube.** The simple
   Ayase-related bench values—0.609 mm full 1/e², 0.527 mm FWHM and 4.75% CV over
   0.42 mm—are contextual measurements, not automatically a full-source-to-sample target.
   Establish matching planes, magnification, spectral response, detector sampling, power
   normalization and uncertainty first. Resolve the source-output discrepancy (~1.74 mm
   predicted versus ~1.54 mm measured diameter) through separately documented calibration.
   Replace or bound the provisional cube's nominal 50% transmission, coating/polarization
   assumptions and omitted optical elements before claiming physical throughput or OCT
   improvement. [Measurement and model limitations](reference-audit.md#missing-evidence-and-acceptable-benchmark-claims).

A useful next decision record would show which controlled variable changes the disagreement,
which numerical conclusions survive independent pitch/window refinement, and what measurement
supports the selected model. Until then, preserve both method baselines and report the
discrepancy explicitly rather than selecting the more attractive width.
