# Optical design review

Action: sensitivity. Outcome: completed.

Local receipt consistency and recorded artifact hashes verified.

No accepted candidate. Rejected or partial results remain diagnostic evidence.

This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.

## Provenance

| Item | Recorded value |
| --- | --- |
| source | {&quot;path&quot;: &quot;C:\\\\Users\\\\erict\\\\OneDrive\\\\Desktop\\\\Projects\\\\optical-design-v1\\\\docs\\\\research\\\\full-release\\\\installed-final-workflow\\\\edit\\\\candidate-model.json&quot;, &quot;sha256&quot;: &quot;a124eab4a27842e5eae280696dcc2ef250605214f5b9d215c63abd5f1780c3aa&quot;} |
| source\_unchanged | True |
| baseline\_restored | True |
| saved\_candidate\_verified | False |
| evaluations | 5 |
| python\_version | 3.11.15 |
| error | unavailable |

Independent validation: not recorded

## Engine and model inspection

~~~json
{
  "name": "Optiland",
  "version": "0.6.2"
}
~~~

## Requirements and measurements

### Baseline requirements

| Requirement | Status | Value / reason | Unit | Constraint |
| --- | --- | --- | --- | --- |
| focal-length | pass | 49.05139286997028 | mm | {&quot;id&quot;: &quot;focal-length&quot;, &quot;max&quot;: 51, &quot;metric&quot;: &quot;efl\_mm&quot;, &quot;min&quot;: 48, &quot;unit&quot;: &quot;mm&quot;} |
| track | pass | 51.82 | mm | {&quot;id&quot;: &quot;track&quot;, &quot;max&quot;: 65, &quot;metric&quot;: &quot;total\_track\_mm&quot;, &quot;unit&quot;: &quot;mm&quot;} |
| spot | pass | 14.816087681558889 | um | {&quot;field&quot;: 1, &quot;id&quot;: &quot;spot&quot;, &quot;max&quot;: 30, &quot;metric&quot;: &quot;rms\_spot\_um&quot;, &quot;unit&quot;: &quot;um&quot;, &quot;wavelength&quot;: 1} |
| contrast-t | pass | 0.4724818125434799 | 1 | {&quot;axis&quot;: &quot;tangential&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast-t&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |
| contrast-s | pass | 0.4724818125433904 | 1 | {&quot;axis&quot;: &quot;sagittal&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast-s&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |

### Metric comparison

| Metric identity | Baseline | Rejected / diagnostic candidate | Delta | Unit |
| --- | --- | --- | --- | --- |
| efl\_mm | 49.05139286997028 | unavailable | unavailable | mm |
| mtf\|f=1\|w=1\|nu=20\|axis=sagittal | 0.4724818125433904 | unavailable | unavailable | 1 |
| mtf\|f=1\|w=1\|nu=20\|axis=tangential | 0.4724818125434799 | unavailable | unavailable | 1 |
| rms\_spot\_um\|f=1\|w=1 | 14.816087681558889 | unavailable | unavailable | um |
| total\_track\_mm | 51.82 | unavailable | unavailable | mm |

## Physical fields and wavelengths

Indices are 1-based engine selections. Physical field coordinates and wavelength values are shown only when recorded; unavailable coordinates are not inferred from indices.

| Evaluation | Metric identity | Physical field \(recorded units\) | Wavelength \(um\) | Analysis settings / identity |
| --- | --- | --- | --- | --- |
| Baseline | rms\_spot\_um\|f=1\|w=1 | \[0.0, 0.0\] | 0.55 | {&quot;distribution&quot;: &quot;hexapolar&quot;, &quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;method&quot;: &quot;geometric RMS radius about centroid&quot;, &quot;num\_rings&quot;: 16, &quot;sampled\_rays&quot;: 817, &quot;sampling&quot;: 64, &quot;scalar&quot;: true, &quot;transmitted\_rays&quot;: 817, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=tangential | \[0.0, 0.0\] | 0.55 | {&quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;frequency\_range\_cyc\_per\_mm&quot;: \[0.0, 535.965602730662\], &quot;interpolation&quot;: &quot;linear, no extrapolation&quot;, &quot;method&quot;: &quot;scalar FFT MTF&quot;, &quot;sampling&quot;: 64, &quot;scalar&quot;: true, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | \[0.0, 0.0\] | 0.55 | {&quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;frequency\_range\_cyc\_per\_mm&quot;: \[0.0, 535.965602730662\], &quot;interpolation&quot;: &quot;linear, no extrapolation&quot;, &quot;method&quot;: &quot;scalar FFT MTF&quot;, &quot;sampling&quot;: 64, &quot;scalar&quot;: true, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |

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

MTF: 2 recorded samples; chart included in standalone HTML.

### RMS spot radius

RMS spot radius: 1 recorded samples; chart included in standalone HTML.

## Prescription changes

Data unavailable.

No change table does not certify unchanged geometry when inspection data are missing.

## Axial schematic

Axial schematic only — surface vertices along the optical axis. No traced rays, lens sag, clear apertures, or imaging performance are depicted.

Recorded axial coordinates \(mm\).

| Surface index | Axial vertex \(mm\) |
| --- | --- |
| 1 | 0.0 |
| 2 | 5.0 |
| 3 | 51.82 |

## Sensitivity comparison

| Surface / parameter | Step \(mm\) | Metric identity | Derivative \(unit/mm\) | Declared-step effect \(unit\) | Nonlinearity indicator |
| --- | --- | --- | --- | --- | --- |
| 1 / radius\_mm | 0.1 | efl\_mm | 0.48199429193541476 | 0.048199429193541476 | 0.0010173698139172812 |
| 1 / radius\_mm | 0.1 | total\_track\_mm | 0.0 | 0.0 | 0.0 |
| 1 / radius\_mm | 0.1 | rms\_spot\_um\|f=1\|w=1 | -0.8741331056534918 | 0.08741331056534918 | 1.0 |
| 1 / radius\_mm | 0.1 | mtf\|f=1\|w=1\|nu=20\|axis=tangential | -0.6520223014112994 | 0.06520223014112994 | 0.24619745448463265 |
| 1 / radius\_mm | 0.1 | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | -0.6520223014112686 | 0.06520223014112686 | 0.24619745448230687 |
| 2 / thickness\_mm | 0.01 | efl\_mm | 0.0 | 0.0 | 0.0 |
| 2 / thickness\_mm | 0.01 | total\_track\_mm | 0.999999999999801 | 0.00999999999999801 | 0.0 |
| 2 / thickness\_mm | 0.01 | rms\_spot\_um\|f=1\|w=1 | 1.4919062014521423 | 0.014919062014521423 | 1.0 |
| 2 / thickness\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=tangential | 1.3282615961174167 | 0.013282615961174167 | 0.04969303043820356 |
| 2 / thickness\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | 1.3282615961045963 | 0.013282615961045963 | 0.049693030440189814 |

## Local sensitivity derivatives

~~~json
[
  {
    "baseline_mm": 50.0,
    "metrics": [
      {
        "baseline_value": 49.05139286997028,
        "declared_step_effect": 0.048199429193541476,
        "derivative_per_mm": 0.48199429193541476,
        "max_absolute_step_effect": 0.04824846583785103,
        "metric": "efl_mm",
        "metric_key": "efl_mm",
        "minus_delta": -0.04824846583785103,
        "minus_value": 49.00314440413243,
        "nonlinearity_indicator": 0.0010173698139172812,
        "plus_delta": 0.048150392549231924,
        "plus_value": 49.09954326251951,
        "second_derivative_per_mm2": -0.009807328861910491,
        "second_difference": -9.807328861910491e-05,
        "unit": "mm"
      },
      {
        "baseline_value": 51.82,
        "declared_step_effect": 0.0,
        "derivative_per_mm": 0.0,
        "max_absolute_step_effect": 0.0,
        "metric": "total_track_mm",
        "metric_key": "total_track_mm",
        "minus_delta": 0.0,
        "minus_value": 51.82,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.0,
        "plus_value": 51.82,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "mm"
      },
      {
        "baseline_value": 14.816087681558889,
        "declared_step_effect": 0.08741331056534918,
        "derivative_per_mm": -0.8741331056534918,
        "field": 1,
        "max_absolute_step_effect": 0.5526962398200084,
        "metric": "rms_spot_um",
        "metric_key": "rms_spot_um|f=1|w=1",
        "minus_delta": 0.5526962398200084,
        "minus_value": 15.368783921378897,
        "nonlinearity_indicator": 1.0,
        "plus_delta": 0.37786961868931,
        "plus_value": 15.193957300248199,
        "second_derivative_per_mm2": 93.05658585093184,
        "second_difference": 0.9305658585093184,
        "unit": "um",
        "wavelength": 1
      },
      {
        "axis": "tangential",
        "baseline_value": 0.4724818125434799,
        "declared_step_effect": 0.06520223014112994,
        "derivative_per_mm": -0.6520223014112994,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.08125485322859732,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "minus_delta": 0.04914960705366256,
        "minus_value": 0.5216314195971424,
        "nonlinearity_indicator": 0.24619745448463265,
        "plus_delta": -0.08125485322859732,
        "plus_value": 0.39122695931488255,
        "second_derivative_per_mm2": -3.2105246174934763,
        "second_difference": -0.032105246174934765,
        "unit": "1",
        "wavelength": 1
      },
      {
        "axis": "sagittal",
        "baseline_value": 0.4724818125433904,
        "declared_step_effect": 0.06520223014112686,
        "derivative_per_mm": -0.6520223014112686,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.08125485322844184,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "minus_delta": 0.04914960705381188,
        "minus_value": 0.5216314195972023,
        "nonlinearity_indicator": 0.24619745448230687,
        "plus_delta": -0.08125485322844184,
        "plus_value": 0.39122695931494855,
        "second_derivative_per_mm2": -3.2105246174629953,
        "second_difference": -0.03210524617462995,
        "unit": "1",
        "wavelength": 1
      }
    ],
    "objective": {
      "baseline_value": 0.5038509880152916,
      "declared_step_effect": 0.021808979297525566,
      "derivative_per_mm": 0.21808979297525566,
      "max_absolute_step_effect": 0.035950623611530896,
      "minus_delta": -0.007667334983520235,
      "minus_value": 0.49618365303177137,
      "nonlinearity_indicator": 0.6484321948808413,
      "plus_delta": 0.035950623611530896,
      "plus_value": 0.5398016116268225,
      "second_derivative_per_mm2": 2.828328862801066,
      "second_difference": 0.02828328862801066,
      "unit": "1"
    },
    "parameter": "radius_mm",
    "parameter_index": 0,
    "step_mm": 0.1,
    "surface": 1
  },
  {
    "baseline_mm": 46.82,
    "metrics": [
      {
        "baseline_value": 49.05139286997028,
        "declared_step_effect": 0.0,
        "derivative_per_mm": 0.0,
        "max_absolute_step_effect": 0.0,
        "metric": "efl_mm",
        "metric_key": "efl_mm",
        "minus_delta": 0.0,
        "minus_value": 49.05139286997028,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.0,
        "plus_value": 49.05139286997028,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "mm"
      },
      {
        "baseline_value": 51.82,
        "declared_step_effect": 0.00999999999999801,
        "derivative_per_mm": 0.999999999999801,
        "max_absolute_step_effect": 0.00999999999999801,
        "metric": "total_track_mm",
        "metric_key": "total_track_mm",
        "minus_delta": -0.00999999999999801,
        "minus_value": 51.81,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.00999999999999801,
        "plus_value": 51.83,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "mm"
      },
      {
        "baseline_value": 14.816087681558889,
        "declared_step_effect": 0.014919062014521423,
        "derivative_per_mm": 1.4919062014521423,
        "field": 1,
        "max_absolute_step_effect": 0.03390649068059304,
        "metric": "rms_spot_um",
        "metric_key": "rms_spot_um|f=1|w=1",
        "minus_delta": 0.004068366651550193,
        "minus_value": 14.820156048210439,
        "nonlinearity_indicator": 1.0,
        "plus_delta": 0.03390649068059304,
        "plus_value": 14.849994172239482,
        "second_derivative_per_mm2": 379.7485733214323,
        "second_difference": 0.03797485733214323,
        "unit": "um",
        "wavelength": 1
      },
      {
        "axis": "tangential",
        "baseline_value": 0.4724818125434799,
        "declared_step_effect": 0.013282615961174167,
        "derivative_per_mm": 1.3282615961174167,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.013942669400431762,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "minus_delta": -0.013942669400431762,
        "minus_value": 0.4585391431430481,
        "nonlinearity_indicator": 0.04969303043820356,
        "plus_delta": 0.01262256252191657,
        "plus_value": 0.48510437506539644,
        "second_derivative_per_mm2": -13.201068785151925,
        "second_difference": -0.0013201068785151926,
        "unit": "1",
        "wavelength": 1
      },
      {
        "axis": "sagittal",
        "baseline_value": 0.4724818125433904,
        "declared_step_effect": 0.013282615961045963,
        "derivative_per_mm": 1.3282615961045963,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.01394266940032357,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "minus_delta": -0.01394266940032357,
        "minus_value": 0.4585391431430668,
        "nonlinearity_indicator": 0.049693030440189814,
        "plus_delta": 0.012622562521768355,
        "plus_value": 0.48510437506515874,
        "second_derivative_per_mm2": -13.201068785552161,
        "second_difference": -0.0013201068785552161,
        "unit": "1",
        "wavelength": 1
      }
    ],
    "objective": {
      "baseline_value": 0.5038509880152916,
      "declared_step_effect": 0.00536831247187014,
      "derivative_per_mm": -0.536831247187014,
      "max_absolute_step_effect": 0.0059344313979923236,
      "minus_delta": 0.0059344313979923236,
      "minus_value": 0.5097854194132839,
      "nonlinearity_indicator": 0.10545565838215197,
      "plus_delta": -0.004802193545747957,
      "plus_value": 0.49904879446954364,
      "second_derivative_per_mm2": 11.322378522443666,
      "second_difference": 0.0011322378522443666,
      "unit": "1"
    },
    "parameter": "thickness_mm",
    "parameter_index": 1,
    "step_mm": 0.01,
    "surface": 2
  }
]
~~~

## Sensitivity rankings

~~~json
[
  {
    "metric_key": "efl_mm",
    "parameters": [
      {
        "declared_step_effect": 0.048199429193541476,
        "metric_key": "efl_mm",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.1,
        "surface": 1,
        "unit": "mm"
      },
      {
        "declared_step_effect": 0.0,
        "metric_key": "efl_mm",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "mm"
      }
    ],
    "unit": "mm"
  },
  {
    "metric_key": "total_track_mm",
    "parameters": [
      {
        "declared_step_effect": 0.00999999999999801,
        "metric_key": "total_track_mm",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "mm"
      },
      {
        "declared_step_effect": 0.0,
        "metric_key": "total_track_mm",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.1,
        "surface": 1,
        "unit": "mm"
      }
    ],
    "unit": "mm"
  },
  {
    "metric_key": "rms_spot_um|f=1|w=1",
    "parameters": [
      {
        "declared_step_effect": 0.08741331056534918,
        "metric_key": "rms_spot_um|f=1|w=1",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.1,
        "surface": 1,
        "unit": "um"
      },
      {
        "declared_step_effect": 0.014919062014521423,
        "metric_key": "rms_spot_um|f=1|w=1",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "um"
      }
    ],
    "unit": "um"
  },
  {
    "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
    "parameters": [
      {
        "declared_step_effect": 0.06520223014112994,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.1,
        "surface": 1,
        "unit": "1"
      },
      {
        "declared_step_effect": 0.013282615961174167,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "1"
      }
    ],
    "unit": "1"
  },
  {
    "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
    "parameters": [
      {
        "declared_step_effect": 0.06520223014112686,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.1,
        "surface": 1,
        "unit": "1"
      },
      {
        "declared_step_effect": 0.013282615961045963,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "1"
      }
    ],
    "unit": "1"
  }
]
~~~

## Sensitivity trials

~~~json
[
  {
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
          "value": 49.00314440413243
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
          "value": 51.82
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
          "value": 15.368783921378897
        },
        {
          "id": "contrast-t",
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "requirement": {
            "axis": "tangential",
            "field": 1,
            "frequency": 20,
            "id": "contrast-t",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.5216314195971424
        },
        {
          "id": "contrast-s",
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "requirement": {
            "axis": "sagittal",
            "field": 1,
            "frequency": 20,
            "id": "contrast-s",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.5216314195972023
        }
      ]
    },
    "direction": -1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.82
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.82,
      "image_surface": 3,
      "import_restrictions": {
        "format": "Optiland native JSON",
        "restrictions": "Centered spherical/plane refractive surfaces in air; EPD; meridional angle fields; millimetres; scalar analysis; no solves, pickups, configurations, coatings, scattering, apodization or unsupported directives. Catalog glass requires an explicit catalog and exact material lookup. Native JSON export only."
      },
      "invariants": {
        "aperture": {
          "type": "EPD",
          "value": 10
        },
        "apodization": null,
        "fields": {
          "field_definition": {
            "field_type": "AngleField"
          },
          "fields": [
            {
              "vx": 0.0,
              "vy": 0.0,
              "weight": 1.0,
              "x": 0.0,
              "y": 0
            }
          ],
          "telecentric": false
        },
        "name": "Synthetic N-BK7 singlet matching defocused-singlet.zmx prescription",
        "pickups": [],
        "ray_tracer": {
          "ray_aiming_config": {
            "max_iter": 10,
            "mode": "paraxial",
            "tol": 1e-06
          }
        },
        "solves": {
          "solves": []
        },
        "surface_group": {
          "surfaces": [
            {
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": "-Infinity"
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "ObjectSurface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 0.0
                },
                "radius": 49.9,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": true,
              "material_post": {
                "catalog": "schott",
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\fuMY41APyLOqqIoR\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
                "match_policy": "strict",
                "max_wavelength": null,
                "min_wavelength": null,
                "name": "N-BK7",
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "reference": null,
                "robust_search": null,
                "type": "Material"
              },
              "thickness": 5,
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 5.0
                },
                "radius": -50.0,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "thickness": 0.0,
              "type": "Surface"
            }
          ]
        },
        "version": 1.0,
        "wavelengths": {
          "polarization": "ignore",
          "wavelengths": [
            {
              "is_primary": true,
              "unit": "um",
              "value": 0.55,
              "weight": 1.0
            }
          ]
        }
      },
      "prescription": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 49.9,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.82
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ],
      "surfaces": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 49.9,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.82
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ]
    },
    "kind": "perturbation",
    "measurements": [
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false,
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "metric": "efl_mm",
        "unit": "mm",
        "value": 49.00314440413243
      },
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.82
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 16,
          "sampled_rays": 817,
          "sampling": 64,
          "scalar": true,
          "transmitted_rays": 817,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 15.368783921378897,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            536.4992311101391
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.5216314195971424,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            536.4992311101391
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "sagittal",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.5216314195972023,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
      "aggregation": "weighted_rms",
      "direction": "minimize",
      "terms": [
        {
          "key": "efl_mm",
          "metric": "efl_mm",
          "normalized_residual": -0.4984277979337861,
          "scale": 2,
          "target": 50,
          "unit": "mm",
          "value": 49.00314440413243,
          "weight": 1,
          "weighted_residual": -0.222903687611095
        },
        {
          "field": 1,
          "key": "rms_spot_um|f=1|w=1",
          "metric": "rms_spot_um",
          "normalized_residual": 0.5122927973792966,
          "scale": 30,
          "target": 0,
          "unit": "um",
          "value": 15.368783921378897,
          "wavelength": 1,
          "weight": 2,
          "weighted_residual": 0.3240024137235431
        },
        {
          "axis": "tangential",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "metric": "mtf",
          "normalized_residual": -0.47836858040285757,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.5216314195971424,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.21393293281617265
        },
        {
          "axis": "sagittal",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "metric": "mtf",
          "normalized_residual": -0.4783685804027977,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.5216314195972023,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.2139329328161459
        }
      ],
      "unit": "1",
      "value": 0.49618365303177137
    },
    "objective_value": 0.49618365303177137,
    "parameter_index": 0,
    "parameters_mm": [
      49.9,
      46.82
    ],
    "requested_parameters_mm": [
      49.9,
      46.82
    ]
  },
  {
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
          "value": 49.09954326251951
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
          "value": 51.82
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
          "value": 15.193957300248199
        },
        {
          "id": "contrast-t",
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "requirement": {
            "axis": "tangential",
            "field": 1,
            "frequency": 20,
            "id": "contrast-t",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.39122695931488255
        },
        {
          "id": "contrast-s",
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "requirement": {
            "axis": "sagittal",
            "field": 1,
            "frequency": 20,
            "id": "contrast-s",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.39122695931494855
        }
      ]
    },
    "direction": 1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.82
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.82,
      "image_surface": 3,
      "import_restrictions": {
        "format": "Optiland native JSON",
        "restrictions": "Centered spherical/plane refractive surfaces in air; EPD; meridional angle fields; millimetres; scalar analysis; no solves, pickups, configurations, coatings, scattering, apodization or unsupported directives. Catalog glass requires an explicit catalog and exact material lookup. Native JSON export only."
      },
      "invariants": {
        "aperture": {
          "type": "EPD",
          "value": 10
        },
        "apodization": null,
        "fields": {
          "field_definition": {
            "field_type": "AngleField"
          },
          "fields": [
            {
              "vx": 0.0,
              "vy": 0.0,
              "weight": 1.0,
              "x": 0.0,
              "y": 0
            }
          ],
          "telecentric": false
        },
        "name": "Synthetic N-BK7 singlet matching defocused-singlet.zmx prescription",
        "pickups": [],
        "ray_tracer": {
          "ray_aiming_config": {
            "max_iter": 10,
            "mode": "paraxial",
            "tol": 1e-06
          }
        },
        "solves": {
          "solves": []
        },
        "surface_group": {
          "surfaces": [
            {
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": "-Infinity"
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "ObjectSurface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 0.0
                },
                "radius": 50.1,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": true,
              "material_post": {
                "catalog": "schott",
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\fuMY41APyLOqqIoR\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
                "match_policy": "strict",
                "max_wavelength": null,
                "min_wavelength": null,
                "name": "N-BK7",
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "reference": null,
                "robust_search": null,
                "type": "Material"
              },
              "thickness": 5,
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 5.0
                },
                "radius": -50.0,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "thickness": 0.0,
              "type": "Surface"
            }
          ]
        },
        "version": 1.0,
        "wavelengths": {
          "polarization": "ignore",
          "wavelengths": [
            {
              "is_primary": true,
              "unit": "um",
              "value": 0.55,
              "weight": 1.0
            }
          ]
        }
      },
      "prescription": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 50.1,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.82
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ],
      "surfaces": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 50.1,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.82
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ]
    },
    "kind": "perturbation",
    "measurements": [
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false,
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "metric": "efl_mm",
        "unit": "mm",
        "value": 49.09954326251951
      },
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.82
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 16,
          "sampled_rays": 817,
          "sampling": 64,
          "scalar": true,
          "transmitted_rays": 817,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 15.193957300248199,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            535.4341306247786
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.39122695931488255,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            535.4341306247786
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "sagittal",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.39122695931494855,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
      "aggregation": "weighted_rms",
      "direction": "minimize",
      "terms": [
        {
          "key": "efl_mm",
          "metric": "efl_mm",
          "normalized_residual": -0.45022836874024463,
          "scale": 2,
          "target": 50,
          "unit": "mm",
          "value": 49.09954326251951,
          "weight": 1,
          "weighted_residual": -0.20134824758040568
        },
        {
          "field": 1,
          "key": "rms_spot_um|f=1|w=1",
          "metric": "rms_spot_um",
          "normalized_residual": 0.5064652433416066,
          "scale": 30,
          "target": 0,
          "unit": "um",
          "value": 15.193957300248199,
          "wavelength": 1,
          "weight": 2,
          "weighted_residual": 0.32031674493418094
        },
        {
          "axis": "tangential",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "metric": "mtf",
          "normalized_residual": -0.6087730406851175,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.39122695931488255,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.27225158036823355
        },
        {
          "axis": "sagittal",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "metric": "mtf",
          "normalized_residual": -0.6087730406850514,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.39122695931494855,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.272251580368204
        }
      ],
      "unit": "1",
      "value": 0.5398016116268225
    },
    "objective_value": 0.5398016116268225,
    "parameter_index": 0,
    "parameters_mm": [
      50.1,
      46.82
    ],
    "requested_parameters_mm": [
      50.1,
      46.82
    ]
  },
  {
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
          "value": 51.81
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
          "value": 14.820156048210439
        },
        {
          "id": "contrast-t",
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "requirement": {
            "axis": "tangential",
            "field": 1,
            "frequency": 20,
            "id": "contrast-t",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.4585391431430481
        },
        {
          "id": "contrast-s",
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "requirement": {
            "axis": "sagittal",
            "field": 1,
            "frequency": 20,
            "id": "contrast-s",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.4585391431430668
        }
      ]
    },
    "direction": -1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.81
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.81,
      "image_surface": 3,
      "import_restrictions": {
        "format": "Optiland native JSON",
        "restrictions": "Centered spherical/plane refractive surfaces in air; EPD; meridional angle fields; millimetres; scalar analysis; no solves, pickups, configurations, coatings, scattering, apodization or unsupported directives. Catalog glass requires an explicit catalog and exact material lookup. Native JSON export only."
      },
      "invariants": {
        "aperture": {
          "type": "EPD",
          "value": 10
        },
        "apodization": null,
        "fields": {
          "field_definition": {
            "field_type": "AngleField"
          },
          "fields": [
            {
              "vx": 0.0,
              "vy": 0.0,
              "weight": 1.0,
              "x": 0.0,
              "y": 0
            }
          ],
          "telecentric": false
        },
        "name": "Synthetic N-BK7 singlet matching defocused-singlet.zmx prescription",
        "pickups": [],
        "ray_tracer": {
          "ray_aiming_config": {
            "max_iter": 10,
            "mode": "paraxial",
            "tol": 1e-06
          }
        },
        "solves": {
          "solves": []
        },
        "surface_group": {
          "surfaces": [
            {
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": "-Infinity"
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "ObjectSurface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 0.0
                },
                "radius": 50.0,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": true,
              "material_post": {
                "catalog": "schott",
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\fuMY41APyLOqqIoR\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
                "match_policy": "strict",
                "max_wavelength": null,
                "min_wavelength": null,
                "name": "N-BK7",
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "reference": null,
                "robust_search": null,
                "type": "Material"
              },
              "thickness": 5,
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 5.0
                },
                "radius": -50.0,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "thickness": 0.0,
              "type": "Surface"
            }
          ]
        },
        "version": 1.0,
        "wavelengths": {
          "polarization": "ignore",
          "wavelengths": [
            {
              "is_primary": true,
              "unit": "um",
              "value": 0.55,
              "weight": 1.0
            }
          ]
        }
      },
      "prescription": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 50.0,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.81
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ],
      "surfaces": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 50.0,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.81
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ]
    },
    "kind": "perturbation",
    "measurements": [
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false,
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "metric": "efl_mm",
        "unit": "mm",
        "value": 49.05139286997028
      },
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.81
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 16,
          "sampled_rays": 817,
          "sampling": 64,
          "scalar": true,
          "transmitted_rays": 817,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 14.820156048210439,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            535.965602730662
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.4585391431430481,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            535.965602730662
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "sagittal",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.4585391431430668,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
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
          "normalized_residual": 0.4940052016070146,
          "scale": 30,
          "target": 0,
          "unit": "um",
          "value": 14.820156048210439,
          "wavelength": 1,
          "weight": 2,
          "weighted_residual": 0.3124363226097677
        },
        {
          "axis": "tangential",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "metric": "mtf",
          "normalized_residual": -0.5414608568569519,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.4585391431430481,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.2421486566174855
        },
        {
          "axis": "sagittal",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "metric": "mtf",
          "normalized_residual": -0.5414608568569332,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.4585391431430668,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.24214865661747717
        }
      ],
      "unit": "1",
      "value": 0.5097854194132839
    },
    "objective_value": 0.5097854194132839,
    "parameter_index": 1,
    "parameters_mm": [
      50.0,
      46.81
    ],
    "requested_parameters_mm": [
      50.0,
      46.81
    ]
  },
  {
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
          "value": 51.83
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
          "value": 14.849994172239482
        },
        {
          "id": "contrast-t",
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "requirement": {
            "axis": "tangential",
            "field": 1,
            "frequency": 20,
            "id": "contrast-t",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.48510437506539644
        },
        {
          "id": "contrast-s",
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "requirement": {
            "axis": "sagittal",
            "field": 1,
            "frequency": 20,
            "id": "contrast-s",
            "metric": "mtf",
            "min": 0.3,
            "unit": "1",
            "wavelength": 1
          },
          "status": "pass",
          "unit": "1",
          "value": 0.48510437506515874
        }
      ]
    },
    "direction": 1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.83
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.83,
      "image_surface": 3,
      "import_restrictions": {
        "format": "Optiland native JSON",
        "restrictions": "Centered spherical/plane refractive surfaces in air; EPD; meridional angle fields; millimetres; scalar analysis; no solves, pickups, configurations, coatings, scattering, apodization or unsupported directives. Catalog glass requires an explicit catalog and exact material lookup. Native JSON export only."
      },
      "invariants": {
        "aperture": {
          "type": "EPD",
          "value": 10
        },
        "apodization": null,
        "fields": {
          "field_definition": {
            "field_type": "AngleField"
          },
          "fields": [
            {
              "vx": 0.0,
              "vy": 0.0,
              "weight": 1.0,
              "x": 0.0,
              "y": 0
            }
          ],
          "telecentric": false
        },
        "name": "Synthetic N-BK7 singlet matching defocused-singlet.zmx prescription",
        "pickups": [],
        "ray_tracer": {
          "ray_aiming_config": {
            "max_iter": 10,
            "mode": "paraxial",
            "tol": 1e-06
          }
        },
        "solves": {
          "solves": []
        },
        "surface_group": {
          "surfaces": [
            {
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": "-Infinity"
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "ObjectSurface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 0.0
                },
                "radius": 50.0,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": true,
              "material_post": {
                "catalog": "schott",
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\fuMY41APyLOqqIoR\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
                "match_policy": "strict",
                "max_wavelength": null,
                "min_wavelength": null,
                "name": "N-BK7",
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "reference": null,
                "robust_search": null,
                "type": "Material"
              },
              "thickness": 5,
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "conic": 0.0,
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0,
                  "z": 5.0
                },
                "radius": -50.0,
                "type": "StandardGeometry"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "type": "Surface"
            },
            {
              "aperture": null,
              "comment": "",
              "geometry": {
                "cs": {
                  "reference_cs": null,
                  "rx": 0.0,
                  "ry": 0.0,
                  "rz": 0.0,
                  "x": 0.0,
                  "y": 0.0
                },
                "radius": "Infinity",
                "type": "Plane"
              },
              "interaction_model": {
                "bsdf": null,
                "coating": null,
                "is_reflective": false,
                "type": "RefractiveReflectiveModel"
              },
              "is_stop": false,
              "material_post": {
                "absorp": 0.0,
                "index": 1.0,
                "propagation_model": {
                  "class": "HomogeneousPropagation"
                },
                "type": "IdealMaterial"
              },
              "thickness": 0.0,
              "type": "Surface"
            }
          ]
        },
        "version": 1.0,
        "wavelengths": {
          "polarization": "ignore",
          "wavelengths": [
            {
              "is_primary": true,
              "unit": "um",
              "value": 0.55,
              "weight": 1.0
            }
          ]
        }
      },
      "prescription": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 50.0,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.83
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ],
      "surfaces": [
        {
          "index": 0,
          "is_image": false,
          "radius_mm": "Infinity",
          "thickness_mm": null
        },
        {
          "index": 1,
          "is_image": false,
          "radius_mm": 50.0,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.83
        },
        {
          "index": 3,
          "is_image": true,
          "radius_mm": "Infinity",
          "thickness_mm": 0.0
        }
      ]
    },
    "kind": "perturbation",
    "measurements": [
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false,
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "metric": "efl_mm",
        "unit": "mm",
        "value": 49.05139286997028
      },
      {
        "analysis": {
          "sampling": 64,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.83
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 16,
          "sampled_rays": 817,
          "sampling": 64,
          "scalar": true,
          "transmitted_rays": 817,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 14.849994172239482,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            535.965602730662
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.48510437506539644,
        "wavelength": 1
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            535.965602730662
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 64,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "sagittal",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.48510437506515874,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
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
          "normalized_residual": 0.4949998057413161,
          "scale": 30,
          "target": 0,
          "unit": "um",
          "value": 14.849994172239482,
          "wavelength": 1,
          "weight": 2,
          "weighted_residual": 0.3130653654966903
        },
        {
          "axis": "tangential",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=tangential",
          "metric": "mtf",
          "normalized_residual": -0.5148956249346035,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.48510437506539644,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.23026832373420184
        },
        {
          "axis": "sagittal",
          "field": 1,
          "frequency": 20,
          "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
          "metric": "mtf",
          "normalized_residual": -0.5148956249348413,
          "scale": 1,
          "target": 1,
          "unit": "1",
          "value": 0.48510437506515874,
          "wavelength": 1,
          "weight": 1,
          "weighted_residual": -0.23026832373430817
        }
      ],
      "unit": "1",
      "value": 0.49904879446954364
    },
    "objective_value": 0.49904879446954364,
    "parameter_index": 1,
    "parameters_mm": [
      50.0,
      46.83
    ],
    "requested_parameters_mm": [
      50.0,
      46.83
    ]
  }
]
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
      "normalized_residual": 0.4938695893852963,
      "scale": 30,
      "target": 0,
      "unit": "um",
      "value": 14.816087681558889,
      "wavelength": 1,
      "weight": 2,
      "weighted_residual": 0.3123505539099306
    },
    {
      "axis": "tangential",
      "field": 1,
      "frequency": 20,
      "key": "mtf|f=1|w=1|nu=20|axis=tangential",
      "metric": "mtf",
      "normalized_residual": -0.5275181874565201,
      "scale": 1,
      "target": 1,
      "unit": "1",
      "value": 0.4724818125434799,
      "wavelength": 1,
      "weight": 1,
      "weighted_residual": -0.23591330530405116
    },
    {
      "axis": "sagittal",
      "field": 1,
      "frequency": 20,
      "key": "mtf|f=1|w=1|nu=20|axis=sagittal",
      "metric": "mtf",
      "normalized_residual": -0.5275181874566096,
      "scale": 1,
      "target": 1,
      "unit": "1",
      "value": 0.4724818125433904,
      "wavelength": 1,
      "weight": 1,
      "weighted_residual": -0.2359133053040912
    }
  ],
  "unit": "1",
  "value": 0.5038509880152916
}
~~~

