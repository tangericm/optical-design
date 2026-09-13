"""Build deterministic native conic/asphere fixtures and verify analytic sag anchors."""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT/'skills/optical-design/assets'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'skills/optical-design/scripts'))
from _lib.zos_backend import ZOSBackend


def main():
    source = ASSETS/'defocused-singlet.zmx'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    evidence = {}
    for name, coefficients in [('conic', {}), ('aspheric', {4: 1e-6, 6: -1e-9, 16: 1e-20})]:
        output = ASSETS/f'{name}-singlet.zmx'
        if output.exists():
            raise FileExistsError(output)
        with ZOSBackend(source) as b:
            row = b.s.LDE.GetSurfaceAt(1)
            if coefficients:
                row.ChangeType(row.GetSurfaceTypeSettings(b.zp.constants.Editors.LDE.SurfaceType.EvenAspheric))
                for order, value in coefficients.items():
                    row.GetSurfaceCell(getattr(b.zp.constants.Editors.LDE.SurfaceColumn, f'Par{order//2}')).DoubleValue = value
            row.Conic = -.5
            b._validate()
            b.save(output)
            b.load(output)
            inspection = b.inspect()
            shape = inspection['surfaces'][1]
            assert shape['conic'] == -.5
            actual = {r['order']: r['value'] for r in shape['asphere_coefficients']}
            assert all(actual[o] == v for o, v in coefficients.items())
            anchors = []
            for radius in [0, 1, 3, 5]:
                c, k = 1/50, -.5
                expected = c*radius**2/(1+math.sqrt(1-(1+k)*c*c*radius**2))
                expected += sum(value*radius**order for order, value in coefficients.items())
                result = b.s.LDE.GetSag(1, 0., float(radius), 0., 0.)
                assert result[0]
                assert math.isclose(result[1], expected, rel_tol=1e-12, abs_tol=1e-12), (result, expected)
                anchors.append(dict(radius_mm=radius, analytic_sag_mm=expected, native_sag_mm=result[1]))
            evidence[name] = dict(model=str(output), sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                                  inspection=inspection, sag_anchors=anchors)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    (HERE/'shape-fixtures.json').write_bytes((json.dumps(evidence, indent=2, allow_nan=False)+'\n').encode())
    print('Conic and even-asphere fixtures saved/reloaded; eight native/analytic sag anchors passed.')


if __name__ == '__main__':
    main()
