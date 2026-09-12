"""Owned OpticStudio Huygens/POP profile analysis with explicit units and settings."""
from __future__ import annotations

import hashlib
import importlib.metadata
import math
from pathlib import Path

import numpy as np

from _lib.design_contract import finite
from _lib.profile_benchmark import validate_case


def _number(value):
    value = float(value)
    if math.isnan(value):
        raise ValueError('native prescription contains NaN')
    return value if math.isfinite(value) else str(value)


def _receipt(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class NativeProfileBackend:
    """Analyze a disposable file. This interface exposes no prescription edits or save action."""

    def __init__(self, model):
        self.model = Path(model).resolve()
        self.z = self.s = None

    def __enter__(self):
        import zospy as zp
        self.zp = zp
        self.z = zp.ZOS()
        try:
            self.s = self.z.connect(mode='standalone')
            self.restore()
            if str(self.s.Mode) != 'Sequential' or self.s.MCE.NumberOfConfigurations != 1:
                raise ValueError('profile benchmark requires single-configuration sequential model')
            if str(self.s.SystemData.Units.LensUnits) != 'Millimeters':
                raise ValueError('profile benchmark currently requires model length units mm')
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        if self.z is not None:
            self.z.disconnect()
        self.z = self.s = None

    def restore(self):
        self.s.load(str(self.model), saveifneeded=False)
        actual = str(self.s.SystemFile)
        if not actual or Path(actual).resolve() != self.model:
            raise RuntimeError('native model load did not reproduce requested SystemFile identity')

    def inspect(self):
        s = self.s
        surfaces = []
        for index in range(s.LDE.NumberOfSurfaces):
            row = s.LDE.GetSurfaceAt(index)
            physical = row.PhysicalOpticsData
            surfaces.append({'index': index, 'type': str(row.Type), 'comment': str(row.Comment),
                             'radius_mm': _number(row.Radius), 'thickness_mm': _number(row.Thickness),
                             'material': str(row.Material), 'catalog': str(row.MaterialCatalog),
                             'conic': _number(row.Conic), 'coating': str(row.Coating),
                             'semi_diameter_mm': _number(row.SemiDiameter), 'stop': bool(row.IsStop),
                             'parameters': [str(row.GetSurfaceCell(getattr(self.zp.constants.Editors.LDE.SurfaceColumn, f'Par{i}')).Value)
                                            for i in range(1, 13)],
                             'pop': {key: str(getattr(physical, key)) for key in
                                     ('ResampleAfterRefraction', 'AutoResample', 'XSampling', 'YSampling',
                                      'XWidth', 'YWidth', 'UseRaysToPropagateToNextSurface',
                                      'DoNotRescaleBeamSizeUsingRayData', 'UseAngularSpectrumPropagator',
                                      'ReComputePilotBeamParameters', 'UseXaxisReference', 'OutputPilotRadius',
                                      'XRadius', 'YRadius')}})
        waves = [{'index': i, 'wavelength_um': float(s.SystemData.Wavelengths.GetWavelength(i).Wavelength),
                  'weight': float(s.SystemData.Wavelengths.GetWavelength(i).Weight),
                  'primary': bool(s.SystemData.Wavelengths.GetWavelength(i).IsPrimary)}
                 for i in range(1, s.SystemData.Wavelengths.NumberOfWavelengths + 1)]
        fields = [{'index': i, 'x': float(s.SystemData.Fields.GetField(i).X),
                   'y': float(s.SystemData.Fields.GetField(i).Y), 'weight': float(s.SystemData.Fields.GetField(i).Weight),
                   'vignetting': {key: float(getattr(s.SystemData.Fields.GetField(i), key))
                                  for key in ('VDX', 'VDY', 'VCX', 'VCY', 'VAN', 'TAN')},
                   'ignore': bool(s.SystemData.Fields.GetField(i).Ignore)}
                  for i in range(1, s.SystemData.Fields.NumberOfFields + 1)]
        catalogs = []
        catalog_names = sorted({str(name) for name in s.SystemData.MaterialCatalogs.GetCatalogsInUse() if str(name)})
        for name in catalog_names:
            found = False
            for suffix in ('.AGF', '.BGF'):
                path = Path(str(self.z.Application.GlassDir)) / (name + suffix)
                if path.is_file():
                    catalogs.append(_receipt(path))
                    found = True
            if not found:
                raise ValueError(f'cannot establish native catalog file provenance: {name}')
        coating_file = Path(str(self.z.Application.CoatingDir)) / str(s.SystemData.Files.CoatingFile)
        coatings = [_receipt(coating_file)]
        for name in sorted({row['coating'] for row in surfaces} - {''}):
            path = Path(str(self.z.Application.CoatingDir)) / (name + '.ZEC')
            if path.is_file():
                coatings.append(_receipt(path))
        return {'engine': {'name': 'OpticStudio', 'version': str(self.z.version),
                           'zospy': importlib.metadata.version('zospy'),
                           'pythonnet': importlib.metadata.version('pythonnet'),
                           'license': str(self.z.Application.LicenseStatus)},
                'mode': str(s.Mode), 'configurations': int(s.MCE.NumberOfConfigurations),
                'catalog_names': catalog_names, 'catalog_files': catalogs, 'coating_files': coatings,
                'environment': {key: str(getattr(s.SystemData.Environment, key)) for key in
                                ('AdjustIndexToEnvironment', 'Temperature', 'Pressure')},
                'polarization': {key: str(getattr(s.SystemData.Polarization, key)) for key in
                                 ('Unpolarized', 'Jx', 'Jy', 'XPhase', 'YPhase', 'Method',
                                  'ConvertThinFilmPhaseToRayEquivalent')},
                'surfaces': surfaces, 'wavelengths': waves, 'fields': fields,
                'field_type': str(s.SystemData.Fields.GetFieldType()),
                'aperture': {key: str(getattr(s.SystemData.Aperture, key)) for key in
                             ('ApertureType', 'ApertureValue', 'ApodizationType', 'ApodizationFactor')},
                'huygens_reference': str(s.SystemData.Advanced.HuygensIntegralMethod),
                'lens_units': str(s.SystemData.Units.LensUnits)}

    def evaluate(self, raw):
        case = validate_case(raw)
        if case['field'] > self.s.SystemData.Fields.NumberOfFields or case['wavelength'] > self.s.SystemData.Wavelengths.NumberOfWavelengths:
            raise ValueError('case refers to an unavailable field/wavelength')
        return self._huygens(case) if case['method'] == 'huygens' else self._pop(case)

    def _huygens(self, case):
        from System import Enum
        advanced = self.s.SystemData.Advanced
        advanced.HuygensIntegralMethod = Enum.Parse(advanced.HuygensIntegralMethod.GetType(), case['reference'])
        a = self.s.Analyses.New_Analysis_SettingsFirst(self.zp.constants.Analysis.AnalysisIDM.HuygensPsfCrossSection)
        try:
            st = a.GetSettings()
            st.Field.SetFieldNumber(case['field'])
            st.Wavelength.SetWavelengthNumber(case['wavelength'])
            st.PupilSampleSize = getattr(self.zp.constants.Analysis.SampleSizes, f"S_{case['pupil']}x{case['pupil']}")
            st.ImageSampleSize = getattr(self.zp.constants.Analysis.SampleSizes, f"S_{case['image']}x{case['image']}")
            st.ImageDelta = case['delta_um']
            st.Normalize, st.UseCentroid, st.UsePolarization = True, False, case['polarization']
            st.Type = getattr(self.zp.constants.Analysis.Settings.PsfTypes, f"{case['axis'].upper()}_Linear")
            st.RowCol = 0
            readback = {'field': st.Field.GetFieldNumber(), 'wavelength': st.Wavelength.GetWavelengthNumber(),
                        'pupil': str(st.PupilSampleSize), 'image': str(st.ImageSampleSize),
                        'delta_um': float(st.ImageDelta), 'polarization': bool(st.UsePolarization),
                        'normalize': bool(st.Normalize), 'use_centroid': bool(st.UseCentroid),
                        'type': str(st.Type), 'row_col': int(st.RowCol),
                        'reference': str(advanced.HuygensIntegralMethod)}
            if (readback['field'] != case['field'] or readback['wavelength'] != case['wavelength'] or
                    readback['reference'] != case['reference'] or readback['delta_um'] != case['delta_um'] or
                    readback['polarization'] != case['polarization'] or
                    readback['pupil'] != f"S_{case['pupil']}x{case['pupil']}" or
                    readback['image'] != f"S_{case['image']}x{case['image']}" or
                    not readback['normalize'] or readback['use_centroid'] or readback['row_col'] != 0 or
                    readback['type'] != f"{case['axis'].upper()}_Linear"):
                raise RuntimeError('native Huygens settings did not reproduce at readback')
            a.ApplyAndWaitForCompletion()
            result = a.GetResults()
            if result.NumberOfDataSeries != 1:
                raise ValueError('native Huygens did not return exactly one cross-section')
            series = result.GetDataSeries(0)
            x = np.asarray(series.XData.Data, float).reshape(-1)
            y = np.asarray(series.YData.Data, float).reshape(-1)
            if not np.all(np.isfinite(y)) or np.any(y < 0) or not np.any(y > 0):
                raise ValueError('native Huygens returned invalid intensity')
            # Native Huygens image-space coordinates and ImageDelta are micrometres for mm models.
            if len(x) != len(y) or len(x) < 3 or not np.allclose(np.diff(x), case['delta_um'], rtol=1e-9, atol=1e-10):
                raise ValueError('native Huygens coordinate spacing/shape differs from requested micrometres')
            return {'case': case, 'settings_readback': readback,
                    'profiles': {case['axis']: {'x_mm': (x / 1000).tolist(), 'intensity': y.tolist(),
                                               'profile_kind': 'cut', 'intensity_unit': 'relative',
                                               'native_coordinate_unit': 'um', 'native_label': str(series.XLabel)}},
                    'messages': [str(result.GetMessageAt(i).Text) for i in range(result.NumberOfMessages)]}
        finally:
            a.Close()

    def _pop(self, case):
        if case['end_surface'] >= self.s.LDE.NumberOfSurfaces:
            raise ValueError('POP end surface is unavailable')
        a = self.s.Analyses.New_Analysis_SettingsFirst(self.zp.constants.Analysis.AnalysisIDM.PhysicalOpticsPropagation)
        try:
            st = a.GetSettings()
            st.StartSurface.SetSurfaceNumber(case['start_surface'])
            st.EndSurface.SetSurfaceNumber(case['end_surface'])
            st.Wavelength.SetWavelengthNumber(case['wavelength'])
            st.Field.SetFieldNumber(case['field'])
            st.SurfaceToBeam = 0
            st.BeamType = self.zp.constants.Analysis.PhysicalOptics.POPBeamTypes.GaussianWaist
            for i in range(st.NumberOfParameters):
                st.SetParameterValue(i, 0)
            st.SetParameterValue(0, case['waist_x_mm'])
            st.SetParameterValue(1, case['waist_y_mm'])
            st.UseTotalPower, st.TotalPower = True, case['power_w']
            st.UsePolarization, st.SeparateXY = case['polarization'], case['separate_xy']
            st.DataType = self.zp.constants.Analysis.PhysicalOptics.POPDataTypes.Irradiance
            st.XWidth = st.YWidth = case['window_mm']
            st.XSampling = st.YSampling = getattr(self.zp.constants.Analysis.SampleSizes, f"S_{case['sampling']}x{case['sampling']}")
            # Declare the complete computational resampling schedule within the propagated path.
            for index in range(case['start_surface'], case['end_surface']):
                self.s.LDE.GetSurfaceAt(index).PhysicalOpticsData.ResampleAfterRefraction = False
            for row in case['resampling']:
                data = self.s.LDE.GetSurfaceAt(row['surface']).PhysicalOpticsData
                data.ResampleAfterRefraction, data.AutoResample = True, False
                data.XSampling = data.YSampling = getattr(self.zp.constants.Editors.LDE.XYSampling, f"S{case['sampling']}")
                data.XWidth = data.YWidth = row['width_mm']
            readback = {'start_surface': st.StartSurface.GetSurfaceNumber(), 'end_surface': st.EndSurface.GetSurfaceNumber(),
                        'field': st.Field.GetFieldNumber(), 'wavelength': st.Wavelength.GetWavelengthNumber(),
                        'waist_x_mm': st.GetParameterValue(0), 'waist_y_mm': st.GetParameterValue(1),
                        'window_x_mm': float(st.XWidth), 'window_y_mm': float(st.YWidth),
                        'x_sampling': str(st.XSampling), 'y_sampling': str(st.YSampling),
                        'power_w': float(st.TotalPower), 'use_total_power': bool(st.UseTotalPower),
                        'polarization': bool(st.UsePolarization), 'separate_xy': bool(st.SeparateXY),
                        'beam_type': str(st.BeamType), 'data_type': str(st.DataType),
                        'surface_to_beam_mm': float(st.SurfaceToBeam),
                        'beam_parameters': [float(st.GetParameterValue(i)) for i in range(st.NumberOfParameters)]}
            for key in ('start_surface', 'end_surface', 'field', 'wavelength', 'waist_x_mm', 'waist_y_mm', 'power_w', 'polarization', 'separate_xy'):
                if readback[key] != case[key]:
                    raise RuntimeError(f'native POP {key} did not reproduce at readback')
            expected = {'window_x_mm': case['window_mm'], 'window_y_mm': case['window_mm'],
                        'x_sampling': f"S_{case['sampling']}x{case['sampling']}",
                        'y_sampling': f"S_{case['sampling']}x{case['sampling']}",
                        'use_total_power': True, 'beam_type': 'GaussianWaist', 'data_type': 'Irradiance',
                        'surface_to_beam_mm': 0.0}
            for key, value in expected.items():
                if readback[key] != value:
                    raise RuntimeError(f'native POP {key} did not reproduce at readback')
            if any(readback['beam_parameters'][2:]):
                raise RuntimeError('native POP unused beam parameters are not zero')
            schedule = {row['surface']: row for row in case['resampling']}
            readback['resampling'] = []
            for index in range(case['start_surface'], case['end_surface']):
                data = self.s.LDE.GetSurfaceAt(index).PhysicalOpticsData
                actual = {'surface': index, 'enabled': bool(data.ResampleAfterRefraction),
                          'auto': bool(data.AutoResample), 'x_sampling': str(data.XSampling),
                          'y_sampling': str(data.YSampling), 'x_width_mm': float(data.XWidth),
                          'y_width_mm': float(data.YWidth)}
                readback['resampling'].append(actual)
                if actual['enabled'] != (index in schedule):
                    raise RuntimeError('native POP resampling enable did not reproduce at readback')
                if index in schedule and (actual['auto'] or
                        actual['x_sampling'] != f"S{case['sampling']}" or
                        actual['y_sampling'] != f"S{case['sampling']}" or
                        actual['x_width_mm'] != schedule[index]['width_mm'] or
                        actual['y_width_mm'] != schedule[index]['width_mm']):
                    raise RuntimeError('native POP resampling grid did not reproduce at readback')
            a.ApplyAndWaitForCompletion()
            result = a.GetResults()
            if result.NumberOfDataGrids != 1:
                raise ValueError('native POP did not return exactly one irradiance grid')
            grid = result.GetDataGrid(0)
            values = np.asarray(grid.Values, float)
            if values.shape != (grid.Ny, grid.Nx) or not np.all(np.isfinite(values)) or np.any(values < 0):
                raise ValueError('native POP returned an invalid irradiance grid')
            dx, dy = finite(float(grid.Dx), 'grid dx'), finite(float(grid.Dy), 'grid dy')
            if dx <= 0 or dy <= 0:
                raise ValueError('native POP grid spacing must be positive')
            x = finite(float(grid.MinX), 'grid MinX') + np.arange(grid.Nx) * dx
            y = finite(float(grid.MinY), 'grid MinY') + np.arange(grid.Ny) * dy
            if not (x[0] <= 0 <= x[-1] and y[0] <= 0 <= y[-1]):
                raise ValueError('native POP grid does not contain the central axes')
            ix, iy = int(np.argmin(abs(x))), int(np.argmin(abs(y)))
            power = float(values.sum() * dx * dy)
            if power <= 0 or power > case['power_w'] * 1.01:
                raise ValueError('native POP transmitted power is nonpositive or exceeds launched power')
            return {'case': case, 'settings_readback': readback, 'power_w': power,
                    'grid': {'shape': list(values.shape), 'dx_mm': dx, 'dy_mm': dy,
                             'coordinate_convention': 'native MinX/MinY + index*spacing; legacy benchmark convention'},
                    'profiles': {'x': {'x_mm': x.tolist(), 'intensity': values[iy, :].tolist(), 'profile_kind': 'cut',
                                       'intensity_unit': 'W/mm^2', 'orthogonal_position_mm': float(y[iy])},
                                 'y': {'x_mm': y.tolist(), 'intensity': values[:, ix].tolist(), 'profile_kind': 'cut',
                                       'intensity_unit': 'W/mm^2', 'orthogonal_position_mm': float(x[ix])}},
                    'messages': [str(result.GetMessageAt(i).Text) for i in range(result.NumberOfMessages)]}
        finally:
            a.Close()
