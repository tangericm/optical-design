import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / 'skills/optical-design/scripts'))
from _lib.zos_backend import interpolate_mtf, validate_surface


@pytest.mark.parametrize('changes', [{'thickness_mm': -2}, {'tilts': [0, 10]}, {'aperture': 'CircularObscuration'}])
def test_nonphysical_or_unsupported_surface_rejected(changes):
    row = {'thickness_mm': 5, 'material': 'N-BK7', 'tilts': [0] * 10, 'aperture': 'None'}
    row.update(changes)
    with pytest.raises(ValueError):
        validate_surface(row)


def test_mtf_interpolation_preserves_axis_and_rejects_extrapolation():
    assert interpolate_mtf([0, 50, 100], [1, .6, .2], 75) == pytest.approx(.4)
    with pytest.raises(ValueError, match='outside'):
        interpolate_mtf([0, 50], [1, .6], 75)


@pytest.mark.parametrize('x,y', [([0, 0], [1, .5]), ([0, 1], [1, float('nan')]),
                                  ([0, 1], [1, -1]), ([0, 1], [1, 1.5])])
def test_invalid_mtf_rejected(x, y):
    with pytest.raises(ValueError):
        interpolate_mtf(x, y, .5)


@pytest.mark.zos
@pytest.mark.skipif(os.environ.get('OPTICAL_DESIGN_LIVE') != '1' or
                    importlib.util.find_spec('zospy') is None, reason='explicit live ZOS opt-in required')
def test_live_zos_copy_audit(tmp_path):
    from _lib.design_contract import DesignSpec
    from _lib.design_jobs import run_job
    from _lib.zos_backend import ZOSBackend
    from test_design_contract import base_spec
    model = Path(__file__).parents[2] / 'skills/optical-design/assets/defocused-singlet.zmx'
    report = run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / 'job', ZOSBackend)
    assert report['source_unchanged']
    rows = report['baseline']['measurements']
    assert next(r['value'] for r in rows if r['metric'] == 'efl_mm') == pytest.approx(49.05139287, rel=1e-6)
    assert next(r['value'] for r in rows if r['metric'] == 'rms_spot_um') > 900


@pytest.mark.zos
@pytest.mark.skipif(os.environ.get('OPTICAL_DESIGN_LIVE') != '1' or
                    importlib.util.find_spec('zospy') is None, reason='explicit live ZOS opt-in required')
def test_live_native_cli_stdout_is_valid_json():
    script = Path(__file__).parents[2] / 'skills/optical-design/scripts/zos.py'
    result = subprocess.run([sys.executable, str(script), 'check', '--json'],
                            capture_output=True, text=True, timeout=120, check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['valid_api_license']
