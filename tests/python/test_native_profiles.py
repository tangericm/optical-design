"""Independent native-adapter contracts; .NET stubs never open OpticStudio.

The stubs intentionally allow a setter to return without accepting its value.
This models the failure readback must detect; numerical output is analytic fixture data.
"""
import sys
from types import SimpleNamespace as NS

import numpy as np
import pytest
from _lib.native_profiles import NativeProfileBackend


@pytest.mark.parametrize("native_file", ["", "previous-model.zmx"])
def test_restore_rejects_silent_native_load_failure_despite_wrapper_cached_path(tmp_path, native_file):
    backend = NativeProfileBackend(tmp_path / "requested.zmx")
    calls = []
    # ZOSPy 2.1.5 caches the requested _OpenFile even if native LoadFile returns
    # without accepting it. SystemFile reads the native model identity directly.
    backend.s = NS(SystemFile=native_file, _OpenFile=str(backend.model),
                   load=lambda path, **kwargs: calls.append((path, kwargs)))
    with pytest.raises(RuntimeError, match="load|file|identity|readback"):
        backend.restore()
    assert calls == [(str(backend.model), {"saveifneeded": False})]


def test_restore_accepts_matching_native_file_without_saving(tmp_path):
    backend = NativeProfileBackend(tmp_path / "requested.zmx")
    calls = []
    backend.s = NS(SystemFile=str(backend.model),
                   load=lambda path, **kwargs: calls.append((path, kwargs)))
    backend.restore()
    assert calls == [(str(backend.model), {"saveifneeded": False})]


class EnumValue(str):
    def GetType(self):
        return type(self)


class RejectingSettings(NS):
    def __setattr__(self, name, value):
        object.__setattr__(self, name, self.__dict__.get("reject", {}).get(name, value))


class IndexSetting:
    def __init__(self):
        self.value = 1

    def SetFieldNumber(self, value):
        self.value = value

    SetWavelengthNumber = SetSurfaceNumber = SetFieldNumber

    def GetFieldNumber(self):
        return self.value

    GetWavelengthNumber = GetSurfaceNumber = GetFieldNumber


class Settings(RejectingSettings):
    def __init__(self, reject=None):
        super().__init__(reject=reject or {}, Field=IndexSetting(), Wavelength=IndexSetting(),
                         StartSurface=IndexSetting(), EndSurface=IndexSetting(), NumberOfParameters=4,
                         parameters=[0, 0, 0, 0])

    def SetParameterValue(self, index, value):
        self.parameters[index] = self.__dict__.get("reject_parameters", {}).get(index, value)

    def GetParameterValue(self, index):
        return self.parameters[index]


class Analysis:
    def __init__(self, settings, result):
        self.settings, self.result = settings, result
        self.closed = False
        self.applied = False

    def GetSettings(self):
        return self.settings

    def GetResults(self):
        return self.result

    def ApplyAndWaitForCompletion(self):
        self.applied = True

    def Close(self):
        self.closed = True


def huygens_case():
    return {"id": "hx", "method": "huygens", "axis": "x", "field": 1, "wavelength": 0,
            "pupil": 512, "image": 128, "delta_um": 6, "polarization": True, "reference": "Planar"}


def pop_case():
    return {"id": "p9", "method": "pop", "field": 1, "wavelength": 9, "sampling": 128,
            "window_mm": .4, "waist_x_mm": .0025, "waist_y_mm": .0025, "start_surface": 1,
            "end_surface": 6, "polarization": True, "separate_xy": True, "power_w": 1,
            "resampling": [{"surface": 4, "width_mm": 8}]}


