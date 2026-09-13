# Optical design review

Action: sensitivity. Outcome: completed.

Local receipt consistency and recorded artifact hashes verified.

No accepted candidate. Rejected or partial results remain diagnostic evidence.

This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.

## Provenance

| Item | Recorded value |
| --- | --- |
| source | {&quot;path&quot;: &quot;C:\\\\Users\\\\erict\\\\OneDrive\\\\Desktop\\\\Projects\\\\optical-design-v1\\\\docs\\\\research\\\\full-release\\\\final-mcp\\\\mcp-jobs\\\\b72380e91005490d8b78dda3be2ecc77\\\\inputs\\\\model.zmx&quot;, &quot;sha256&quot;: &quot;217526648ca75334c9dc49e32992b24a4f4a73edcb90d6835c83d3b59bf78eba&quot;} |
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
| track | pass | 51.76947 | mm | {&quot;id&quot;: &quot;track&quot;, &quot;max&quot;: 65, &quot;metric&quot;: &quot;total\_track\_mm&quot;, &quot;unit&quot;: &quot;mm&quot;} |
| contrast | pass | 0.3985805096694023 | 1 | {&quot;axis&quot;: &quot;tangential&quot;, &quot;field&quot;: 1, &quot;frequency&quot;: 20, &quot;id&quot;: &quot;contrast&quot;, &quot;metric&quot;: &quot;mtf&quot;, &quot;min&quot;: 0.3, &quot;unit&quot;: &quot;1&quot;, &quot;wavelength&quot;: 1} |
| spot | pass | 15.841366208313875 | um | {&quot;field&quot;: 1, &quot;id&quot;: &quot;spot&quot;, &quot;max&quot;: 30, &quot;metric&quot;: &quot;rms\_spot\_um&quot;, &quot;unit&quot;: &quot;um&quot;, &quot;wavelength&quot;: 1} |

### Metric comparison

| Metric identity | Baseline | Rejected / diagnostic candidate | Delta | Unit |
| --- | --- | --- | --- | --- |
| efl\_mm | 49.05139286997028 | unavailable | unavailable | mm |
| f\_number | 4.905139 | unavailable | unavailable | 1 |
| image\_distance\_mm | 46.7694746245767 | unavailable | unavailable | mm |
| mtf\|f=1\|w=1\|nu=20\|axis=sagittal | 0.3985805096694023 | unavailable | unavailable | 1 |
| mtf\|f=1\|w=1\|nu=20\|axis=tangential | 0.3985805096694023 | unavailable | unavailable | 1 |
| rms\_spot\_um\|f=1\|w=1 | 15.841366208313875 | unavailable | unavailable | um |
| total\_track\_mm | 51.76947 | unavailable | unavailable | mm |

## Physical fields and wavelengths

Indices are 1-based engine selections. Physical field coordinates and wavelength values are shown only when recorded; unavailable coordinates are not inferred from indices.

| Evaluation | Metric identity | Physical field \(recorded units\) | Wavelength \(um\) | Analysis settings / identity |
| --- | --- | --- | --- | --- |
| Baseline | rms\_spot\_um\|f=1\|w=1 | \[0.0, 0.0\] | 0.55 | {&quot;field&quot;: 1, &quot;field\_xy\_deg&quot;: \[0.0, 0.0\], &quot;native\_analysis&quot;: &quot;StandardSpot&quot;, &quot;ray\_check\_count&quot;: 17, &quot;ray\_density&quot;: 16, &quot;reference&quot;: &quot;centroid&quot;, &quot;spectral\_mode&quot;: &quot;monochromatic&quot;, &quot;wavelength&quot;: 1, &quot;wavelength\_um&quot;: 0.55} |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=tangential | \[0.0, 0.0\] | 0.55 | {&quot;analysis&quot;: &quot;FFTMTF&quot;, &quot;frequency\_interpolation&quot;: &quot;linear; no extrapolation&quot;, &quot;polarization&quot;: false, &quot;sampling&quot;: 128} |
| Baseline | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | \[0.0, 0.0\] | 0.55 | {&quot;analysis&quot;: &quot;FFTMTF&quot;, &quot;frequency\_interpolation&quot;: &quot;linear; no extrapolation&quot;, &quot;polarization&quot;: false, &quot;sampling&quot;: 128} |

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

