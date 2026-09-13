"""Conservative standalone OpticStudio adapter; never attaches to an editor session."""
from __future__ import annotations

import importlib.metadata
import math
from pathlib import Path

import numpy as np

from _lib.design_contract import finite


def interpolate_mtf(frequencies, values, frequency):
    x, y = np.asarray(frequencies, float), np.asarray(values, float)
    if (x.ndim != 1 or len(x) < 2 or x.shape != y.shape or
            not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or
            np.any(np.diff(x) <= 0) or np.any(y < -1e-8) or np.any(y > 1 + 1e-8)):
        raise ValueError('invalid native MTF samples')
    if not x[0] <= frequency <= x[-1]:
        raise ValueError('requested frequency outside native MTF support; extrapolation prohibited')
    return float(np.interp(frequency, x, np.clip(y, 0, 1)))


def _number(value):
    value = float(value)
    return value if math.isfinite(value) else ('Infinity' if value > 0 else '-Infinity')


def validate_surface(row):
    thickness = finite(row['thickness_mm'], 'internal thickness')
    if thickness < 0 or (row['material'] and thickness == 0):
        raise ValueError('internal thickness must be nonnegative; glass thickness must be positive')
    if any(finite(v, 'surface tilt/decenter') != 0 for v in row['tilts']):
        raise ValueError('surface tilt/decenter is outside the centered v1 contract')
    if row['aperture'] != 'None':
        raise ValueError('explicit surface apertures/obscurations are outside the v1 contract')


def _surface_geometry(row):
    tilt = row.TiltDecenterData
    return {'tilts': [float(getattr(tilt, side + 'Surface' + name)) for side in ('Before', 'After')
                      for name in ('DecenterX', 'DecenterY', 'TiltX', 'TiltY', 'TiltZ')],
            'aperture': str(row.ApertureData.CurrentType),
            'semi_diameter_solve': str(row.SemiDiameterCell.GetSolveData().Type)}


def surface_shape(row, columns):
    """Read every fixed shape term for verified centered native surface types."""
    kind = str(row.Type)
    if kind not in {'Standard', 'EvenAspheric'}:
        raise ValueError(f'unsupported native surface type: {kind}')
    if str(row.ConicCell.GetSolveData().Type) != 'Fixed':
        raise ValueError('conic solve must be fixed')
    result = {'conic': finite(float(row.Conic), 'conic'), 'asphere_coefficients': []}
    if kind == 'EvenAspheric':
        for index in range(1, 9):
            cell = row.GetSurfaceCell(getattr(columns, f'Par{index}'))
            if str(cell.GetSolveData().Type) != 'Fixed':
                raise ValueError('asphere coefficient solves must be fixed')
            order = 2*index
            result['asphere_coefficients'].append({'order': order,
                'value': finite(float(cell.DoubleValue), f'asphere coefficient {order}'),
                'unit': f'mm^{1-order}'})
    return result


def capability_check():
    import zospy as zp
    z = zp.ZOS()
    try:
        z.connect(mode='standalone')
        return {'available': True, 'engine': 'OpticStudio', 'version': str(z.version),
                'zospy_version': importlib.metadata.version('zospy'),
                'pythonnet_version': importlib.metadata.version('pythonnet'),
                'license': str(z.Application.LicenseStatus),
                'valid_api_license': bool(z.Application.IsValidLicenseForAPI),
                'connection_mode': 'standalone'}
    finally:
        z.disconnect()


