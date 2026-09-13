"""Native centered conic/asphere shape identity is complete and immutable."""
import importlib.util
import math
import os
import shutil
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from _lib import zos_backend


def cell(value=0., solve='Fixed'):
    return NS(DoubleValue=value, GetSolveData=lambda: NS(Type=solve))


def surface(kind='EvenAspheric', conic=-1, bad=None):
    cells = {i: cell(i*1e-12, 'Variable' if bad == i else 'Fixed') for i in range(1, 9)}
    return NS(Type=kind, Conic=conic, ConicCell=cell(solve='Variable' if bad == 'conic' else 'Fixed'),
              GetSurfaceCell=lambda column: cells[column])


COLUMNS = NS(**{f'Par{i}': i for i in range(1, 9)})


def test_native_shape_retains_every_even_power_and_units():
    result = zos_backend.surface_shape(surface(), COLUMNS)
    assert result['conic'] == -1
    assert [r['order'] for r in result['asphere_coefficients']] == list(range(2, 17, 2))
    assert [r['value'] for r in result['asphere_coefficients']] == [i*1e-12 for i in range(1, 9)]
    assert [r['unit'] for r in result['asphere_coefficients']] == [f'mm^{1-i}' for i in range(2, 17, 2)]


def test_standard_conic_needs_no_polynomial_coefficients():
    assert zos_backend.surface_shape(surface('Standard', -2), COLUMNS) == {
        'conic': -2., 'asphere_coefficients': []}


@pytest.mark.parametrize('bad', ['conic', 1, 8])
def test_shape_solves_are_rejected(bad):
    with pytest.raises(ValueError, match='fixed'):
        zos_backend.surface_shape(surface(bad=bad), COLUMNS)


@pytest.mark.parametrize('kind', ['OddAsphere', 'ExtendedAsphere', 'CoordinateBreak'])
def test_unverified_shape_types_rejected(kind):
    with pytest.raises(ValueError, match='surface type'):
        zos_backend.surface_shape(surface(kind), COLUMNS)


def test_nonfinite_shape_cannot_enter_inspection():
    with pytest.raises(ValueError, match='finite'):
        zos_backend.surface_shape(surface(conic=float('nan')), COLUMNS)


@pytest.mark.zos
@pytest.mark.skipif(os.environ.get('OPTICAL_DESIGN_LIVE') != '1' or
                   importlib.util.find_spec('zospy') is None, reason='explicit live ZOS opt-in required')
@pytest.mark.parametrize('name', ['conic', 'aspheric'])
def test_live_shapes_sag_saved_reload_and_undeclared_coefficient_detection(tmp_path, name):
    from _lib.design_jobs import sha256
    from _lib.optimization import _fixed_inspection
    source = Path(__file__).parents[2]/f'skills/optical-design/assets/{name}-singlet.zmx'
    original_hash = sha256(source)
    working = tmp_path/'working.zmx'
    shutil.copy2(source, working)
    variables = [{'surface': 1, 'parameter': 'radius_mm'}, {'surface': 2, 'parameter': 'thickness_mm'}]
    with zos_backend.ZOSBackend(working) as backend:
        initial = backend.inspect()
        fixed = _fixed_inspection(initial, initial, variables)
        coefficients = {4: 1e-6, 6: -1e-9, 16: 1e-20} if name == 'aspheric' else {}
        for curvature_radius in [50, 52]:
            backend.set_parameter(1, 'radius_mm', curvature_radius)
            backend.set_parameter(2, 'thickness_mm', 47.5)
            saved = tmp_path/f'candidate-{curvature_radius}.zmx'
            backend.save(saved)
            backend.load(saved)
            assert _fixed_inspection(backend.inspect(), initial, variables) == fixed
            for r in [0, 1, 3, 5]:
                c = 1/curvature_radius
                expected = c*r*r/(1+math.sqrt(1-.5*c*c*r*r))
                expected += sum(value*r**order for order, value in coefficients.items())
                result = backend.s.LDE.GetSag(1, 0., float(r), 0., 0.)
                assert result[0] and result[1] == pytest.approx(expected, rel=1e-12, abs=1e-12)
        if name == 'aspheric':
            row = backend.s.LDE.GetSurfaceAt(1)
            row.GetSurfaceCell(backend.zp.constants.Editors.LDE.SurfaceColumn.Par8).DoubleValue = 2e-20
            assert _fixed_inspection(backend.inspect(), initial, variables) != fixed
    assert sha256(source) == original_hash
