"""Build the dev.5 synthetic field/wavelength example; never edits a source lens.

Run once with --native in the pinned ZOSPy environment to include the native fixture.
All acceptance limits are specified here before any optical evaluation.
"""
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT/'skills/optical-design/assets'
OUT = ASSETS/'field-validation'
HERE = Path(__file__).resolve().parent
FIELDS = [0, 3, 6]
WAVES = [.4861327, .55, .6562725]


def write(path, data):
    path.write_bytes((json.dumps(data, indent=2)+'\n').encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=False)
    portable = json.loads((ASSETS/'portable-singlet.json').read_text())
    portable['name'] = 'Synthetic singlet: fields 0, 3, 6 deg; three wavelengths; primary index 2'
    portable['fields']['fields'] = [dict(x=0., y=y, vx=0., vy=0., weight=1.) for y in FIELDS]
    portable['wavelengths']['wavelengths'] = [dict(value=w, is_primary=i == 1, unit='um', weight=1.)
                                             for i, w in enumerate(WAVES)]
    write(OUT/'portable.json', portable)
    search = json.loads((ASSETS/'optimization-spec.json').read_text())
    search['name'] = 'Search on axis at model primary wavelength index 2'
    search['wavelengths'] = [2]
    for row in [*search['requirements'], search['objective']]:
        if 'wavelength' in row:
            row['wavelength'] = 2
    write(OUT/'search.json', search)
    control = copy.deepcopy(search)
    control.pop('objective')
    control['name'] = 'Control validation repeats the search conditions and limits'
    control['budget'] = dict(max_evaluations=7, timeout_s=120)
    write(OUT/'control.json', control)
    validation = copy.deepcopy(control)
    validation['name'] = 'Separate validation: same limits over all nine field/wavelength pairs'
    validation['fields'] = [1, 2, 3]
    validation['wavelengths'] = [1, 2, 3]
    validation['budget']['timeout_s'] = 300
    validation['requirements'] = [r for r in validation['requirements'] if 'field' not in r]
    for field in [1, 2, 3]:
        for wave in [1, 2, 3]:
            validation['requirements'].append(dict(id=f'spot-f{field}-w{wave}', metric='rms_spot_um',
                unit='um', field=field, wavelength=wave, max=30))
            for axis in ('tangential', 'sagittal'):
                validation['requirements'].append(dict(id=f'mtf-{axis}-f{field}-w{wave}', metric='mtf',
                    unit='1', field=field, wavelength=wave, frequency=20, axis=axis, min=.3))
    write(OUT/'validation.json', validation)
    if args.native:
        sys.path.insert(0, str(ROOT/'skills/optical-design/scripts'))
        from _lib.zos_backend import ZOSBackend
        source = ASSETS/'defocused-singlet.zmx'
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        with ZOSBackend(source) as backend:
            fields = backend.s.SystemData.Fields
            for y in FIELDS[1:]:
                fields.AddField(0, y, 1)
            waves = backend.s.SystemData.Wavelengths
            waves.GetWavelength(1).Wavelength = WAVES[0]
            for wavelength in WAVES[1:]:
                waves.AddWavelength(wavelength, 1)
            waves.GetWavelength(2).MakePrimary()
            assert waves.GetWavelength(2).IsPrimary
            backend._validate()
            backend.save(OUT/'native.zmx')
            backend.load(OUT/'native.zmx')
            inspection = backend.inspect()
            assert [w['primary'] for w in inspection['invariants']['wavelengths']] == [False, True, False]
            assert [w['um'] for w in inspection['invariants']['wavelengths']] == WAVES
            assert [f['y_deg'] for f in inspection['invariants']['fields']] == FIELDS
            write(HERE/'native-fixture-inspection.json', inspection)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    manifest = {'fields_y_deg': FIELDS, 'wavelengths_um': WAVES, 'primary_wavelength_index': 2,
                'rms_limit_um': 30, 'mtf_limit_20_cyc_per_mm': .3, 'sampling': 64,
                'purpose': 'predeclared synthetic numerical coverage example; not physical validation',
                'inputs_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(OUT.iterdir()) if p.suffix.lower() != '.zda'}}
    write(HERE/'predeclared-inputs.json', manifest)
    print('Built example and frozen input manifest.')


if __name__ == '__main__':
    main()
