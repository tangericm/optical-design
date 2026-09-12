import pytest
from _lib.design_contract import DesignSpec, assess, metric_key


def base_spec():
    return {"schema": "1", "fields": [1], "wavelengths": [1],
            "frequencies_cyc_per_mm": [50],
            "requirements": [{"id": "contrast", "metric": "mtf", "field": 1,
                              "wavelength": 1, "frequency": 50, "axis": "tangential",
                              "unit": "1", "min": 0.4}],
            "objective": {"metric": "mtf", "field": 1, "wavelength": 1,
                          "frequency": 50, "axis": "tangential", "direction": "maximize"},
            "focus": {"min_mm": 40, "max_mm": 55},
            "budget": {"max_evaluations": 17, "timeout_s": 60}}


def test_requirement_typos_and_boolean_indices_rejected():
    raw = base_spec()
    raw['requirements'][0]['maxx'] = .5
    with pytest.raises(ValueError, match='unknown'):
        DesignSpec.from_dict(raw)
    raw = base_spec()
    raw['requirements'][0]['field'] = True
    with pytest.raises(ValueError):
        DesignSpec.from_dict(raw)


def test_close_frequencies_keep_distinct_identity():
    row = base_spec()['requirements'][0]
    assert metric_key(dict(row, frequency=50.00001)) != metric_key(dict(row, frequency=50.00002))


def test_missing_required_metric_is_unknown_not_pass():
    spec = DesignSpec.from_dict(base_spec())
    result = assess(spec, [])
    assert result["passes"] is False
    assert result["requirements"][0]["status"] == "unavailable"


def test_metric_identity_includes_field_wavelength_frequency_axis():
    spec = DesignSpec.from_dict(base_spec())
    rows = [{"metric": "mtf", "field": 2, "wavelength": 1, "frequency": 50,
             "axis": "tangential", "unit": "1", "value": 0.9}]
    assert not assess(spec, rows)["passes"]
    rows[0]["field"] = 1
    assert assess(spec, rows)["passes"]
    assert metric_key(rows[0]) == "mtf|f=1|w=1|nu=50|axis=tangential"


@pytest.mark.parametrize("mutate", [
    lambda s: s.update(fields=[0]),
    lambda s: s.update(wavelengths=[]),
    lambda s: s.update(requirements=[]),
    lambda s: s["focus"].update(min_mm=80),
    lambda s: s["budget"].update(max_evaluations=0),
    lambda s: s["requirements"][0].update(min=float("nan")),
    lambda s: s["requirements"][0].update(unit="mm"),
    lambda s: s["requirements"][0].update(field=2),
])
def test_invalid_spec_rejected_before_optical_session(mutate):
    s = base_spec()
    mutate(s)
    with pytest.raises(ValueError):
        DesignSpec.from_dict(s)


def test_units_mismatch_cannot_satisfy_requirement():
    spec = DesignSpec.from_dict(base_spec())
    row = {**base_spec()["requirements"][0], "value": 0.8, "unit": "mm"}
    assert assess(spec, [row])["requirements"][0]["status"] == "incomparable"
