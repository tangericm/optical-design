"""Render a `summary.json` review package into one self-contained HTML page.

No optical engine is used here; this module only lays out numbers and pictures
someone else already computed. See ``render_review.py``'s module docstring for
the full `summary.json` input contract -- this module implements it.
"""
from __future__ import annotations

import base64
import html
import json
import math
from pathlib import Path, PureWindowsPath
from typing import Any

REQUIRED_KEYS = {"model", "sha256", "engine", "first_order", "metrics", "figures"}
OPTIONAL_KEYS = {"changes", "verdict", "diagnosis", "settings"}
ALLOWED_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS

# Display order for known figure roles; any other role the caller supplies is
# appended afterward, in the order it appears in the `figures` object.
FIGURE_ORDER = ["layout", "spot", "ray_fan", "opd_fan", "field_curvature", "distortion", "mtf"]
FIGURE_CAPTIONS = {
    "layout": "Layout", "spot": "Spot diagram", "ray_fan": "Ray fan", "opd_fan": "OPD fan",
    "field_curvature": "Field curvature", "distortion": "Distortion", "mtf": "MTF",
}

# Units rounded to 3 significant figures rather than a fixed decimal count.
SIG_FIG_UNITS = {"mm", "um", "µm", "nm", "deg", "degree", "degrees", "arcsec",
                 "cyc/mm", "1/mm", "lp/mm"}
# Units shown as a fixed 2 decimals (MTF, Strehl); other dimensionless quantities
# (F/#, NA, ...) fall through to the default 3-significant-figure rounding below.
TWO_DECIMAL_UNITS = {"mtf", "strehl"}
TWO_DECIMAL_NAME_HINTS = ("mtf", "strehl")

ACCENT = "#087F8C"


def validate_summary(data: Any) -> dict:
    """Raise ValueError or TypeError with a clear message for anything malformed; else
    return data. Callers should catch both to map a malformed summary to one exit code."""
    if not isinstance(data, dict):
        raise TypeError("summary must be a JSON object")
    missing = REQUIRED_KEYS - set(data)
    if missing:
        raise ValueError(f"summary is missing required key(s): {sorted(missing)}")
    unknown = set(data) - ALLOWED_KEYS
    if unknown:
        raise ValueError(f"summary has unknown top-level key(s): {sorted(unknown)}")
    if not isinstance(data["model"], str) or not data["model"]:
        raise ValueError("summary.model must be a nonempty string")
    if not isinstance(data["sha256"], str) or not data["sha256"]:
        raise ValueError("summary.sha256 must be a nonempty string")
    engine = data["engine"]
    if not isinstance(engine, dict) or not isinstance(engine.get("name"), str) or not engine.get("name"):
        raise ValueError("summary.engine must be an object with at least a nonempty 'name'")
    if not isinstance(data["first_order"], dict):
        raise TypeError("summary.first_order must be an object of name -> {value, unit}")
    for key, row in data["first_order"].items():
        if not isinstance(row, dict) or "value" not in row:
            raise ValueError(f"summary.first_order[{key!r}] must be an object with a 'value'")
    if not isinstance(data["metrics"], list):
        raise TypeError("summary.metrics must be a list")
    for i, row in enumerate(data["metrics"]):
        if not isinstance(row, dict) or "name" not in row or "value" not in row:
            raise ValueError(f"summary.metrics[{i}] must be an object with at least 'name' and 'value'")
        requirement = row.get("requirement")
        if requirement is not None and not isinstance(requirement, dict):
            raise ValueError(f"summary.metrics[{i}].requirement must be an object")
    if not isinstance(data["figures"], dict):
        raise TypeError("summary.figures must be an object of role -> PNG path")
    for role, path in data["figures"].items():
        if not isinstance(path, str) or not path:
            raise ValueError(f"summary.figures[{role!r}] must be a nonempty path string")
    changes = data.get("changes")
    if changes is not None:
        if not isinstance(changes, list):
            raise ValueError("summary.changes must be a list")
        for i, row in enumerate(changes):
            if not isinstance(row, dict) or "surface" not in row or "parameter" not in row:
                raise ValueError(f"summary.changes[{i}] must have at least 'surface' and 'parameter'")
    for key in ("verdict", "diagnosis"):
        if data.get(key) is not None and not isinstance(data[key], str):
            raise ValueError(f"summary.{key} must be a string when present")
    if data.get("settings") is not None and not isinstance(data["settings"], dict):
        raise ValueError("summary.settings must be an object")
    return data