@pytest.fixture
def native_stub(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "System", NS(Enum=NS(Parse=lambda _type, value: EnumValue(value))))
    monkeypatch.setattr("_lib.native_profiles.importlib.metadata.version", lambda _name: "stub")
    sizes = NS(**{f"S_{n}x{n}": f"S_{n}x{n}" for n in (32, 64, 128, 256, 512, 1024)})
    physical_constants = NS(POPBeamTypes=NS(GaussianWaist="GaussianWaist"), POPDataTypes=NS(Irradiance="Irradiance"))
    constants = NS(Analysis=NS(SampleSizes=sizes, PhysicalOptics=physical_constants,
                              Settings=NS(PsfTypes=NS(X_Linear="X_Linear", Y_Linear="Y_Linear")),
                              AnalysisIDM=NS(HuygensPsfCrossSection="H", PhysicalOpticsPropagation="P")),
                   Editors=NS(LDE=NS(XYSampling=NS(S128="S128"), SurfaceColumn=NS(**{f"Par{i}": i for i in range(1, 13)}))))
    physical = []
    surfaces = []
    for i in range(8):
        p = RejectingSettings(ResampleAfterRefraction=False, AutoResample=False, XSampling="S128", YSampling="S128",
                              XWidth=.4, YWidth=.4, UseRaysToPropagateToNextSurface=False,
                              DoNotRescaleBeamSizeUsingRayData=False, UseAngularSpectrumPropagator=False,
                              ReComputePilotBeamParameters=False, UseXaxisReference=False, OutputPilotRadius=False,
                              XRadius=0, YRadius=0)
        physical.append(p)
        surfaces.append(NS(PhysicalOpticsData=p, Type="Standard", Comment="", Radius=50, Thickness=5,
                           Material="", MaterialCatalog="", Conic=0, Coating="", SemiDiameter=1, IsStop=i == 1,
                           GetSurfaceCell=lambda _column: NS(Value=0)))
    wave = NS(Wavelength=.532, Weight=1, IsPrimary=True)
    field = NS(X=0, Y=0, Weight=1, VDX=0, VDY=0, VCX=0, VCY=0, VAN=0, TAN=0, Ignore=False)
    (tmp_path / "coating.dat").write_text("synthetic coating provenance fixture", encoding="utf-8")
    data = NS(Wavelengths=NS(NumberOfWavelengths=18, GetWavelength=lambda _index: wave),
              Fields=NS(NumberOfFields=1, GetField=lambda _index: field, GetFieldType=lambda: "Angle"),
              Units=NS(LensUnits="Millimeters"),
              Aperture=NS(ApertureType="EPD", ApertureValue=2, ApodizationType="Gaussian", ApodizationFactor=1),
              Advanced=NS(HuygensIntegralMethod=EnumValue("Planar")),
              Environment=NS(Temperature=20, Pressure=1, AdjustIndexToEnvironment=False),
              Polarization=NS(Jx=1, Jy=0, XPhase=0, YPhase=0, Unpolarized=False,
                              Method="Standard", ConvertThinFilmPhaseToRayEquivalent=False),
              MaterialCatalogs=NS(GetCatalogsInUse=list), Files=NS(CoatingFile="coating.dat"))
    backend = NativeProfileBackend(tmp_path / "never-opened.zmx")
    backend.zp = NS(constants=constants)
    backend.z = NS(version="stub", Application=NS(LicenseStatus="stub", GlassDir=str(tmp_path), CoatingDir=str(tmp_path)))
    backend.s = NS(SystemData=data, Mode="Sequential", MCE=NS(NumberOfConfigurations=1, CurrentConfiguration=1),
                   LDE=NS(NumberOfSurfaces=len(surfaces), GetSurfaceAt=lambda i: surfaces[i]))

    def prepare(method, *, reject=None, y_override=None, grid_origin=None):
        settings = Settings(reject)
        if method == "huygens":
            x = (np.arange(128)-64)*6
            y = np.exp(-2*(x/200)**2) if y_override is None else y_override
            series = NS(XData=NS(Data=x), YData=NS(Data=y), XLabel="Image position (microns)")
            result = NS(NumberOfDataSeries=1, NumberOfMessages=0, GetDataSeries=lambda _index: series)
        else:
            iy, ix = np.indices((128, 128))
            values = 2 + iy/128 + 2*ix/128
            grid = NS(Values=values, Ny=128, Nx=128, Dx=.001, Dy=.001,
                      MinX=-.064 if grid_origin is None else grid_origin, MinY=-.064)
            result = NS(NumberOfDataGrids=1, NumberOfMessages=0, GetDataGrid=lambda _index: grid)
        analysis = Analysis(settings, result)
        backend.s.Analyses = NS(New_Analysis_SettingsFirst=lambda _which: analysis)
        return backend, analysis, physical
    return prepare


def test_huygens_micrometre_axis_converts_to_mm_without_normalizing_again(native_stub):
    backend, analysis, _ = native_stub("huygens")
    result = backend.evaluate(huygens_case())
    profile = result["profiles"]["x"]
    np.testing.assert_allclose(profile["x_mm"], (np.arange(128)-64)*.006)
    np.testing.assert_allclose(profile["intensity"], np.exp(-2*(((np.arange(128)-64)*6)/200)**2))
    assert profile["profile_kind"] == "cut" and profile["intensity_unit"] == "relative"
    assert analysis.closed


@pytest.mark.parametrize("setting,value", [("Normalize", False), ("ImageSampleSize", "S_64x64"),
                                          ("UsePolarization", False), ("RowCol", 1)])
def test_huygens_rejected_settings_fail_before_analysis_and_close(native_stub, setting, value):
    backend, analysis, _ = native_stub("huygens", reject={setting: value})
    with pytest.raises(RuntimeError, match="readback"):
        backend.evaluate(huygens_case())
    assert not analysis.applied and analysis.closed


