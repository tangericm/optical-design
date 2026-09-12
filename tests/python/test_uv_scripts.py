import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "optical-design" / "scripts"
pytestmark = pytest.mark.uv


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
@pytest.mark.parametrize("script,argv", [
    ("resolve.py", ["airy", "--wavelength-um", "0.55", "--fnum", "4"]),
    ("zernike.py", ["strehl", "--rms-waves", "0.05"]),
    ("wavefront.py", ["sample-check", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "1"]),
    ("interfero.py", ["cavity", "--gap-mm", "5", "--wavelength-um", "0.6328"]),
])
def test_scripts_run_through_uv(script, argv):
    result = subprocess.run(
        ["uv", "run", str(SCRIPTS / script), *argv, "--json"],
        capture_output=True, text=True, timeout=600, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["schema"] == "1"


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
def test_usage_error_exits_2():
    result = subprocess.run(
        ["uv", "run", str(SCRIPTS / "resolve.py"), "airy"],
        capture_output=True, text=True, timeout=600, check=False,
    )
    assert result.returncode == 2
