# Optical design review

Action: sensitivity. Outcome: completed.

Local receipt consistency and recorded artifact hashes verified.

No accepted candidate. Rejected or partial results remain diagnostic evidence.

This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.

## Provenance

| Item | Recorded value |
| --- | --- |
| source | {&quot;path&quot;: &quot;C:\\\\Users\\\\erict\\\\OneDrive\\\\Desktop\\\\Projects\\\\optical-design-v1\\\\docs\\\\research\\\\full-release\\\\mcp-jobs\\\\4888293e06784bd4a6c0fa7ab7676fea\\\\inputs\\\\model.json&quot;, &quot;sha256&quot;: &quot;a910db4a1dc27b10e638d9fbaaced32563b433af04a5e4be442b508826e325da&quot;} |
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
| track | pass | 51.8191425091652 | mm | {&quot;id&quot;: &quot;track&quot;, &quot;max&quot;: 65, &quot;metric&quot;: &quot;total\_track\_mm&quot;, &quot;unit&quot;: &quot;mm&quot;} |
| contrast | pass | 0.4706893577206028 | 1 | {&quot;axis&quot;: &quot;tangential&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |
| spot | pass | 14.271818695450222 | um | {&quot;field&quot;: 1, &quot;id&quot;: &quot;spot&quot;, &quot;max&quot;: 30, &quot;metric&quot;: &quot;rms\_spot\_um&quot;, &quot;unit&quot;: &quot;um&quot;, &quot;wavelength&quot;: 1} |

### Metric comparison

| Metric identity | Baseline | Rejected / diagnostic candidate | Delta | Unit |
| --- | --- | --- | --- | --- |
| efl\_mm | 49.05139286997028 | unavailable | unavailable | mm |
| mtf\|f=1\|w=1\|nu=20\|axis=tangential | 0.4706893577206028 | unavailable | unavailable | 1 |
| rms\_spot\_um\|f=1\|w=1 | 14.271818695450222 | unavailable | unavailable | um |
| total\_track\_mm | 51.8191425091652 | unavailable | unavailable | mm |

## Physical fields and wavelengths

Indices are 1-based engine selections. Physical field coordinates and wavelength values are shown only when recorded; unavailable coordinates are not inferred from indices.

| Evaluation | Metric identity | Physical field \(recorded units\) | Wavelength \(um\) | Analysis settings / identity |
| --- | --- | --- | --- | --- |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=tangential | \[0.0, 0.0\] | 0.55 | {&quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;frequency\_range\_cyc\_per\_mm&quot;: \[0.0, 754.5920352882184\], &quot;interpolation&quot;: &quot;linear, no extrapolation&quot;, &quot;method&quot;: &quot;scalar FFT MTF&quot;, &quot;sampling&quot;: 128, &quot;scalar&quot;: true, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |
| Baseline | rms\_spot\_um\|f=1\|w=1 | \[0.0, 0.0\] | 0.55 | {&quot;distribution&quot;: &quot;hexapolar&quot;, &quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;method&quot;: &quot;geometric RMS radius about centroid&quot;, &quot;num\_rings&quot;: 32, &quot;sampled\_rays&quot;: 3169, &quot;sampling&quot;: 128, &quot;scalar&quot;: true, &quot;transmitted\_rays&quot;: 3169, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |

## Declared analysis coverage

~~~json
{
  "analysis": {
    "sampling": 128,
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

MTF: 1 recorded samples; chart included in standalone HTML.

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
| 3 | 51.8191425091652 |

## Sensitivity comparison

| Surface / parameter | Step \(mm\) | Metric identity | Derivative \(unit/mm\) | Declared-step effect \(unit\) | Nonlinearity indicator |
| --- | --- | --- | --- | --- | --- |
| 1 / radius\_mm | 0.01 | efl\_mm | 0.4819937980403921 | 0.004819937980403921 | 0.00010173698233801938 |
| 1 / radius\_mm | 0.01 | total\_track\_mm | 0.0 | 0.0 | 0.0 |
| 1 / radius\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=tangential | -0.7059272763451724 | 0.007059272763451724 | 0.024505471642962448 |
| 1 / radius\_mm | 0.01 | rms\_spot\_um\|f=1\|w=1 | 2.324144368239711 | 0.02324144368239711 | 0.20379667101395763 |
| 2 / thickness\_mm | 0.01 | efl\_mm | 0.0 | 0.0 | 0.0 |
| 2 / thickness\_mm | 0.01 | total\_track\_mm | 0.999999999999801 | 0.00999999999999801 | 0.0 |
| 2 / thickness\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=tangential | 1.4281245132548581 | 0.014281245132548581 | 0.04893478277994795 |
| 2 / thickness\_mm | 0.01 | rms\_spot\_um\|f=1\|w=1 | -4.9219918378829774 | 0.049219918378829774 | 0.3872366529591317 |

## Local sensitivity derivatives

~~~json
[
  {
    "baseline_mm": 50.0,
    "metrics": [
      {
        "baseline_value": 49.05139286997028,
        "declared_step_effect": 0.004819937980403921,
        "derivative_per_mm": 0.4819937980403921,
        "max_absolute_step_effect": 0.004820428346349104,
        "metric": "efl_mm",
        "metric_key": "efl_mm",
        "minus_delta": -0.004820428346349104,
        "minus_value": 49.04657244162393,
        "nonlinearity_indicator": 0.00010173698233801938,
        "plus_delta": 0.004819447614458738,
        "plus_value": 49.05621231758474,
        "second_derivative_per_mm2": -0.00980731890365405,
        "second_difference": -9.80731890365405e-07,
        "unit": "mm"
      },
      {
        "baseline_value": 51.8191425091652,
        "declared_step_effect": 0.0,
        "derivative_per_mm": 0.0,
        "max_absolute_step_effect": 0.0,
        "metric": "total_track_mm",
        "metric_key": "total_track_mm",
        "minus_delta": 0.0,
        "minus_value": 51.8191425091652,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.0,
        "plus_value": 51.8191425091652,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "mm"
      },
      {
        "axis": "tangential",
        "baseline_value": 0.4706893577206028,
        "declared_step_effect": 0.007059272763451724,
        "derivative_per_mm": -0.7059272763451724,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.007232263571976427,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "minus_delta": 0.0068862819549270204,
        "minus_value": 0.4775756396755298,
        "nonlinearity_indicator": 0.024505471642962448,
        "plus_delta": -0.007232263571976427,
        "plus_value": 0.46345709414862635,
        "second_derivative_per_mm2": -3.4598161704940678,
        "second_difference": -0.0003459816170494068,
        "unit": "1",
        "wavelength": 1
      },
      {
        "baseline_value": 14.271818695450222,
        "declared_step_effect": 0.02324144368239711,
        "derivative_per_mm": 2.324144368239711,
        "field": 1,
        "max_absolute_step_effect": 0.02797797253442802,
        "metric": "rms_spot_um",
        "metric_key": "rms_spot_um|f=1|w=1",
        "minus_delta": -0.018504914830366204,
        "minus_value": 14.253313780619855,
        "nonlinearity_indicator": 0.20379667101395763,
        "plus_delta": 0.02797797253442802,
        "plus_value": 14.29979666798465,
        "second_derivative_per_mm2": 94.73057704061816,
        "second_difference": 0.009473057704061816,
        "unit": "um",
        "wavelength": 1
      }
    ],
    "objective": {
      "baseline_value": 14.271818695450222,
      "declared_step_effect": 0.02324144368239711,
      "derivative_per_mm": 2.324144368239711,
      "max_absolute_step_effect": 0.02797797253442802,
      "minus_delta": -0.018504914830366204,
      "minus_value": 14.253313780619855,
      "nonlinearity_indicator": 0.20379667101395763,
      "plus_delta": 0.02797797253442802,
      "plus_value": 14.29979666798465,
      "second_derivative_per_mm2": 94.73057704061816,
      "second_difference": 0.009473057704061816,
      "unit": "um"
    },
    "parameter": "radius_mm",
    "parameter_index": 0,
    "step_mm": 0.01,
    "surface": 1
  },
  {
    "baseline_mm": 46.8191425091652,
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
        "baseline_value": 51.8191425091652,
        "declared_step_effect": 0.00999999999999801,
        "derivative_per_mm": 0.999999999999801,
        "max_absolute_step_effect": 0.00999999999999801,
        "metric": "total_track_mm",
        "metric_key": "total_track_mm",
        "minus_delta": -0.00999999999999801,
        "minus_value": 51.8091425091652,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.00999999999999801,
        "plus_value": 51.829142509165194,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "mm"
      },
      {
        "axis": "tangential",
        "baseline_value": 0.4706893577206028,
        "declared_step_effect": 0.014281245132548581,
        "derivative_per_mm": 1.4281245132548581,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.014980094760937035,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "minus_delta": -0.014980094760937035,
        "minus_value": 0.45570926295966574,
        "nonlinearity_indicator": 0.04893478277994795,
        "plus_delta": 0.013582395504160127,
        "plus_value": 0.4842717532247629,
        "second_derivative_per_mm2": -13.976992567769075,
        "second_difference": -0.0013976992567769075,
        "unit": "1",
        "wavelength": 1
      },
      {
        "baseline_value": 14.271818695450222,
        "declared_step_effect": 0.049219918378829774,
        "derivative_per_mm": -4.9219918378829774,
        "field": 1,
        "max_absolute_step_effect": 0.06827967483076947,
        "metric": "rms_spot_um",
        "metric_key": "rms_spot_um|f=1|w=1",
        "minus_delta": 0.06827967483076947,
        "minus_value": 14.340098370280991,
        "nonlinearity_indicator": 0.3872366529591317,
        "plus_delta": -0.030160161926890083,
        "plus_value": 14.241658533523331,
        "second_derivative_per_mm2": 381.1951290387938,
        "second_difference": 0.03811951290387938,
        "unit": "um",
        "wavelength": 1
      }
    ],
    "objective": {
      "baseline_value": 14.271818695450222,
      "declared_step_effect": 0.049219918378829774,
      "derivative_per_mm": -4.9219918378829774,
      "max_absolute_step_effect": 0.06827967483076947,
      "minus_delta": 0.06827967483076947,
      "minus_value": 14.340098370280991,
      "nonlinearity_indicator": 0.3872366529591317,
      "plus_delta": -0.030160161926890083,
      "plus_value": 14.241658533523331,
      "second_derivative_per_mm2": 381.1951290387938,
      "second_difference": 0.03811951290387938,
      "unit": "um"
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
        "declared_step_effect": 0.004819937980403921,
        "metric_key": "efl_mm",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.01,
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
        "step_mm": 0.01,
        "surface": 1,
        "unit": "mm"
      }
    ],
    "unit": "mm"
  },
  {
    "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
    "parameters": [
      {
        "declared_step_effect": 0.014281245132548581,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "1"
      },
      {
        "declared_step_effect": 0.007059272763451724,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.01,
        "surface": 1,
        "unit": "1"
      }
    ],
    "unit": "1"
  },
  {
    "metric_key": "rms_spot_um|f=1|w=1",
    "parameters": [
      {
        "declared_step_effect": 0.049219918378829774,
        "metric_key": "rms_spot_um|f=1|w=1",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "um"
      },
      {
        "declared_step_effect": 0.02324144368239711,
        "metric_key": "rms_spot_um|f=1|w=1",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.01,
        "surface": 1,
        "unit": "um"
      }
    ],
    "unit": "um"
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
          "value": 49.04657244162393
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
          "value": 51.8191425091652
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
          "value": 0.4775756396755298
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
          "value": 14.253313780619855
        }
      ]
    },
    "direction": -1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.8191425091652
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.8191425091652,
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
                "radius": 49.99,
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
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\1oTiDYYjy2XEHm8e\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
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
          "radius_mm": 49.99,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.8191425091652
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
          "radius_mm": 49.99,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.8191425091652
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
          "sampling": 128,
          "use_polarization": false,
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "metric": "efl_mm",
        "unit": "mm",
        "value": 49.04657244162393
      },
      {
        "analysis": {
          "sampling": 128,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.8191425091652
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            754.6670285133202
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 128,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.4775756396755298,
        "wavelength": 1
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 32,
          "sampled_rays": 3169,
          "sampling": 128,
          "scalar": true,
          "transmitted_rays": 3169,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 14.253313780619855,
        "wavelength": 1
      }
    ],
    "objective_value": 14.253313780619855,
    "parameter_index": 0,
    "parameters_mm": [
      49.99,
      46.8191425091652
    ],
    "requested_parameters_mm": [
      49.99,
      46.8191425091652
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
          "value": 49.05621231758474
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
          "value": 51.8191425091652
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
          "value": 0.46345709414862635
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
          "value": 14.29979666798465
        }
      ]
    },
    "direction": 1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.8191425091652
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.8191425091652,
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
                "radius": 50.01,
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
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\1oTiDYYjy2XEHm8e\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
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
          "radius_mm": 50.01,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.8191425091652
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
          "radius_mm": 50.01,
          "thickness_mm": 5
        },
        {
          "index": 2,
          "is_image": false,
          "radius_mm": -50.0,
          "thickness_mm": 46.8191425091652
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
          "sampling": 128,
          "use_polarization": false,
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "metric": "efl_mm",
        "unit": "mm",
        "value": 49.05621231758474
      },
      {
        "analysis": {
          "sampling": 128,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.8191425091652
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            754.517072421471
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 128,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.46345709414862635,
        "wavelength": 1
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 32,
          "sampled_rays": 3169,
          "sampling": 128,
          "scalar": true,
          "transmitted_rays": 3169,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 14.29979666798465,
        "wavelength": 1
      }
    ],
    "objective_value": 14.29979666798465,
    "parameter_index": 0,
    "parameters_mm": [
      50.01,
      46.8191425091652
    ],
    "requested_parameters_mm": [
      50.01,
      46.8191425091652
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
          "value": 51.8091425091652
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
          "value": 0.45570926295966574
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
          "value": 14.340098370280991
        }
      ]
    },
    "direction": -1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.8091425091652
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.8091425091652,
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
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\1oTiDYYjy2XEHm8e\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
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
          "thickness_mm": 46.8091425091652
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
          "thickness_mm": 46.8091425091652
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
          "sampling": 128,
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
          "sampling": 128,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.8091425091652
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            754.5920352882184
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 128,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.45570926295966574,
        "wavelength": 1
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 32,
          "sampled_rays": 3169,
          "sampling": 128,
          "scalar": true,
          "transmitted_rays": 3169,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 14.340098370280991,
        "wavelength": 1
      }
    ],
    "objective_value": 14.340098370280991,
    "parameter_index": 1,
    "parameters_mm": [
      50.0,
      46.8091425091652
    ],
    "requested_parameters_mm": [
      50.0,
      46.8091425091652
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
          "value": 51.829142509165194
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
          "value": 0.4842717532247629
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
          "value": 14.241658533523331
        }
      ]
    },
    "direction": 1,
    "inspection": {
      "axial_positions_mm": [
        "-Infinity",
        0.0,
        5.0,
        51.829142509165194
      ],
      "engine": {
        "name": "Optiland",
        "version": "0.6.2"
      },
      "focus_mm": 46.829142509165194,
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
                "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\1oTiDYYjy2XEHm8e\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
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
          "thickness_mm": 46.829142509165194
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
          "thickness_mm": 46.829142509165194
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
          "sampling": 128,
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
          "sampling": 128,
          "use_polarization": false
        },
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.829142509165194
      },
      {
        "analysis": {
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "frequency_range_cyc_per_mm": [
            0.0,
            754.5920352882184
          ],
          "interpolation": "linear, no extrapolation",
          "method": "scalar FFT MTF",
          "sampling": 128,
          "scalar": true,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "axis": "tangential",
        "field": 1,
        "frequency": 20,
        "metric": "mtf",
        "unit": "1",
        "value": 0.4842717532247629,
        "wavelength": 1
      },
      {
        "analysis": {
          "distribution": "hexapolar",
          "field_xy_deg": [
            0.0,
            0.0
          ],
          "method": "geometric RMS radius about centroid",
          "num_rings": 32,
          "sampled_rays": 3169,
          "sampling": 128,
          "scalar": true,
          "transmitted_rays": 3169,
          "use_polarization": false,
          "wavelength_um": 0.55
        },
        "field": 1,
        "metric": "rms_spot_um",
        "unit": "um",
        "value": 14.241658533523331,
        "wavelength": 1
      }
    ],
    "objective_value": 14.241658533523331,
    "parameter_index": 1,
    "parameters_mm": [
      50.0,
      46.829142509165194
    ],
    "requested_parameters_mm": [
      50.0,
      46.829142509165194
    ]
  }
]
~~~

## Objective definition

~~~json
{
  "direction": "minimize",
  "field": 1,
  "metric": "rms_spot_um",
  "wavelength": 1
}
~~~

## Baseline physical model inventory

~~~json
{
  "axial_positions_mm": [
    "-Infinity",
    0.0,
    5.0,
    51.8191425091652
  ],
  "engine": {
    "name": "Optiland",
    "version": "0.6.2"
  },
  "focus_mm": 46.8191425091652,
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
            "filename": "C:\\Users\\erict\\AppData\\Local\\uv\\cache\\archive-v0\\1oTiDYYjy2XEHm8e\\Lib\\site-packages\\optiland\\database\\data-nk\\glass\\schott\\N-BK7.yml",
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
      "thickness_mm": 46.8191425091652
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
      "thickness_mm": 46.8191425091652
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

