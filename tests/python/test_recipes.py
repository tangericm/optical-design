"""Executes every ```python fenced block in optiland-recipes.md and asserts it runs.

Each recipe in the reference is meant to be self-contained and runnable as-is
against `optiland.samples` objects. This test is the thing that keeps that
promise true over time: it extracts every fenced Python block from the markdown,
in order, and runs it in a fresh temp directory, failing with the recipe's title
if the block raises.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")  # headless before optiland/matplotlib.pyplot is ever imported

pytest.importorskip("optiland", reason="run with --with optiland==0.6.2")

REPO_ROOT = Path(__file__).resolve().parents[2]
RECIPES_MD = (
    REPO_ROOT / "skills" / "optical-design" / "references" / "optiland-recipes.md"
)

_HEADING_RE = re.compile(r"^## (\d+\..*)$", re.MULTILINE)
_FENCE_RE = re.compile(r"```python\n(.*?)\n```", re.DOTALL)


def _extract_recipes(text: str) -> list[tuple[str, str]]:
    """Return [(heading, code), ...] for every fenced python block in the doc.

    Each block is paired with the nearest preceding "## N. Title" heading, so a
    failure names the recipe rather than a bare index.
    """
    headings = [(m.start(), m.group(1)) for m in _HEADING_RE.finditer(text)]
    recipes = []
    for m in _FENCE_RE.finditer(text):
        pos = m.start()
        heading = "unknown"
        for start, title in headings:
            if start < pos:
                heading = title
            else:
                break
        recipes.append((heading, m.group(1)))
    return recipes


def _ids(recipes: list[tuple[str, str]]) -> list[str]:
    return [heading.split(".", 1)[0] for heading, _ in recipes]


_TEXT = RECIPES_MD.read_text(encoding="utf-8")
_RECIPES = _extract_recipes(_TEXT)


def test_recipes_found() -> None:
    """Sanity check the extraction itself found all 14 recipes before running any."""
    assert len(_RECIPES) == 14, f"expected 14 fenced python blocks, found {len(_RECIPES)}"


@pytest.mark.tier1
@pytest.mark.parametrize("heading,code", _RECIPES, ids=_ids(_RECIPES))
def test_recipe_runs(heading, code, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    namespace = {"__name__": "__main__"}
    # compile's filename shows up in the traceback on failure, naming the recipe;
    # the parametrize id (its number) does the same in the pytest summary line.
    try:
        exec(compile(code, f"<recipe {heading}>", "exec"), namespace)  # noqa: S102
    finally:
        # every recipe that plots leaves figures open under Agg; close them so
        # later recipes in the same process don't accumulate matplotlib state.
        plt = sys.modules.get("matplotlib.pyplot")
        if plt is not None:
            plt.close("all")
