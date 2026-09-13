# Optical design review

Action: tolerance. Outcome: completed.

Local receipt consistency and recorded artifact hashes verified.

No accepted candidate. Rejected or partial results remain diagnostic evidence.

This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.

## Provenance

| Item | Recorded value |
| --- | --- |
| source | {&quot;path&quot;: &quot;C:\\\\Users\\\\erict\\\\OneDrive\\\\Desktop\\\\Projects\\\\optical-design-v1\\\\docs\\\\research\\\\full-release\\\\final-mcp\\\\mcp-jobs\\\\3a04a88562b045f7b919e776c1e1b7ec\\\\inputs\\\\model.json&quot;, &quot;sha256&quot;: &quot;a910db4a1dc27b10e638d9fbaaced32563b433af04a5e4be442b508826e325da&quot;} |
| source\_unchanged | True |
| baseline\_restored | True |
| saved\_candidate\_verified | unavailable |
| evaluations | 8 |
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

## Tolerance sensitivity trials

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
    "baseline_verified": true,
    "index": 0,
    "kind": "sensitivity",
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
    "perturbations": [
      {
        "applied": true,
        "baseline_mm": 50.0,
        "delta_mm": -0.01,
        "parameter": "radius_mm",
        "readback_mm": 49.99,
        "surface": 1,
        "value_mm": 49.99
      }
    ],
    "scale_factor": -1,
    "status": "pass"
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
          "value": 0.4706893577206028
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
          "value": 14.271818695450222
        }
      ]
    },
    "baseline_verified": true,
    "index": 1,
    "kind": "sensitivity",
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
        "value": 0.4706893577206028,
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
        "value": 14.271818695450222,
        "wavelength": 1
      }
    ],
    "perturbations": [
      {
        "applied": true,
        "baseline_mm": 50.0,
        "delta_mm": 0.0,
        "parameter": "radius_mm",
        "readback_mm": 50.0,
        "surface": 1,
        "value_mm": 50.0
      }
    ],
    "scale_factor": 0,
    "status": "pass"
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
    "baseline_verified": true,
    "index": 2,
    "kind": "sensitivity",
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
    "perturbations": [
      {
        "applied": true,
        "baseline_mm": 50.0,
        "delta_mm": 0.01,
        "parameter": "radius_mm",
        "readback_mm": 50.01,
        "surface": 1,
        "value_mm": 50.01
      }
    ],
    "scale_factor": 1,
    "status": "pass"
  }
]
~~~

## Recorded tolerance yield

~~~json
{
  "analysis_failures": 0,
  "attempted": 4,
  "failures": 0,
  "fraction": 1.0,
  "interval_scope": "completed independent Monte Carlo trials; analysis failures count as failures; no compensation",
  "not_run": 0,
  "passes": 4,
  "requested": 4,
  "wilson_95": [
    0.5101091635454027,
    1.0
  ]
}
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