@pytest.mark.parametrize("kind", ["nan", "negative", "zero"])
def test_huygens_invalid_native_intensity_is_rejected_and_closed(native_stub, kind):
    y = np.ones(128)
    if kind == "zero":
        y[:] = 0
    else:
        y[3] = np.nan if kind == "nan" else -1
    backend, analysis, _ = native_stub("huygens", y_override=y)
    with pytest.raises(ValueError):
        backend.evaluate(huygens_case())
    assert analysis.closed


def test_pop_preserves_absolute_irradiance_and_central_cut_orientation(native_stub):
    backend, analysis, _ = native_stub("pop")
    result = backend.evaluate(pop_case())
    np.testing.assert_allclose(result["profiles"]["x"]["intensity"], 2.5+2*np.arange(128)/128)
    np.testing.assert_allclose(result["profiles"]["y"]["intensity"], 3+np.arange(128)/128)
    assert result["profiles"]["x"]["orthogonal_position_mm"] == pytest.approx(0)
    assert result["profiles"]["x"]["intensity_unit"] == "W/mm^2"
    assert result["power_w"] == pytest.approx((2+3*127/256)*128**2*.001**2)
    assert analysis.closed


@pytest.mark.parametrize("setting,value", [("XSampling", "S_64x64"), ("YSampling", "S_64x64"),
                                          ("XWidth", 3), ("YWidth", 3), ("UseTotalPower", False),
                                          ("BeamType", "TopHat"), ("DataType", "Phase"), ("SurfaceToBeam", 1)])
def test_pop_verifies_every_setting_that_controls_physical_meaning(native_stub, setting, value):
    backend, analysis, _ = native_stub("pop", reject={setting: value})
    with pytest.raises(RuntimeError, match="readback"):
        backend.evaluate(pop_case())
    assert not analysis.applied and analysis.closed


@pytest.mark.parametrize("surface,setting,value", [(2, "ResampleAfterRefraction", True),
                                                 (4, "AutoResample", True), (4, "XWidth", 3)])
def test_pop_verifies_full_computational_resampling_schedule(native_stub, surface, setting, value):
    backend, analysis, physical = native_stub("pop")
    physical[surface].reject = {setting: value}
    setattr(physical[surface], setting, value)
    with pytest.raises(RuntimeError, match="readback|resampl"):
        backend.evaluate(pop_case())
    assert not analysis.applied and analysis.closed


@pytest.mark.parametrize("origin", [float("nan"), float("inf"), 1])
def test_pop_invalid_or_off_axis_grid_is_not_returned_as_central_cut(native_stub, origin):
    backend, analysis, _ = native_stub("pop", grid_origin=origin)
    with pytest.raises(ValueError):
        backend.evaluate(pop_case())
    assert analysis.closed


@pytest.mark.parametrize("change", ["units", "mode", "configuration", "environment", "polarization", "vignetting", "coating"])
def test_baseline_inspection_cannot_hide_model_identity_changes(native_stub, change):
    backend, _, _ = native_stub("pop")
    before = backend.inspect()
    if change == "units":
        backend.s.SystemData.Units.LensUnits = "Centimeters"
    elif change == "mode":
        backend.s.Mode = "NonSequential"
    elif change == "configuration":
        backend.s.MCE.NumberOfConfigurations = 2
    elif change == "environment":
        backend.s.SystemData.Environment.Temperature = 60
    elif change == "polarization":
        backend.s.SystemData.Polarization.Jy = 1
    elif change == "vignetting":
        backend.s.SystemData.Fields.GetField(1).VDX = .1
    else:
        from pathlib import Path
        (Path(backend.z.Application.CoatingDir) / "coating.dat").write_text("changed synthetic coating")
    try:
        after = backend.inspect()
    except ValueError:
        return
    assert after != before, f"baseline inspection hid changed {change}"


def test_pop_unused_beam_parameter_must_read_back_zero(native_stub):
    backend, analysis, _ = native_stub("pop")
    analysis.settings.reject_parameters = {2: .1}
    with pytest.raises(RuntimeError, match="beam parameters|readback"):
        backend.evaluate(pop_case())
    assert not analysis.applied and analysis.closed


@pytest.mark.parametrize("invalid", ["nan", "negative", "zero", "shape", "excess_power"])
def test_pop_invalid_irradiance_never_returns_physical_profiles(native_stub, invalid):
    backend, analysis, _ = native_stub("pop")
    grid = analysis.result.GetDataGrid(0)
    if invalid == "nan":
        grid.Values[0, 0] = np.nan
    elif invalid == "negative":
        grid.Values[0, 0] = -1
    elif invalid == "zero":
        grid.Values[:] = 0
    elif invalid == "shape":
        grid.Values = grid.Values[:100]
    else:
        grid.Values[:] = 1e5
    with pytest.raises(ValueError):
        backend.evaluate(pop_case())
    assert analysis.closed
