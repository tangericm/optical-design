"""The external grader must distinguish focal position from detector position."""
import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("optiland")

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("eval_checker", ROOT / "evals/check_first_order.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.mark.tier1
def test_back_focus_uses_parallel_ray_intercept_not_detector_gap(tmp_path):
    from optiland.fileio import load_optiland_file

    # Thick-lens power and back focus provide an anchor independent of the checker trace.
    model = ROOT / "skills/optical-design/assets/portable-singlet.json"
    lens = load_optiland_file(str(model))
    n = float(lens.surfaces.surfaces[1].material_post.n(0.55).item())
    front_power, back_power = (n - 1) / 50, (1 - n) / -50
    power = front_power + back_power - 5 * front_power * back_power / n
    expected_bfl = (1 - 5 * front_power / n) / power
    result = checker.first_order_summary(model)
    assert result["bfl_mm"] == pytest.approx(expected_bfl)
    assert result["image_distance_mm"] == pytest.approx(60)