class ZOSBackend:
    """mm, sequential, centered conic/even-aspheric refractive models, angle fields, EPD."""

    model_suffix = '.zmx'

    def __init__(self, model):
        self.model = Path(model).resolve()
        self.z = self.s = None

    def __enter__(self):
        import zospy as zp
        self.zp = zp
        self.z = zp.ZOS()
        try:
            self.s = self.z.connect(mode='standalone')
            self.load(self.model)
            self._validate()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        if self.z is not None:
            self.z.disconnect()
        self.s = self.z = None

    def _validate(self):
        s = self.s
        if str(s.Mode) != 'Sequential' or s.MCE.NumberOfConfigurations != 1:
            raise ValueError('only single-configuration sequential models are supported')
        if str(s.SystemData.Units.LensUnits) != 'Millimeters':
            raise ValueError('native model must use millimeters')
        if str(s.SystemData.Fields.GetFieldType()) != 'Angle':
            raise ValueError('v1 supports angle fields only')
        if str(s.SystemData.Fields.Normalization) != 'Radial':
            raise ValueError('v1 ray validation requires radial field normalization')
        if str(s.SystemData.Aperture.ApertureType) != 'EntrancePupilDiameter':
            raise ValueError('v1 requires entrance pupil diameter aperture')
        if s.LDE.NumberOfSurfaces < 3:
            raise ValueError('model needs an optical surface and an image')
        if s.LDE.GetSurfaceAt(0).Material:
            raise ValueError('object space must be air')
        for i in range(1, s.SystemData.Fields.NumberOfFields + 1):
            field = s.SystemData.Fields.GetField(i)
            if field.Ignore or any(getattr(field, p) != 0 for p in ('VDX', 'VDY', 'VCX', 'VCY', 'VAN', 'TAN')):
                raise ValueError('ignored or vignetted/tilted fields are outside the v1 contract')
        for i in range(s.LDE.NumberOfSurfaces):
            row = s.LDE.GetSurfaceAt(i)
            surface_shape(row, self.zp.constants.Editors.LDE.SurfaceColumn)
            if str(row.Material).upper() == 'MIRROR':
                raise ValueError('reflective systems are outside the v1 contract')
            if str(row.Coating):
                raise ValueError('coated surfaces are outside the scalar native contract')
            if any(str(cell.GetSolveData().Type) != 'Fixed' for cell in (row.RadiusCell, row.ThicknessCell)):
                raise ValueError('radius/thickness solves must be fixed before running this workflow')
            geometry = _surface_geometry(row)
            if any(v != 0 for v in geometry['tilts']) or geometry['aperture'] != 'None':
                raise ValueError('surface tilt/decenter and explicit apertures are outside the v1 contract')
            if 0 < i < self.image_surface:
                validate_surface(dict(geometry, thickness_mm=float(row.Thickness), material=str(row.Material)))
            if str(row.TiltDecenterData.AfterSurfaceMode) != 'Explicit' or str(row.TiltDecenterData.CoordinateReturn) != 'None':
                raise ValueError('coordinate returns and implicit after-surface transforms are unsupported')
            if geometry['semi_diameter_solve'] not in {'Automatic', 'Fixed'} or row.ApertureData.IsPickedUp:
                raise ValueError('aperture solves/pickups are unsupported')
        if self.s.LDE.GetSurfaceAt(self.image_surface - 1).Material:
            raise ValueError('final image-space gap must be air')
        if self.focus_position() <= 0:
            raise ValueError('final image-space gap must be positive and finite')

    @property
    def image_surface(self):
        return self.s.LDE.NumberOfSurfaces - 1

    def focus_position(self):
        return finite(float(self.s.LDE.GetSurfaceAt(self.image_surface - 1).Thickness), 'focus')

    def set_focus(self, position):
        position = finite(position, 'focus')
        if position <= 0:
            raise ValueError('focus gap must be positive')
        self.s.LDE.GetSurfaceAt(self.image_surface - 1).Thickness = position

    def _parameter_cell(self, surface, name):
        if type(surface) is not int or not 1 <= surface < self.image_surface:
            raise ValueError('parameter surface must be a real surface excluding object/image')
        if name not in {'radius_mm', 'thickness_mm'}:
            raise ValueError('supported parameters: radius_mm, thickness_mm')
        return self.s.LDE.GetSurfaceAt(surface), 'Radius' if name == 'radius_mm' else 'Thickness'

    def get_parameter(self, surface, name):
        row, attr = self._parameter_cell(surface, name)
        return finite(float(getattr(row, attr)), name)

    def set_parameter(self, surface, name, value):
        row, attr = self._parameter_cell(surface, name)
        value = finite(value, name)
        if (name == 'thickness_mm' and value <= 0) or (name == 'radius_mm' and value == 0):
            raise ValueError('perturbation creates nonphysical thickness or zero radius')
        setattr(row, attr, value)

    def save(self, path):
        self.s.save_as(str(Path(path).resolve()))

    def load(self, path):
        requested = Path(path).resolve()
        self.s.load(str(requested), saveifneeded=False)
        actual = str(self.s.SystemFile)
        if not actual or Path(actual).resolve() != requested:
            raise RuntimeError('native model load did not reproduce requested SystemFile identity')

    def inspect(self):
        s = self.s
        surfaces, fixed = [], []
        for i in range(s.LDE.NumberOfSurfaces):
            row = s.LDE.GetSurfaceAt(i)
            item = {'index': i, 'is_image': bool(row.IsImage), 'is_stop': bool(row.IsStop),
                    'type': str(row.Type), 'radius_mm': _number(row.Radius),
                    'thickness_mm': _number(row.Thickness), 'material': str(row.Material),
                    'conic': float(row.Conic), 'coating': str(row.Coating)}
            item.update(_surface_geometry(row))
            item.update(surface_shape(row, self.zp.constants.Editors.LDE.SurfaceColumn))
            if item['semi_diameter_solve'] == 'Fixed':
                item['semi_diameter_mm'] = float(row.SemiDiameter)
            surfaces.append(item)
            invariant = item.copy()
            if i == self.image_surface - 1:
                del invariant['thickness_mm']
            fixed.append(invariant)
        fields = [{'index': i, 'x_deg': float(s.SystemData.Fields.GetField(i).X),
                   'y_deg': float(s.SystemData.Fields.GetField(i).Y),
                   'weight': float(s.SystemData.Fields.GetField(i).Weight)}
                  for i in range(1, s.SystemData.Fields.NumberOfFields + 1)]
        waves = [{'index': i, 'um': float(s.SystemData.Wavelengths.GetWavelength(i).Wavelength),
                  'weight': float(s.SystemData.Wavelengths.GetWavelength(i).Weight),
                  'primary': bool(s.SystemData.Wavelengths.GetWavelength(i).IsPrimary)}
                 for i in range(1, s.SystemData.Wavelengths.NumberOfWavelengths + 1)]
        invariants = {'surfaces': fixed, 'fields': fields, 'wavelengths': waves,
                      'aperture_type': str(s.SystemData.Aperture.ApertureType),
                      'aperture_mm': float(s.SystemData.Aperture.ApertureValue), 'lens_units': 'mm'}
        return {'engine': {'name': 'OpticStudio', 'version': str(self.z.version),
                           'zospy_version': importlib.metadata.version('zospy'),
                           'pythonnet_version': importlib.metadata.version('pythonnet'),
                           'license': str(self.z.Application.LicenseStatus)},
                'focus_mm': self.focus_position(), 'image_surface': self.image_surface,
                'surfaces': surfaces, 'invariants': invariants,
                'limits': ['Sequential centered Standard conic/EvenAspheric refractive systems; fixed shape coefficients; angle fields; mm; EPD.',
                           'Geometric centroid RMS spot and scalar FFT MTF are distinct metrics.',
                           'A sparse pupil ray check detects gross failures; it is not a full vignetting analysis.']}

    def _check_rays(self, field, wave):
        fields = self.s.SystemData.Fields
        f = fields.GetField(field)
        scale = max(math.hypot(fields.GetField(i).X, fields.GetField(i).Y)
                    for i in range(1, fields.NumberOfFields + 1))
        hx, hy = (f.X / scale, f.Y / scale) if scale else (0, 0)
        tool = self.s.Tools.OpenBatchRayTrace()
        try:
            points = [(0, 0)] + [(r * math.cos(t), r * math.sin(t))
                                       for r in (.5, .95) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
            data = tool.CreateNormUnpol(len(points), self.zp.constants.Tools.RayTrace.RaysType.Real, self.image_surface)
            for px, py in points:
                data.AddRay(wave, hx, hy, float(px), float(py), self.zp.constants.Tools.RayTrace.OPDMode.None_)
            tool.RunAndWaitForCompletion()
            data.StartReadingResults()
            for _ in points:
                result = data.ReadNextResult()
                if not result[0] or result[2] != 0 or result[3] != 0:
                    raise ValueError(f'ray failure or vignetting at field {field}, wavelength {wave}: {result[:4]}')
        finally:
            tool.Close()

    def evaluate(self, spec):
        from System import Enum
        from zospy.analyses.mtf import FFTMTF
        from zospy.analyses.reports import SystemData
        s = self.s
        if max(spec.data['fields']) > s.SystemData.Fields.NumberOfFields or max(spec.data['wavelengths']) > s.SystemData.Wavelengths.NumberOfWavelengths:
            raise ValueError('specification references a missing native field/wavelength')
        if spec.data['analysis']['use_polarization']:
            raise ValueError('v1 metric contract is scalar; polarized analysis is not yet supported')
        general = SystemData().run(s).data.general_lens_data
        primary = next(i for i in range(1, s.SystemData.Wavelengths.NumberOfWavelengths + 1)
                       if s.SystemData.Wavelengths.GetWavelength(i).IsPrimary)
        rows = [{'metric': name, 'unit': unit, 'value': finite(value, name)} for name, unit, value in [
            ('efl_mm', 'mm', s.MFE.GetOperandValue(self.zp.constants.Editors.MFE.MeritOperandType.EFFL, 0, primary, 0, 0, 0, 0, 0, 0)),
            ('f_number', '1', general.image_space_f_number),
            ('total_track_mm', 'mm', general.total_track),
            ('image_distance_mm', 'mm', self.focus_position())]]
        for row in rows[:2]:
            row['settings'] = {'wavelength': primary, 'wavelength_um': float(s.SystemData.Wavelengths.GetWavelength(primary).Wavelength)}
        sampling = spec.data['analysis']['sampling']
        for field in spec.data['fields']:
            for wave in spec.data['wavelengths']:
                self._check_rays(field, wave)
                analysis = s.Analyses.New_StandardSpot()
                try:
                    settings = analysis.GetSettings()
                    # StandardSpot with wavelength 0 returns a combined result even
                    # when GetRMSSpotSizeFor is called with different wavelength indices.
                    settings.Field.SetFieldNumber(field)
                    settings.Wavelength.SetWavelengthNumber(wave)
                    settings.ReferTo = Enum.Parse(settings.ReferTo.GetType(), 'Centroid')
                    settings.RayDensity = max(6, sampling // 8)
                    settings.UsePolarization = False
                    analysis.ApplyAndWaitForCompletion()
                    if (settings.Field.GetFieldNumber() != field or
                            settings.Wavelength.GetWavelengthNumber() != wave):
                        raise ValueError('native spot field/wavelength selection did not persist')
                    spot = finite(float(analysis.GetResults().SpotData.GetRMSSpotSizeFor(field, wave)), 'RMS spot')
                    if spot < 0:
                        raise ValueError('negative native RMS spot')
                finally:
                    analysis.Close()
                rows.append({'metric': 'rms_spot_um', 'field': field, 'wavelength': wave, 'unit': 'um', 'value': spot,
                             'settings': {'reference': 'centroid', 'ray_density': max(6, sampling // 8),
                                          'native_analysis': 'StandardSpot', 'ray_check_count': 17,
                                          'field': field, 'field_xy_deg': [float(s.SystemData.Fields.GetField(field).X),
                                                                         float(s.SystemData.Fields.GetField(field).Y)],
                                          'wavelength': wave, 'wavelength_um': float(s.SystemData.Wavelengths.GetWavelength(wave).Wavelength),
                                          'spectral_mode': 'monochromatic'}})
                frequencies = spec.data['frequencies_cyc_per_mm']
                if not frequencies:
                    continue
                df = FFTMTF(sampling=f'{sampling}x{sampling}', field=field, wavelength=wave,
                            maximum_frequency=max(frequencies) * 1.01, use_polarization=False).run(s).data
                if df is None or df.shape[1] != 2:
                    raise ValueError('native FFT MTF did not return the expected two axes')
                for axis, column in [('tangential', 0), ('sagittal', 1)]:
                    if axis.lower() not in str(df.columns[column]).lower():
                        raise ValueError('unexpected native FFT MTF column identity')
                    for frequency in frequencies:
                        rows.append({'metric': 'mtf', 'field': field, 'wavelength': wave, 'frequency': frequency,
                                     'axis': axis, 'unit': '1', 'value': interpolate_mtf(df.index, df.iloc[:, column], frequency),
                                     'settings': {'analysis': 'FFTMTF', 'sampling': sampling, 'polarization': False,
                                                  'frequency_interpolation': 'linear; no extrapolation'}})
        return rows
