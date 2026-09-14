# /// script
# requires-python = ">=3.11"
# dependencies = ["optiland==0.6.2", "matplotlib"]
# ///
"""Regenerate docs/examples/cooke-triplet-layout-spot.png.

Loads the bundled cooke-triplet form (skills/optical-design/assets/forms/cooke-triplet.json)
and renders its layout (recipe 3) and spot diagram (recipe 4) from
skills/optical-design/references/optiland-recipes.md as one stacked figure.

    uv run scripts/render-example.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from optiland.analysis import SpotDiagram
from optiland.fileio import load_optiland_file

REPO_ROOT = Path(__file__).resolve().parents[1]
FORM = REPO_ROOT / "skills/optical-design/assets/forms/cooke-triplet.json"
OUT = REPO_ROOT / "docs/examples/cooke-triplet-layout-spot.png"


def main() -> None:
    optic = load_optiland_file(str(FORM))
    p = optic.paraxial
    airy_radius_um = 1.22 * float(p.FNO()) * optic.primary_wavelength

    layout_fig, layout_ax = optic.draw(fields="all", wavelengths="all", num_rays=5, figsize=(9, 3.4))
    layout_fig.canvas.draw()

    spot = SpotDiagram(optic, fields="all", wavelengths="all")
    spot_fig, _ = spot.view(figsize=(9, 3.2), add_airy_disk=True, show=False)
    spot_fig.canvas.draw()

    fig = plt.figure(figsize=(9, 7.6), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=(1, 1.05), hspace=0.06, top=0.90, bottom=0.09, left=0.03, right=0.97)

    top_ax = fig.add_subplot(gs[0])
    top_ax.imshow(_rasterize(layout_fig), interpolation="antialiased")
    top_ax.axis("off")
    top_ax.set_title("Layout — 5 rays per field, 3 fields, 3 wavelengths", loc="left", fontsize=10)

    bottom_ax = fig.add_subplot(gs[1])
    bottom_ax.imshow(_rasterize(spot_fig), interpolation="antialiased")
    bottom_ax.axis("off")
    bottom_ax.set_title(
        f"Spot diagram — Airy radius {airy_radius_um:.1f} µm at 550 nm, f/{float(p.FNO()):.1f}",
        loc="left",
        fontsize=10,
    )

    fig.suptitle(
        "Cooke triplet — nominal design: EFL 50 mm, f/5, 480/550/650 nm, fields 0°/14°/20°",
        x=0.03,
        ha="left",
        fontsize=12,
        weight="bold",
    )

    plt.close(layout_fig)
    plt.close(spot_fig)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160, facecolor="white")
    plt.close(fig)
    print(OUT)


def _rasterize(fig):
    """Render a figure to an RGBA array, respecting elements (like a legend) that
    extend past the axes — tight bbox avoids clipping them at the canvas edge."""
    import io

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    return plt.imread(buf)


if __name__ == "__main__":
    main()