def _resolve_figure_path(summary_dir: Path, raw: str) -> Path | None:
    """Resolve a figure path relative to the summary's directory; None if unsafe/missing."""
    if not raw or "\x00" in raw:
        return None
    win = PureWindowsPath(raw)
    if win.is_absolute() or win.drive or raw.startswith(("\\\\", "//")):
        return None
    candidate = (summary_dir / raw).resolve()
    try:
        candidate.relative_to(summary_dir.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _round_sig(value: float, sig: int = 3) -> str:
    if value == 0:
        return "0"
    magnitude = math.floor(math.log10(abs(value)))
    decimals = max(sig - 1 - magnitude, 0)
    text = f"{value:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if text not in ("", "-") else "0"


def format_value(value: Any, unit: str | None, name: str | None = None) -> str:
    """Human-readable value text; 3 significant figures by default (mm, um, F/#, NA, ...),
    2 fixed decimals for MTF/Strehl-like scores, and never a raw Python float repr."""
    if value is None:
        return "—"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return html.escape(str(value))
    if not math.isfinite(value):
        return "—"
    key = (unit or "").strip().lower()
    name_key = (name or "").strip().lower()
    if key in TWO_DECIMAL_UNITS or any(hint in name_key for hint in TWO_DECIMAL_NAME_HINTS):
        return f"{value:.2f}"
    return _round_sig(value, 3)


def _unit_text(unit: str | None) -> str:
    return "" if not unit or unit == "1" else f" {unit}"


def _condition_text(metric: dict) -> str:
    parts = []
    freq = metric.get("frequency")
    if freq is not None:
        parts.append(f"{_round_sig(float(freq), 3)} cyc/mm")
    axis = metric.get("axis")
    if axis:
        parts.append(str(axis))
    field = metric.get("field")
    if field is not None:
        parts.append(f"field {field if isinstance(field, str) else _round_sig(float(field), 3)}")
    wavelength = metric.get("wavelength")
    if wavelength is not None:
        parts.append(f"{wavelength if isinstance(wavelength, str) else _round_sig(float(wavelength), 3)} µm")
    return ", ".join(parts)


def _requirement_text(metric: dict) -> str:
    requirement = metric.get("requirement")
    if not requirement:
        return "—"
    unit = metric.get("unit")
    name = metric.get("name")
    bounds = []
    if requirement.get("min") is not None:
        bounds.append(f"≥ {format_value(requirement['min'], unit, name)}{_unit_text(unit)}")
    if requirement.get("max") is not None:
        bounds.append(f"≤ {format_value(requirement['max'], unit, name)}{_unit_text(unit)}")
    if not bounds:
        return "—"
    text = " and ".join(bounds)
    condition = _condition_text(metric)
    return f"{text} at {condition}" if condition else text


def _pass_chip(value: bool | None) -> str:
    if value is None:
        return '<span class="chip chip-unknown">—</span>'
    return ('<span class="chip chip-pass">PASS</span>' if value
            else '<span class="chip chip-fail">FAIL</span>')


def _esc(value: Any) -> str:
    return html.escape("—" if value is None else str(value))


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "<p>No data.</p>"
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<div class="table-scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def _figures_html(figures: dict, summary_dir: Path) -> tuple[str, list[str], list[str]]:
    ordered_roles = [r for r in FIGURE_ORDER if r in figures]
    ordered_roles += [r for r in figures if r not in FIGURE_ORDER]
    embedded, missing = [], []
    blocks = []
    for role in ordered_roles:
        resolved = _resolve_figure_path(summary_dir, figures[role])
        if resolved is None:
            missing.append(role)
            continue
        data_uri = "data:image/png;base64," + base64.b64encode(resolved.read_bytes()).decode("ascii")
        caption = FIGURE_CAPTIONS.get(role, role.replace("_", " ").title())
        blocks.append(f'<figure><img src="{data_uri}" alt="{html.escape(caption)}">'
                      f'<figcaption>{html.escape(caption)}</figcaption></figure>')
        embedded.append(role)
    figures_html = f'<div class="figures">{"".join(blocks)}</div>' if blocks else "<p>No figures were supplied.</p>"
    return figures_html, embedded, missing


def render_html(summary: dict, summary_dir: Path) -> tuple[str, dict]:
    """Render the review HTML; returns (html_text, stats) where stats reports what was
    embedded/skipped for the CLI's JSON envelope."""
    model_name = Path(summary["model"]).name
    short_hash = summary["sha256"][:8]
    title = f"{model_name} · {short_hash}"

    verdict = summary.get("verdict")
    verdict_html = html.escape(verdict) if verdict else "No verdict was written."
    diagnosis = summary.get("diagnosis")

    figures_html, embedded, missing_figures = _figures_html(summary["figures"], summary_dir)

    first_order_rows = [
        [_esc(name), format_value(row.get("value"), row.get("unit"), name), _esc(row.get("unit") or "")]
        for name, row in summary["first_order"].items()
    ]

    pass_count = 0
    metric_rows = []
    for metric in summary["metrics"]:
        passed = metric.get("pass")
        if passed:
            pass_count += 1
        metric_rows.append([
            _esc(metric.get("name")), _esc(metric.get("field")), _esc(metric.get("wavelength")),
            f"{format_value(metric.get('value'), metric.get('unit'), metric.get('name'))}{_unit_text(metric.get('unit'))}",
            html.escape(_requirement_text(metric)), _pass_chip(passed),
        ])

    changes = summary.get("changes") or []
    change_rows = [
        [_esc(c.get("surface")), _esc(c.get("parameter")),
         format_value(c.get("before"), c.get("unit")), format_value(c.get("after"), c.get("unit")),
         _esc(c.get("unit") or "")]
        for c in changes
    ]

    engine = summary["engine"]
    provenance = {
        "model": summary["model"], "sha256": summary["sha256"], "engine": engine,
        "settings": summary.get("settings", {}),
    }
    provenance_json = html.escape(json.dumps(provenance, indent=2, ensure_ascii=False, sort_keys=True, default=str))

    diagnosis_html = f'<p class="diagnosis">{html.escape(diagnosis)}</p>' if diagnosis else ""

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root {{
  --bg: #fbfbfa; --panel: #ffffff; --text: #1b1f22; --muted: #5b6570; --border: #e2e5e8;
  --accent: {ACCENT}; --pass-bg: #e3f4f1; --pass-fg: #066255; --fail-bg: #fdecec; --fail-fg: #9c2b2b;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #14181a; --panel: #1c2225; --text: #e8ecee; --muted: #9aa5ab; --border: #2c3438;
    --pass-bg: #103832; --pass-fg: #7fe0cd; --fail-bg: #3a1d1d; --fail-fg: #f4a3a3;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #14181a; --panel: #1c2225; --text: #e8ecee; --muted: #9aa5ab; --border: #2c3438;
  --pass-bg: #103832; --pass-fg: #7fe0cd; --fail-bg: #3a1d1d; --fail-fg: #f4a3a3;
}}
* {{ box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
main {{ max-width: 920px; margin: 0 auto; padding: 24px 16px 56px; }}
h1 {{ font-size: 1.4rem; margin: 0 0 4px; }}
h1 .hash {{ color: var(--muted); font-weight: 400; font-size: 0.85em; }}
h2 {{ font-size: 1.05rem; margin: 32px 0 10px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }}
.verdict {{ font-size: 1.05rem; line-height: 1.5; background: var(--panel); border: 1px solid var(--border);
           border-left: 4px solid var(--accent); border-radius: 6px; padding: 14px 16px; margin: 12px 0 0; }}
.diagnosis {{ color: var(--muted); font-size: 0.95rem; margin-top: 8px; }}
.figures {{ display: flex; flex-wrap: wrap; gap: 16px; }}
figure {{ margin: 0; background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
         padding: 10px; flex: 1 1 260px; max-width: 100%; }}
figure img {{ display: block; width: 100%; height: auto; border-radius: 4px; }}
figcaption {{ text-align: center; color: var(--muted); font-size: 0.85rem; margin-top: 6px; }}
.table-scroll {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
th, td {{ text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--border); white-space: nowrap; }}
th {{ color: var(--muted); font-weight: 600; }}
.chip {{ display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }}
.chip-pass {{ background: var(--pass-bg); color: var(--pass-fg); }}
.chip-fail {{ background: var(--fail-bg); color: var(--fail-fg); }}
.chip-unknown {{ color: var(--muted); }}
details {{ margin-top: 32px; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; }}
summary {{ cursor: pointer; color: var(--muted); font-weight: 600; }}
pre {{ overflow-x: auto; font-size: 0.82rem; }}
</style>
</head>
<body>
<main>
<h1>{html.escape(model_name)} <span class="hash">{html.escape(short_hash)}</span></h1>
<div class="verdict">{verdict_html}</div>
{diagnosis_html}
<h2>Figures</h2>
{figures_html}
<h2>First-order summary</h2>
{_table(["Quantity", "Value", "Unit"], first_order_rows)}
<h2>Metrics</h2>
{_table(["Metric", "Field", "Wavelength", "Value", "Requirement", "Status"], metric_rows)}
<h2>Changes</h2>
{_table(["Surface", "Parameter", "Before", "After", "Unit"], change_rows) if change_rows else "<p>No changes were recorded.</p>"}
<details>
<summary>Settings and provenance</summary>
<pre>{provenance_json}</pre>
</details>
</main>
</body>
</html>
"""
    stats = {
        "figures_embedded": embedded, "figures_missing": missing_figures,
        "metrics_total": len(summary["metrics"]), "metrics_pass": pass_count,
        "changes_count": len(changes),
    }
    return doc, stats