RMS spot radius: 1 recorded samples; chart included in standalone HTML.

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
| 3 | 51.7694746245767 |

## Sensitivity comparison

| Surface / parameter | Step \(mm\) | Metric identity | Derivative \(unit/mm\) | Declared-step effect \(unit\) | Nonlinearity indicator |
| --- | --- | --- | --- | --- | --- |
| 1 / radius\_mm | 0.01 | efl\_mm | 0.4819937980407474 | 0.004819937980407474 | 0.00010173698160085738 |
| 1 / radius\_mm | 0.01 | f\_number | 0.04819999999998714 | 0.0004819999999998714 | 0.0 |
| 1 / radius\_mm | 0.01 | total\_track\_mm | 0.0 | 0.0 | 0.0 |
| 1 / radius\_mm | 0.01 | image\_distance\_mm | 0.0 | 0.0 | 0.0 |
| 1 / radius\_mm | 0.01 | rms\_spot\_um\|f=1\|w=1 | 0.9716014886000934 | 0.009716014886000934 | 0.44864985838062416 |
| 1 / radius\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=tangential | -0.7400613617667112 | 0.007400613617667112 | 0.0202058061547445 |
| 1 / radius\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | -0.7400613617667112 | 0.007400613617667112 | 0.0202058061547445 |
| 2 / thickness\_mm | 0.01 | efl\_mm | 0.0 | 0.0 | 0.0 |
| 2 / thickness\_mm | 0.01 | f\_number | 0.0 | 0.0 | 0.0 |
| 2 / thickness\_mm | 0.01 | total\_track\_mm | 1.0000000000001563 | 0.010000000000001563 | 3.5527136787999456e-13 |
| 2 / thickness\_mm | 0.01 | image\_distance\_mm | 1.0000000000001563 | 0.010000000000001563 | 3.5527136787999456e-13 |
| 2 / thickness\_mm | 0.01 | rms\_spot\_um\|f=1\|w=1 | -2.075664960315571 | 0.020756649603155708 | 0.856705408065369 |
| 2 / thickness\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=tangential | 1.5000008999199954 | 0.015000008999199954 | 0.04092853939400918 |
| 2 / thickness\_mm | 0.01 | mtf\|f=1\|w=1\|nu=20\|axis=sagittal | 1.5000008999199954 | 0.015000008999199954 | 0.04092853939400918 |

## Local sensitivity derivatives

