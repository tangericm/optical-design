import sys
import traceback

def main():
    import zospy as zp
    print("zospy version:", zp.__version__)

    zos = zp.ZOS()
    print("ZOS object created:", zos)

    oss = zos.connect(mode="standalone")
    print("connected, OpticStudioSystem:", oss)

    # Try to report app/version info
    try:
        app = zos.Application
        print("Application:", app)
    except Exception as e:
        print("no .Application attr:", e)

    try:
        print("ZOSAPI version info:", zos.version)
    except Exception as e:
        print("no .version attr:", e)

    try:
        print("LicenseStatus:", zos.Application.LicenseStatus if hasattr(zos, "Application") else "n/a")
    except Exception as e:
        print("license status err:", e)

    # Build a trivial singlet system
    oss.new(saveifneeded=False)
    lde = oss.LDE
    print("Number of surfaces initially:", lde.NumberOfSurfaces)

    # Insert a surface to make a simple singlet: OBJ, STOP, front, back, IMA
    lde.InsertNewSurfaceAt(1)
    lde.InsertNewSurfaceAt(2)

    surf1 = lde.GetSurfaceAt(1)
    surf1.Radius = 50.0
    surf1.Thickness = 5.0
    surf1.Material = "N-BK7"

    surf2 = lde.GetSurfaceAt(2)
    surf2.Radius = -50.0
    surf2.Thickness = 95.0

    # Set wavelength and EPD
    wave_data = oss.SystemData.Wavelengths
    wave_data.GetWavelength(1).Wavelength = 0.55

    system_data = oss.SystemData
    system_data.Aperture.ApertureValue = 10.0

    print("Surfaces after build:", lde.NumberOfSurfaces)

    # Run an analysis
    from zospy.analyses.mtf import FFTMTF
    result = FFTMTF().run(oss)
    print("FFT MTF analysis ran OK. Result type:", type(result))
    try:
        print(result.data)
    except Exception as e:
        print("could not print result data:", e)

    oss.close(saveifneeded=False)
    zos.disconnect()
    print("DISCONNECTED CLEANLY")
    print("PROBE_SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("PROBE_FAILURE")
        traceback.print_exc()
        sys.exit(1)
