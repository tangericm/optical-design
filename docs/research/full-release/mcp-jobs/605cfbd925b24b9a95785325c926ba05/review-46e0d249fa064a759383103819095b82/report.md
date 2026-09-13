# Optical design review

Action: edit. Outcome: requirements\_not\_met.

Local receipt consistency and recorded artifact hashes verified.

No accepted candidate. Rejected or partial results remain diagnostic evidence.

This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.

## Provenance

| Item | Recorded value |
| --- | --- |
| source | {&quot;path&quot;: &quot;C:\\\\Users\\\\erict\\\\OneDrive\\\\Desktop\\\\Projects\\\\optical-design-v1\\\\docs\\\\research\\\\full-release\\\\mcp-jobs\\\\605cfbd925b24b9a95785325c926ba05\\\\inputs\\\\model.json&quot;, &quot;sha256&quot;: &quot;73d813dea1ad75db10d87d5023b3608740c652a6ccc38b999eec38599aa803ca&quot;} |
| source\_unchanged | True |
| baseline\_restored | True |
| saved\_candidate\_verified | False |
| evaluations | 3 |
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
| track | pass | 65.0 | mm | {&quot;id&quot;: &quot;track&quot;, &quot;max&quot;: 65, &quot;metric&quot;: &quot;total\_track\_mm&quot;, &quot;unit&quot;: &quot;mm&quot;} |
| contrast | fail | 0.002489848452484078 | 1 | {&quot;axis&quot;: &quot;tangential&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |
| spot | fail | 973.842027568571 | um | {&quot;field&quot;: 1, &quot;id&quot;: &quot;spot&quot;, &quot;max&quot;: 30, &quot;metric&quot;: &quot;rms\_spot\_um&quot;, &quot;unit&quot;: &quot;um&quot;, &quot;wavelength&quot;: 1} |

### Rejected / diagnostic candidate requirements

| Requirement | Status | Value / reason | Unit | Constraint |
| --- | --- | --- | --- | --- |
| focal-length | pass | 49.05139286997028 | mm | {&quot;id&quot;: &quot;focal-length&quot;, &quot;max&quot;: 51, &quot;metric&quot;: &quot;efl\_mm&quot;, &quot;min&quot;: 48, &quot;unit&quot;: &quot;mm&quot;} |
| track | pass | 52.5 | mm | {&quot;id&quot;: &quot;track&quot;, &quot;max&quot;: 65, &quot;metric&quot;: &quot;total\_track\_mm&quot;, &quot;unit&quot;: &quot;mm&quot;} |
| contrast | fail | 0.14595374576966064 | 1 | {&quot;axis&quot;: &quot;tangential&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |
| spot | fail | 51.40799555848414 | um | {&quot;field&quot;: 1, &quot;id&quot;: &quot;spot&quot;, &quot;max&quot;: 30, &quot;metric&quot;: &quot;rms\_spot\_um&quot;, &quot;unit&quot;: &quot;um&quot;, &quot;wavelength&quot;: 1} |

### Metric comparison

| Metric identity | Baseline | Rejected / diagnostic candidate | Delta | Unit |
| --- | --- | --- | --- | --- |
| efl\_mm | 49.05139286997028 | 49.05139286997028 | 0.0 | mm |
| mtf\|f=1\|w=1\|nu=20\|axis=tangential | 0.002489848452484078 | 0.14595374576966064 | 0.14346389731717657 | 1 |
| rms\_spot\_um\|f=1\|w=1 | 973.842027568571 | 51.40799555848414 | -922.4340320100869 | um |
| total\_track\_mm | 65.0 | 52.5 | -12.5 | mm |

## Physical fields and wavelengths

Indices are 1-based engine selections. Physical field coordinates and wavelength values are shown only when recorded; unavailable coordinates are not inferred from indices.

| Evaluation | Metric identity | Physical field \(recorded units\) | Wavelength \(um\) | Analysis settings / identity |
| --- | --- | --- | --- | --- |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=tangential | \[0.0, 0.0\] | 0.55 | {&quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;frequency\_range\_cyc\_per\_mm&quot;: \[0.0, 754.5920352882184\], &quot;interpolation&quot;: &quot;linear, no extrapolation&quot;, &quot;method&quot;: &quot;scalar FFT MTF&quot;, &quot;sampling&quot;: 128, &quot;scalar&quot;: true, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |
| Baseline | rms\_spot\_um\|f=1\|w=1 | \[0.0, 0.0\] | 0.55 | {&quot;distribution&quot;: &quot;hexapolar&quot;, &quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;method&quot;: &quot;geometric RMS radius about centroid&quot;, &quot;num\_rings&quot;: 32, &quot;sampled\_rays&quot;: 3169, &quot;sampling&quot;: 128, &quot;scalar&quot;: true, &quot;transmitted\_rays&quot;: 3169, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |
| Rejected / diagnostic candidate | mtf\|f=1\|w=1\|nu=20\|axis=tangential | \[0.0, 0.0\] | 0.55 | {&quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;frequency\_range\_cyc\_per\_mm&quot;: \[0.0, 754.5920352882184\], &quot;interpolation&quot;: &quot;linear, no extrapolation&quot;, &quot;method&quot;: &quot;scalar FFT MTF&quot;, &quot;sampling&quot;: 128, &quot;scalar&quot;: true, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |
| Rejected / diagnostic candidate | rms\_spot\_um\|f=1\|w=1 | \[0.0, 0.0\] | 0.55 | {&quot;distribution&quot;: &quot;hexapolar&quot;, &quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;method&quot;: &quot;geometric RMS radius about centroid&quot;, &quot;num\_rings&quot;: 32, &quot;sampled\_rays&quot;: 3169, &quot;sampling&quot;: 128, &quot;scalar&quot;: true, &quot;transmitted\_rays&quot;: 3169, &quot;use\_polarization&quot;: false, &quot;wavelength\_um&quot;: 0.55} |

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

MTF: 2 recorded samples; chart included in standalone HTML.

### RMS spot radius

RMS spot radius: 2 recorded samples; chart included in standalone HTML.

## Prescription changes

| Surface | Parameter | Baseline | Rejected / diagnostic candidate |
| --- | --- | --- | --- |
| 2 | thickness\_mm | 60 | 47.5 |
| image-space gap | focus\_mm | 60.0 | 47.5 |

No change table does not certify unchanged geometry when inspection data are missing.

## Axial schematic

Axial schematic only — surface vertices along the optical axis. No traced rays, lens sag, clear apertures, or imaging performance are depicted.

Recorded axial coordinates \(mm\).

| Surface index | Axial vertex \(mm\) |
| --- | --- |
| 1 | 0.0 |
| 2 | 5.0 |
| 3 | 65.0 |

## Objective definition

~~~json
{
  "direction": "minimize",
  "field": 1,
  "metric": "rms_spot_um",
  "wavelength": 1
}
~~~

## Baseline objective evidence

~~~json
{
  "aggregation": "scalar",
  "direction": "minimize",
  "terms": [
    {
      "field": 1,
      "key": "rms_spot_um|f=1|w=1",
      "metric": "rms_spot_um",
      "unit": "um",
      "value": 973.842027568571,
      "wavelength": 1
    }
  ],
  "unit": "um",
  "value": 973.842027568571
}
~~~

## Rejected / diagnostic candidate objective evidence

~~~json
{
  "aggregation": "scalar",
  "direction": "minimize",
  "terms": [
    {
      "field": 1,
      "key": "rms_spot_um|f=1|w=1",
      "metric": "rms_spot_um",
      "unit": "um",
      "value": 51.40799555848414,
      "wavelength": 1
    }
  ],
  "unit": "um",
  "value": 51.40799555848414
}
~~~

## Baseline physical model inventory

~~~json
{
  "axial_positions_mm": [
    "-Infinity",
    0.0,
    5.0,
    65.0
  ],
  "engine": {
    "name": "Optiland",
    "version": "0.6.2"
  },
  "focus_mm": 60.0,
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
      "thickness_mm": 60
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
      "thickness_mm": 60
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

## Rejected / diagnostic candidate physical model inventory

~~~json
{
  "axial_positions_mm": [
    "-Infinity",
    0.0,
    5.0,
    52.5
  ],
  "engine": {
    "name": "Optiland",
    "version": "0.6.2"
  },
  "focus_mm": 47.5,
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
      "thickness_mm": 47.5
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
      "thickness_mm": 47.5
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

