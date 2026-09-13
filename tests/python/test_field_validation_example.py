"""Scientific coverage checks for the shipped multi-field, multi-wavelength example."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest
from _lib.design_contract import DesignSpec, metric_key

ASSETS = Path(__file__).parents[2]/'skills/optical-design/assets/field-validation'
LIVE = os.environ.get('OPTICAL_DESIGN_LIVE') == '1' and importlib.util.find_spec('zospy') is not None


def test_validation_example_requires_every_field_wave_and_both_mtf_axes():
    search = DesignSpec.from_dict(json.loads((ASSETS/'search.json').read_text()))
    validation = DesignSpec.from_dict(json.loads((ASSETS/'validation.json').read_text()))
    assert search.data['fields'] == [1] and search.data['wavelengths'] == [2]
    expected = {(f, w, metric, axis) for f in (1, 2, 3) for w in (1, 2, 3)
                for metric, axis in [('rms_spot_um', None), ('mtf', 'tangential'), ('mtf', 'sagittal')]}
    scoped = [r for r in validation.data['requirements'] if 'field' in r]
    assert {(r['field'], r['wavelength'], r['metric'], r.get('axis')) for r in scoped} == expected
    assert all(r.get('max') == 30 if r['metric'] == 'rms_spot_um' else r['min'] == .3 for r in scoped)
    assert validation.objective is None


@pytest.mark.parametrize('engine', [pytest.param('optiland', marks=pytest.mark.tier1),
    pytest.param('zos', marks=[pytest.mark.zos, pytest.mark.skipif(not LIVE, reason='explicit live ZOS opt-in required')])])
def test_grid_measurements_match_isolated_nonprimary_offaxis_selection(engine):
    if engine == 'optiland':
        pytest.importorskip('optiland')
        from _lib.optiland_backend import OptilandBackend as Backend
        model = ASSETS/'portable.json'
    else:
        from _lib.zos_backend import ZOSBackend as Backend
        model = ASSETS/'native.zmx'
    raw = json.loads((ASSETS/'validation.json').read_text())
    before = hashlib.sha256(model.read_bytes()).hexdigest()
    with Backend(model) as backend:
        backend.set_focus(47.5)
        grid = {metric_key(row): row for row in backend.evaluate(DesignSpec.from_dict(raw))}
        scoped = [row for row in grid.values() if 'field' in row]
        assert len(scoped) == 27
        assert all(row['value'] is not None for row in grid.values())
        if engine == 'zos':
            for row in scoped:
                if row['metric'] == 'rms_spot_um':
                    settings = row['settings']
                    assert settings['field'] == row['field']
                    assert settings['wavelength'] == row['wavelength']
                    assert settings['field_xy_deg'] == [0, [0, 3, 6][row['field']-1]]
                    assert settings['wavelength_um'] == [.4861327, .55, .6562725][row['wavelength']-1]
                    assert settings['spectral_mode'] == 'monochromatic'
        efl = grid['efl_mm']
        settings = efl.get('settings', efl.get('analysis'))
        assert settings['wavelength'] == 2 and settings['wavelength_um'] == .55
        # Deliberately reorder both axes and omit the primary wavelength and on-axis field.
        subset = copy.deepcopy(raw)
        subset.update(fields=[3, 2], wavelengths=[3, 1])
        subset['requirements'] = [r for r in subset['requirements']
                                  if 'field' not in r or (r['field'] in [3, 2] and r['wavelength'] in [3, 1])]
        subset['requirements'].sort(key=lambda r: (
            [3, 2].index(r['field']) if 'field' in r else -1,
            [3, 1].index(r['wavelength']) if 'wavelength' in r else -1))
        isolated = backend.evaluate(DesignSpec.from_dict(subset))
        expected_scoped = [metric_key(r) for r in subset['requirements'] if 'field' in r]
        actual_scoped = [metric_key(r) for r in isolated if 'field' in r]
        assert actual_scoped == expected_scoped
        for row in isolated:
            assert row['value'] == pytest.approx(grid[metric_key(row)]['value'], rel=1e-10, abs=1e-10)
        spots = [r['value'] for r in scoped if r['metric'] == 'rms_spot_um']
        assert max(spots) > min(spots) * 1.5  # Data respond to the physical conditions.
    assert hashlib.sha256(model.read_bytes()).hexdigest() == before


@pytest.mark.zos
@pytest.mark.skipif(not LIVE, reason='explicit live ZOS opt-in required')
def test_native_wavelength_rows_match_models_with_only_that_wavelength():
    from _lib.zos_backend import ZOSBackend
    model = ASSETS/'native.zmx'
    raw = json.loads((ASSETS/'validation.json').read_text())
    raw['frequencies_cyc_per_mm'] = []
    raw['requirements'] = [r for r in raw['requirements'] if r['metric'] == 'rms_spot_um']
    with ZOSBackend(model) as backend:
        backend.set_focus(47.5)
        grid = {metric_key(r): r['value'] for r in backend.evaluate(DesignSpec.from_dict(raw))}
        assert {k for k in grid if k.startswith('rms_spot_um')} == {
            f'rms_spot_um|f={f}|w={w}' for f in (1, 2, 3) for w in (1, 2, 3)}
        # Independent oracle: retain all physical fields but remove the other wavelengths.
        # An all-wavelength spot analysis is then unambiguously monochromatic.
        for wave, value in enumerate([.4861327, .55, .6562725], start=1):
            backend.load(model)
            backend.set_focus(47.5)
            wavelengths = backend.s.SystemData.Wavelengths
            wavelengths.GetWavelength(1).MakePrimary()
            wavelengths.RemoveWavelength(3)
            wavelengths.RemoveWavelength(2)
            wavelengths.GetWavelength(1).Wavelength = value
            single = copy.deepcopy(raw)
            single['wavelengths'] = [1]
            single['requirements'] = [r for r in single['requirements'] if r['wavelength'] == wave]
            for req in single['requirements']:
                req['wavelength'] = 1
            rows = backend.evaluate(DesignSpec.from_dict(single))
            assert {metric_key(r) for r in rows if r['metric'] == 'rms_spot_um'} == {
                f'rms_spot_um|f={f}|w=1' for f in (1, 2, 3)}
            for row in rows:
                if row['metric'] == 'rms_spot_um':
                    lookup = dict(row, wavelength=wave)
                    assert row['value'] == pytest.approx(grid[metric_key(lookup)], rel=1e-10, abs=1e-10)
