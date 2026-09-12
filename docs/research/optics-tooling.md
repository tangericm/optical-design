# Tooling Landscape for an AI-Agent Optical Design Skill

Scope: resolution/PSF/MTF/WFE/Zernike/Strehl/tolerancing analysis skill that interoperates with
Ansys Zemax OpticStudio (local install: `C:\Program Files\Ansys Zemax OpticStudio 2024 R1.00`).

## 1. ZOS-API

**Access from Python.** ZOS-API is a .NET API. Recommended Python access is via **pythonnet** (CLR
bridge), not the older COM interface. Boilerplate code locates the ZOS-API DLLs under the OpticStudio
`ZemaxData` folder using `ZOSAPI_NetHelper` to resolve the install path and load assemblies.
[Ansys — ZOS-API.NET: An Overview](https://optics.ansys.com/hc/en-us/articles/42661790380179-ZOS-API-NET-An-Overview) ·
[Zemax Community — ZOSAPI_NetHelper cannot be added](https://community.zemax.com/zos-api-12/zosapi-nethelper-cannot-be-added-455)

**Standalone vs. Interactive Extension.** Two connection modes:
- *Standalone*: Python launches its own invisible/headless OpticStudio instance (default mode in most templates).
- *Interactive Extension*: OpticStudio GUI is already open; user clicks the "Interactive Extension" button in the ZOS-API.NET ribbon area (shows instance number, waits for a client), then Python attaches to that running instance.
[ZOSPy docs](https://zospy.readthedocs.io/en/v1.3.0/api/zospy.zpcore.ZOS.html) · [Zemax Community — Python ZOS-API example](https://community.zemax.com/zos-api-12/python-zos-api-example-not-working-out-of-the-box-since-ansys-5239)

**License requirement — important gating fact.** ZOS-API requires a **Professional or Premium**
OpticStudio license; the **Standard** tier does not include API access.
[Zemax subscription tiers](https://www.zemax.com/pages/opticstudio) (per WebSearch synthesis).
Separately, the free **Ansys Zemax OpticStudio Student** edition explicitly does **not** support ZPL,
ZOS-API, or user-defined DLLs (also disables STAR, Contrast/Global/High-Yield Optimization, limits to
4 CPU cores, 1 instance). [Zemax Community — Ansys Zemax OpticStudio Student](https://community.zemax.com/people-pointers-9/ansys-zemax-opticstudio-student-free-software-download-5252) · [Ansys Learning Forum — Zemax Student Version](https://innovationspace.ansys.com/forum/forums/topic/zemax-student-version/)
→ **Implication:** confirm which license tier the local 2024 R1.00 install carries before assuming
ZOS-API automation is available; if only Standard/Student, the skill must fall back to open-source
compute or ZMX-file parsing rather than live ZOS-API calls. UNVERIFIED which tier is installed locally.

**Key analyses exposed via ZOS-API.** FFT/Huygens PSF, FFT/Huygens MTF, Zernike Standard Coefficients
and Zernike Fringe Coefficients analyses, wavefront map, spot diagram, Seidel diagram, Physical Optics
Propagation (POP), Tolerancing (`ISystemTools`/`TDETools`), optimization (Merit Function Editor,
Local/Hammer/Global optimization), Quick Focus. Confirmed present in third-party MCP tool inventories
built directly against ZOS-API (see §4). [Ansys Developer Portal — ZOS-API interface reference](https://developer.ansys.com/product/ZOS-API-interface-2024-R1/interface_z_o_s_a_p_i_1_1_analysis_1_1_data_1_1_i_a_r__.xhtml)

**Reading out results.** Pattern: instantiate an analysis, call `GetResults()`, then read either
`.DataGrid` (2-D matrix, e.g. Sag) or `.DataSeries` (2-column list, e.g. FFT MTF vs. spatial frequency)
if the analysis populates one of those structured types; otherwise fall back to `GetTextFile()` which
dumps the analysis window's numeric text report to disk for parsing — "not all analyses return
detailed results via DataGrid/DataSeries... all analyses that support text output should support
GetTextFile." [Ansys — Generating a list of output data types for each analysis in ZOS-API](https://support.zemax.com/hc/en-us/articles/1500005489021-Generating-a-list-of-output-data-types-for-each-analysis-in-the-ZOS-API) · [Zemax Community discussion on DataGrid/DataSeries mismatch](https://community.zemax.com/zos-api-12/how-to-extract-universal-plot-1d-analyses-data-using-matlab-api-2405)

**ZMX file format.** Plain text, but **not officially documented/supported** by Zemax/Ansys as a public
spec — third parties reverse-engineer it. Structure: `VERS` (Zemax version), `MODE SEQ`/`NSC`, `GCAT`
(glass catalogs used), then a sequence of `SURF n` blocks each with `TYPE` (STANDARD, EVENASPH, etc.),
`CURV` (curvature = 1/R), `DISZ` (thickness to next surface), `CONI` (conic constant), `GLAS` (glass
name, looked up in the referenced `.AGF` catalog file), `PARM` (surface-type-specific parameters, e.g.
asphere coefficients). A ray trace needs both the `.zmx` and its `.AGF` glass catalog file(s).
[Zemax Community — ZMX File Specification (community thread)](https://community.zemax.com/zpl-13/zmx-file-specification-106) ·
[quartiq/rayopt zemax.py parser (reference implementation)](https://github.com/quartiq/rayopt/blob/master/rayopt/zemax.py) ·
[Optiland zemax_handler source](https://optiland.readthedocs.io/en/latest/_modules/fileio/zemax_handler.html)

## 2. ZOSPy (MREYE-LUMC)

- **Latest release:** v2.1.5 (GitHub Releases page; exact 2026 date shown but page didn't surface full date string in fetch — flag as UNVERIFIED precise day). [ZOSPy Releases](https://github.com/MREYE-LUMC/ZOSPy/releases)
- **What it wraps:** a Pythonic, more ergonomic layer over the raw ZOS-API .NET objects (analyses,
  system setup, results parsing) — described as "a wrapper around the Ansys Zemax OpticStudio API...
  via a .NET connection." [ZOSPy docs index](https://github.com/MREYE-LUMC/ZOSPy/blob/main/docs/index.md)
- **Python version support:** officially 3.10–3.14 per docs (Note: some tool metadata elsewhere said
  "not updated for 3.10" — that refers to the underlying **pythonnet** library historically, not
  ZOSPy itself; treat as UNVERIFIED which exact pythonnet version ZOSPy currently pins).
- **pythonnet requirement / install pitfalls on Windows:** ZOSPy historically required
  **pythonnet 2.5.2** because some ZOS-API calls broke under pythonnet 3.x ("since Python.NET 3.0 int
  can not be converted to Enum implicitly"); ZOSPy 1.2.0 added a custom encoder to support pythonnet 3.
  pythonnet 2.5.2 install on Python 3.10/Windows has known failures needing .NET Runtime ≥4.6.1
  (4.7.2+ recommended) and sometimes the .NET SDK on PATH (`dotnet` command). [pythonnet issue #1728](https://github.com/pythonnet/pythonnet/issues/1728) · [Zemax Community — Python.NET 3.x is completely "Fixed"](https://community.zemax.com/zos-api-12/python-net-3-x-is-completely-fixed-4926) · [zospy 0.6.1 PyPI page](https://pypi.org/project/zospy/0.6.1/)
- **Analyses exposed:** wraps the same catalog as ZOS-API — PSF, MTF, Zernike, wavefront, spot diagram
  etc. — via typed Python analysis wrapper functions (`zospy.analyses.*`). UNVERIFIED complete list;
  recommend reading `zospy.analyses` module listing directly if adopted.
- **OpticStudio 2024 R1 support:** compatibility matrix explicitly lists **24.1.0** as tested with full
  support on Python 3.10–3.12+. [ZOSPy compatibility discussion](https://zospy.readthedocs.io/) — this
  is a strong match for the local "2024 R1.00" install.
- **Connection modes:** supports both `standalone` (spins up invisible OpticStudio instance, default)
  and `extension` (attaches to an already-open GUI in Interactive Extension mode).

## 3. Open-source Python optics libraries (fallback / independent compute)

| Library | License | Maintenance | Python | Imports .zmx/.seq | Key analyses | Docs |
|---|---|---|---|---|---|---|
| **prysm** (Brandon Dube) | MIT | Active-ish; JOSS paper 2019, GitHub still current | 3.10+ | No (pupil/propagation focus, not sequential ray trace) | PSF/MTF/PTF/OTF, Strehl, Zernike/Legendre/Chebyshev wavefront bases, encircled energy, PSD, interferogram synthesis; GPU (cupy) & numba acceleration, "100–1000x" faster than comparable tools per authors | [GitHub](https://github.com/brandondube/prysm) · [JOSS paper](https://joss.theoj.org/papers/10.21105/joss.01352) · [ReadTheDocs](https://prysm.readthedocs.io/) |
| **poppy** (STScI) | BSD-style (STScI OSS norm) UNVERIFIED exact license text | Active — v1.2.0 released Aug 2026 | ≥3.12 | No | Fraunhofer/Fresnel diffraction propagation, PSF formation for JWST/Roman (powers WebbPSF); "not a substitute for Zemax/CODE V," meant for diffractive-optics-focused, lightweight modeling | [GitHub](https://github.com/spacetelescope/poppy) · [PyPI](https://pypi.org/project/poppy/) · [docs](https://poppy-optics.readthedocs.io/) |
| **optiland** | MIT | Very active — v0.6.2 released Aug 2026 | 3.11–3.14 | **Yes** — imports/exports Zemax `.zmx`, CODE V `.seq`, OSLO `.len`; native JSON | Sequential ray trace (incl. freeform/asymmetric), spot diagrams, wavefront error maps, ray fans, PSF/MTF plots, Zernike decomposition, distortion, Monte Carlo + parametric sensitivity (tolerancing-equivalent), GPU-accelerated & PyTorch-differentiable ray tracing (150M+ ray-surfaces/s), Numba backend | [GitHub](https://github.com/optiland/optiland) · [docs](https://optiland.readthedocs.io/) · [optiland.org](https://www.optiland.org/) |
| **rayoptics** (Michael Hayford) | BSD-3-Clause | Maintained, no tagged GitHub "Releases" entries found but PyPI package active | UNVERIFIED (repo supports modern Python 3) | **Yes** — `open_model()` reads Zemax `.zmx`/`.zar` and CODE V `.seq`, plus native `.roa` JSON | Sequential geometric ray trace, paraxial (y-ybar) layout, third-order/Seidel-style aberration data, transverse ray & wavefront aberration analysis; usable from scripts, Jupyter, or Qt GUI | [GitHub](https://github.com/mjhoptics/ray-optics) · [ReadTheDocs](https://ray-optics.readthedocs.io/) |
| **pyoptools** | GPL-3.0 | Repository active (379 commits); release cadence UNVERIFIED | UNVERIFIED | UNVERIFIED (no zmx mention found) | Non-sequential 3-D ray tracing, wavefront calculations, Python+Cython core, FreeCAD workbench in progress | [GitHub](https://github.com/cihologramas/pyoptools) · [docs](https://pyoptools.readthedocs.io/) |
| **KrakenOS** | UNVERIFIED (SPIE-published, appears open on GitHub) | Peer-reviewed 2022 (Optical Engineering), GitHub active | UNVERIFIED | UNVERIFIED | Exact sequential/non-sequential ray tracing, 2-D/3-D visualization (PyVista/PyVTK/Matplotlib), Zernike wavefront analysis, Seidel sums, glass/lens catalogs, validated against Zemax to ~9×10⁻⁸ mm agreement | [GitHub](https://github.com/Garchupiter/Kraken-Optical-Simulator) · [SPIE paper](https://www.spiedigitallibrary.org/journals/optical-engineering/volume-61/issue-1/015101/KrakenOS-Python-based-general-exact-ray-tracing-library/10.1117/1.OE.61.1.015101.short) |
| **opticspy** | UNVERIFIED — no reliable current info surfaced; likely stale/abandoned (last known activity pre-2020) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Historically: Zernike analysis, ray tracing toy examples | not independently confirmed this pass |
| **zmxtools** / other ZMX-only readers | UNVERIFIED | UNVERIFIED | UNVERIFIED | Yes (by definition, parser-only) | File parsing only, no propagation/analysis | not independently confirmed this pass |

**Recommendation for compute backends:** **optiland** + **prysm** (see §6).
- *optiland* covers the ray-tracing / geometric side (import real ZMX files, spot/ray-fan/Zernike/PSF/MTF,
  Monte Carlo tolerancing) with an actively maintained, MIT-licensed, GPU-capable engine and direct ZMX
  interoperability — closest single library to "OpticStudio without OpticStudio."
  *rayoptics* is a strong secondary/cross-check for paraxial & Seidel third-order numbers and CODE V `.seq` ingestion.
- *prysm* covers diffraction-based physical optics (PSF/MTF via FFT/Huygens-equivalent, Zernike wavefront
  fitting, Strehl) with best-in-class performance claims, complementing optiland's geometric ray trace.
- *poppy* is a viable alternative to prysm specifically for physical (Fresnel/Fraunhofer) propagation if
  the task resembles space-telescope-style coronagraph/segmented-aperture work; otherwise prysm is more
  general-purpose for the requested lens-design-style analyses.

## 4. Existing AI/LLM tooling for Zemax/optics (avoid duplicating)

Multiple independent MCP servers already exist that drive OpticStudio via ZOS-API from an LLM agent:

- **webworn/zemax-mcp-server** — MIT license, v0.1, ~10 GitHub stars. Exposes 31 MCP tools spanning
  connection, system setup, Lens Data Editor edits, optimization (merit function wizard, local/hammer/
  global), and analysis (RayFan, StandardSpot, FFT-PSF, FFT-MTF, wavefront map, batch ray trace),
  plus advanced (multi-config editing, tolerancing, non-sequential, detector analysis). Verified
  end-to-end against **OpticStudio 2025 R2.02 Enterprise** (optimization loop reducing merit 1.03→0.08).
  Ships a "GUI feature ↔ ZOS-API member ↔ AI use-case" master map doc. Known issue: standalone/headless
  mode unavailable on their tested license (Enterprise); Interactive Extension needs one-click arming
  per session. [GitHub](https://github.com/webworn/zemax-mcp-server)
- **Hao-xl/zemax-python-connect** — MIT, "Codex/agent skill," very early (2 commits, ~10 stars, no
  releases). Deliberately scoped to **connection only** (standalone + extension mode setup, DLL
  auto-discovery, connection diagnostics) — explicitly excludes design/analysis/optimization/tolerancing
  logic. Could be referenced for its Windows DLL-discovery approach but not a full solution.
  [GitHub](https://github.com/Hao-xl/zemax-python-connect)
- **jaruiz6363/OpticStudioMCPServer** and its forks (e.g. **zym1998year/OpticStudioMCPServer**) — MCP
  servers targeting Claude Desktop/Claude Code/Ollama; the zym1998year fork claims a fix for a 3-second
  cold-start timeout crash and adds `ExportAnalysisTool` (17 analysis types → BMP + TXT export, including
  heatmap rendering of 2-D grid analyses like PSF/wavefront) and a 25+-parameter `GeometricImageAnalysisTool`.
  [GitHub](https://github.com/zym1998year/OpticStudioMCPServer) · [DeepWiki docs](https://deepwiki.com/jaruiz6363/OpticStudioMCPServer/1.1-getting-started-and-installation)
- **dongzhaohe321418-lab/zemax-mcp** — "safety-first" MCP server for sequential-mode workflows,
  includes a mock backend for testing without a live OpticStudio license. [Glama listing](https://glama.ai/mcp/servers/dongzhaohe321418-lab/zemax-mcp)

**Takeaway:** the ZOS-API-bridge problem is already being solved by several small, MIT-licensed,
low-star (~10) community projects, none clearly dominant or hardened. None of them appear to bundle
the independent-compute fallback (prysm/optiland) or the reference-formula layer this skill also
needs — that combination looks like the differentiating gap to fill rather than duplicate.

## 5. Reference formulas/values to encode as lookup tables

| Concept | Formula | Source |
|---|---|---|
| Rayleigh criterion | R = 0.61 λ / NA (angular: 1.22 λ/D) | [Edinburgh Instruments](https://www.edinst.com/us/news/the-rayleigh-criterion-for-microscope-resolution/) |
| Airy disk radius | r = 1.22 λ (F/#) | standard optics identity, consistent with Rayleigh criterion in image space (converted from NA to F/#) |
| Abbe diffraction limit | d = λ / (2 NA) (FWHM-based) | [ResearchGate — 3 widely-used resolution formulae](https://www.researchgate.net/figure/The-3-widely-utilized-formulae-ie-Rayleigh-Sparrow-and-Abbe-for-resolution_fig1_346965618) |
| Sparrow criterion | R = 0.5 λ / NA (≈ diffraction limit λ/D, ~20% tighter than Rayleigh) | [Wikipedia — Sparrow's resolution limit](https://en.wikipedia.org/wiki/Sparrow's_resolution_limit) |
| Microscopy resolution | d = 0.61 λ / NA | same Rayleigh-criterion source above |
| Maréchal criterion | Strehl ≥ 0.80 ⇔ RMS WFE ≤ λ/14 (≈0.071λ) | [community/derived from Maréchal's tolerance rule](https://qiweb.tudelft.nl/aoi/wavefieldaberrations/wavefieldaberrations.html) |
| Strehl approximation (Maréchal) | S ≈ exp[−(2πσ/λ)²], valid for σ ≲ 0.2λ (extended form: S ≈ e^(−σφ²) for phase variance) | [Edmund Optics — Beam Quality and Strehl Ratio](https://www.edmundoptics.com/knowledge-center/application-notes/lasers/beam-quality-and-strehl-ratio/) |
| Zernike ordering/normalization | **Fringe** (a.k.a. "Air Force"/U. Arizona): ordered by n+\|m\|, L² norm = π on unit disc, no leading sqrt normalization constants. **Standard/Noll/OSA/ANSI Z80.28**: ordered by radial order n first, then azimuthal m, L² norm = π, but WITH sqrt normalization prefactors, so coefficient *values* differ from Fringe for the same wavefront even though both are "normalized to π." ANSI Z80.28-2022 formalizes term = normalization × radial term × meridional term for ophthalmic aberration reporting. | [Lambda Research — Comparing Zernike Order Conventions](https://lambdares.com/support-posts/ordering-of-terms-in-different-representations-of-zernike-polynomials) · [ANSI Blog — Z80.28-2022](https://blog.ansi.org/ansi/ansi-z80-28-2022-ophthalmics-optical-aberrations/) · [Schwiegerling — Review of Zernike polynomials (U. Arizona)](https://wp.optics.arizona.edu/jsasian/wp-content/uploads/sites/33/2018/04/Schwiegerling-Zernike-2018.pdf) |
| Seidel sums (5 monochromatic aberrations) | S_I spherical, S_II coma, S_III astigmatism, S_IV field curvature (Petzval), S_V distortion — each a surface-by-surface sum over paraxial ray-trace data | [John Savard — The Five Seidel Aberrations](http://www.quadibloc.com/science/opt0505.htm) · [JEOL glossary — Five Seidel aberrations](https://www.jeol.com/words/emterms/20121023.035259.php) |
| MTF cutoff frequency | ξ_cutoff = 1 / (λ · F/#) | [SPIE Optipedia — Diffraction MTF](https://spie.org/publications/spie-publication-resources/optipedia-free-optics-information/tt52_151_diffraction_mtf) |
| Depth of focus | Δf = ±2 λ (F/#)² is the common "geometric" rule of thumb; SPIE-adjacent source gives Δf = 4λf²/D² = 4λ(F/#)² for full range from waist — reconcile ± convention before encoding (UNVERIFIED which exact prefactor the skill should standardize on; encode both ±2λF² (half-range, common lens-design convention) and 4λF² (full range) with a note) | derived; needs a primary optics-textbook citation before hard-coding — flag UNVERIFIED prefactor |
| Gaussian beam: Rayleigh range | z_R = π w₀² / λ | [RP Photonics — Beam Divergence](https://www.rp-photonics.com/beam_divergence.html) |
| Gaussian beam: divergence half-angle | θ = λ / (π w₀) | same RP Photonics source |
| Gaussian beam: spot size vs. z | w(z) = w₀ √(1+(z/z_R)²) | Edmund Optics Gaussian beam propagation note |
| OCT axial resolution | Δz = (2 ln2/π) · λ₀² / Δλ (FWHM bandwidth, vacuum); divide by n for in-medium | [TU Delft — Advanced Optical Imaging, ch.14 OCT](https://qiweb.tudelft.nl/aoi/opticalcoherencetomography/opticalcoherencetomography.html) |
| OCT lateral resolution | Δx = 4λ₀f / (π D) = 0.61 λ₀/NA | same TU Delft source |
| Telescope Dawes limit | R(arcsec) = 116 / D(mm) [=4.56/D(inch)]; empirical, tighter than but comparable to Rayleigh (≈140/D) | [Wikipedia — Dawes' limit](https://en.wikipedia.org/wiki/Dawes'_limit) |
| Fizeau vs. Twyman-Green | Fizeau: common-path test/reference beams, only the reference surface needs high-precision figure, needs short-coherence source + precise OPD-near-zero tuning for phase shifting (source-side shift). Twyman-Green: separated arms, needs a full high-quality reference flat/sphere as external optic, phase-shifted by moving the reference mirror (or polarization-based simultaneous 4-frame shift, e.g. 4D Technology). | [4D Technology — What Is a Twyman-Green Interferometer](https://4dtechnology.com/products/twyman-green-interferometers/twyman-green-interferometer/) · [J.C. Wyant — Phase-Shifting Interferometry](https://wp.optics.arizona.edu/jcwyant/published-papers/phase-shifting-interferometry/) |

## 6. Recommendations

**(a) Primary compute backend:** Use **optiland** as the default independent ray-tracing/analysis
engine (MIT, actively released as of Aug 2026, native `.zmx`/`.seq`/`.len` import, PSF/MTF/Zernike/
spot/wavefront/Monte-Carlo-tolerancing already built in, GPU/PyTorch path for speed and future
differentiable-optimization use). Pair it with **prysm** as the diffraction/Fourier-optics specialist
for PSF/MTF/Strehl/Zernike-wavefront work that benefits from prysm's speed claims and polychromatic
support, and as a cross-check against optiland's own PSF/MTF module. Keep **rayoptics** on the shelf
specifically for CODE V `.seq` ingestion and quick paraxial/Seidel sanity checks, since it's a second
independent implementation to diff against. Do not build on pyoptools/KrakenOS/opticspy initially —
maintenance/version-support signals were too weak/UNVERIFIED to justify as a primary dependency; revisit
if optiland or prysm prove insufficient for non-sequential or exotic-surface cases.

**(b) OpticStudio bridge approach:** Adopt **ZOSPy** (not raw pythonnet) as the ZOS-API bridge —
it already targets OpticStudio 24.1.0 and Python 3.10–3.12 (a solid match for the local 2024 R1.00
install) and abstracts away the low-level `ZOSAPI_NetHelper`/pythonnet plumbing and the pythonnet-2.5.2-
vs-3.x enum-conversion breakage. Support both its `standalone` mode (default, for unattended/background
skill runs) and `extension` mode (for sessions where the user has OpticStudio open and wants to see the
agent's edits live). Before wiring this up, **verify the installed license tier** — ZOS-API needs
Professional or Premium; if the local install is Standard or Student, ZOS-API calls will fail outright
and the skill must route all "OpticStudio" requests through the ZMX-file-based fallback (parse the
`.zmx`/`.AGF` with optiland's importer, run equivalent analyses locally) instead. Do not build a new
MCP server from scratch before checking whether **webworn/zemax-mcp-server** (MIT, 31 tools, tested
against 2025 R2.02) already covers the needed surface — it may be adoptable/forkable rather than
reimplemented, though its low star count and single-maintainer status mean budgeting time to audit and
patch it.

**(c) Static reference tables vs. scripts:** Encode as **static lookup tables/constants** (no need to
recompute, unlikely to change): Rayleigh/Abbe/Sparrow coefficients (0.61/0.5/1.22), Maréchal λ/14
threshold, the Strehl exponential-approximation formula, Zernike Fringe-vs-Standard/Noll index mapping
tables (first ~37 terms) and their normalization prefactors, Dawes-limit constant (116), OCT resolution
formula constants (2ln2/π), Gaussian-beam relations, MTF-cutoff formula. Encode as **scripts/functions**
(need live numeric inputs — wavelength, NA, F/#, bandwidth, aperture, actual wavefront-map data from
OpticStudio or optiland): Strehl computation from an actual RMS WFE or Zernike coefficient set, Seidel
sum evaluation (requires surface-by-surface paraxial ray data), depth-of-focus for a specific system
(resolve the ±2λF² vs. 4λF² convention against a primary textbook citation before shipping — currently
UNVERIFIED which the skill should standardize on), and anything that consumes a live ZMX/ZOS-API
dataset (spot diagrams, PSF/MTF curves, tolerancing Monte Carlo output) — these must run through
optiland/prysm/ZOSPy rather than being pre-tabulated.

## Notable gaps / UNVERIFIED items to close before shipping
- Exact OpticStudio 2024 R1.00 **license tier** installed locally (Standard/Professional/Premium) — gates whether ZOS-API is usable at all.
- Precise ZOSPy pythonnet version pin as of v2.1.5 (fetch didn't confirm current requirement post the "Python.NET 3.x fixed" note).
- Correct depth-of-focus prefactor convention (±2λF² vs. 4λF²) — needs a primary textbook source (e.g. Smith, *Modern Optical Engineering*) before hard-coding.
- opticspy and zmxtools current status — could not confirm they are still maintained or even still exist in usable form.
- pyoptools/KrakenOS exact license text and current Python-version support.