~~~json
[
  {
    "baseline_mm": 50.0,
    "metrics": [
      {
        "baseline_value": 49.05139286997028,
        "declared_step_effect": 0.004819937980407474,
        "derivative_per_mm": 0.4819937980407474,
        "max_absolute_step_effect": 0.004820428346349104,
        "metric": "efl_mm",
        "metric_key": "efl_mm",
        "minus_delta": -0.004820428346349104,
        "minus_value": 49.04657244162393,
        "nonlinearity_indicator": 0.00010173698160085738,
        "plus_delta": 0.004819447614465844,
        "plus_value": 49.056212317584745,
        "second_derivative_per_mm2": -0.009807318832599776,
        "second_difference": -9.807318832599776e-07,
        "unit": "mm"
      },
      {
        "baseline_value": 4.905139,
        "declared_step_effect": 0.0004819999999998714,
        "derivative_per_mm": 0.04819999999998714,
        "max_absolute_step_effect": 0.0004819999999998714,
        "metric": "f_number",
        "metric_key": "f_number",
        "minus_delta": -0.0004819999999998714,
        "minus_value": 4.904657,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.0004819999999998714,
        "plus_value": 4.905621,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "1"
      },
      {
        "baseline_value": 51.76947,
        "declared_step_effect": 0.0,
        "derivative_per_mm": 0.0,
        "max_absolute_step_effect": 0.0,
        "metric": "total_track_mm",
        "metric_key": "total_track_mm",
        "minus_delta": 0.0,
        "minus_value": 51.76947,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.0,
        "plus_value": 51.76947,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "mm"
      },
      {
        "baseline_value": 46.7694746245767,
        "declared_step_effect": 0.0,
        "derivative_per_mm": 0.0,
        "max_absolute_step_effect": 0.0,
        "metric": "image_distance_mm",
        "metric_key": "image_distance_mm",
        "minus_delta": 0.0,
        "minus_value": 46.7694746245767,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.0,
        "plus_value": 46.7694746245767,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "mm"
      },
      {
        "baseline_value": 15.841366208313875,
        "declared_step_effect": 0.009716014886000934,
        "derivative_per_mm": 0.9716014886000934,
        "field": 1,
        "max_absolute_step_effect": 0.01407510358862929,
        "metric": "rms_spot_um",
        "metric_key": "rms_spot_um|f=1|w=1",
        "minus_delta": -0.005356926183372579,
        "minus_value": 15.836009282130503,
        "nonlinearity_indicator": 0.44864985838062416,
        "plus_delta": 0.01407510358862929,
        "plus_value": 15.855441311902505,
        "second_derivative_per_mm2": 87.1817740525671,
        "second_difference": 0.00871817740525671,
        "unit": "um",
        "wavelength": 1
      },
      {
        "axis": "tangential",
        "baseline_value": 0.3985805096694023,
        "declared_step_effect": 0.007400613617667112,
        "derivative_per_mm": -0.7400613617667112,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.007550148981851856,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "minus_delta": 0.007251078253482368,
        "minus_value": 0.40583158792288465,
        "nonlinearity_indicator": 0.0202058061547445,
        "plus_delta": -0.007550148981851856,
        "plus_value": 0.3910303606875504,
        "second_derivative_per_mm2": -2.9907072836948823,
        "second_difference": -0.0002990707283694882,
        "unit": "1",
        "wavelength": 1
      },
      {
        "axis": "sagittal",
        "baseline_value": 0.3985805096694023,
        "declared_step_effect": 0.007400613617667112,
        "derivative_per_mm": -0.7400613617667112,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.007550148981851856,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "minus_delta": 0.007251078253482368,
        "minus_value": 0.40583158792288465,
        "nonlinearity_indicator": 0.0202058061547445,
        "plus_delta": -0.007550148981851856,
        "plus_value": 0.3910303606875504,
        "second_derivative_per_mm2": -2.9907072836948823,
        "second_difference": -0.0002990707283694882,
        "unit": "1",
        "wavelength": 1
      }
    ],
    "objective": {
      "baseline_value": 15.841366208313875,
      "declared_step_effect": 0.009716014886000934,
      "derivative_per_mm": 0.9716014886000934,
      "max_absolute_step_effect": 0.01407510358862929,
      "minus_delta": -0.005356926183372579,
      "minus_value": 15.836009282130503,
      "nonlinearity_indicator": 0.44864985838062416,
      "plus_delta": 0.01407510358862929,
      "plus_value": 15.855441311902505,
      "second_derivative_per_mm2": 87.1817740525671,
      "second_difference": 0.00871817740525671,
      "unit": "um"
    },
    "parameter": "radius_mm",
    "parameter_index": 0,
    "step_mm": 0.01,
    "surface": 1
  },
  {
    "baseline_mm": 46.7694746245767,
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
        "baseline_value": 4.905139,
        "declared_step_effect": 0.0,
        "derivative_per_mm": 0.0,
        "max_absolute_step_effect": 0.0,
        "metric": "f_number",
        "metric_key": "f_number",
        "minus_delta": 0.0,
        "minus_value": 4.905139,
        "nonlinearity_indicator": 0.0,
        "plus_delta": 0.0,
        "plus_value": 4.905139,
        "second_derivative_per_mm2": 0.0,
        "second_difference": 0.0,
        "unit": "1"
      },
      {
        "baseline_value": 51.76947,
        "declared_step_effect": 0.010000000000001563,
        "derivative_per_mm": 1.0000000000001563,
        "max_absolute_step_effect": 0.010000000000005116,
        "metric": "total_track_mm",
        "metric_key": "total_track_mm",
        "minus_delta": -0.00999999999999801,
        "minus_value": 51.75947,
        "nonlinearity_indicator": 3.5527136787999456e-13,
        "plus_delta": 0.010000000000005116,
        "plus_value": 51.77947,
        "second_derivative_per_mm2": 7.105427357601002e-11,
        "second_difference": 7.105427357601002e-15,
        "unit": "mm"
      },
      {
        "baseline_value": 46.7694746245767,
        "declared_step_effect": 0.010000000000001563,
        "derivative_per_mm": 1.0000000000001563,
        "max_absolute_step_effect": 0.010000000000005116,
        "metric": "image_distance_mm",
        "metric_key": "image_distance_mm",
        "minus_delta": -0.010000000000005116,
        "minus_value": 46.7594746245767,
        "nonlinearity_indicator": 3.5527136787999456e-13,
        "plus_delta": 0.00999999999999801,
        "plus_value": 46.7794746245767,
        "second_derivative_per_mm2": -7.105427357601002e-11,
        "second_difference": -7.105427357601002e-15,
        "unit": "mm"
      },
      {
        "baseline_value": 15.841366208313875,
        "declared_step_effect": 0.020756649603155708,
        "derivative_per_mm": -2.075664960315571,
        "field": 1,
        "max_absolute_step_effect": 0.0385389835714971,
        "metric": "rms_spot_um",
        "metric_key": "rms_spot_um|f=1|w=1",
        "minus_delta": 0.0385389835714971,
        "minus_value": 15.879905191885372,
        "nonlinearity_indicator": 0.856705408065369,
        "plus_delta": -0.0029743156348143174,
        "plus_value": 15.838391892679061,
        "second_derivative_per_mm2": 355.6466793668278,
        "second_difference": 0.03556466793668278,
        "unit": "um",
        "wavelength": 1
      },
      {
        "axis": "tangential",
        "baseline_value": 0.3985805096694023,
        "declared_step_effect": 0.015000008999199954,
        "derivative_per_mm": 1.5000008999199954,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.015613937458434202,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "minus_delta": -0.015613937458434202,
        "minus_value": 0.3829665722109681,
        "nonlinearity_indicator": 0.04092853939400918,
        "plus_delta": 0.014386080539965707,
        "plus_value": 0.412966590209368,
        "second_derivative_per_mm2": -12.278569184684951,
        "second_difference": -0.001227856918468495,
        "unit": "1",
        "wavelength": 1
      },
      {
        "axis": "sagittal",
        "baseline_value": 0.3985805096694023,
        "declared_step_effect": 0.015000008999199954,
        "derivative_per_mm": 1.5000008999199954,
        "field": 1,
        "frequency": 20,
        "max_absolute_step_effect": 0.015613937458434202,
        "metric": "mtf",
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "minus_delta": -0.015613937458434202,
        "minus_value": 0.3829665722109681,
        "nonlinearity_indicator": 0.04092853939400918,
        "plus_delta": 0.014386080539965707,
        "plus_value": 0.412966590209368,
        "second_derivative_per_mm2": -12.278569184684951,
        "second_difference": -0.001227856918468495,
        "unit": "1",
        "wavelength": 1
      }
    ],
    "objective": {
      "baseline_value": 15.841366208313875,
      "declared_step_effect": 0.020756649603155708,
      "derivative_per_mm": -2.075664960315571,
      "max_absolute_step_effect": 0.0385389835714971,
      "minus_delta": 0.0385389835714971,
      "minus_value": 15.879905191885372,
      "nonlinearity_indicator": 0.856705408065369,
      "plus_delta": -0.0029743156348143174,
      "plus_value": 15.838391892679061,
      "second_derivative_per_mm2": 355.6466793668278,
      "second_difference": 0.03556466793668278,
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
        "declared_step_effect": 0.004819937980407474,
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
    "metric_key": "f_number",
    "parameters": [
      {
        "declared_step_effect": 0.0004819999999998714,
        "metric_key": "f_number",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.01,
        "surface": 1,
        "unit": "1"
      },
      {
        "declared_step_effect": 0.0,
        "metric_key": "f_number",
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
    "metric_key": "total_track_mm",
    "parameters": [
      {
        "declared_step_effect": 0.010000000000001563,
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
    "metric_key": "image_distance_mm",
    "parameters": [
      {
        "declared_step_effect": 0.010000000000001563,
        "metric_key": "image_distance_mm",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "mm"
      },
      {
        "declared_step_effect": 0.0,
        "metric_key": "image_distance_mm",
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
    "metric_key": "rms_spot_um|f=1|w=1",
    "parameters": [
      {
        "declared_step_effect": 0.020756649603155708,
        "metric_key": "rms_spot_um|f=1|w=1",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "um"
      },
      {
        "declared_step_effect": 0.009716014886000934,
        "metric_key": "rms_spot_um|f=1|w=1",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.01,
        "surface": 1,
        "unit": "um"
      }
    ],
    "unit": "um"
  },
  {
    "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
    "parameters": [
      {
        "declared_step_effect": 0.015000008999199954,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=tangential",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "1"
      },
      {
        "declared_step_effect": 0.007400613617667112,
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
    "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
    "parameters": [
      {
        "declared_step_effect": 0.015000008999199954,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "parameter": "thickness_mm",
        "parameter_index": 1,
        "step_mm": 0.01,
        "surface": 2,
        "unit": "1"
      },
      {
        "declared_step_effect": 0.007400613617667112,
        "metric_key": "mtf|f=1|w=1|nu=20|axis=sagittal",
        "parameter": "radius_mm",
        "parameter_index": 0,
        "step_mm": 0.01,
        "surface": 1,
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
          "value": 51.76947
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
          "value": 0.40583158792288465
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
          "value": 15.836009282130503
        }
      ]
    },
    "direction": -1,
    "inspection": {
      "engine": {
        "license": "PremiumEdition",
        "name": "OpticStudio",
        "pythonnet_version": "3.1.0",
        "version": "24.1.0",
        "zospy_version": "2.1.5"
      },
      "focus_mm": 46.7694746245767,
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
            "radius_mm": 49.989999999999995,
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
          "radius_mm": 49.989999999999995,
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
          "thickness_mm": 46.7694746245767,
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
    "kind": "perturbation",
    "measurements": [
      {
        "metric": "efl_mm",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "mm",
        "value": 49.04657244162393
      },
      {
        "metric": "f_number",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "1",
        "value": 4.904657
      },
      {
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.76947
      },
      {
        "metric": "image_distance_mm",
        "unit": "mm",
        "value": 46.7694746245767
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
          "ray_density": 16,
          "reference": "centroid",
          "spectral_mode": "monochromatic",
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "um",
        "value": 15.836009282130503,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.40583158792288465,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.40583158792288465,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
      "aggregation": "scalar",
      "direction": "minimize",
      "terms": [
        {
          "field": 1,
          "key": "rms_spot_um|f=1|w=1",
          "metric": "rms_spot_um",
          "unit": "um",
          "value": 15.836009282130503,
          "wavelength": 1
        }
      ],
      "unit": "um",
      "value": 15.836009282130503
    },
    "objective_value": 15.836009282130503,
    "parameter_index": 0,
    "parameters_mm": [
      49.989999999999995,
      46.7694746245767
    ],
    "requested_parameters_mm": [
      49.99,
      46.7694746245767
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
          "value": 49.056212317584745
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
          "value": 51.76947
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
          "value": 0.3910303606875504
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
          "value": 15.855441311902505
        }
      ]
    },
    "direction": 1,
    "inspection": {
      "engine": {
        "license": "PremiumEdition",
        "name": "OpticStudio",
        "pythonnet_version": "3.1.0",
        "version": "24.1.0",
        "zospy_version": "2.1.5"
      },
      "focus_mm": 46.7694746245767,
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
            "radius_mm": 50.00999999999999,
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
          "radius_mm": 50.00999999999999,
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
          "thickness_mm": 46.7694746245767,
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
    "kind": "perturbation",
    "measurements": [
      {
        "metric": "efl_mm",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "mm",
        "value": 49.056212317584745
      },
      {
        "metric": "f_number",
        "settings": {
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "1",
        "value": 4.905621
      },
      {
        "metric": "total_track_mm",
        "unit": "mm",
        "value": 51.76947
      },
      {
        "metric": "image_distance_mm",
        "unit": "mm",
        "value": 46.7694746245767
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
          "ray_density": 16,
          "reference": "centroid",
          "spectral_mode": "monochromatic",
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "um",
        "value": 15.855441311902505,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.3910303606875504,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.3910303606875504,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
      "aggregation": "scalar",
      "direction": "minimize",
      "terms": [
        {
          "field": 1,
          "key": "rms_spot_um|f=1|w=1",
          "metric": "rms_spot_um",
          "unit": "um",
          "value": 15.855441311902505,
          "wavelength": 1
        }
      ],
      "unit": "um",
      "value": 15.855441311902505
    },
    "objective_value": 15.855441311902505,
    "parameter_index": 0,
    "parameters_mm": [
      50.00999999999999,
      46.7694746245767
    ],
    "requested_parameters_mm": [
      50.01,
      46.7694746245767
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
          "value": 51.75947
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
          "value": 0.3829665722109681
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
          "value": 15.879905191885372
        }
      ]
    },
    "direction": -1,
    "inspection": {
      "engine": {
        "license": "PremiumEdition",
        "name": "OpticStudio",
        "pythonnet_version": "3.1.0",
        "version": "24.1.0",
        "zospy_version": "2.1.5"
      },
      "focus_mm": 46.7594746245767,
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
          "thickness_mm": 46.7594746245767,
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
    "kind": "perturbation",
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
        "value": 51.75947
      },
      {
        "metric": "image_distance_mm",
        "unit": "mm",
        "value": 46.7594746245767
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
          "ray_density": 16,
          "reference": "centroid",
          "spectral_mode": "monochromatic",
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "um",
        "value": 15.879905191885372,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.3829665722109681,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.3829665722109681,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
      "aggregation": "scalar",
      "direction": "minimize",
      "terms": [
        {
          "field": 1,
          "key": "rms_spot_um|f=1|w=1",
          "metric": "rms_spot_um",
          "unit": "um",
          "value": 15.879905191885372,
          "wavelength": 1
        }
      ],
      "unit": "um",
      "value": 15.879905191885372
    },
    "objective_value": 15.879905191885372,
    "parameter_index": 1,
    "parameters_mm": [
      50.0,
      46.7594746245767
    ],
    "requested_parameters_mm": [
      50.0,
      46.759474624576704
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
          "value": 51.77947
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
          "value": 0.412966590209368
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
          "value": 15.838391892679061
        }
      ]
    },
    "direction": 1,
    "inspection": {
      "engine": {
        "license": "PremiumEdition",
        "name": "OpticStudio",
        "pythonnet_version": "3.1.0",
        "version": "24.1.0",
        "zospy_version": "2.1.5"
      },
      "focus_mm": 46.7794746245767,
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
          "thickness_mm": 46.7794746245767,
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
    "kind": "perturbation",
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
        "value": 51.77947
      },
      {
        "metric": "image_distance_mm",
        "unit": "mm",
        "value": 46.7794746245767
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
          "ray_density": 16,
          "reference": "centroid",
          "spectral_mode": "monochromatic",
          "wavelength": 1,
          "wavelength_um": 0.55
        },
        "unit": "um",
        "value": 15.838391892679061,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.412966590209368,
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
          "sampling": 128
        },
        "unit": "1",
        "value": 0.412966590209368,
        "wavelength": 1
      }
    ],
    "objective_breakdown": {
      "aggregation": "scalar",
      "direction": "minimize",
      "terms": [
        {
          "field": 1,
          "key": "rms_spot_um|f=1|w=1",
          "metric": "rms_spot_um",
          "unit": "um",
          "value": 15.838391892679061,
          "wavelength": 1
        }
      ],
      "unit": "um",
      "value": 15.838391892679061
    },
    "objective_value": 15.838391892679061,
    "parameter_index": 1,
    "parameters_mm": [
      50.0,
      46.7794746245767
    ],
    "requested_parameters_mm": [
      50.0,
      46.7794746245767
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
      "value": 15.841366208313875,
      "wavelength": 1
    }
  ],
  "unit": "um",
  "value": 15.841366208313875
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
  "focus_mm": 46.7694746245767,
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
      "thickness_mm": 46.7694746245767,
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

