# Optical design review

Action: optimize. Outcome: improved.

Local receipt consistency and recorded artifact hashes verified.

Accepted candidate: saved and verified in the recorded job.

This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.

## Provenance

| Item | Recorded value |
| --- | --- |
| source | {&quot;path&quot;: &quot;C:\\\\Users\\\\erict\\\\OneDrive\\\\Desktop\\\\Projects\\\\optical-design-v1\\\\docs\\\\research\\\\full-release\\\\final-mcp\\\\mcp-jobs\\\\025276915f4945698e78912c47bb5e95\\\\inputs\\\\model.zmx&quot;, &quot;sha256&quot;: &quot;4fe32615eac8c57b2d80c6745c99f0e3235f7586a2917e62dffe0aba2b9f7cf8&quot;} |
| source\_unchanged | True |
| baseline\_restored | True |
| saved\_candidate\_verified | True |
| evaluations | 41 |
| python\_version | 3.11.15 |
| error | unavailable |

Independent validation: passed

## Engine and model inspection

~~~json
{
  "license": "PremiumEdition",
  "name": "OpticStudio",
  "pythonnet_version": "3.1.0",
  "version": "24.1.0",
  "zospy_version": "2.1.5"
}
~~~

## Requirements and measurements

### Baseline requirements

| Requirement | Status | Value / reason | Unit | Constraint |
| --- | --- | --- | --- | --- |
| focal-length | pass | 49.05139286997028 | mm | {&quot;id&quot;: &quot;focal-length&quot;, &quot;max&quot;: 51, &quot;metric&quot;: &quot;efl\_mm&quot;, &quot;min&quot;: 48, &quot;unit&quot;: &quot;mm&quot;} |
| track | pass | 65.0 | mm | {&quot;id&quot;: &quot;track&quot;, &quot;max&quot;: 65, &quot;metric&quot;: &quot;total\_track\_mm&quot;, &quot;unit&quot;: &quot;mm&quot;} |
| spot | fail | 1023.625390429006 | um | {&quot;field&quot;: 1, &quot;id&quot;: &quot;spot&quot;, &quot;max&quot;: 30, &quot;metric&quot;: &quot;rms\_spot\_um&quot;, &quot;unit&quot;: &quot;um&quot;, &quot;wavelength&quot;: 1} |
| contrast-t | fail | 0.015642258462500985 | 1 | {&quot;axis&quot;: &quot;tangential&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast-t&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |
| contrast-s | fail | 0.015642258462500985 | 1 | {&quot;axis&quot;: &quot;sagittal&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast-s&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |

### Candidate requirements

| Requirement | Status | Value / reason | Unit | Constraint |
| --- | --- | --- | --- | --- |
| focal-length | pass | 49.71780612068609 | mm | {&quot;id&quot;: &quot;focal-length&quot;, &quot;max&quot;: 51, &quot;metric&quot;: &quot;efl\_mm&quot;, &quot;min&quot;: 48, &quot;unit&quot;: &quot;mm&quot;} |
| track | pass | 52.50684 | mm | {&quot;id&quot;: &quot;track&quot;, &quot;max&quot;: 65, &quot;metric&quot;: &quot;total\_track\_mm&quot;, &quot;unit&quot;: &quot;mm&quot;} |
| spot | pass | 17.85366256212163 | um | {&quot;field&quot;: 1, &quot;id&quot;: &quot;spot&quot;, &quot;max&quot;: 30, &quot;metric&quot;: &quot;rms\_spot\_um&quot;, &quot;unit&quot;: &quot;um&quot;, &quot;wavelength&quot;: 1} |
| contrast-t | pass | 0.462704422384276 | 1 | {&quot;axis&quot;: &quot;tangential&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast-t&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |
| contrast-s | pass | 0.462704422384276 | 1 | {&quot;axis&quot;: &quot;sagittal&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast-s&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |

### Metric comparison

| Metric identity | Baseline | Candidate | Delta | Unit |
| --- | --- | --- | --- | --- |
| efl\_mm | 49.05139286997028 | 49.71780612068609 | 0.6664132507158129 | mm |
| f\_number | 4.905139 | 4.971781 | 0.06664199999999987 | 1 |
| image\_distance\_mm | 60.0 | 47.5068359375 | -12.4931640625 | mm |
| mtf\|f=1\|w=1\|nu=20\|axis=sagittal | 0.015642258462500985 | 0.462704422384276 | 0.447062163921775 | 1 |
| mtf\|f=1\|w=1\|nu=20\|axis=tangential | 0.015642258462500985 | 0.462704422384276 | 0.447062163921775 | 1 |
| rms\_spot\_um\|f=1\|w=1 | 1023.625390429006 | 17.85366256212163 | -1005.7717278668844 | um |
| total\_track\_mm | 65.0 | 52.50684 | -12.493160000000003 | mm |

## Physical fields and wavelengths

Indices are 1-based engine selections. Physical field coordinates and wavelength values are shown only when recorded; unavailable coordinates are not inferred from indices.

| Evaluation | Metric identity | Physical field \(recorded units\) | Wavelength \(um\) | Analysis settings / identity |
| --- | --- | --- | --- | --- |
| Baseline | rms\_spot\_um\|f=1\|w=1 | \[0.0, 0.0\] | 0.55 | {&quot;field&quot;: 1, &quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;native\_analysis&quot;: &quot;StandardSpot&quot;, &quot;ray\_check\_count&quot;: 17, &quot;ray\_density&quot;: 8, &quot;reference&quot;: &quot;centroid&quot;, &quot;spectral\_mode&quot;: &quot;monochromatic&quot;, &quot;wavelength&quot;: 1, &quot;wavelength\_um&quot;: 0.55} |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=tangential | \[0.0, 0.0\] | 0.55 | {&quot;analysis&quot;: &quot;FFTMTF&quot;, &quot;frequency\_interpolation&quot;: &quot;linear; no extrapolation&quot;, &quot;polarization&quot;: false, &quot;sampling&quot;: 64} |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | \[0.0, 0.0\] | 0.55 | {&quot;analysis&quot;: &quot;FFTMTF&quot;, &quot;frequency\_interpolation&quot;: &quot;linear; no extrapolation&quot;, &quot;polarization&quot;: false, &quot;sampling&quot;: 64} |
| Candidate | rms\_spot\_um\|f=1\|w=1 | \[0.0, 0.0\] | 0.55 | {&quot;field&quot;: 1, &quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;native\_analysis&quot;: &quot;StandardSpot&quot;, &quot;ray\_check\_count&quot;: 17, &quot;ray\_density&quot;: 8, &quot;reference&quot;: &quot;centroid&quot;, &quot;spectral\_mode&quot;: &quot;monochromatic&quot;, &quot;wavelength&quot;: 1, &quot;wavelength\_um&quot;: 0.55} |
| Candidate | mtf\|f=1\|w=1\|nu=20\|axis=tangential | \[0.0, 0.0\] | 0.55 | {&quot;analysis&quot;: &quot;FFTMTF&quot;, &quot;frequency\_interpolation&quot;: &quot;linear; no extrapolation&quot;, &quot;polarization&quot;: false, &quot;sampling&quot;: 64} |
| Candidate | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | \[0.0, 0.0\] | 0.55 | {&quot;analysis&quot;: &quot;FFTMTF&quot;, &quot;frequency\_interpolation&quot;: &quot;linear; no extrapolation&quot;, &quot;polarization&quot;: false, &quot;sampling&quot;: 64} |

## Declared analysis coverage

~~~json
{
  "analysis": {
    "sampling": 64,
    "use_polarization": false
  },
  "fields": [
    1
  ],
  "frequencies_cyc_per_mm": [
    20
  ],
  "wavelengths": [
    1
  ]
}
~~~

## Recorded MTF and spot samples

Charts show only recorded samples. No fitted curve, inferred ray intercepts, or unmeasured frequency coverage is supplied. Exact values and full identities appear above.

### MTF

MTF: 4 recorded samples; chart included in standalone HTML.

### RMS spot radius

RMS spot radius: 2 recorded samples; chart included in standalone HTML.

## Prescription changes

| Surface | Parameter | Baseline | Candidate |
| --- | --- | --- | --- |
| 1 | radius\_mm | 50.0 | 51.40234375 |
| 2 | thickness\_mm | 60.0 | 47.5068359375 |
| image-space gap | focus\_mm | 60.0 | 47.5068359375 |

No change table does not certify unchanged geometry when inspection data are missing.

## Axial schematic

Axial schematic only — surface vertices along the optical axis. No traced rays, lens sag, clear apertures, or imaging performance are depicted.

Axial positions derived from recorded thicknesses; first real surface = 0 mm.

| Surface index | Axial vertex \(mm\) |
| --- | --- |
| 1 | 0.0 |
| 2 | 5.0 |
| 3 | 65.0 |

## Independent validation evidence

~~~json
{
  "baseline": {
    "assessment": {
      "passes": false,
      "requirements": [
        {
          "id": "focal-length",
          "key": "efl_mm",
          "requirement": {
            "id": "focal-length",
            "max": 51,
            "metric": "efl_mm",
            "min": 48,
            "unit": "mm"
          },
          "status": "pass",
          "unit": "mm",
          "value": 49.05139286997028
        },
        {
          "id": "track",
          "key": "total_track_mm",
          "requirement": {
            "id": "track",
            "max": 65,
            "metric": "total_track_mm",
            "unit": "mm"
          },
          "status": "pass",
          "unit": "mm",
          "value": 65.0
        },
        {
          "id": "contrast",
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "requirement": {
            "axis": "tangential",
            "field": 1,
            "frequency": 20,
            "id": "contrast",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "fail",
          "unit": "1",
          "value": 0.0007165152793272212
        },
        {
          "id": "spot",
          "key": "rms_spot_um|f=1|w=1",
          "requirement": {
            "field": 1,
            "id": "spot",
            "max": 30,
            "metric": "rms_spot_um",
            "unit": "um",
            "wavelength": 1
          },
          "status": "fail",
          "unit": "um",
          "value": 977.567318548919
        }
      ]
    },
    "inspection": {
      "engine": {
        "license": "PremiumEdition",
        "name": "OpticStudio",
        "pythonnet_version": "3.1.0",
        "version": "24.1.0",
        "zospy_version": "2.1.5"
      },
      "focus_mm": 60.0,
      "image_surface": 3,
      "invariants": {
        "aperture_mm": 10.0,
        "aperture_type": "EntrancePupilDiameter",
        "fields": [
          {
            "index": 1,
            "weight": 1.0,
            "x_deg": 0.0,
            "y_deg": 0.0
          }
        ],
        "lens_units": "mm",
        "surfaces": [
          {
            "aperture": "None",
            "asphere_coefficients": [],
            "coating": "",
            "conic": 0.0,
            "index": 0,
            "is_image": false,
            "is_stop": false,
            "material": "",
            "radius_mm": "Infinity",
            "semi_diameter_solve": "Automatic",
            "thickness_mm": "Infinity",
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "Standard"
          },
          {
            "aperture": "None",
            "asphere_coefficients": [
              {
                "order": 2,
                "unit": "mm^-1",
                "value": 0.0
              },
              {
                "order": 4,
                "unit": "mm^-3",
                "value": 1e-06
              },
              {
                "order": 6,
                "unit": "mm^-5",
                "value": -1e-09
              },
              {
                "order": 8,
                "unit": "mm^-7",
                "value": 0.0
              },
              {
                "order": 10,
                "unit": "mm^-9",
                "value": 0.0
              },
              {
                "order": 12,
                "unit": "mm^-11",
                "value": 0.0
              },
              {
                "order": 14,
                "unit": "mm^-13",
                "value": 0.0
              },
              {
                "order": 16,
                "unit": "mm^-15",
                "value": 1e-20
              }
            ],
            "coating": "",
            "conic": -0.5,
            "index": 1,
            "is_image": false,
            "is_stop": true,
            "material": "N-BK7",
            "radius_mm": 50.0,
            "semi_diameter_solve": "Automatic",
            "thickness_mm": 5.0,
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "EvenAspheric"
          },
          {
            "aperture": "None",
            "asphere_coefficients": [],
            "coating": "",
            "conic": 0.0,
            "index": 2,
            "is_image": false,
            "is_stop": false,
            "material": "",
            "radius_mm": -50.0,
            "semi_diameter_solve": "Automatic",
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "Standard"
          },
          {
            "aperture": "None",
            "asphere_coefficients": [],
            "coating": "",
            "conic": 0.0,
            "index": 3,
            "is_image": true,
            "is_stop": false,
            "material": "",
            "radius_mm": "Infinity",
            "semi_diameter_solve": "Automatic",
            "thickness_mm": "Infinity",
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "Standard"
          }
        ],
        "wavelengths": [
          {
            "index": 1,
            "primary": true,
            "um": 0.55,
            "weight": 1.0
          }
        ]
      },
      "limits": [
        "Sequential centered Standard conic/EvenAspheric refractive systems; fixed shape coefficients; angle fields; mm; EPD.",
        "Geometric centroid RMS spot and scalar FFT MTF are distinct metrics.",
        "A sparse pupil ray check detects gross failures; it is not a full vignetting analysis."
      ],
      "surfaces": [
        {
          "aperture": "None",
          "asphere_coefficients": [],
          "coating": "",
          "conic": 0.0,
          "index": 0,
          "is_image": false,
          "is_stop": false,
          "material": "",
          "radius_mm": "Infinity",
          "semi_diameter_solve": "Automatic",
          "thickness_mm": "Infinity",
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "Standard"
        },
        {
          "aperture": "None",
          "asphere_coefficients": [
            {
              "order": 2,
              "unit": "mm^-1",
              "value": 0.0
            },
            {
              "order": 4,
              "unit": "mm^-3",
              "value": 1e-06
            },
            {
              "order": 6,
              "unit": "mm^-5",
              "value": -1e-09
            },
            {
              "order": 8,
              "unit": "mm^-7",
              "value": 0.0
            },
            {
              "order": 10,
              "unit": "mm^-9",
              "value": 0.0
            },
            {
              "order": 12,
              "unit": "mm^-11",
              "value": 0.0
            },
            {
              "order": 14,
              "unit": "mm^-13",
              "value": 0.0
            },
            {
              "order": 16,
              "unit": "mm^-15",
              "value": 1e-20
            }
          ],
          "coating": "",
          "conic": -0.5,
          "index": 1,
          "is_image": false,
          "is_stop": true,
          "material": "N-BK7",
          "radius_mm": 50.0,
          "semi_diameter_solve": "Automatic",
          "thickness_mm": 5.0,
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "EvenAspheric"
        },
        {
          "aperture": "None",
          "asphere_coefficients": [],
          "coating": "",
          "conic": 0.0,
          "index": 2,
          "is_image": false,
          "is_stop": false,
          "material": "",
          "radius_mm": -50.0,
          "semi_diameter_solve": "Automatic",
          "thickness_mm": 60.0,
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "Standard"
        },
        {
          "aperture": "None",
          "asphere_coefficients": [],
          "coating": "",
          "conic": 0.0,
          "index": 3,
          "is_image": true,
          "is_stop": false,
          "material": "",
          "radius_mm": "Infinity",
          "semi_diameter_solve": "Automatic",
          "thickness_mm": "Infinity",
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "Standard"
        }
      ]
    },
    "kind": "validation_baseline",
    "measurements": [
      {
        "metric": "efl_mm",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "mm",
        "value": 49.05139286997028
      },
      {
        "metric": "f_number",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "1",
        "value": 4.905139
      },
      {
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 65.0
      },
      {
        "metric": "image_distance_mm",
        "unit": "mm",
        "value": 60.0
      },
      {
        "field": 1,
        "metric": "rms_spot_um",
        "settings": {
          "field": 1,
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "native_analysis": "StandardSpot",
          "ray_check_count": 17,
          "ray_density": 32,
          "reference": "centroid",
          "spectral_mode": "monochromatic",
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "um",
        "value": 977.567318548919,
        "wavelength": 1
      },
      {
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "settings": {
          "analysis": "FFTMTF",
          "frequency_interpolation": "linear; no extrapolation",
          "polarization": false,
          "sampling": 256
        },
        "unit": "1",
        "value": 0.0007165152793272212,
        "wavelength": 1
      },
      {
        "axis": "sagittal",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "settings": {
          "analysis": "FFTMTF",
          "frequency_interpolation": "linear; no extrapolation",
          "polarization": false,
          "sampling": 256
        },
        "unit": "1",
        "value": 0.0007165152793272212,
        "wavelength": 1
      }
    ],
    "parameters_mm": [
      50.0,
      60.0
    ]
  },
  "budget_policy": "all analyses share optimization budget; validation stage also obeys its own timeout",
  "candidate": {
    "assessment": {
      "passes": true,
      "requirements": [
        {
          "id": "focal-length",
          "key": "efl_mm",
          "requirement": {
            "id": "focal-length",
            "max": 51,
            "metric": "efl_mm",
            "min": 48,
            "unit": "mm"
          },
          "status": "pass",
          "unit": "mm",
          "value": 49.71780612068609
        },
        {
          "id": "track",
          "key": "total_track_mm",
          "requirement": {
            "id": "track",
            "max": 65,
            "metric": "total_track_mm",
            "unit": "mm"
          },
          "status": "pass",
          "unit": "mm",
          "value": 52.50684
        },
        {
          "id": "contrast",
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "requirement": {
            "axis": "tangential",
            "field": 1,
            "frequency": 20,
            "id": "contrast",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.46625510647453605
        },
        {
          "id": "spot",
          "key": "rms_spot_um|f=1|w=1",
          "requirement": {
            "field": 1,
            "id": "spot",
            "max": 30,
            "metric": "rms_spot_um",
            "unit": "um",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "um",
          "value": 15.308438621267047
        }
      ]
    },
    "inspection": {
      "engine": {
        "license": "PremiumEdition",
        "name": "OpticStudio",
        "pythonnet_version": "3.1.0",
        "version": "24.1.0",
        "zospy_version": "2.1.5"
      },
      "focus_mm": 47.5068359375,
      "image_surface": 3,
      "invariants": {
        "aperture_mm": 10.0,
        "aperture_type": "EntrancePupilDiameter",
        "fields": [
          {
            "index": 1,
            "weight": 1.0,
            "x_deg": 0.0,
            "y_deg": 0.0
          }
        ],
        "lens_units": "mm",
        "surfaces": [
          {
            "aperture": "None",
            "asphere_coefficients": [],
            "coating": "",
            "conic": 0.0,
            "index": 0,
            "is_image": false,
            "is_stop": false,
            "material": "",
            "radius_mm": "Infinity",
            "semi_diameter_solve": "Automatic",
            "thickness_mm": "Infinity",
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "Standard"
          },
          {
            "aperture": "None",
            "asphere_coefficients": [
              {
                "order": 2,
                "unit": "mm^-1",
                "value": 0.0
              },
              {
                "order": 4,
                "unit": "mm^-3",
                "value": 1e-06
              },
              {
                "order": 6,
                "unit": "mm^-5",
                "value": -1e-09
              },
              {
                "order": 8,
                "unit": "mm^-7",
                "value": 0.0
              },
              {
                "order": 10,
                "unit": "mm^-9",
                "value": 0.0
              },
              {
                "order": 12,
                "unit": "mm^-11",
                "value": 0.0
              },
              {
                "order": 14,
                "unit": "mm^-13",
                "value": 0.0
              },
              {
                "order": 16,
                "unit": "mm^-15",
                "value": 1e-20
              }
            ],
            "coating": "",
            "conic": -0.5,
            "index": 1,
            "is_image": false,
            "is_stop": true,
            "material": "N-BK7",
            "radius_mm": 51.40234375,
            "semi_diameter_solve": "Automatic",
            "thickness_mm": 5.0,
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "EvenAspheric"
          },
          {
            "aperture": "None",
            "asphere_coefficients": [],
            "coating": "",
            "conic": 0.0,
            "index": 2,
            "is_image": false,
            "is_stop": false,
            "material": "",
            "radius_mm": -50.0,
            "semi_diameter_solve": "Automatic",
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "Standard"
          },
          {
            "aperture": "None",
            "asphere_coefficients": [],
            "coating": "",
            "conic": 0.0,
            "index": 3,
            "is_image": true,
            "is_stop": false,
            "material": "",
            "radius_mm": "Infinity",
            "semi_diameter_solve": "Automatic",
            "thickness_mm": "Infinity",
            "tilts": [
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0,
              0.0
            ],
            "type": "Standard"
          }
        ],
        "wavelengths": [
          {
            "index": 1,
            "primary": true,
            "um": 0.55,
            "weight": 1.0
          }
        ]
      },
      "limits": [
        "Sequential centered Standard conic/EvenAspheric refractive systems; fixed shape coefficients; angle fields; mm; EPD.",
        "Geometric centroid RMS spot and scalar FFT MTF are distinct metrics.",
        "A sparse pupil ray check detects gross failures; it is not a full vignetting analysis."
      ],
      "surfaces": [
        {
          "aperture": "None",
          "asphere_coefficients": [],
          "coating": "",
          "conic": 0.0,
          "index": 0,
          "is_image": false,
          "is_stop": false,
          "material": "",
          "radius_mm": "Infinity",
          "semi_diameter_solve": "Automatic",
          "thickness_mm": "Infinity",
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "Standard"
        },
        {
          "aperture": "None",
          "asphere_coefficients": [
            {
              "order": 2,
              "unit": "mm^-1",
              "value": 0.0
            },
            {
              "order": 4,
              "unit": "mm^-3",
              "value": 1e-06
            },
            {
              "order": 6,
              "unit": "mm^-5",
              "value": -1e-09
            },
            {
              "order": 8,
              "unit": "mm^-7",
              "value": 0.0
            },
            {
              "order": 10,
              "unit": "mm^-9",
              "value": 0.0
            },
            {
              "order": 12,
              "unit": "mm^-11",
              "value": 0.0
            },
            {
              "order": 14,
              "unit": "mm^-13",
              "value": 0.0
            },
            {
              "order": 16,
              "unit": "mm^-15",
              "value": 1e-20
            }
          ],
          "coating": "",
          "conic": -0.5,
          "index": 1,
          "is_image": false,
          "is_stop": true,
          "material": "N-BK7",
          "radius_mm": 51.40234375,
          "semi_diameter_solve": "Automatic",
          "thickness_mm": 5.0,
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "EvenAspheric"
        },
        {
          "aperture": "None",
          "asphere_coefficients": [],
          "coating": "",
          "conic": 0.0,
          "index": 2,
          "is_image": false,
          "is_stop": false,
          "material": "",
          "radius_mm": -50.0,
          "semi_diameter_solve": "Automatic",
          "thickness_mm": 47.5068359375,
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "Standard"
        },
        {
          "aperture": "None",
          "asphere_coefficients": [],
          "coating": "",
          "conic": 0.0,
          "index": 3,
          "is_image": true,
          "is_stop": false,
          "material": "",
          "radius_mm": "Infinity",
          "semi_diameter_solve": "Automatic",
          "thickness_mm": "Infinity",
          "tilts": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "type": "Standard"
        }
      ]
    },
    "kind": "validation_candidate",
    "measurements": [
      {
        "metric": "efl_mm",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "mm",
        "value": 49.71780612068609
      },
      {
        "metric": "f_number",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "1",
        "value": 4.971781
      },
      {
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 52.50684
      },
      {
        "metric": "image_distance_mm",
        "unit": "mm",
        "value": 47.5068359375
      },
      {
        "field": 1,
        "metric": "rms_spot_um",
        "settings": {
          "field": 1,
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "native_analysis": "StandardSpot",
          "ray_check_count": 17,
          "ray_density": 32,
          "reference": "centroid",
          "spectral_mode": "monochromatic",
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "um",
        "value": 15.308438621267047,
        "wavelength": 1
      },
      {
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "settings": {
          "analysis": "FFTMTF",
          "frequency_interpolation": "linear; no extrapolation",
          "polarization": false,
          "sampling": 256
        },
        "unit": "1",
        "value": 0.46625510647453605,
        "wavelength": 1
      },
      {
        "axis": "sagittal",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "settings": {
          "analysis": "FFTMTF",
          "frequency_interpolation": "linear; no extrapolation",
          "polarization": false,
          "sampling": 256
        },
        "unit": "1",
        "value": 0.46625510647453605,
        "wavelength": 1
      }
    ],
    "parameters_mm": [
      51.40234375,
      47.5068359375
    ]
  },
  "evaluation_differences": [
    "analysis"
  ],
  "evaluations": 2,
  "scope": "separate-spec numerical check; not measured physical validation or unbiased holdout",
  "spec": {
    "analysis": {
      "sampling": 256,
      "use_polarization": false
    },
    "budget": {
      "max_evaluations": 7,
      "timeout_s": 120
    },
    "fields": [
      1
    ],
    "frequencies_cyc_per_mm": [
      20
    ],
    "minimum_gain": 0.001,
    "name": "Separate validation: higher sampling, frozen before optimization",
    "requirements": [
      {
        "id": "focal-length",
        "max": 51,
        "metric": "efl_mm",
        "min": 48,
        "unit": "mm"
      },
      {
        "id": "track",
        "max": 65,
        "metric": "total_track_mm",
        "unit": "mm"
      },
      {
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "id": "contrast",
        "metric": "mtf",
        "min": 0.3,
        "unit": "1",
        "wavelength": 1
      },
      {
        "field": 1,
        "id": "spot",
        "max": 30,
        "metric": "rms_spot_um",
        "unit": "um",
        "wavelength": 1
      }
    ],
    "schema": "1",
    "wavelengths": [
      1
    ]
  },
  "spec_sha256": "2d48a04a9f2c1efd5de2f763918c02236cae293e227cc568c3432645d65b9916",
  "status": "passed"
}
~~~

## Objective definition

~~~json
{
  "aggregation": "weighted_rms",
  "direction": "minimize",
  "terms": [
    {
      "metric": "efl_mm",
      "scale": 2,
      "target": 50,
      "unit": "mm",
      "weight": 1
    },
    {
      "field": 1,
      "metric": "rms_spot_um",
      "scale": 30,
      "target": 0,
      "unit": "um",
      "wavelength": 1,
      "weight": 2
    },
    {
      "axis": "tangential",
      "field": 1,
      "frequency": 20,
      "metric": "mtf",
      "scale": 1,
      "target": 1,
      "unit": "1",
      "wavelength": 1,
      "weight": 1
    },
    {
      "axis": "sagittal",
      "field": 1,
      "frequency": 20,
      "metric": "mtf",
      "scale": 1,
      "target": 1,
      "unit": "1",
      "wavelength": 1,
      "weight": 1
    }
  ]
}
~~~

## Baseline objective evidence

~~~json
{
  "aggregation": "weighted_rms",
  "direction": "minimize",
  "terms": [
    {
      "key": "efl_mm",
      "metric": "efl_mm",
      "normalized_residual": -0.4743035650148606,
      "scale": 2,
      "target": 50,
      "unit": "mm",
      "value": 49.05139286997028,
      "weight": 1,
      "weighted_residual": -0.21211500266874386
    },
    {
      "field": 1,
      "key": "rms_spot_um|f=1|w=1",
      "metric": "rms_spot_um",
      "normalized_residual": 34.12084634763353,
      "scale": 30,
      "target": 0,
      "unit": "um",
      "value": 1023.625390429006,
      "wavelength": 1,
      "weight": 2,
      "weighted_residual": 21.579918030231873
    },
    {
      "axis": "tangential",
      "field": 1,
      "frequency": 20,
      "key": "mtf|f=1|w=1|nu=20|axis=tangential",
      "metric": "mtf",
      "normalized_residual": -0.984357741537499,
      "scale": 1,
      "target": 1,
      "unit": "1",
      "value": 0.015642258462500985,
      "wavelength": 1,
      "weight": 1,
      "weighted_residual": -0.4402181648512032
    },
    {
      "axis": "sagittal",
      "field": 1,
      "frequency": 20,
      "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
      "metric": "mtf",
      "normalized_residual": -0.984357741537499,
      "scale": 1,
      "target": 1,
      "unit": "1",
      "value": 0.015642258462500985,
      "wavelength": 1,
      "weight": 1,
      "weighted_residual": -0.4402181648512032
    }
  ],
  "unit": "1",
  "value": 21.589938374882262
}
~~~

## Candidate objective evidence

~~~json
{
  "aggregation": "weighted_rms",
  "direction": "minimize",
  "terms": [
    {
      "key": "efl_mm",
      "metric": "efl_mm",
      "normalized_residual": -0.14109693965695413,
      "scale": 2,
      "target": 50,
      "unit": "mm",
      "value": 49.71780612068609,
      "weight": 1,
      "weighted_residual": -0.06310046969802706
    },
    {
      "field": 1,
      "key": "rms_spot_um|f=1|w=1",
      "metric": "rms_spot_um",
      "normalized_residual": 0.5951220854040543,
      "scale": 30,
      "target": 0,
      "unit": "um",
      "value": 17.85366256212163,
      "wavelength": 1,
      "weight": 2,
      "weighted_residual": 0.37638825514921187
    },
    {
      "axis": "tangential",
      "field": 1,
      "frequency": 20,
      "key": "mtf|f=1|w=1|nu=20|axis=tangential",
      "metric": "mtf",
      "normalized_residual": -0.537295577615724,
      "scale": 1,
      "target": 1,
      "unit": "1",
      "value": 0.462704422384276,
      "wavelength": 1,
      "weight": 1,
      "weighted_residual": -0.24028588711175464
    },
    {
      "axis": "sagittal",
      "field": 1,
      "frequency": 20,
      "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
      "metric": "mtf",
      "normalized_residual": -0.537295577615724,
      "scale": 1,
      "target": 1,
      "unit": "1",
      "value": 0.462704422384276,
      "wavelength": 1,
      "weight": 1,
      "weighted_residual": -0.24028588711175464
    }
  ],
  "unit": "1",
  "value": 0.5110033297157129
}
~~~

## Baseline physical model inventory

~~~json
{
  "engine": {
    "license": "PremiumEdition",
    "name": "OpticStudio",
    "pythonnet_version": "3.1.0",
    "version": "24.1.0",
    "zospy_version": "2.1.5"
  },
  "focus_mm": 60.0,
  "image_surface": 3,
  "invariants": {
    "aperture_mm": 10.0,
    "aperture_type": "EntrancePupilDiameter",
    "fields": [
      {
        "index": 1,
        "weight": 1.0,
        "x_deg": 0.0,
        "y_deg": 0.0
      }
    ],
    "lens_units": "mm",
    "surfaces": [
      {
        "aperture": "None",
        "asphere_coefficients": [],
        "coating": "",
        "conic": 0.0,
        "index": 0,
        "is_image": false,
        "is_stop": false,
        "material": "",
        "radius_mm": "Infinity",
        "semi_diameter_solve": "Automatic",
        "thickness_mm": "Infinity",
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "Standard"
      },
      {
        "aperture": "None",
        "asphere_coefficients": [
          {
            "order": 2,
            "unit": "mm^-1",
            "value": 0.0
          },
          {
            "order": 4,
            "unit": "mm^-3",
            "value": 1e-06
          },
          {
            "order": 6,
            "unit": "mm^-5",
            "value": -1e-09
          },
          {
            "order": 8,
            "unit": "mm^-7",
            "value": 0.0
          },
          {
            "order": 10,
            "unit": "mm^-9",
            "value": 0.0
          },
          {
            "order": 12,
            "unit": "mm^-11",
            "value": 0.0
          },
          {
            "order": 14,
            "unit": "mm^-13",
            "value": 0.0
          },
          {
            "order": 16,
            "unit": "mm^-15",
            "value": 1e-20
          }
        ],
        "coating": "",
        "conic": -0.5,
        "index": 1,
        "is_image": false,
        "is_stop": true,
        "material": "N-BK7",
        "radius_mm": 50.0,
        "semi_diameter_solve": "Automatic",
        "thickness_mm": 5.0,
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "EvenAspheric"
      },
      {
        "aperture": "None",
        "asphere_coefficients": [],
        "coating": "",
        "conic": 0.0,
        "index": 2,
        "is_image": false,
        "is_stop": false,
        "material": "",
        "radius_mm": -50.0,
        "semi_diameter_solve": "Automatic",
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "Standard"
      },
      {
        "aperture": "None",
        "asphere_coefficients": [],
        "coating": "",
        "conic": 0.0,
        "index": 3,
        "is_image": true,
        "is_stop": false,
        "material": "",
        "radius_mm": "Infinity",
        "semi_diameter_solve": "Automatic",
        "thickness_mm": "Infinity",
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "Standard"
      }
    ],
    "wavelengths": [
      {
        "index": 1,
        "primary": true,
        "um": 0.55,
        "weight": 1.0
      }
    ]
  },
  "limits": [
    "Sequential centered Standard conic/EvenAspheric refractive systems; fixed shape coefficients; angle fields; mm; EPD.",
    "Geometric centroid RMS spot and scalar FFT MTF are distinct metrics.",
    "A sparse pupil ray check detects gross failures; it is not a full vignetting analysis."
  ],
  "surfaces": [
    {
      "aperture": "None",
      "asphere_coefficients": [],
      "coating": "",
      "conic": 0.0,
      "index": 0,
      "is_image": false,
      "is_stop": false,
      "material": "",
      "radius_mm": "Infinity",
      "semi_diameter_solve": "Automatic",
      "thickness_mm": "Infinity",
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "Standard"
    },
    {
      "aperture": "None",
      "asphere_coefficients": [
        {
          "order": 2,
          "unit": "mm^-1",
          "value": 0.0
        },
        {
          "order": 4,
          "unit": "mm^-3",
          "value": 1e-06
        },
        {
          "order": 6,
          "unit": "mm^-5",
          "value": -1e-09
        },
        {
          "order": 8,
          "unit": "mm^-7",
          "value": 0.0
        },
        {
          "order": 10,
          "unit": "mm^-9",
          "value": 0.0
        },
        {
          "order": 12,
          "unit": "mm^-11",
          "value": 0.0
        },
        {
          "order": 14,
          "unit": "mm^-13",
          "value": 0.0
        },
        {
          "order": 16,
          "unit": "mm^-15",
          "value": 1e-20
        }
      ],
      "coating": "",
      "conic": -0.5,
      "index": 1,
      "is_image": false,
      "is_stop": true,
      "material": "N-BK7",
      "radius_mm": 50.0,
      "semi_diameter_solve": "Automatic",
      "thickness_mm": 5.0,
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "EvenAspheric"
    },
    {
      "aperture": "None",
      "asphere_coefficients": [],
      "coating": "",
      "conic": 0.0,
      "index": 2,
      "is_image": false,
      "is_stop": false,
      "material": "",
      "radius_mm": -50.0,
      "semi_diameter_solve": "Automatic",
      "thickness_mm": 60.0,
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "Standard"
    },
    {
      "aperture": "None",
      "asphere_coefficients": [],
      "coating": "",
      "conic": 0.0,
      "index": 3,
      "is_image": true,
      "is_stop": false,
      "material": "",
      "radius_mm": "Infinity",
      "semi_diameter_solve": "Automatic",
      "thickness_mm": "Infinity",
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "Standard"
    }
  ]
}
~~~

## Candidate physical model inventory

~~~json
{
  "engine": {
    "license": "PremiumEdition",
    "name": "OpticStudio",
    "pythonnet_version": "3.1.0",
    "version": "24.1.0",
    "zospy_version": "2.1.5"
  },
  "focus_mm": 47.5068359375,
  "image_surface": 3,
  "invariants": {
    "aperture_mm": 10.0,
    "aperture_type": "EntrancePupilDiameter",
    "fields": [
      {
        "index": 1,
        "weight": 1.0,
        "x_deg": 0.0,
        "y_deg": 0.0
      }
    ],
    "lens_units": "mm",
    "surfaces": [
      {
        "aperture": "None",
        "asphere_coefficients": [],
        "coating": "",
        "conic": 0.0,
        "index": 0,
        "is_image": false,
        "is_stop": false,
        "material": "",
        "radius_mm": "Infinity",
        "semi_diameter_solve": "Automatic",
        "thickness_mm": "Infinity",
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "Standard"
      },
      {
        "aperture": "None",
        "asphere_coefficients": [
          {
            "order": 2,
            "unit": "mm^-1",
            "value": 0.0
          },
          {
            "order": 4,
            "unit": "mm^-3",
            "value": 1e-06
          },
          {
            "order": 6,
            "unit": "mm^-5",
            "value": -1e-09
          },
          {
            "order": 8,
            "unit": "mm^-7",
            "value": 0.0
          },
          {
            "order": 10,
            "unit": "mm^-9",
            "value": 0.0
          },
          {
            "order": 12,
            "unit": "mm^-11",
            "value": 0.0
          },
          {
            "order": 14,
            "unit": "mm^-13",
            "value": 0.0
          },
          {
            "order": 16,
            "unit": "mm^-15",
            "value": 1e-20
          }
        ],
        "coating": "",
        "conic": -0.5,
        "index": 1,
        "is_image": false,
        "is_stop": true,
        "material": "N-BK7",
        "radius_mm": 51.40234375,
        "semi_diameter_solve": "Automatic",
        "thickness_mm": 5.0,
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "EvenAspheric"
      },
      {
        "aperture": "None",
        "asphere_coefficients": [],
        "coating": "",
        "conic": 0.0,
        "index": 2,
        "is_image": false,
        "is_stop": false,
        "material": "",
        "radius_mm": -50.0,
        "semi_diameter_solve": "Automatic",
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "Standard"
      },
      {
        "aperture": "None",
        "asphere_coefficients": [],
        "coating": "",
        "conic": 0.0,
        "index": 3,
        "is_image": true,
        "is_stop": false,
        "material": "",
        "radius_mm": "Infinity",
        "semi_diameter_solve": "Automatic",
        "thickness_mm": "Infinity",
        "tilts": [
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0,
          0.0
        ],
        "type": "Standard"
      }
    ],
    "wavelengths": [
      {
        "index": 1,
        "primary": true,
        "um": 0.55,
        "weight": 1.0
      }
    ]
  },
  "limits": [
    "Sequential centered Standard conic/EvenAspheric refractive systems; fixed shape coefficients; angle fields; mm; EPD.",
    "Geometric centroid RMS spot and scalar FFT MTF are distinct metrics.",
    "A sparse pupil ray check detects gross failures; it is not a full vignetting analysis."
  ],
  "surfaces": [
    {
      "aperture": "None",
      "asphere_coefficients": [],
      "coating": "",
      "conic": 0.0,
      "index": 0,
      "is_image": false,
      "is_stop": false,
      "material": "",
      "radius_mm": "Infinity",
      "semi_diameter_solve": "Automatic",
      "thickness_mm": "Infinity",
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "Standard"
    },
    {
      "aperture": "None",
      "asphere_coefficients": [
        {
          "order": 2,
          "unit": "mm^-1",
          "value": 0.0
        },
        {
          "order": 4,
          "unit": "mm^-3",
          "value": 1e-06
        },
        {
          "order": 6,
          "unit": "mm^-5",
          "value": -1e-09
        },
        {
          "order": 8,
          "unit": "mm^-7",
          "value": 0.0
        },
        {
          "order": 10,
          "unit": "mm^-9",
          "value": 0.0
        },
        {
          "order": 12,
          "unit": "mm^-11",
          "value": 0.0
        },
        {
          "order": 14,
          "unit": "mm^-13",
          "value": 0.0
        },
        {
          "order": 16,
          "unit": "mm^-15",
          "value": 1e-20
        }
      ],
      "coating": "",
      "conic": -0.5,
      "index": 1,
      "is_image": false,
      "is_stop": true,
      "material": "N-BK7",
      "radius_mm": 51.40234375,
      "semi_diameter_solve": "Automatic",
      "thickness_mm": 5.0,
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "EvenAspheric"
    },
    {
      "aperture": "None",
      "asphere_coefficients": [],
      "coating": "",
      "conic": 0.0,
      "index": 2,
      "is_image": false,
      "is_stop": false,
      "material": "",
      "radius_mm": -50.0,
      "semi_diameter_solve": "Automatic",
      "thickness_mm": 47.5068359375,
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "Standard"
    },
    {
      "aperture": "None",
      "asphere_coefficients": [],
      "coating": "",
      "conic": 0.0,
      "index": 3,
      "is_image": true,
      "is_stop": false,
      "material": "",
      "radius_mm": "Infinity",
      "semi_diameter_solve": "Automatic",
      "thickness_mm": "Infinity",
      "tilts": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "type": "Standard"
    }
  ]
}
~~~

## Evidence boundary

Missing data remain unavailable. A failed requirement remains failed. Sensitivity describes local finite steps; it is not a manufacturing yield estimate. Optimizer results do not prove a global optimum. Separate validation is reported only when present.