## Baseline physical model inventory

~~~json
{
  "axial_positions_mm": [
    "-Infinity",
    0.0,
    5.0,
    51.82
  ],
  "engine": {
    "name": "Optiland",
    "version": "0.6.2"
  },
  "focus_mm": 46.82,
  "image_surface": 3,
  "import_restrictions": {
    "format": "Optiland native JSON",
    "restrictions": "Centered spherical/plane refractive surfaces in air; EPD; meridional angle fields; millimetres; scalar analysis; no solves, pickups, configurations, coatings, scattering, apodization or unsupported directives. Catalog glass requires an explicit catalog and exact material lookup. Native JSON export only."
  },
  "invariants": {
    "aperture": {
      "type": "EPD",
      "value": 10
    },
    "apodization": null,
    "fields": {
      "field_definition": {
        "field_type": "AngleField"
      },
      "fields": [
        {
          "vx": 0.0,
          "vy": 0.0,
          "weight": 1.0,
          "x": 0.0,
          "y": 0
        }
      ],
      "telecentric": false
    },
    "name": "Synthetic N-BK7 singlet matching defocused-singlet.zmx prescription",
    "pickups": [],
    "ray_tracer": {
      "ray_aiming_config": {
        "max_iter": 10,
        "mode": "paraxial",
        "tol": 1e-06
      }
    },
    "solves": {
      "solves": []
    },
    "surface_group": {
      "surfaces": [
        {
          "comment": "",
          "geometry": {
            "cs": {
              "reference_cs": null,
              "rx": 0.0,
              "ry": 0.0,
              "rz": 0.0,
              "x": 0.0,
              "y": 0.0,
              "z": "-Infinity"
            },
            "radius": "Infinity",
            "type": "Plane"
          },
          "material_post": {
            "absorp": 0.0,
            "index": 1.0,
            "propagation_model": {
              "class": "HomogeneousPropagation"
            },
            "type": "IdealMaterial"
          },
          "type": "ObjectSurface"
        },
        {
          "aperture": null,
          "comment": "",
          "geometry": {
            "conic": 0.0,
            "cs": {
              "reference_cs": null,
              "rx": 0.0,
              "ry": 0.0,
              "rz": 0.0,
              "x": 0.0,
              "y": 0.0,
              "z": 0.0
            },
            "radius": 50.0,
            "type": "StandardGeometry"
          },
          "interaction_model": {
            "bsdf": null,
            "coating": null,
            "is_reflective": false,
            "type": "RefractiveReflectiveModel"
          },
          "is_stop": true,
          "material_post": {
            "catalog": "schott",
            "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\fuMY41APyLOqqIoR\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
            "match_policy": "strict",
            "max_wavelength": null,
            "min_wavelength": null,
            "name": "N-BK7",
            "propagation_model": {
              "class": "HomogeneousPropagation"
            },
            "reference": null,
            "robust_search": null,
            "type": "Material"
          },
          "thickness": 5,
          "type": "Surface"
        },
        {
          "aperture": null,
          "comment": "",
          "geometry": {
            "conic": 0.0,
            "cs": {
              "reference_cs": null,
              "rx": 0.0,
              "ry": 0.0,
              "rz": 0.0,
              "x": 0.0,
              "y": 0.0,
              "z": 5.0
            },
            "radius": -50.0,
            "type": "StandardGeometry"
          },
          "interaction_model": {
            "bsdf": null,
            "coating": null,
            "is_reflective": false,
            "type": "RefractiveReflectiveModel"
          },
          "is_stop": false,
          "material_post": {
            "absorp": 0.0,
            "index": 1.0,
            "propagation_model": {
              "class": "HomogeneousPropagation"
            },
            "type": "IdealMaterial"
          },
          "type": "Surface"
        },
        {
          "aperture": null,
          "comment": "",
          "geometry": {
            "cs": {
              "reference_cs": null,
              "rx": 0.0,
              "ry": 0.0,
              "rz": 0.0,
              "x": 0.0,
              "y": 0.0
            },
            "radius": "Infinity",
            "type": "Plane"
          },
          "interaction_model": {
            "bsdf": null,
            "coating": null,
            "is_reflective": false,
            "type": "RefractiveReflectiveModel"
          },
          "is_stop": false,
          "material_post": {
            "absorp": 0.0,
            "index": 1.0,
            "propagation_model": {
              "class": "HomogeneousPropagation"
            },
            "type": "IdealMaterial"
          },
          "thickness": 0.0,
          "type": "Surface"
        }
      ]
    },
    "version": 1.0,
    "wavelengths": {
      "polarization": "ignore",
      "wavelengths": [
        {
          "is_primary": true,
          "unit": "um",
          "value": 0.55,
          "weight": 1.0
        }
      ]
    }
  },
  "prescription": [
    {
      "index": 0,
      "is_image": false,
      "radius_mm": "Infinity",
      "thickness_mm": null
    },
    {
      "index": 1,
      "is_image": false,
      "radius_mm": 50.0,
      "thickness_mm": 5
    },
    {
      "index": 2,
      "is_image": false,
      "radius_mm": -50.0,
      "thickness_mm": 46.82
    },
    {
      "index": 3,
      "is_image": true,
      "radius_mm": "Infinity",
      "thickness_mm": 0.0
    }
  ],
  "surfaces": [
    {
      "index": 0,
      "is_image": false,
      "radius_mm": "Infinity",
      "thickness_mm": null
    },
    {
      "index": 1,
      "is_image": false,
      "radius_mm": 50.0,
      "thickness_mm": 5
    },
    {
      "index": 2,
      "is_image": false,
      "radius_mm": -50.0,
      "thickness_mm": 46.82
    },
    {
      "index": 3,
      "is_image": true,
      "radius_mm": "Infinity",
      "thickness_mm": 0.0
    }
  ]
}
~~~

## Evidence boundary

Missing data remain unavailable. A failed requirement remains failed. Sensitivity describes local finite steps; it is not a manufacturing yield estimate. Optimizer results do not prove a global optimum. Separate validation is reported only when present.

