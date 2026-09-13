# Optical design review

Action: inspect. Outcome: inspected.

Local receipt consistency and recorded artifact hashes verified.

No accepted candidate. Rejected or partial results remain diagnostic evidence.

This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.

## Provenance

| Item | Recorded value |
| --- | --- |
| source | {&quot;path&quot;: &quot;C:\\\\Users\\\\erict\\\\OneDrive\\\\Desktop\\\\Projects\\\\optical-design-v1\\\\docs\\\\research\\\\full-release\\\\final-mcp\\\\mcp-jobs\\\\8d9390a8dd804767bd95cfd6b35edb3d\\\\inputs\\\\model.zmx&quot;, &quot;sha256&quot;: &quot;4fe32615eac8c57b2d80c6745c99f0e3235f7586a2917e62dffe0aba2b9f7cf8&quot;} |
| source\_unchanged | True |
| baseline\_restored | True |
| saved\_candidate\_verified | False |
| evaluations | 0 |
| python\_version | 3.11.15 |
| error | unavailable |

Independent validation: not recorded

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

Requirements: not supplied. No requirement pass is inferred.

### Baseline requirements

Data unavailable.

### Metric comparison

Data unavailable.

## Physical fields and wavelengths

Indices are 1-based engine selections. Physical field coordinates and wavelength values are shown only when recorded; unavailable coordinates are not inferred from indices.

Data unavailable.

## Declared analysis coverage

Data unavailable.

## Recorded MTF and spot samples

Charts show only recorded samples. No fitted curve, inferred ray intercepts, or unmeasured frequency coverage is supplied. Exact values and full identities appear above.

## Prescription changes

Data unavailable.

No change table does not certify unchanged geometry when inspection data are missing.

## Axial schematic

Axial schematic only — surface vertices along the optical axis. No traced rays, lens sag, clear apertures, or imaging performance are depicted.

Axial positions derived from recorded thicknesses; first real surface = 0 mm.

| Surface index | Axial vertex \(mm\) |
| --- | --- |
| 1 | 0.0 |
| 2 | 5.0 |
| 3 | 65.0 |

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

## Evidence boundary

Missing data remain unavailable. A failed requirement remains failed. Sensitivity describes local finite steps; it is not a manufacturing yield estimate. Optimizer results do not prove a global optimum. Separate validation is reported only when present.

