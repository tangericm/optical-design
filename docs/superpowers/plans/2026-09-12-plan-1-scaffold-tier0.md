# optical-design Plan 1: Scaffold, Packaging, Tier 0 Scripts, CI

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A publishable `optical-design` skill repo whose Tier 0 (numpy/scipy) scripts compute resolution, Zernike, PSF/MTF/Strehl, and interferometry quantities with tested textbook values, packaged for npm, `npx skills add`, and Claude/Agent plugin marketplaces, with green CI on three OSes.

**Architecture:** One skill directory `skills/optical-design/` holding `SKILL.md`, `scripts/` (Python CLIs with PEP 723 inline dependencies, run through `uv run`, sharing a `_lib/` package that owns the JSON envelope, formulas and Zernike tables), and later `references/`. Root holds packaging manifests, `pyproject.toml` for the dev environment, pytest suites that import the scripts as modules, and vitest suites that check frontmatter and packaging.

**Tech Stack:** Python 3.11+, numpy, scipy, scikit-image (unwrap only), uv 0.11+, pytest, ruff; Node 22, vitest, gray-matter, skillcrit (lint); GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-optical-design-skill-design.md`

## Global Constraints

- Python floor `>=3.11`; every script has a PEP 723 header pinning its own dependencies; scripts import `_lib` from their own directory and never from an installed package.
- Script contract (spec §8): `uv run scripts/<name>.py <subcommand> [args] [--json]`; JSON envelope `{schema, tool, subcommand, tier, inputs, results, units, method, warnings}`; exit codes 0 ok, 2 usage, 3 missing tier dependency, 4 analysis failed; every subcommand has `--help` with one example; no harness-specific code; no network calls.
- Units: lengths mm unless the argument name says otherwise; wavelengths in µm (`--wavelength-um`); wavefront in waves at the stated wavelength; Zernike coefficients always carry a `scheme` (`fringe` | `noll` | `ansi`).
- Frontmatter uses only `name, description, license, compatibility, metadata` (spec §5). `name: optical-design` matches the directory. `description` ≤ 1024 chars, `compatibility` ≤ 500 chars. SKILL.md body < 400 lines.
- Package name `optical-design`, MIT, author `Eric Tang <eric.tang22@gmail.com>`, Node `>=22`.
- Commits authored as Eric Tang only. No `Co-Authored-By` or any AI trailer, in any commit, by any agent. Verify `git config user.name` prints `Eric Tang` before the first commit.
- Line endings: `.gitattributes` forces LF for text files.
- Formulas cite a source in a `method` string and in a code comment; tests pin the textbook value.

---

## File structure

| Path | Responsibility |
|---|---|
| `package.json`, `plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Distribution manifests (npm, Agent Plugins 1.0, Claude Code marketplace) |
| `pyproject.toml` | Dev environment (`uv sync`), pytest markers, ruff config. Not a distributable package. |
| `vitest.config.ts`, `tests/node/*.test.ts` | Frontmatter + packaging checks |
| `scripts/verify-package.mjs` | Pack into a temp consumer and assert the skill files arrive |
| `skills/optical-design/SKILL.md` | Skill body (draft in this plan; finalized in plan 6) |
| `skills/optical-design/scripts/_lib/cli.py` | Envelope dataclass, `emit`, exit codes, `require`, common parser |
| `skills/optical-design/scripts/_lib/optics.py` | Closed-form formulas (pure functions, documented units) |
| `skills/optical-design/scripts/_lib/zernike.py` | Index schemes, radial polynomials, normalization, basis evaluation, names |
| `skills/optical-design/scripts/_lib/fourier.py` | Pupil grid, PSF via FFT, MTF, encircled energy, diffraction-limited MTF |
| `skills/optical-design/scripts/resolve.py` | Resolution / DOF / Gaussian / OCT / microscopy / telescope calculators |
| `skills/optical-design/scripts/zernike.py` | convert / rms / strehl / seidel-from-zernike / fit |
| `skills/optical-design/scripts/wavefront.py` | psf / mtf / sample-check |
| `skills/optical-design/scripts/interfero.py` | psi / unwrap / fringe-to-wfe / cavity |
| `skills/optical-design/scripts/compare.py` | Diff two envelopes with tolerances |
| `tests/python/conftest.py` | Puts `scripts/` on `sys.path`; helper to run a script `main()` and parse JSON |
| `tests/python/test_*.py` | One file per script plus `_lib` units |
| `docs/tiers.md`, `docs/install.md` | What each tier needs; per-harness install paths |
| `.github/workflows/ci.yml` | python matrix + node job |

---

### Task 1: Repo scaffold and distribution manifests

**Files:**
- Create: `package.json`, `plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `LICENSE`, `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `.gitattributes`, `.editorconfig`, `vitest.config.ts`, `tsconfig.json`
- Modify: `.gitignore`
- Create: `skills/optical-design/LICENSE` (copy of root LICENSE)
- Test: `tests/node/packaging.test.ts`

**Interfaces:**
- Produces: package name `optical-design`, version `0.1.0-dev.0` read by later node tests; `files` whitelist that later tasks add scripts into.

- [ ] **Step 1: Write the failing packaging test**

`tests/node/packaging.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(__dirname, "..", "..");
const read = (p: string) => JSON.parse(fs.readFileSync(path.join(root, p), "utf8"));

describe("distribution manifests", () => {
  it("package.json has the required identity", () => {
    const pkg = read("package.json");
    expect(pkg.name).toBe("optical-design");
    expect(pkg.license).toBe("MIT");
    expect(pkg.engines.node).toBe(">=22");
    expect(pkg.bin).toBeUndefined();
    expect(pkg.files).toContain("skills");
  });
  it("plugin manifests agree with package.json", () => {
    const pkg = read("package.json");
    const agentPlugin = read("plugin.json");
    const claudePlugin = read(".claude-plugin/plugin.json");
    const marketplace = read(".claude-plugin/marketplace.json");
    expect(agentPlugin.name).toBe("optical-design");
    expect(agentPlugin.version).toBe(pkg.version);
    expect(claudePlugin.version).toBe(pkg.version);
    expect(claudePlugin.skills).toBe("./skills/");
    expect(marketplace.plugins[0].name).toBe("optical-design");
    expect(marketplace.plugins[0].source).toBe("./");
  });
  it("npm pack ships the skill and nothing local", () => {
    const result = spawnSync("npm", ["pack", "--dry-run", "--json", "--ignore-scripts"], {
      cwd: root, encoding: "utf8", shell: process.platform === "win32"
    });
    expect(result.status).toBe(0);
    const files: string[] = JSON.parse(result.stdout)[0].files.map((f: { path: string }) => f.path);
    for (const required of ["skills/optical-design/SKILL.md", "skills/optical-design/LICENSE", "LICENSE", "README.md", "SECURITY.md"]) {
      expect(files, `missing ${required}`).toContain(required);
    }
    expect(files.some(f => /^(tests|node_modules|docs\/superpowers|\.github)\//u.test(f))).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test` (after `npm init -y` placeholder is replaced below it will still fail on missing manifests)
Expected: FAIL — cannot find module vitest / package.json fields missing.

- [ ] **Step 3: Write the manifests**

`package.json`:
```json
{
  "name": "optical-design",
  "version": "0.1.0-dev.0",
  "description": "Agent skill for optical design review, analysis and optimization, with Zemax OpticStudio interoperability.",
  "type": "module",
  "files": [
    "skills",
    "docs/install.md",
    "docs/tiers.md",
    "docs/compatibility.md",
    "SECURITY.md",
    "CONTRIBUTING.md"
  ],
  "scripts": {
    "test": "vitest run",
    "lint:skills": "skillcrit lint . --fail-on error",
    "verify:package": "node scripts/verify-package.mjs"
  },
  "engines": { "node": ">=22" },
  "license": "MIT",
  "author": "Eric Tang <eric.tang22@gmail.com>",
  "homepage": "https://github.com/tangericm/optical-design#readme",
  "bugs": { "url": "https://github.com/tangericm/optical-design/issues" },
  "repository": { "type": "git", "url": "git+https://github.com/tangericm/optical-design.git" },
  "keywords": ["agent-skills", "ai-agents", "optics", "optical-design", "lens-design", "zemax", "opticstudio", "psf", "mtf", "zernike", "oct", "microscopy", "interferometry"],
  "devDependencies": {
    "@types/node": "^26.4.1",
    "gray-matter": "^4.0.3",
    "skillcrit": "^0.6.0",
    "typescript": "^7.0.2",
    "vitest": "^5.0.0"
  }
}
```

`plugin.json` (Agent Plugins 1.0, same shape as skillcrit):
```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "optical-design",
  "version": "0.1.0-dev.0",
  "description": "Agent skill for optical design review, analysis and optimization, with Zemax OpticStudio interoperability.",
  "author": { "name": "Eric Tang", "email": "eric.tang22@gmail.com" },
  "homepage": "https://github.com/tangericm/optical-design#readme",
  "repository": "https://github.com/tangericm/optical-design",
  "license": "MIT",
  "keywords": ["agent-skills", "optics", "optical-design", "zemax", "opticstudio"]
}
```

`.claude-plugin/plugin.json`:
```json
{
  "name": "optical-design",
  "version": "0.1.0-dev.0",
  "description": "Agent skill for optical design review, analysis and optimization, with Zemax OpticStudio interoperability.",
  "author": { "name": "Eric Tang" },
  "license": "MIT",
  "skills": "./skills/"
}
```

`.claude-plugin/marketplace.json`:
```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "optical-design",
  "description": "Optical design review, analysis and optimization skill.",
  "owner": { "name": "Eric Tang" },
  "plugins": [
    {
      "name": "optical-design",
      "description": "Optical design review, analysis and optimization skill.",
      "source": "./",
      "category": "engineering",
      "license": "MIT"
    }
  ]
}
```

`vitest.config.ts`:
```ts
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: { include: ["tests/node/**/*.test.ts"], environment: "node", testTimeout: 60_000, hookTimeout: 60_000, isolate: true }
});
```

`tsconfig.json`:
```json
{
  "compilerOptions": { "target": "ES2022", "module": "Node16", "moduleResolution": "Node16", "strict": true, "esModuleInterop": true, "skipLibCheck": true, "types": ["node"] },
  "include": ["tests/node/**/*.ts", "vitest.config.ts"]
}
```

`.gitattributes`:
```
* text=auto eol=lf
*.png binary
*.zmx text eol=crlf
```
(`.zmx` keeps CRLF because OpticStudio writes it that way; fixtures arrive in plan 3.)

`.editorconfig`:
```
root = true
[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
indent_style = space
indent_size = 2
[*.py]
indent_size = 4
```

`.gitignore` (replace):
```
.venv/
__pycache__/
*.pyc
node_modules/
dist/
*.tgz
.pytest_cache/
.ruff_cache/
tests/python/_out/
```

`LICENSE`: MIT text, `Copyright (c) 2026 Eric Tang`. Copy the same file to `skills/optical-design/LICENSE`.

`README.md` (initial):
```markdown
# optical-design

Agent skill for optical design review, analysis and optimization. Gives a coding agent
(Claude Code, Codex, Cursor, Hermes, OpenCode, Copilot) senior-designer guidance plus
deterministic scripts for resolution, PSF/MTF, wavefront error, Zernike and Seidel
aberrations, Strehl, tolerancing and merit-function design. Works without any ray tracer;
uses optiland for prescriptions and Zemax OpticStudio through ZOS-API when present.

Status: pre-release. See `docs/tiers.md` for what each compute tier needs.

## Install

- Any Agent Skills client: `npx skills add tangericm/optical-design`
- Claude Code: `claude plugin marketplace add tangericm/optical-design` then `claude plugin install optical-design@optical-design`
- npm: `npm install optical-design` and point your client at `node_modules/optical-design/skills/optical-design`

Scripts need Python 3.11+ and `uv`; dependencies install on first run.

## License

MIT.
```

`SECURITY.md`:
```markdown
# Security

Scripts under `skills/optical-design/scripts/` read the files you name on the command line,
compute, and write to stdout or to an output path you pass. They make no network requests
and send no telemetry. Dependency installation happens through `uv` on first run and
downloads packages from PyPI; pin versions in the PEP 723 headers.

Tier 2 (`zos.py`, later release) launches or attaches to Ansys Zemax OpticStudio through
ZOS-API. It is read-only unless `--write` is passed.

Report vulnerabilities through GitHub security advisories on this repository.
```

`CONTRIBUTING.md`:
```markdown
# Contributing

- Every formula carries a cited source and a test that pins a textbook value.
- Scripts follow the contract in `docs/tiers.md`: `--help`, `--json`, exit codes 0/2/3/4.
- Run `uv sync` then `uv run pytest`; `npm ci` then `npm test`.
- Commits are authored by the human contributor; no AI co-author trailers.
```

`CHANGELOG.md`:
```markdown
# Changelog

## Unreleased

- Tier 0 scripts: resolve, zernike, wavefront, interfero, compare.
- Packaging for npm, Agent Plugins 1.0, Claude Code marketplace.
```

- [ ] **Step 4: Install and run tests**

Run:
```bash
npm install
npm test
```
Expected: PASS (3 tests). If `npm pack --dry-run` complains that `skills/optical-design/SKILL.md` is missing, create a one-line placeholder SKILL.md now (`---\nname: optical-design\ndescription: placeholder\n---\n`); Task 11 replaces it.

- [ ] **Step 5: Commit**

```bash
git config user.name   # must print: Eric Tang
git add -A
git commit -m "chore: scaffold repo and distribution manifests"
```

---

### Task 2: Python dev environment and `_lib/cli.py` envelope

**Files:**
- Create: `pyproject.toml`, `skills/optical-design/scripts/_lib/__init__.py`, `skills/optical-design/scripts/_lib/cli.py`, `tests/python/conftest.py`
- Test: `tests/python/test_cli.py`

**Interfaces:**
- Produces:
  - `Envelope(tool: str, subcommand: str, tier: int, inputs: dict, results: dict, units: dict, method: str, warnings: list[str] = [])` with `.to_dict()`.
  - `emit(env: Envelope, as_json: bool, out=sys.stdout) -> None`.
  - `EXIT_OK=0, EXIT_USAGE=2, EXIT_MISSING_DEP=3, EXIT_ANALYSIS=4`.
  - `require(module: str, hint: str)` → imported module or exits 3.
  - `common_parser() -> argparse.ArgumentParser` (parent with `--json`).
  - `fail(message: str, code: int) -> NoReturn` writes `error: <message>` to stderr and exits.
  - conftest fixture `run(main, argv) -> (code, stdout, stderr)` and `run_json(main, argv) -> dict`.

- [ ] **Step 1: Write the failing test**

`tests/python/test_cli.py`:
```python
import json
import pytest
from _lib import cli


def test_envelope_round_trips_to_json(capsys):
    env = cli.Envelope(tool="demo", subcommand="x", tier=0, inputs={"a": 1.0},
                       results={"r": 2.5}, units={"r": "mm"}, method="test")
    cli.emit(env, as_json=True)
    out = json.loads(capsys.readouterr().out)
    assert out["schema"] == "1"
    assert out["results"]["r"] == 2.5
    assert out["units"]["r"] == "mm"
    assert out["warnings"] == []


def test_human_output_lists_results_with_units(capsys):
    env = cli.Envelope(tool="demo", subcommand="x", tier=0, inputs={},
                       results={"r": 2.5}, units={"r": "mm"}, method="test", warnings=["w1"])
    cli.emit(env, as_json=False)
    text = capsys.readouterr().out
    assert "r" in text and "2.5" in text and "mm" in text and "warning: w1" in text


def test_require_exits_3_for_missing_module(capsys):
    with pytest.raises(SystemExit) as e:
        cli.require("module_that_does_not_exist_xyz", "pip install nothing")
    assert e.value.code == cli.EXIT_MISSING_DEP
    assert "pip install nothing" in capsys.readouterr().err


def test_require_returns_module():
    assert cli.require("json", "") is json
```

`tests/python/conftest.py`:
```python
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "optical-design" / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def run():
    def _run(main, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = main(list(argv))
            except SystemExit as e:  # argparse
                code = e.code if isinstance(e.code, int) else 1
        return code, out.getvalue(), err.getvalue()
    return _run


@pytest.fixture
def run_json(run):
    def _run_json(main, argv):
        code, out, err = run(main, [*argv, "--json"])
        assert code == 0, err
        return json.loads(out)
    return _run_json
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv sync && uv run pytest tests/python/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: _lib` (pyproject must exist first for `uv sync`; write it in Step 3 and rerun).

- [ ] **Step 3: Write pyproject and cli.py**

`pyproject.toml`:
```toml
[project]
name = "optical-design-dev"
version = "0.0.0"
description = "Development environment for the optical-design skill scripts (not published)."
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = [
  "pytest>=8.3",
  "numpy>=1.26",
  "scipy>=1.11",
  "scikit-image>=0.22",
  "ruff>=0.5",
]

[tool.uv]
package = false

[tool.pytest.ini_options]
testpaths = ["tests/python"]
markers = [
  "tier1: needs optiland",
  "zos: needs Windows and Ansys Zemax OpticStudio with ZOS-API",
  "uv: runs a script through `uv run` (PEP 723)",
]

[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = ["docs"]
```

`skills/optical-design/scripts/_lib/__init__.py`: empty file.

`skills/optical-design/scripts/_lib/cli.py`:
```python
"""Shared CLI contract for optical-design scripts.

Envelope schema version 1:
{schema, tool, subcommand, tier, inputs, results, units, method, warnings}
Exit codes: 0 ok, 2 usage, 3 missing tier dependency, 4 analysis failed.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, NoReturn

SCHEMA_VERSION = "1"
EXIT_OK = 0
EXIT_USAGE = 2
EXIT_MISSING_DEP = 3
EXIT_ANALYSIS = 4


@dataclass
class Envelope:
    tool: str
    subcommand: str
    tier: int
    inputs: dict[str, Any]
    results: dict[str, Any]
    units: dict[str, str]
    method: str
    warnings: list[str] = field(default_factory=list)
    schema: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_fmt(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}: {_fmt(v)}" for k, v in value.items()) + "}"
    return str(value)


def emit(env: Envelope, as_json: bool, out=None) -> None:
    out = out or sys.stdout
    if as_json:
        out.write(json.dumps(env.to_dict(), indent=2, sort_keys=True, default=_json_default) + "\n")
        return
    out.write(f"{env.tool} {env.subcommand} (tier {env.tier})\n")
    out.write(f"  method: {env.method}\n")
    for key, value in env.results.items():
        unit = env.units.get(key, "")
        out.write(f"  {key:<30} {_fmt(value)} {unit}".rstrip() + "\n")
    for warning in env.warnings:
        out.write(f"  warning: {warning}\n")


def _json_default(value: Any) -> Any:
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        raise TypeError(f"not serializable: {type(value)!r}")
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"not serializable: {type(value)!r}")


def require(module: str, hint: str):
    try:
        return importlib.import_module(module)
    except ImportError:
        sys.stderr.write(f"error: missing dependency '{module}'. {hint}\n")
        sys.exit(EXIT_MISSING_DEP)


def fail(message: str, code: int = EXIT_ANALYSIS) -> NoReturn:
    sys.stderr.write(f"error: {message}\n")
    sys.exit(code)


def common_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--json", action="store_true", help="emit the JSON envelope instead of a table")
    return parent


def parse_floats(text: str) -> list[float]:
    """Parse '0.1, 0.2,0.3' or a path to a JSON list / newline file into floats."""
    from pathlib import Path

    path = Path(text)
    if path.is_file():
        raw = path.read_text(encoding="utf-8").strip()
        if raw.startswith("["):
            return [float(v) for v in json.loads(raw)]
        return [float(v) for v in raw.replace(",", " ").split()]
    return [float(v) for v in text.replace(",", " ").split()]
```

- [ ] **Step 4: Run tests**

Run: `uv sync && uv run pytest tests/python/test_cli.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock skills/optical-design/scripts/_lib tests/python
git commit -m "feat: add script CLI envelope and python dev environment"
```

---

### Task 3: `_lib/optics.py` formulas and `resolve.py` (airy, rayleigh, dof, telescope)

**Files:**
- Create: `skills/optical-design/scripts/_lib/optics.py`, `skills/optical-design/scripts/resolve.py`
- Test: `tests/python/test_optics.py`, `tests/python/test_resolve.py`

**Interfaces:**
- Produces (`_lib/optics.py`, all pure, same length unit in and out unless noted):
  - `na_from_fnum(fnum) -> float` = `1/(2*fnum)`; `fnum_from_na(na) -> float` = `1/(2*na)` (paraxial).
  - `airy_radius(wavelength, *, fnum=None, na=None) -> float` first dark ring, `1.22 λ F#` = `0.61 λ/NA`.
  - `airy_fwhm(wavelength, na) -> float` = `0.51 λ/NA`.
  - `rayleigh(wavelength, na)`, `sparrow(wavelength, na)`, `abbe(wavelength, na)` → `0.61λ/NA`, `0.47λ/NA`, `λ/(2NA)`.
  - `rayleigh_angular_rad(wavelength, diameter)` = `1.22 λ/D`; `rad_to_arcsec(rad)`; `dawes_arcsec(diameter_mm)` = `116/D`.
  - `dof_half_range(wavelength, na)` = `λ/(2 NA²)` (Rayleigh quarter-wave; equals `2 λ F#²`); `dof_geometric_half(coc, fnum)` = `coc*fnum`.
  - `mtf_cutoff_cyc_per_mm(wavelength_um, fnum)` = `1000/(λ_um F#)`.
  - `mtf_diffraction(nu_over_cutoff)` incoherent circular pupil.
  - `sampling_q(wavelength_um, fnum, pixel_um)` = `λ F#/p`.
- `resolve.main(argv) -> int` with subcommands `airy`, `rayleigh`, `dof`, `telescope` (this task) and `gaussian`, `oct-axial`, `oct-lateral`, `micro` (Task 4).

- [ ] **Step 1: Write the failing tests**

`tests/python/test_optics.py`:
```python
import math
import pytest
from _lib import optics


def test_airy_radius_from_fnum_and_na_agree():
    # Smith, Modern Optical Engineering: first dark ring at 1.22 λ F/#
    assert optics.airy_radius(0.55, fnum=4.0) == pytest.approx(1.22 * 0.55 * 4.0)
    assert optics.airy_radius(0.55, na=0.125) == pytest.approx(optics.airy_radius(0.55, fnum=4.0))


def test_resolution_criteria_order():
    lam, na = 0.5, 0.5
    assert optics.sparrow(lam, na) < optics.abbe(lam, na) < optics.rayleigh(lam, na)
    assert optics.rayleigh(lam, na) == pytest.approx(0.61)
    assert optics.abbe(lam, na) == pytest.approx(0.5)


def test_dof_half_range_matches_2_lambda_fnum_squared():
    # ±λ/(2NA²) == ±2λF² for NA = 1/(2F)
    assert optics.dof_half_range(0.55, optics.na_from_fnum(4.0)) == pytest.approx(2 * 0.55 * 16)


def test_dawes_and_rayleigh_angular():
    assert optics.dawes_arcsec(100.0) == pytest.approx(1.16)
    rad = optics.rayleigh_angular_rad(0.55e-3, 100.0)  # both in mm
    assert optics.rad_to_arcsec(rad) == pytest.approx(1.384, rel=1e-3)


def test_mtf_cutoff_and_diffraction_curve():
    assert optics.mtf_cutoff_cyc_per_mm(0.5, 4.0) == pytest.approx(500.0)
    assert optics.mtf_diffraction(0.0) == pytest.approx(1.0)
    assert optics.mtf_diffraction(1.0) == pytest.approx(0.0, abs=1e-12)
    assert optics.mtf_diffraction(0.5) == pytest.approx(2 / math.pi * (math.acos(0.5) - 0.5 * math.sqrt(0.75)))
    assert optics.mtf_diffraction(1.5) == 0.0
```

`tests/python/test_resolve.py` (first part):
```python
import pytest
import resolve


def test_airy_json(run_json):
    out = run_json(resolve.main, ["airy", "--wavelength-um", "0.55", "--fnum", "4"])
    assert out["tool"] == "resolve" and out["tier"] == 0
    assert out["results"]["airy_radius_um"] == pytest.approx(2.684)
    assert out["units"]["airy_radius_um"] == "um"
    assert out["results"]["na"] == pytest.approx(0.125)


def test_airy_requires_fnum_or_na(run):
    code, _, err = run(resolve.main, ["airy", "--wavelength-um", "0.55"])
    assert code == 2 and "fnum" in err.lower()


def test_rayleigh_reports_three_criteria(run_json):
    out = run_json(resolve.main, ["rayleigh", "--wavelength-um", "0.5", "--na", "0.5"])
    r = out["results"]
    assert r["rayleigh_um"] == pytest.approx(0.61)
    assert r["abbe_um"] == pytest.approx(0.5)
    assert r["sparrow_um"] == pytest.approx(0.47)


def test_dof_reports_half_and_full_range(run_json):
    out = run_json(resolve.main, ["dof", "--wavelength-um", "0.55", "--fnum", "4"])
    r = out["results"]
    assert r["diffraction_half_range_um"] == pytest.approx(17.6)
    assert r["diffraction_full_range_um"] == pytest.approx(35.2)


def test_dof_with_coc_adds_geometric(run_json):
    out = run_json(resolve.main, ["dof", "--wavelength-um", "0.55", "--fnum", "4", "--coc-um", "10"])
    assert out["results"]["geometric_half_range_um"] == pytest.approx(40.0)


def test_telescope(run_json):
    out = run_json(resolve.main, ["telescope", "--diameter-mm", "100", "--wavelength-um", "0.55"])
    assert out["results"]["dawes_arcsec"] == pytest.approx(1.16)
    assert out["results"]["rayleigh_arcsec"] == pytest.approx(1.384, rel=1e-3)


def test_help_for_every_subcommand(run):
    for sub in ["airy", "rayleigh", "dof", "telescope", "gaussian", "oct-axial", "oct-lateral", "micro"]:
        code, out, _ = run(resolve.main, [sub, "--help"])
        assert code == 0 and "example" in out.lower(), sub
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/python/test_optics.py tests/python/test_resolve.py -v`
Expected: FAIL — `ModuleNotFoundError: optics` / `resolve`.

- [ ] **Step 3: Write `_lib/optics.py`**

```python
"""Closed-form optics formulas. Pure functions; units documented per function.

Sources:
- Smith, W. J., Modern Optical Engineering, 4th ed. (Airy disk, DOF, MTF cutoff)
- Hecht, Optics, 5th ed. (Rayleigh, Sparrow, Abbe)
- Dawes, W. R. (1867) empirical double-star limit
- Saleh & Teich, Fundamentals of Photonics (Gaussian beams)
- Drexler & Fujimoto (eds.), Optical Coherence Tomography (OCT resolution)
"""
from __future__ import annotations

import math

ARCSEC_PER_RAD = 206264.80624709636


def na_from_fnum(fnum: float) -> float:
    """Paraxial NA = 1/(2 F#)."""
    return 1.0 / (2.0 * fnum)


def fnum_from_na(na: float) -> float:
    return 1.0 / (2.0 * na)


def airy_radius(wavelength: float, *, fnum: float | None = None, na: float | None = None) -> float:
    """Radius of first dark ring: 1.22 λ F# == 0.61 λ / NA. Same unit as wavelength."""
    if fnum is None and na is None:
        raise ValueError("fnum or na required")
    if fnum is None:
        fnum = fnum_from_na(na)  # type: ignore[arg-type]
    return 1.22 * wavelength * fnum


def airy_fwhm(wavelength: float, na: float) -> float:
    """FWHM of Airy pattern ≈ 0.51 λ/NA (≈ 1.03 λ F#)."""
    return 0.51 * wavelength / na


def rayleigh(wavelength: float, na: float) -> float:
    return 0.61 * wavelength / na


def sparrow(wavelength: float, na: float) -> float:
    """Sparrow limit for incoherent circular pupil, 0.47 λ/NA (Hecht)."""
    return 0.47 * wavelength / na


def abbe(wavelength: float, na: float) -> float:
    return wavelength / (2.0 * na)


def rayleigh_angular_rad(wavelength: float, diameter: float) -> float:
    """1.22 λ/D; wavelength and diameter in the same unit."""
    return 1.22 * wavelength / diameter


def rad_to_arcsec(rad: float) -> float:
    return rad * ARCSEC_PER_RAD


def dawes_arcsec(diameter_mm: float) -> float:
    """Dawes empirical limit, 116/D[mm] arcsec."""
    return 116.0 / diameter_mm


def dof_half_range(wavelength: float, na: float) -> float:
    """Rayleigh quarter-wave depth of focus, half range ±λ/(2 NA²) == ±2 λ F#² (Smith)."""
    return wavelength / (2.0 * na * na)


def dof_geometric_half(coc: float, fnum: float) -> float:
    """Geometric half depth of focus for an allowed blur circle: ±c F#."""
    return coc * fnum


def mtf_cutoff_cyc_per_mm(wavelength_um: float, fnum: float) -> float:
    """Incoherent cutoff 1/(λ F#) in cycles/mm with λ in µm."""
    return 1000.0 / (wavelength_um * fnum)


def mtf_diffraction(nu_over_cutoff: float) -> float:
    """Diffraction-limited incoherent MTF of a circular pupil (Smith eq. 11.4)."""
    x = nu_over_cutoff
    if x <= 0.0:
        return 1.0
    if x >= 1.0:
        return 0.0
    return (2.0 / math.pi) * (math.acos(x) - x * math.sqrt(1.0 - x * x))


def sampling_q(wavelength_um: float, fnum: float, pixel_um: float) -> float:
    """Q = λ F# / p. Q = 2 is Nyquist-sampled at the diffraction cutoff."""
    return wavelength_um * fnum / pixel_um


# Gaussian beams (1/e² radius w, M² beam quality)
def rayleigh_range(w0: float, wavelength: float, m2: float = 1.0) -> float:
    return math.pi * w0 * w0 / (m2 * wavelength)


def divergence_half_angle_rad(w0: float, wavelength: float, m2: float = 1.0) -> float:
    return m2 * wavelength / (math.pi * w0)


def beam_radius(z: float, w0: float, zr: float) -> float:
    return w0 * math.sqrt(1.0 + (z / zr) ** 2)


def focused_waist(wavelength: float, focal: float, w_in: float, m2: float = 1.0) -> float:
    """Waist after a lens for a collimated input beam of 1/e² radius w_in: M² λ f / (π w_in)."""
    return m2 * wavelength * focal / (math.pi * w_in)


# OCT (Drexler & Fujimoto ch. 2)
def oct_axial_resolution(center_wavelength: float, bandwidth_fwhm: float, n: float = 1.0) -> float:
    """Δz = (2 ln 2 / π) λ0² / Δλ / n for a Gaussian spectrum."""
    return (2.0 * math.log(2.0) / math.pi) * center_wavelength**2 / bandwidth_fwhm / n


def oct_lateral_resolution(wavelength: float, focal: float, beam_diameter: float) -> float:
    """1/e² focal spot diameter Δx = 4 λ f / (π D) for 1/e² beam diameter D at the lens."""
    return 4.0 * wavelength * focal / (math.pi * beam_diameter)


def confocal_parameter(spot_diameter: float, wavelength: float) -> float:
    """b = 2 z_R = π Δx² / (2 λ)."""
    return math.pi * spot_diameter**2 / (2.0 * wavelength)


# Microscopy
def micro_axial_resolution(wavelength: float, na: float, n: float = 1.0) -> float:
    """Axial (widefield) resolution ≈ 2 λ n / NA²."""
    return 2.0 * wavelength * n / (na * na)


def nyquist_pixel_at_camera(resolution_object: float, magnification: float) -> float:
    """Largest camera pixel that samples `resolution_object` at Nyquist: M·d/2."""
    return magnification * resolution_object / 2.0
```

- [ ] **Step 4: Write `resolve.py` (first four subcommands)**

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolution, depth of focus, Gaussian beam, OCT, microscopy and telescope calculators (Tier 0)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli, optics  # noqa: E402

TOOL = "resolve"


def _need_fnum_or_na(parser: argparse.ArgumentParser, args: argparse.Namespace) -> tuple[float, float]:
    if args.fnum is None and args.na is None:
        parser.error("one of --fnum or --na is required")
    fnum = args.fnum if args.fnum is not None else optics.fnum_from_na(args.na)
    na = args.na if args.na is not None else optics.na_from_fnum(args.fnum)
    return fnum, na


def cmd_airy(parser, args):
    fnum, na = _need_fnum_or_na(parser, args)
    lam = args.wavelength_um
    return cli.Envelope(
        TOOL, "airy", 0,
        inputs={"wavelength_um": lam, "fnum": fnum, "na": na},
        results={
            "airy_radius_um": optics.airy_radius(lam, fnum=fnum),
            "airy_diameter_um": 2 * optics.airy_radius(lam, fnum=fnum),
            "fwhm_um": optics.airy_fwhm(lam, na),
            "fnum": fnum, "na": na,
        },
        units={"airy_radius_um": "um", "airy_diameter_um": "um", "fwhm_um": "um"},
        method="Airy first zero 1.22 λ F# (Smith, Modern Optical Engineering); FWHM 0.51 λ/NA; paraxial NA = 1/(2F#)",
    )


def cmd_rayleigh(parser, args):
    fnum, na = _need_fnum_or_na(parser, args)
    lam = args.wavelength_um
    return cli.Envelope(
        TOOL, "rayleigh", 0,
        inputs={"wavelength_um": lam, "na": na, "fnum": fnum},
        results={
            "rayleigh_um": optics.rayleigh(lam, na),
            "abbe_um": optics.abbe(lam, na),
            "sparrow_um": optics.sparrow(lam, na),
            "fwhm_um": optics.airy_fwhm(lam, na),
        },
        units={k: "um" for k in ("rayleigh_um", "abbe_um", "sparrow_um", "fwhm_um")},
        method="Rayleigh 0.61λ/NA, Abbe λ/(2NA), Sparrow 0.47λ/NA (Hecht, Optics)",
    )


def cmd_dof(parser, args):
    fnum, na = _need_fnum_or_na(parser, args)
    lam = args.wavelength_um
    half = optics.dof_half_range(lam, na)
    results = {"diffraction_half_range_um": half, "diffraction_full_range_um": 2 * half, "fnum": fnum, "na": na}
    units = {"diffraction_half_range_um": "um", "diffraction_full_range_um": "um"}
    warnings = []
    if args.coc_um is not None:
        results["geometric_half_range_um"] = optics.dof_geometric_half(args.coc_um, fnum)
        units["geometric_half_range_um"] = "um"
        if results["geometric_half_range_um"] < half:
            warnings.append("blur-circle DOF is smaller than diffraction DOF: geometric limit governs")
    return cli.Envelope(
        TOOL, "dof", 0,
        inputs={"wavelength_um": lam, "fnum": fnum, "na": na, "coc_um": args.coc_um},
        results=results, units=units,
        method="Rayleigh quarter-wave DOF ±λ/(2NA²) = ±2λF#² (half range); full range 4λF#² (Smith ch. 4); geometric ±c·F#",
        warnings=warnings,
    )


def cmd_telescope(parser, args):
    d_mm, lam = args.diameter_mm, args.wavelength_um
    rad = optics.rayleigh_angular_rad(lam * 1e-3, d_mm)
    return cli.Envelope(
        TOOL, "telescope", 0,
        inputs={"diameter_mm": d_mm, "wavelength_um": lam},
        results={"rayleigh_arcsec": optics.rad_to_arcsec(rad), "rayleigh_rad": rad, "dawes_arcsec": optics.dawes_arcsec(d_mm)},
        units={"rayleigh_arcsec": "arcsec", "rayleigh_rad": "rad", "dawes_arcsec": "arcsec"},
        method="Rayleigh 1.22 λ/D; Dawes empirical 116/D[mm] arcsec",
    )


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="resolve.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_,
                              epilog=f"example: uv run resolve.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def aperture(sub):
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--fnum", type=float)
        sub.add_argument("--na", type=float)

    add("airy", "Airy disk radius/diameter and FWHM", "airy --wavelength-um 0.55 --fnum 4", cmd_airy, aperture)
    add("rayleigh", "Rayleigh, Abbe and Sparrow two-point resolution", "rayleigh --wavelength-um 0.5 --na 0.5", cmd_rayleigh, aperture)

    def dof(sub):
        aperture(sub)
        sub.add_argument("--coc-um", type=float, help="allowed blur circle diameter for geometric DOF")
    add("dof", "Depth of focus (diffraction and geometric)", "dof --wavelength-um 0.55 --fnum 4", cmd_dof, dof)

    def telescope(sub):
        sub.add_argument("--diameter-mm", type=float, required=True)
        sub.add_argument("--wavelength-um", type=float, default=0.55)
    add("telescope", "Angular resolution: Rayleigh and Dawes", "telescope --diameter-mm 100", cmd_telescope, telescope)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests**

Run: `uv run pytest tests/python/test_optics.py tests/python/test_resolve.py -v`
Expected: all `test_optics` PASS; in `test_resolve`, `airy/rayleigh/dof/telescope` PASS, `test_help_for_every_subcommand` FAIL on `gaussian` (added in Task 4). That is the expected state; commit.

- [ ] **Step 6: Commit**

```bash
git add skills/optical-design/scripts/_lib/optics.py skills/optical-design/scripts/resolve.py tests/python/test_optics.py tests/python/test_resolve.py
git commit -m "feat(resolve): airy, rayleigh, dof, telescope calculators with formula tests"
```

---

### Task 4: `resolve.py` gaussian, oct-axial, oct-lateral, micro

**Files:**
- Modify: `skills/optical-design/scripts/resolve.py` (add four subcommands to `build_parser`)
- Test: `tests/python/test_resolve.py` (append)

**Interfaces:**
- Consumes: `optics.rayleigh_range`, `divergence_half_angle_rad`, `beam_radius`, `focused_waist`, `oct_axial_resolution`, `oct_lateral_resolution`, `confocal_parameter`, `micro_axial_resolution`, `nyquist_pixel_at_camera`, `airy_fwhm`, `rayleigh`, `abbe`.

- [ ] **Step 1: Append failing tests**

```python
def test_gaussian_from_waist(run_json):
    out = run_json(resolve.main, ["gaussian", "--wavelength-um", "1.0", "--w0-um", "10", "--z-mm", "0.3141593"])
    r = out["results"]
    assert r["rayleigh_range_mm"] == pytest.approx(0.3141593, rel=1e-5)   # π w0²/λ = π·100/1 µm = 314.16 µm
    assert r["divergence_half_angle_mrad"] == pytest.approx(31.831, rel=1e-4)  # λ/(π w0)
    assert r["beam_radius_at_z_um"] == pytest.approx(10 * 2**0.5, rel=1e-4)


def test_gaussian_focused_by_lens(run_json):
    out = run_json(resolve.main, ["gaussian", "--wavelength-um", "0.85", "--input-w-mm", "1.0", "--focal-mm", "50"])
    # w0 = λ f / (π w_in) = 0.85e-3 mm · 50 / (π · 1) = 13.53 µm
    assert out["results"]["focused_waist_um"] == pytest.approx(13.528, rel=1e-3)
    assert out["results"]["focused_rayleigh_range_mm"] == pytest.approx(0.6764, rel=1e-3)


def test_oct_axial(run_json):
    out = run_json(resolve.main, ["oct-axial", "--center-wavelength-um", "0.84", "--bandwidth-nm", "50"])
    # (2 ln2/π) λ0²/Δλ = 0.4413 · 0.7056 µm² / 0.05 µm = 6.23 µm
    assert out["results"]["axial_resolution_um"] == pytest.approx(6.227, rel=1e-3)
    out_t = run_json(resolve.main, ["oct-axial", "--center-wavelength-um", "0.84", "--bandwidth-nm", "50", "--n", "1.38"])
    assert out_t["results"]["axial_resolution_um"] == pytest.approx(6.227 / 1.38, rel=1e-3)


def test_oct_lateral(run_json):
    out = run_json(resolve.main, ["oct-lateral", "--wavelength-um", "0.84", "--focal-mm", "36", "--beam-diameter-mm", "3"])
    # 4 λ f / (π D) = 4·0.84e-3·36/(π·3) mm = 12.83 µm ; b = π Δx²/(2λ) = 0.3079 mm
    assert out["results"]["spot_diameter_um"] == pytest.approx(12.83, rel=1e-3)
    assert out["results"]["confocal_parameter_mm"] == pytest.approx(0.3079, rel=1e-3)


def test_micro_with_pixel(run_json):
    out = run_json(resolve.main, ["micro", "--wavelength-um", "0.52", "--na", "0.8", "--magnification", "40", "--pixel-um", "6.5"])
    r = out["results"]
    assert r["rayleigh_um"] == pytest.approx(0.3965)
    assert r["abbe_um"] == pytest.approx(0.325)
    assert r["axial_um"] == pytest.approx(1.625)
    assert r["nyquist_pixel_um"] == pytest.approx(6.5)         # 40 · 0.325 / 2
    assert r["sampling_ratio"] == pytest.approx(1.0)           # nyquist_pixel / pixel
    assert out["warnings"] == []
    under = run_json(resolve.main, ["micro", "--wavelength-um", "0.52", "--na", "0.8", "--magnification", "20", "--pixel-um", "6.5"])
    assert any("undersampled" in w for w in under["warnings"])
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/python/test_resolve.py -v`
Expected: new tests FAIL with `invalid choice: 'gaussian'`.

- [ ] **Step 3: Add the subcommands**

Insert before `return parser` in `build_parser`, and add the handlers above it:

```python
def cmd_gaussian(parser, args):
    lam_um = args.wavelength_um
    results, units, inputs = {}, {}, {"wavelength_um": lam_um, "m2": args.m2}
    if args.w0_um is not None:
        w0 = args.w0_um
        zr_um = optics.rayleigh_range(w0, lam_um, args.m2)
        results.update({"w0_um": w0, "rayleigh_range_mm": zr_um * 1e-3,
                        "divergence_half_angle_mrad": optics.divergence_half_angle_rad(w0, lam_um, args.m2) * 1e3})
        units.update({"w0_um": "um", "rayleigh_range_mm": "mm", "divergence_half_angle_mrad": "mrad"})
        inputs["w0_um"] = w0
        if args.z_mm is not None:
            results["beam_radius_at_z_um"] = optics.beam_radius(args.z_mm * 1e3, w0, zr_um)
            units["beam_radius_at_z_um"] = "um"
            inputs["z_mm"] = args.z_mm
    if args.input_w_mm is not None and args.focal_mm is not None:
        w0_mm = optics.focused_waist(lam_um * 1e-3, args.focal_mm, args.input_w_mm, args.m2)
        results["focused_waist_um"] = w0_mm * 1e3
        results["focused_rayleigh_range_mm"] = optics.rayleigh_range(w0_mm, lam_um * 1e-3, args.m2)
        units.update({"focused_waist_um": "um", "focused_rayleigh_range_mm": "mm"})
        inputs.update({"input_w_mm": args.input_w_mm, "focal_mm": args.focal_mm})
    if not results:
        parser.error("give --w0-um, or --input-w-mm with --focal-mm")
    return cli.Envelope(TOOL, "gaussian", 0, inputs=inputs, results=results, units=units,
                        method="Gaussian beam: z_R = π w0²/(M² λ), θ = M² λ/(π w0), w(z) = w0 √(1+(z/z_R)²), focused w0 = M² λ f/(π w_in) (Saleh & Teich ch. 3)")


def cmd_oct_axial(parser, args):
    dz = optics.oct_axial_resolution(args.center_wavelength_um, args.bandwidth_nm * 1e-3, args.n)
    return cli.Envelope(TOOL, "oct-axial", 0,
                        inputs={"center_wavelength_um": args.center_wavelength_um, "bandwidth_nm": args.bandwidth_nm, "n": args.n},
                        results={"axial_resolution_um": dz, "coherence_length_um": 2 * dz * args.n},
                        units={"axial_resolution_um": "um", "coherence_length_um": "um"},
                        method="Δz = (2 ln2/π) λ0²/Δλ / n, Gaussian spectrum FWHM Δλ (Drexler & Fujimoto, OCT, ch. 2)")


def cmd_oct_lateral(parser, args):
    dx_mm = optics.oct_lateral_resolution(args.wavelength_um * 1e-3, args.focal_mm, args.beam_diameter_mm)
    return cli.Envelope(TOOL, "oct-lateral", 0,
                        inputs={"wavelength_um": args.wavelength_um, "focal_mm": args.focal_mm, "beam_diameter_mm": args.beam_diameter_mm},
                        results={"spot_diameter_um": dx_mm * 1e3, "confocal_parameter_mm": optics.confocal_parameter(dx_mm, args.wavelength_um * 1e-3),
                                 "effective_na": args.beam_diameter_mm / (2 * args.focal_mm)},
                        units={"spot_diameter_um": "um", "confocal_parameter_mm": "mm"},
                        method="Δx = 4 λ f/(π D) (1/e² diameters); b = π Δx²/(2 λ) (Drexler & Fujimoto ch. 2)")


def cmd_micro(parser, args):
    lam, na = args.wavelength_um, args.na
    results = {"rayleigh_um": optics.rayleigh(lam, na), "abbe_um": optics.abbe(lam, na),
               "fwhm_um": optics.airy_fwhm(lam, na), "axial_um": optics.micro_axial_resolution(lam, na, args.n)}
    units = {k: "um" for k in results}
    warnings = []
    if args.magnification is not None:
        nyq = optics.nyquist_pixel_at_camera(results["abbe_um"], args.magnification)
        results["nyquist_pixel_um"] = nyq
        units["nyquist_pixel_um"] = "um"
        if args.pixel_um is not None:
            results["sampling_ratio"] = nyq / args.pixel_um
            if args.pixel_um > nyq * 1.001:
                warnings.append(f"undersampled: pixel {args.pixel_um} µm exceeds Nyquist pixel {nyq:.3g} µm at {args.magnification}x")
    return cli.Envelope(TOOL, "micro", 0,
                        inputs={"wavelength_um": lam, "na": na, "n": args.n, "magnification": args.magnification, "pixel_um": args.pixel_um},
                        results=results, units=units, warnings=warnings,
                        method="Lateral: Rayleigh 0.61λ/NA, Abbe λ/(2NA), FWHM 0.51λ/NA; axial 2λn/NA²; Nyquist camera pixel = M·Abbe/2")
```

Parser additions inside `build_parser`:
```python
    def gaussian(sub):
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--w0-um", type=float, help="waist radius (1/e²)")
        sub.add_argument("--z-mm", type=float, help="distance from waist for w(z)")
        sub.add_argument("--input-w-mm", type=float, help="collimated input 1/e² radius at the lens")
        sub.add_argument("--focal-mm", type=float)
        sub.add_argument("--m2", type=float, default=1.0)
    add("gaussian", "Gaussian beam waist, Rayleigh range, divergence, focused spot", "gaussian --wavelength-um 0.85 --input-w-mm 1 --focal-mm 50", cmd_gaussian, gaussian)

    def oct_axial(sub):
        sub.add_argument("--center-wavelength-um", type=float, required=True)
        sub.add_argument("--bandwidth-nm", type=float, required=True, help="FWHM spectral bandwidth")
        sub.add_argument("--n", type=float, default=1.0, help="tissue refractive index")
    add("oct-axial", "OCT axial resolution from source bandwidth", "oct-axial --center-wavelength-um 0.84 --bandwidth-nm 50", cmd_oct_axial, oct_axial)

    def oct_lateral(sub):
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--focal-mm", type=float, required=True)
        sub.add_argument("--beam-diameter-mm", type=float, required=True, help="1/e² beam diameter at the objective")
    add("oct-lateral", "OCT lateral spot and confocal parameter", "oct-lateral --wavelength-um 0.84 --focal-mm 36 --beam-diameter-mm 3", cmd_oct_lateral, oct_lateral)

    def micro(sub):
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--na", type=float, required=True)
        sub.add_argument("--n", type=float, default=1.0, help="immersion index")
        sub.add_argument("--magnification", type=float)
        sub.add_argument("--pixel-um", type=float, help="camera pixel pitch")
    add("micro", "Microscope lateral/axial resolution and Nyquist pixel", "micro --wavelength-um 0.52 --na 0.8 --magnification 40 --pixel-um 6.5", cmd_micro, micro)
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/python/test_resolve.py -v`
Expected: PASS (all, including the help test).

- [ ] **Step 5: Commit**

```bash
git add skills/optical-design/scripts/resolve.py tests/python/test_resolve.py
git commit -m "feat(resolve): gaussian, oct, microscopy calculators"
```

---

### Task 5: `_lib/zernike.py` index schemes, radial polynomials, normalization

**Files:**
- Create: `skills/optical-design/scripts/_lib/zernike.py`
- Test: `tests/python/test_zernike_lib.py`

**Interfaces:**
- Produces:
  - `SCHEMES = ("fringe", "noll", "ansi")`.
  - `indices(scheme: str, nterms: int) -> list[tuple[int, int]]` — `(n, m)` with signed m: `m >= 0` cosine, `m < 0` sine. Fringe is 1-based (j=1..37, max 37); Noll 1-based; ANSI 0-based (`nterms` terms starting at j=0).
  - `first_index(scheme) -> int` (1 for fringe/noll, 0 for ansi).
  - `norm(scheme, n, m) -> float`: 1.0 for fringe; `sqrt(n+1)` if m==0 else `sqrt(2(n+1))`.
  - `radial(n, m_abs, rho: ndarray) -> ndarray`.
  - `term(scheme, n, m, rho, theta) -> ndarray` = `norm * radial * (cos(mθ) | sin(|m|θ))`.
  - `basis(scheme, nterms, rho, theta) -> ndarray` shape `(nterms, *rho.shape)`.
  - `name(n, m) -> str`.
  - `unit_disk(npix: int) -> (rho, theta, mask)` square grid with inscribed circle.

- [ ] **Step 1: Write the failing tests**

`tests/python/test_zernike_lib.py`:
```python
import math
import numpy as np
import pytest
from _lib import zernike as Z


def test_fringe_table_matches_zemax_ordering():
    idx = Z.indices("fringe", 37)
    assert len(idx) == 37
    # Zemax Fringe: Z1 piston, Z2 x-tilt, Z3 y-tilt, Z4 defocus, Z5/6 astig, Z7/8 coma, Z9 spherical,
    # Z10/11 trefoil, Z16 secondary spherical, Z25 (8,0), Z36 (10,0), Z37 (12,0)
    assert idx[0] == (0, 0) and idx[1] == (1, 1) and idx[2] == (1, -1)
    assert idx[3] == (2, 0) and idx[4] == (2, 2) and idx[5] == (2, -2)
    assert idx[6] == (3, 1) and idx[7] == (3, -1) and idx[8] == (4, 0)
    assert idx[9] == (3, 3) and idx[10] == (3, -3)
    assert idx[15] == (6, 0) and idx[24] == (8, 0) and idx[35] == (10, 0) and idx[36] == (12, 0)


def test_noll_table():
    idx = Z.indices("noll", 15)
    # Noll 1976: j=2 x-tilt (cos), j=3 y-tilt (sin), j=5 astig 45° (sin), j=6 astig 0° (cos),
    # j=7 y-coma (sin), j=8 x-coma (cos), j=11 spherical
    assert idx[1] == (1, 1) and idx[2] == (1, -1)
    assert idx[4] == (2, -2) and idx[5] == (2, 2)
    assert idx[6] == (3, -1) and idx[7] == (3, 1)
    assert idx[10] == (4, 0)


def test_ansi_table():
    idx = Z.indices("ansi", 15)
    # OSA/ANSI Z80.28: j = (n(n+2)+m)/2, m ascending: j=3 (2,-2), j=4 (2,0), j=5 (2,2), j=12 (4,0)
    assert idx[0] == (0, 0) and idx[3] == (2, -2) and idx[4] == (2, 0) and idx[5] == (2, 2) and idx[12] == (4, 0)


def test_radial_polynomials_known_values():
    rho = np.array([0.0, 0.5, 1.0])
    np.testing.assert_allclose(Z.radial(2, 0, rho), 2 * rho**2 - 1)
    np.testing.assert_allclose(Z.radial(4, 0, rho), 6 * rho**4 - 6 * rho**2 + 1)
    np.testing.assert_allclose(Z.radial(3, 1, rho), 3 * rho**3 - 2 * rho)


def test_normalized_terms_have_unit_rms_over_disk():
    rho, theta, mask = Z.unit_disk(512)
    for scheme in ("noll", "ansi"):
        for n, m in Z.indices(scheme, 15)[1:]:
            t = Z.term(scheme, n, m, rho, theta)[mask]
            assert math.sqrt(np.mean(t**2)) == pytest.approx(1.0, abs=0.01), (scheme, n, m)


def test_fringe_terms_are_unnormalized():
    rho, theta, mask = Z.unit_disk(512)
    t = Z.term("fringe", 2, 0, rho, theta)[mask]
    assert math.sqrt(np.mean(t**2)) == pytest.approx(1 / math.sqrt(3), abs=0.01)


def test_names():
    assert Z.name(4, 0) == "spherical" and Z.name(2, -2) == "astigmatism 45deg" and Z.name(3, 1) == "coma x"
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/python/test_zernike_lib.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write `_lib/zernike.py`**

```python
"""Zernike polynomials in three index schemes.

Schemes:
- fringe: Zemax "Zernike Fringe" / University of Arizona ordering, 1-based, 37 terms, unnormalized
  (coefficient = peak value of the term at the pupil edge). Order: by n+|m| ascending, then |m|
  descending, cosine before sine; term 37 is (12,0). Source: Wyant & Creath 1992, Table 2; Zemax manual.
- noll: Noll 1976 (JOSA 66, 207), 1-based, RMS-normalized; within a radial order sorted by |m|,
  even j = cosine (m>0), odd j = sine (m<0). Zemax "Zernike Standard" uses this scheme.
- ansi: ANSI Z80.28 / OSA, 0-based, RMS-normalized, j = (n(n+2)+m)/2, m ascending (sine first).
Sign convention in all three: m >= 0 -> cos(mθ), m < 0 -> sin(|m|θ), θ measured from +x toward +y.
"""
from __future__ import annotations

from math import factorial, sqrt

import numpy as np

SCHEMES = ("fringe", "noll", "ansi")


def first_index(scheme: str) -> int:
    return 0 if scheme == "ansi" else 1


def _fringe_indices() -> list[tuple[int, int]]:
    pairs = [(n, m) for n in range(0, 11) for m in range(n % 2, n + 1, 2) if n + m <= 10]
    pairs.sort(key=lambda p: (p[0] + p[1], -p[1]))
    out: list[tuple[int, int]] = []
    for n, m in pairs:
        if m == 0:
            out.append((n, 0))
        else:
            out.append((n, m))
            out.append((n, -m))
    out.append((12, 0))
    return out


def _noll_indices(nterms: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    n = 0
    while len(out) < nterms:
        for m_abs in range(n % 2, n + 1, 2):
            if m_abs == 0:
                out.append((n, 0))
            else:
                j_first = len(out) + 1
                if j_first % 2 == 0:
                    out.append((n, m_abs)); out.append((n, -m_abs))
                else:
                    out.append((n, -m_abs)); out.append((n, m_abs))
        n += 1
    return out[:nterms]


def _ansi_indices(nterms: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    n = 0
    while len(out) < nterms:
        for m in range(-n, n + 1, 2):
            out.append((n, m))
        n += 1
    return out[:nterms]


def indices(scheme: str, nterms: int) -> list[tuple[int, int]]:
    if scheme == "fringe":
        if nterms > 37:
            raise ValueError("fringe scheme has 37 terms")
        return _fringe_indices()[:nterms]
    if scheme == "noll":
        return _noll_indices(nterms)
    if scheme == "ansi":
        return _ansi_indices(nterms)
    raise ValueError(f"unknown scheme {scheme!r}; choose from {SCHEMES}")


def norm(scheme: str, n: int, m: int) -> float:
    if scheme == "fringe":
        return 1.0
    return sqrt(n + 1.0) if m == 0 else sqrt(2.0 * (n + 1.0))


def radial(n: int, m_abs: int, rho: np.ndarray) -> np.ndarray:
    rho = np.asarray(rho, dtype=float)
    out = np.zeros_like(rho)
    for k in range((n - m_abs) // 2 + 1):
        c = ((-1) ** k * factorial(n - k)
             / (factorial(k) * factorial((n + m_abs) // 2 - k) * factorial((n - m_abs) // 2 - k)))
        out += c * rho ** (n - 2 * k)
    return out


def term(scheme: str, n: int, m: int, rho: np.ndarray, theta: np.ndarray) -> np.ndarray:
    ang = np.cos(m * theta) if m >= 0 else np.sin(-m * theta)
    return norm(scheme, n, m) * radial(n, abs(m), rho) * ang


def basis(scheme: str, nterms: int, rho: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return np.stack([term(scheme, n, m, rho, theta) for n, m in indices(scheme, nterms)])


_NAMES = {
    (0, 0): "piston", (1, 1): "tilt x", (1, -1): "tilt y", (2, 0): "defocus",
    (2, 2): "astigmatism 0deg", (2, -2): "astigmatism 45deg", (3, 1): "coma x", (3, -1): "coma y",
    (3, 3): "trefoil x", (3, -3): "trefoil y", (4, 0): "spherical",
    (4, 2): "secondary astigmatism 0deg", (4, -2): "secondary astigmatism 45deg",
    (4, 4): "tetrafoil x", (4, -4): "tetrafoil y", (5, 1): "secondary coma x", (5, -1): "secondary coma y",
    (6, 0): "secondary spherical", (8, 0): "tertiary spherical",
}


def name(n: int, m: int) -> str:
    return _NAMES.get((n, m), f"Z({n},{m})")


def unit_disk(npix: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Square grid of npix² with the unit circle inscribed; returns rho, theta, boolean mask."""
    x = (np.arange(npix) - (npix - 1) / 2) / (npix / 2)
    xx, yy = np.meshgrid(x, x)
    rho = np.hypot(xx, yy)
    theta = np.arctan2(yy, xx)
    return rho, theta, rho <= 1.0
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/python/test_zernike_lib.py -v`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add skills/optical-design/scripts/_lib/zernike.py tests/python/test_zernike_lib.py
git commit -m "feat(zernike): index schemes, radial polynomials, normalization"
```

---

### Task 6: `zernike.py` convert, rms, strehl

**Files:**
- Create: `skills/optical-design/scripts/zernike.py`
- Test: `tests/python/test_zernike_cli.py`

**Interfaces:**
- Consumes: `_lib.zernike` (`indices`, `norm`, `basis`, `unit_disk`, `name`, `first_index`), `cli.parse_floats`.
- Produces: `zernike.main(argv)`; helper `coefficients_to_map(scheme, coeffs, npix) -> (map, mask)` reused by `wavefront.py`; `rms_from_coeffs(scheme, coeffs, exclude=("piston","tilt")) -> float`.

- [ ] **Step 1: Write the failing tests**

```python
import math
import pytest
import zernike


def test_convert_fringe_defocus_to_noll(run_json):
    # Fringe Z4 = 0.25 waves peak defocus -> Noll j=4 coefficient 0.25/sqrt(3) (RMS-normalized)
    out = run_json(zernike.main, ["convert", "--from", "fringe", "--to", "noll", "--coeffs", "0,0,0,0.25"])
    c = out["results"]["coefficients"]
    assert c[3] == pytest.approx(0.25 / math.sqrt(3))
    assert out["results"]["terms"][3]["name"] == "defocus"


def test_convert_noll_to_ansi_keeps_wavefront(run_json):
    out = run_json(zernike.main, ["convert", "--from", "noll", "--to", "ansi", "--coeffs", "0,0,0,0,0.3,0.1"])
    c = out["results"]["coefficients"]  # ansi j=3 is (2,-2), j=5 is (2,2)
    assert c[3] == pytest.approx(0.3) and c[5] == pytest.approx(0.1)


def test_convert_warns_on_unmapped_terms(run_json):
    out = run_json(zernike.main, ["convert", "--from", "fringe", "--to", "noll", "--nterms", "4", "--coeffs", "0,0,0,0,0,0,0,0,0.1"])
    assert any("dropped" in w for w in out["warnings"])


def test_rms_normalized_scheme_is_root_sum_square(run_json):
    out = run_json(zernike.main, ["rms", "--scheme", "noll", "--coeffs", "0,0,0,0.3,0.4"])
    assert out["results"]["rms_waves"] == pytest.approx(0.5)


def test_rms_fringe_divides_by_norm(run_json):
    out = run_json(zernike.main, ["rms", "--scheme", "fringe", "--coeffs", "0,0,0,0.25"])
    assert out["results"]["rms_waves"] == pytest.approx(0.25 / math.sqrt(3), rel=1e-2)
    assert out["results"]["pv_waves"] == pytest.approx(0.5, rel=2e-2)


def test_rms_excludes_piston_and_tilt_by_default(run_json):
    out = run_json(zernike.main, ["rms", "--scheme", "noll", "--coeffs", "5,1,1,0.3"])
    assert out["results"]["rms_waves"] == pytest.approx(0.3)


def test_strehl_from_rms(run_json):
    out = run_json(zernike.main, ["strehl", "--rms-waves", "0.0714"])   # λ/14
    r = out["results"]
    assert r["strehl_marechal"] == pytest.approx(0.80, abs=0.01)
    assert r["strehl_extended"] == pytest.approx(0.818, abs=0.01)
    assert out["warnings"] == []
    big = run_json(zernike.main, ["strehl", "--rms-waves", "0.3"])
    assert any("valid" in w for w in big["warnings"])


def test_strehl_from_coeffs(run_json):
    out = run_json(zernike.main, ["strehl", "--scheme", "fringe", "--coeffs", "0,0,0,0.125"])
    assert out["results"]["strehl_marechal"] == pytest.approx(0.794, abs=0.01)
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/python/test_zernike_cli.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write `zernike.py`**

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Zernike coefficient tools: convert schemes, RMS/PV, Strehl, Seidel from Fringe, fit a map (Tier 0)."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402
from _lib import zernike as Z  # noqa: E402

TOOL = "zernike"
LOW_ORDER = {(0, 0), (1, 1), (1, -1)}


def coefficients_to_map(scheme: str, coeffs: list[float], npix: int = 256):
    rho, theta, mask = Z.unit_disk(npix)
    B = Z.basis(scheme, len(coeffs), rho, theta)
    wmap = np.tensordot(np.asarray(coeffs, float), B, axes=1)
    wmap[~mask] = np.nan
    return wmap, mask


def rms_from_coeffs(scheme: str, coeffs: list[float], exclude_low_order: bool = True) -> float:
    total = 0.0
    for c, (n, m) in zip(coeffs, Z.indices(scheme, len(coeffs))):
        if exclude_low_order and (n, m) in LOW_ORDER:
            continue
        total += (c / Z.norm(scheme, n, m)) ** 2 if scheme == "fringe" else c * c
    return math.sqrt(total)


def _terms(scheme: str, coeffs: list[float]):
    j0 = Z.first_index(scheme)
    return [{"j": j0 + i, "n": n, "m": m, "name": Z.name(n, m), "value": c}
            for i, (c, (n, m)) in enumerate(zip(coeffs, Z.indices(scheme, len(coeffs))))]


def cmd_convert(parser, args):
    src, dst = args.from_scheme, args.to_scheme
    coeffs = cli.parse_floats(args.coeffs)
    src_idx = Z.indices(src, len(coeffs))
    nterms = args.nterms or (37 if dst == "fringe" else max(len(coeffs), 1))
    dst_idx = Z.indices(dst, nterms)
    lookup = {nm: i for i, nm in enumerate(dst_idx)}
    out = [0.0] * len(dst_idx)
    warnings = []
    for c, nm in zip(coeffs, src_idx):
        if c == 0.0:
            continue
        if nm in lookup:
            n, m = nm
            out[lookup[nm]] = c * Z.norm(src, n, m) / Z.norm(dst, n, m)
        else:
            warnings.append(f"dropped {Z.name(*nm)} {nm}: not within {nterms} terms of {dst}")
    return cli.Envelope(TOOL, "convert", 0,
                        inputs={"from": src, "to": dst, "coefficients": coeffs, "nterms": nterms},
                        results={"coefficients": out, "terms": _terms(dst, out), "scheme": dst},
                        units={"coefficients": "waves (same unit as input)"},
                        method="Same wavefront in both schemes: c_dst = c_src · N_src/N_dst, matched by (n, m); "
                               "Fringe N=1, Noll/ANSI N=√(n+1) (m=0) or √(2(n+1)) (Wyant & Creath 1992; Noll 1976; ANSI Z80.28)",
                        warnings=warnings)


def cmd_rms(parser, args):
    coeffs = cli.parse_floats(args.coeffs)
    rms = rms_from_coeffs(args.scheme, coeffs, exclude_low_order=not args.include_low_order)
    wmap, mask = coefficients_to_map(args.scheme, coeffs, npix=256)
    if not args.include_low_order:
        low = [c if (n, m) in LOW_ORDER else 0.0 for c, (n, m) in zip(coeffs, Z.indices(args.scheme, len(coeffs)))]
        wmap -= coefficients_to_map(args.scheme, low, npix=256)[0]
    pv = float(np.nanmax(wmap) - np.nanmin(wmap))
    contributions = [{"name": Z.name(n, m), "rms": abs(c) / Z.norm(args.scheme, n, m) if args.scheme == "fringe" else abs(c)}
                     for c, (n, m) in zip(coeffs, Z.indices(args.scheme, len(coeffs))) if c != 0.0]
    return cli.Envelope(TOOL, "rms", 0,
                        inputs={"scheme": args.scheme, "coefficients": coeffs, "include_low_order": args.include_low_order},
                        results={"rms_waves": rms, "pv_waves": pv, "per_term_rms": contributions},
                        units={"rms_waves": "waves", "pv_waves": "waves"},
                        method="RMS = √Σ(c_j/N_j)² over the unit disk (orthogonality); piston and tilt excluded unless --include-low-order; PV sampled on 256² grid")


def strehl_pair(rms_waves: float) -> tuple[float, float]:
    phase = 2 * math.pi * rms_waves
    return 1.0 - phase**2, math.exp(-(phase**2))


def cmd_strehl(parser, args):
    if args.rms_waves is None and args.coeffs is None:
        parser.error("give --rms-waves or --scheme with --coeffs")
    rms = args.rms_waves if args.rms_waves is not None else rms_from_coeffs(args.scheme, cli.parse_floats(args.coeffs))
    marechal, extended = strehl_pair(rms)
    warnings = []
    if rms > 0.1:
        warnings.append("RMS > 0.1 waves: Maréchal approximation not valid; compute the PSF (wavefront.py psf) instead")
    return cli.Envelope(TOOL, "strehl", 0,
                        inputs={"rms_waves": rms, "scheme": args.scheme, "coefficients": args.coeffs},
                        results={"rms_waves": rms, "strehl_marechal": marechal, "strehl_extended": extended,
                                 "meets_marechal_criterion": rms <= 1 / 14},
                        units={"rms_waves": "waves"},
                        method="Maréchal S ≈ 1 − (2πσ)²; extended S ≈ exp(−(2πσ)²); diffraction-limited when σ ≤ λ/14 (S ≥ 0.8) (Born & Wolf §9.3; Mahajan 1983)",
                        warnings=warnings)


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="zernike.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_, epilog=f"example: uv run zernike.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def convert(sub):
        sub.add_argument("--from", dest="from_scheme", choices=Z.SCHEMES, required=True)
        sub.add_argument("--to", dest="to_scheme", choices=Z.SCHEMES, required=True)
        sub.add_argument("--coeffs", required=True, help="comma list or file; ordered by the source scheme starting at its first index")
        sub.add_argument("--nterms", type=int, help="terms in the output (default: enough to hold the input)")
    add("convert", "Convert coefficients between fringe, noll and ansi schemes", "convert --from fringe --to noll --coeffs 0,0,0,0.25", cmd_convert, convert)

    def rms(sub):
        sub.add_argument("--scheme", choices=Z.SCHEMES, required=True)
        sub.add_argument("--coeffs", required=True)
        sub.add_argument("--include-low-order", action="store_true", help="keep piston and tilt")
    add("rms", "RMS and PV wavefront error from coefficients", "rms --scheme fringe --coeffs 0,0,0,0.25", cmd_rms, rms)

    def strehl(sub):
        sub.add_argument("--rms-waves", type=float)
        sub.add_argument("--scheme", choices=Z.SCHEMES)
        sub.add_argument("--coeffs")
    add("strehl", "Strehl ratio from RMS wavefront error or coefficients", "strehl --rms-waves 0.0714", cmd_strehl, strehl)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/python/test_zernike_cli.py -v`
Expected: PASS (8 tests).

- [ ] **Step 5: Commit**

```bash
git add skills/optical-design/scripts/zernike.py tests/python/test_zernike_cli.py
git commit -m "feat(zernike): convert, rms, strehl subcommands"
```

---

### Task 7: `zernike.py` seidel-from-zernike and fit

**Files:**
- Modify: `skills/optical-design/scripts/zernike.py`
- Test: `tests/python/test_zernike_cli.py` (append)

**Interfaces:**
- Produces: `fit_map(wmap: ndarray, scheme: str, nterms: int, mask: ndarray | None) -> (coeffs: list[float], residual_rms: float)` reused by `interfero.py`.

- [ ] **Step 1: Append failing tests**

```python
import numpy as np


def test_seidel_from_fringe_spherical_and_coma(run_json):
    # Wyant & Creath 1992, Table 3 (0-based Z index there; 1-based here):
    # spherical W040 = 6·Z9 ; coma W131 = 3·√(Z7²+Z8²) ; astig W222 = 2·√(Z5²+Z6²)
    coeffs = [0, 0, 0, 0, 0.05, 0, 0.1, 0, 0.2]
    out = run_json(zernike.main, ["seidel-from-zernike", "--coeffs", ",".join(map(str, coeffs))])
    r = out["results"]
    assert r["spherical_w040_waves"] == pytest.approx(1.2)
    assert r["coma_w131_waves"] == pytest.approx(0.3)
    assert r["coma_angle_deg"] == pytest.approx(0.0)
    assert r["astigmatism_w222_waves"] == pytest.approx(0.1)


def test_seidel_requires_nine_fringe_terms(run):
    code, _, err = run(zernike.main, ["seidel-from-zernike", "--coeffs", "0,0,0,0.1"])
    assert code == 2 and "9" in err


def test_fit_recovers_known_coefficients(run_json, tmp_path):
    truth = [0, 0, 0, 0.2, 0.05, -0.03, 0, 0, 0.1]
    wmap, _ = zernike.coefficients_to_map("fringe", truth, npix=128)
    path = tmp_path / "map.npy"
    np.save(path, wmap)
    out = run_json(zernike.main, ["fit", "--map", str(path), "--scheme", "fringe", "--nterms", "9"])
    np.testing.assert_allclose(out["results"]["coefficients"], truth, atol=1e-6)
    assert out["results"]["residual_rms_waves"] == pytest.approx(0.0, abs=1e-6)


def test_fit_accepts_csv_with_nan_outside_pupil(run_json, tmp_path):
    truth = [0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1]
    wmap, _ = zernike.coefficients_to_map("noll", truth + [0, 0], npix=64)
    path = tmp_path / "map.csv"
    np.savetxt(path, wmap, delimiter=",")
    out = run_json(zernike.main, ["fit", "--map", str(path), "--scheme", "noll", "--nterms", "11"])
    assert out["results"]["coefficients"][8] == pytest.approx(0.1, abs=1e-6)
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/python/test_zernike_cli.py -v -k "seidel or fit"`
Expected: FAIL — invalid choice.

- [ ] **Step 3: Implement**

Add to `zernike.py`:

```python
def load_map(path: str) -> np.ndarray:
    p = Path(path)
    if p.suffix.lower() == ".npy":
        return np.load(p).astype(float)
    return np.loadtxt(p, delimiter=",").astype(float)


def fit_map(wmap: np.ndarray, scheme: str, nterms: int, mask: np.ndarray | None = None):
    """Least-squares Zernike fit on the inscribed unit disk; NaN samples are ignored."""
    npix = wmap.shape[0]
    if wmap.shape[0] != wmap.shape[1]:
        raise ValueError("map must be square (pupil inscribed)")
    rho, theta, disk = Z.unit_disk(npix)
    valid = disk & np.isfinite(wmap)
    if mask is not None:
        valid &= mask.astype(bool)
    B = Z.basis(scheme, nterms, rho, theta)
    A = B[:, valid].T
    y = wmap[valid]
    coeffs, *_ = np.linalg.lstsq(A, y, rcond=None)
    residual = y - A @ coeffs
    return [float(c) for c in coeffs], float(np.sqrt(np.mean(residual**2)))


def cmd_seidel(parser, args):
    z = cli.parse_floats(args.coeffs)
    if len(z) < 9:
        parser.error("seidel-from-zernike needs at least 9 Fringe coefficients (Z1..Z9)")
    Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8, Z9 = z[:9]
    astig = 2 * math.hypot(Z5, Z6)
    coma = 3 * math.hypot(Z7, Z8)
    sph = 6 * Z9
    return cli.Envelope(TOOL, "seidel-from-zernike", 0,
                        inputs={"scheme": "fringe", "coefficients": z[:9]},
                        results={
                            "tilt_waves": math.hypot(Z2 - 2 * Z7, Z3 - 2 * Z8),
                            "tilt_angle_deg": math.degrees(math.atan2(Z3 - 2 * Z8, Z2 - 2 * Z7)),
                            "defocus_w020_waves": 2 * Z4 - 6 * Z9,
                            "astigmatism_w222_waves": astig,
                            "astigmatism_angle_deg": 0.5 * math.degrees(math.atan2(Z6, Z5)),
                            "coma_w131_waves": coma,
                            "coma_angle_deg": math.degrees(math.atan2(Z8, Z7)),
                            "spherical_w040_waves": sph,
                        },
                        units={k: "waves" for k in ("tilt_waves", "defocus_w020_waves", "astigmatism_w222_waves", "coma_w131_waves", "spherical_w040_waves")},
                        method="Wyant & Creath 1992, 'Basic Wavefront Aberration Theory for Optical Metrology', Table 3, "
                               "Fringe (unnormalized) coefficients: W040=6Z9, W131=3√(Z7²+Z8²), W222=2√(Z5²+Z6²), "
                               "W020=2Z4−6Z9 (add ±W222/2 to reach the sagittal/tangential foci), tilt=√((Z2−2Z7)²+(Z3−2Z8)²)")


def cmd_fit(parser, args):
    wmap = load_map(args.map)
    coeffs, resid = fit_map(wmap, args.scheme, args.nterms)
    return cli.Envelope(TOOL, "fit", 0,
                        inputs={"map": args.map, "scheme": args.scheme, "nterms": args.nterms, "shape": list(wmap.shape)},
                        results={"coefficients": coeffs, "terms": _terms(args.scheme, coeffs), "residual_rms_waves": resid,
                                 "rms_waves": rms_from_coeffs(args.scheme, coeffs)},
                        units={"coefficients": "map units", "residual_rms_waves": "map units", "rms_waves": "map units"},
                        method="Linear least squares on the inscribed unit disk; NaN samples excluded; RMS excludes piston/tilt")
```

Parser additions inside `build_parser`, before `return parser`:
```python
    def seidel(sub):
        sub.add_argument("--coeffs", required=True, help="Fringe coefficients Z1..Z9 (or more) in waves")
    add("seidel-from-zernike", "Seidel-type aberration magnitudes from Fringe coefficients", "seidel-from-zernike --coeffs 0,0,0,0,0.05,0,0.1,0,0.2", cmd_seidel, seidel)

    def fit(sub):
        sub.add_argument("--map", required=True, help=".npy or .csv square wavefront map, NaN outside the pupil")
        sub.add_argument("--scheme", choices=Z.SCHEMES, default="fringe")
        sub.add_argument("--nterms", type=int, default=37)
    add("fit", "Least-squares Zernike fit of a wavefront map", "fit --map wfe.npy --scheme fringe --nterms 37", cmd_fit, fit)
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/python/test_zernike_cli.py -v`
Expected: PASS (12 tests).

- [ ] **Step 5: Commit**

```bash
git add skills/optical-design/scripts/zernike.py tests/python/test_zernike_cli.py
git commit -m "feat(zernike): seidel-from-zernike and map fitting"
```

---

### Task 8: `_lib/fourier.py` and `wavefront.py` psf / mtf / sample-check

**Files:**
- Create: `skills/optical-design/scripts/_lib/fourier.py`, `skills/optical-design/scripts/wavefront.py`
- Test: `tests/python/test_wavefront.py`

**Interfaces:**
- Produces (`_lib/fourier.py`):
  - `psf_from_wavefront(wmap_waves: ndarray, mask: ndarray, pad: int = 8) -> dict` with keys `psf` (2-D, normalized to unit sum), `strehl` (peak ratio vs. unaberrated pupil), `pixel_lambda_fnum` (PSF sample pitch in units of λF# = `Dpx/M`), `fwhm_lambda_fnum`, `encircled_energy_airy` (fraction within 1.22 λF#).
  - `mtf_from_psf(psf: ndarray, pixel_lambda_fnum: float) -> (nu_over_cutoff: ndarray, mtf_x: ndarray, mtf_y: ndarray)` where `nu_over_cutoff` runs 0..1 (values beyond cutoff dropped).
- `wavefront.main(argv)` subcommands `psf`, `mtf`, `sample-check`; options `--scheme --coeffs` or `--map`; `--wavelength-um --fnum` optional to report physical units; `--out path.npy` saves the PSF grid.

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np
import pytest
import wavefront
from _lib import fourier, optics, zernike as Z


def test_unaberrated_psf_has_unit_strehl_and_airy_energy():
    rho, theta, mask = Z.unit_disk(128)
    res = fourier.psf_from_wavefront(np.zeros_like(rho), mask, pad=8)
    assert res["strehl"] == pytest.approx(1.0, abs=1e-6)
    assert res["encircled_energy_airy"] == pytest.approx(0.838, abs=0.01)   # Born & Wolf: 83.8 % inside first dark ring
    assert res["fwhm_lambda_fnum"] == pytest.approx(1.03, abs=0.03)


def test_mtf_matches_diffraction_limited_curve():
    rho, theta, mask = Z.unit_disk(128)
    res = fourier.psf_from_wavefront(np.zeros_like(rho), mask, pad=8)
    nu, mtf_x, mtf_y = fourier.mtf_from_psf(res["psf"], res["pixel_lambda_fnum"])
    for x, m in zip(nu, mtf_x):
        if x <= 0.9:
            assert m == pytest.approx(optics.mtf_diffraction(x), abs=0.01), x


def test_quarter_wave_defocus_gives_strehl_0_8(run_json):
    # W020 = λ/4 -> Fringe Z4 = 0.125 (balanced) -> Strehl ≈ 0.80 (Rayleigh quarter-wave rule)
    out = run_json(wavefront.main, ["psf", "--scheme", "fringe", "--coeffs", "0,0,0,0.125"])
    assert out["results"]["strehl"] == pytest.approx(0.80, abs=0.02)
    assert out["results"]["rms_waves"] == pytest.approx(0.0722, abs=0.002)


def test_psf_physical_units_and_out_file(run_json, tmp_path):
    out_path = tmp_path / "psf.npy"
    out = run_json(wavefront.main, ["psf", "--scheme", "noll", "--coeffs", "0", "--wavelength-um", "0.55", "--fnum", "4", "--out", str(out_path)])
    assert out["results"]["pixel_um"] == pytest.approx(0.55 * 4 * out["results"]["pixel_lambda_fnum"])
    assert out["results"]["airy_radius_um"] == pytest.approx(2.684)
    assert np.load(out_path).ndim == 2


def test_mtf_reports_requested_frequencies_and_nyquist(run_json):
    out = run_json(wavefront.main, ["mtf", "--scheme", "noll", "--coeffs", "0", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "5", "--freqs", "50,100"])
    r = out["results"]
    assert r["cutoff_cyc_per_mm"] == pytest.approx(500.0)
    assert r["nyquist_cyc_per_mm"] == pytest.approx(100.0)
    assert r["mtf_at"]["100"]["x"] == pytest.approx(optics.mtf_diffraction(0.2), abs=0.01)
    assert r["mtf_at"]["100"]["diffraction_limit"] == pytest.approx(optics.mtf_diffraction(0.2))


def test_sample_check(run_json):
    out = run_json(wavefront.main, ["sample-check", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "1.0"])
    assert out["results"]["q"] == pytest.approx(2.0)
    assert out["warnings"] == []
    under = run_json(wavefront.main, ["sample-check", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "5.0"])
    assert under["results"]["q"] == pytest.approx(0.4) and any("aliases" in w for w in under["warnings"])
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/python/test_wavefront.py -v`
Expected: FAIL — modules missing.

- [ ] **Step 3: Write `_lib/fourier.py`**

```python
"""FFT-based PSF/MTF from a pupil wavefront. Units: PSF sample pitch in λF#, frequency in ν/ν_cutoff."""
from __future__ import annotations

import numpy as np


def _peak_and_center(psf: np.ndarray) -> tuple[float, tuple[int, int]]:
    idx = np.unravel_index(int(np.argmax(psf)), psf.shape)
    return float(psf[idx]), (int(idx[0]), int(idx[1]))


def psf_from_wavefront(wmap_waves: np.ndarray, mask: np.ndarray, pad: int = 8) -> dict:
    npix = mask.shape[0]
    dpx = int(np.count_nonzero(mask[npix // 2]))  # pupil diameter in samples along the center row
    M = npix * pad
    w = np.where(mask, np.nan_to_num(wmap_waves), 0.0)
    field = mask * np.exp(2j * np.pi * w)
    ref = mask.astype(complex)

    def _psf(f):
        F = np.fft.fftshift(np.fft.fft2(f, s=(M, M)))
        return np.abs(F) ** 2

    psf, psf_ref = _psf(field), _psf(ref)
    peak, center = _peak_and_center(psf)
    peak_ref, _ = _peak_and_center(psf_ref)
    strehl = peak / peak_ref
    psf_n = psf / psf.sum()
    pitch = dpx / M  # PSF sample pitch in units of λF#

    yy, xx = np.indices(psf.shape)
    r = np.hypot(yy - center[0], xx - center[1]) * pitch
    ee_airy = float(psf_n[r <= 1.22].sum())

    row = psf[center[0]]
    half = peak / 2
    left = center[1]
    while left > 0 and row[left] > half:
        left -= 1
    right = center[1]
    while right < M - 1 and row[right] > half:
        right += 1
    # linear interpolation at the half-maximum crossings
    xl = left + (half - row[left]) / (row[left + 1] - row[left])
    xr = right - (half - row[right]) / (row[right - 1] - row[right])
    fwhm = (xr - xl) * pitch
    return {"psf": psf_n, "strehl": float(strehl), "pixel_lambda_fnum": float(pitch),
            "fwhm_lambda_fnum": float(fwhm), "encircled_energy_airy": ee_airy, "center": center}


def mtf_from_psf(psf: np.ndarray, pixel_lambda_fnum: float):
    otf = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(psf)))
    mtf = np.abs(otf) / np.abs(otf).max()
    M = psf.shape[0]
    c = M // 2
    # frequency step per bin = 1/(M·pitch) in units of 1/(λF#) == ν_cutoff
    step = 1.0 / (M * pixel_lambda_fnum)
    nu = np.arange(0, M - c) * step
    keep = nu <= 1.0
    return nu[keep], mtf[c, c:][keep], mtf[c:, c][keep]
```

- [ ] **Step 4: Write `wavefront.py`**

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""PSF, MTF and sampling checks from a wavefront (Zernike coefficients or a map) (Tier 0)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli, fourier, optics  # noqa: E402
from _lib import zernike as Z  # noqa: E402
from zernike import coefficients_to_map, load_map, rms_from_coeffs  # noqa: E402

TOOL = "wavefront"


def _wavefront(parser, args, npix: int):
    if args.map:
        wmap = load_map(args.map)
        _, _, mask = Z.unit_disk(wmap.shape[0])
        mask &= np.isfinite(wmap)
        rms = float(np.sqrt(np.nanmean((wmap[mask] - np.nanmean(wmap[mask])) ** 2)))
        return wmap, mask, rms, {"map": args.map}
    if args.coeffs is None or args.scheme is None:
        parser.error("give --scheme with --coeffs, or --map")
    coeffs = cli.parse_floats(args.coeffs)
    wmap, mask = coefficients_to_map(args.scheme, coeffs, npix=npix)
    return wmap, mask, rms_from_coeffs(args.scheme, coeffs), {"scheme": args.scheme, "coefficients": coeffs}


def _physical(results, units, args):
    if args.wavelength_um is not None and args.fnum is not None:
        lf = args.wavelength_um * args.fnum
        results["pixel_um"] = results["pixel_lambda_fnum"] * lf
        results["fwhm_um"] = results["fwhm_lambda_fnum"] * lf
        results["airy_radius_um"] = optics.airy_radius(args.wavelength_um, fnum=args.fnum)
        units.update({"pixel_um": "um", "fwhm_um": "um", "airy_radius_um": "um"})


def cmd_psf(parser, args):
    wmap, mask, rms, inputs = _wavefront(parser, args, args.npix)
    res = fourier.psf_from_wavefront(wmap, mask, pad=args.pad)
    results = {"strehl": res["strehl"], "rms_waves": rms, "fwhm_lambda_fnum": res["fwhm_lambda_fnum"],
               "encircled_energy_airy": res["encircled_energy_airy"], "pixel_lambda_fnum": res["pixel_lambda_fnum"]}
    units = {"rms_waves": "waves", "fwhm_lambda_fnum": "lambda*F#", "pixel_lambda_fnum": "lambda*F#"}
    _physical(results, units, args)
    warnings = []
    if rms <= 0.1:
        marechal = 1 - (2 * np.pi * rms) ** 2
        if abs(marechal - res["strehl"]) > 0.05:
            warnings.append(f"Strehl {res['strehl']:.3f} disagrees with Maréchal estimate {marechal:.3f}; check coefficient scheme/normalization")
    if args.out:
        np.save(args.out, res["psf"])
        results["psf_file"] = args.out
    return cli.Envelope(TOOL, "psf", 0, inputs={**inputs, "npix": args.npix, "pad": args.pad, "wavelength_um": args.wavelength_um, "fnum": args.fnum},
                        results=results, units=units, warnings=warnings,
                        method="Fraunhofer PSF = |FFT(P·exp(2πiW))|², Strehl = peak / unaberrated peak, zero-padded ×pad (Goodman, Fourier Optics ch. 6)")


def cmd_mtf(parser, args):
    wmap, mask, rms, inputs = _wavefront(parser, args, args.npix)
    res = fourier.psf_from_wavefront(wmap, mask, pad=args.pad)
    nu, mx, my = fourier.mtf_from_psf(res["psf"], res["pixel_lambda_fnum"])
    results = {"strehl": res["strehl"], "rms_waves": rms}
    units = {"rms_waves": "waves"}
    warnings = []
    if args.wavelength_um is not None and args.fnum is not None:
        cutoff = optics.mtf_cutoff_cyc_per_mm(args.wavelength_um, args.fnum)
        results["cutoff_cyc_per_mm"] = cutoff
        units["cutoff_cyc_per_mm"] = "cyc/mm"
        freqs = cli.parse_floats(args.freqs) if args.freqs else []
        if args.pixel_um is not None:
            nyq = 1000.0 / (2 * args.pixel_um)
            results["nyquist_cyc_per_mm"] = nyq
            units["nyquist_cyc_per_mm"] = "cyc/mm"
            freqs.append(nyq)
        results["mtf_at"] = {}
        for f in freqs:
            x = f / cutoff
            results["mtf_at"][f"{f:g}"] = {"x": float(np.interp(x, nu, mx)), "y": float(np.interp(x, nu, my)),
                                           "diffraction_limit": optics.mtf_diffraction(x)}
        if any(v["x"] > v["diffraction_limit"] + 0.02 for v in results["mtf_at"].values()):
            warnings.append("MTF exceeds the diffraction limit: numerical artifact, increase --pad/--npix")
    results["curve_nu_over_cutoff"] = nu[::max(1, len(nu) // 50)].tolist()
    results["curve_mtf_x"] = mx[::max(1, len(nu) // 50)].tolist()
    results["curve_mtf_y"] = my[::max(1, len(nu) // 50)].tolist()
    return cli.Envelope(TOOL, "mtf", 0, inputs={**inputs, "wavelength_um": args.wavelength_um, "fnum": args.fnum, "pixel_um": args.pixel_um, "freqs": args.freqs},
                        results=results, units=units, warnings=warnings,
                        method="MTF = |FFT(PSF)| normalized; diffraction limit (2/π)(acos x − x√(1−x²)), x = ν λ F# (Smith ch. 11)")


def cmd_sample_check(parser, args):
    q = optics.sampling_q(args.wavelength_um, args.fnum, args.pixel_um)
    cutoff = optics.mtf_cutoff_cyc_per_mm(args.wavelength_um, args.fnum)
    nyq = 1000.0 / (2 * args.pixel_um)
    warnings = []
    if q < 2:
        warnings.append(f"Q = {q:.2f} < 2: detector Nyquist ({nyq:.1f} cyc/mm) is below the optical cutoff ({cutoff:.1f} cyc/mm); the image aliases")
    return cli.Envelope(TOOL, "sample-check", 0,
                        inputs={"wavelength_um": args.wavelength_um, "fnum": args.fnum, "pixel_um": args.pixel_um},
                        results={"q": q, "cutoff_cyc_per_mm": cutoff, "nyquist_cyc_per_mm": nyq,
                                 "airy_radius_pixels": optics.airy_radius(args.wavelength_um, fnum=args.fnum) / args.pixel_um},
                        units={"cutoff_cyc_per_mm": "cyc/mm", "nyquist_cyc_per_mm": "cyc/mm", "airy_radius_pixels": "px"},
                        method="Q = λF#/p; Q = 2 is critically sampled (Fiete 1999, Opt. Eng. 38)", warnings=warnings)


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="wavefront.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_, epilog=f"example: uv run wavefront.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def source(sub):
        sub.add_argument("--scheme", choices=Z.SCHEMES)
        sub.add_argument("--coeffs", help="Zernike coefficients in waves")
        sub.add_argument("--map", help=".npy/.csv wavefront map in waves, NaN outside pupil")
        sub.add_argument("--wavelength-um", type=float)
        sub.add_argument("--fnum", type=float)
        sub.add_argument("--npix", type=int, default=128, help="pupil samples across (coefficient input)")
        sub.add_argument("--pad", type=int, default=8, help="FFT zero-padding factor")

    def psf(sub):
        source(sub)
        sub.add_argument("--out", help="save the normalized PSF grid as .npy")
    add("psf", "PSF, Strehl, FWHM and encircled energy from a wavefront", "psf --scheme fringe --coeffs 0,0,0,0.125 --wavelength-um 0.55 --fnum 4", cmd_psf, psf)

    def mtf(sub):
        source(sub)
        sub.add_argument("--pixel-um", type=float, help="detector pitch, adds MTF at Nyquist")
        sub.add_argument("--freqs", help="comma list of cyc/mm to report")
    add("mtf", "MTF curve with diffraction-limit comparison", "mtf --scheme noll --coeffs 0 --wavelength-um 0.5 --fnum 4 --pixel-um 5 --freqs 50,100", cmd_mtf, mtf)

    def sample(sub):
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--fnum", type=float, required=True)
        sub.add_argument("--pixel-um", type=float, required=True)
    add("sample-check", "Detector sampling Q vs. optical cutoff", "sample-check --wavelength-um 0.5 --fnum 4 --pixel-um 1", cmd_sample_check, sample)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests**

Run: `uv run pytest tests/python/test_wavefront.py -v`
Expected: PASS (6 tests). If `encircled_energy_airy` lands outside ±0.01, raise `--pad` default to 16 in both the test call and the default and re-run; record the chosen default in `method`.

- [ ] **Step 6: Commit**

```bash
git add skills/optical-design/scripts/_lib/fourier.py skills/optical-design/scripts/wavefront.py tests/python/test_wavefront.py
git commit -m "feat(wavefront): FFT PSF, MTF and sampling checks"
```

---

### Task 9: `interfero.py` psi / unwrap / fringe-to-wfe / cavity

**Files:**
- Create: `skills/optical-design/scripts/interfero.py`
- Test: `tests/python/test_interfero.py`

**Interfaces:**
- Consumes: `zernike.fit_map`, `zernike.load_map`, `zernike.rms_from_coeffs`, `_lib.zernike`.
- Produces: `interfero.main(argv)`; `psi_phase(frames: ndarray, algorithm: str) -> ndarray` (wrapped phase, radians).

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np
import pytest
import interfero
from _lib import zernike as Z
from zernike import coefficients_to_map


def _frames(phase, steps):
    return np.stack([1.0 + 0.8 * np.cos(phase + s) for s in steps])


@pytest.mark.parametrize("algorithm,steps", [
    ("4step", [0, np.pi / 2, np.pi, 3 * np.pi / 2]),
    ("3step", [0, 2 * np.pi / 3, 4 * np.pi / 3]),
    ("5step", [-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi]),
])
def test_psi_recovers_wrapped_phase(algorithm, steps):
    rho, theta, mask = Z.unit_disk(64)
    phase = 2 * np.pi * 0.3 * (2 * rho**2 - 1)
    rec = interfero.psi_phase(_frames(phase, steps), algorithm)
    diff = np.angle(np.exp(1j * (rec - phase)))
    assert np.max(np.abs(diff[mask])) < 1e-6


def test_psi_cli_writes_phase(run_json, tmp_path):
    rho, theta, mask = Z.unit_disk(32)
    frames = _frames(0.5 * rho, [0, np.pi / 2, np.pi, 3 * np.pi / 2])
    fp = tmp_path / "frames.npy"
    np.save(fp, frames)
    out = run_json(interfero.main, ["psi", "--frames", str(fp), "--algorithm", "4step", "--out", str(tmp_path / "phase.npy")])
    assert out["results"]["shape"] == [32, 32]
    assert np.load(tmp_path / "phase.npy").shape == (32, 32)


def test_unwrap_recovers_multi_wave_ramp(run_json, tmp_path):
    x = np.linspace(0, 6 * np.pi, 64)
    phase = np.tile(x, (64, 1))
    wrapped = np.angle(np.exp(1j * phase))
    fp = tmp_path / "wrapped.npy"
    np.save(fp, wrapped)
    out = run_json(interfero.main, ["unwrap", "--phase", str(fp), "--out", str(tmp_path / "unwrapped.npy")])
    un = np.load(tmp_path / "unwrapped.npy")
    assert np.ptp(un) == pytest.approx(6 * np.pi, rel=1e-3)
    assert out["results"]["pv_waves"] == pytest.approx(3.0, rel=1e-3)


def test_fringe_to_wfe_double_pass_and_zernike(run_json, tmp_path):
    truth = [0, 0, 0, 0.1, 0, 0, 0, 0, 0.05]
    wmap, mask = coefficients_to_map("fringe", truth, npix=96)
    phase = 2 * np.pi * 2 * wmap  # double pass (Fizeau on a mirror)
    fp = tmp_path / "phase.npy"
    np.save(fp, phase)
    out = run_json(interfero.main, ["fringe-to-wfe", "--phase", str(fp), "--passes", "2", "--scheme", "fringe", "--nterms", "9"])
    r = out["results"]
    np.testing.assert_allclose(r["coefficients"], truth, atol=1e-6)
    assert r["rms_waves"] == pytest.approx((0.1 / np.sqrt(3))**2 + (0.05 / np.sqrt(5))**2, abs=1e-3) or True
    assert r["passes"] == 2


def test_cavity(run_json):
    out = run_json(interfero.main, ["cavity", "--gap-mm", "5", "--wavelength-um", "0.6328", "--tilt-arcsec", "10", "--linewidth-nm", "0.001"])
    r = out["results"]
    # fringe spacing for double-pass tilt: λ / (2 tan θ), θ = 10 arcsec = 4.848e-5 rad -> 6.53 mm
    assert r["fringe_spacing_mm"] == pytest.approx(6.527, rel=1e-3)
    assert r["coherence_length_mm"] == pytest.approx(400.4, rel=1e-3)   # λ²/Δλ = 0.4004 µm² / 1e-6 µm = 400.4 mm
    assert r["opd_mm"] == pytest.approx(10.0)
    assert out["warnings"] == []
```

Note: the `rms_waves` assertion in `test_fringe_to_wfe_double_pass_and_zernike` is deliberately loose (`or True`); replace it with `assert r["rms_waves"] == pytest.approx(np.sqrt((0.1/np.sqrt(3))**2 + (0.05/np.sqrt(5))**2), rel=1e-3)` once the command runs — that is the exact expected value (0.0619).

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/python/test_interfero.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write `interfero.py`**

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "scikit-image>=0.22"]
# ///
"""Phase-shifting interferometry, unwrapping, fringe-to-wavefront, cavity checks (Tier 0)."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402
from _lib import zernike as Z  # noqa: E402
from zernike import _terms, fit_map, load_map, rms_from_coeffs  # noqa: E402

TOOL = "interfero"
ALGORITHMS = ("3step", "4step", "5step")


def psi_phase(frames: np.ndarray, algorithm: str) -> np.ndarray:
    """Wrapped phase from N intensity frames (Malacara, Optical Shop Testing, ch. 14).

    3step: steps 0, 2π/3, 4π/3 -> atan2(√3 (I3 − I2), 2 I1 − I2 − I3)
    4step: steps 0, π/2, π, 3π/2 -> atan2(I4 − I2, I1 − I3)
    5step (Hariharan): steps −π, −π/2, 0, π/2, π -> atan2(2 (I2 − I4), 2 I3 − I1 − I5)
    """
    I = [f.astype(float) for f in frames]
    if algorithm == "3step":
        if len(I) != 3:
            raise ValueError("3step needs 3 frames")
        return np.arctan2(math.sqrt(3) * (I[2] - I[1]), 2 * I[0] - I[1] - I[2])
    if algorithm == "4step":
        if len(I) != 4:
            raise ValueError("4step needs 4 frames")
        return np.arctan2(I[3] - I[1], I[0] - I[2])
    if algorithm == "5step":
        if len(I) != 5:
            raise ValueError("5step needs 5 frames")
        return np.arctan2(2 * (I[1] - I[3]), 2 * I[2] - I[0] - I[4])
    raise ValueError(f"unknown algorithm {algorithm}")


def cmd_psi(parser, args):
    frames = np.load(args.frames)
    try:
        phase = psi_phase(frames, args.algorithm)
    except ValueError as e:
        parser.error(str(e))
    np.save(args.out, phase)
    return cli.Envelope(TOOL, "psi", 0, inputs={"frames": args.frames, "algorithm": args.algorithm, "n_frames": int(frames.shape[0])},
                        results={"phase_file": args.out, "shape": list(phase.shape), "wrapped": True},
                        units={}, method=psi_phase.__doc__.strip().splitlines()[0])


def cmd_unwrap(parser, args):
    skimage = cli.require("skimage.restoration", "install scikit-image (uv run installs it from the script header)")
    wrapped = load_map(args.phase)
    un = np.asarray(skimage.unwrap_phase(np.ma.masked_invalid(wrapped)))
    un = np.where(np.isfinite(wrapped), un, np.nan)
    np.save(args.out, un)
    pv = float(np.nanmax(un) - np.nanmin(un))
    return cli.Envelope(TOOL, "unwrap", 0, inputs={"phase": args.phase},
                        results={"phase_file": args.out, "pv_rad": pv, "pv_waves": pv / (2 * math.pi)},
                        units={"pv_rad": "rad", "pv_waves": "waves"},
                        method="2-D phase unwrapping, Herráez et al. 2002 (scikit-image unwrap_phase)")


def cmd_fringe_to_wfe(parser, args):
    phase = load_map(args.phase)
    wfe = phase / (2 * math.pi) / args.passes
    results = {"passes": args.passes}
    units = {}
    if args.nterms:
        coeffs, resid = fit_map(wfe, args.scheme, args.nterms)
        low = [c if (n, m) in {(0, 0), (1, 1), (1, -1)} else 0.0 for c, (n, m) in zip(coeffs, Z.indices(args.scheme, len(coeffs)))]
        rho, theta, mask = Z.unit_disk(wfe.shape[0])
        wfe = wfe - np.tensordot(np.asarray(low), Z.basis(args.scheme, len(low), rho, theta), axes=1)
        results.update({"coefficients": coeffs, "terms": _terms(args.scheme, coeffs), "scheme": args.scheme,
                        "rms_waves": rms_from_coeffs(args.scheme, coeffs), "fit_residual_rms_waves": resid})
        units.update({"rms_waves": "waves", "fit_residual_rms_waves": "waves"})
    valid = np.isfinite(wfe)
    results["pv_waves"] = float(np.nanmax(wfe) - np.nanmin(wfe))
    results["rms_map_waves"] = float(np.sqrt(np.mean((wfe[valid] - wfe[valid].mean()) ** 2)))
    units.update({"pv_waves": "waves", "rms_map_waves": "waves"})
    if args.out:
        np.save(args.out, wfe)
        results["wfe_file"] = args.out
    return cli.Envelope(TOOL, "fringe-to-wfe", 0, inputs={"phase": args.phase, "passes": args.passes, "scheme": args.scheme, "nterms": args.nterms},
                        results=results, units=units,
                        method="W = φ/(2π)/passes (passes=2 for Fizeau/Twyman-Green reflection tests); piston/tilt removed after Zernike fit")


def cmd_cavity(parser, args):
    lam_mm = args.wavelength_um * 1e-3
    results = {"opd_mm": 2 * args.gap_mm}
    units = {"opd_mm": "mm"}
    warnings = []
    if args.tilt_arcsec is not None:
        theta = math.radians(args.tilt_arcsec / 3600)
        results["fringe_spacing_mm"] = lam_mm / (2 * math.tan(theta))
        results["fringes_across_100mm"] = 100.0 / results["fringe_spacing_mm"]
        units["fringe_spacing_mm"] = "mm"
    if args.linewidth_nm is not None:
        lc = (args.wavelength_um ** 2) / (args.linewidth_nm * 1e-3) * 1e-3  # µm²/µm -> µm -> mm
        results["coherence_length_mm"] = lc
        units["coherence_length_mm"] = "mm"
        results["opd_over_coherence_length"] = results["opd_mm"] / lc
        if results["opd_over_coherence_length"] > 0.5:
            warnings.append("cavity OPD exceeds half the coherence length: fringe contrast will collapse")
    return cli.Envelope(TOOL, "cavity", 0,
                        inputs={"gap_mm": args.gap_mm, "wavelength_um": args.wavelength_um, "tilt_arcsec": args.tilt_arcsec, "linewidth_nm": args.linewidth_nm},
                        results=results, units=units, warnings=warnings,
                        method="Double-pass cavity: OPD = 2·gap; tilt fringe spacing λ/(2 tan θ); coherence length λ²/Δλ (Malacara ch. 1)")


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="interfero.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_, epilog=f"example: uv run interfero.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def psi(sub):
        sub.add_argument("--frames", required=True, help=".npy stack shaped (N, H, W)")
        sub.add_argument("--algorithm", choices=ALGORITHMS, default="4step")
        sub.add_argument("--out", default="phase_wrapped.npy")
    add("psi", "Wrapped phase from phase-shifted frames", "psi --frames frames.npy --algorithm 4step --out phase.npy", cmd_psi, psi)

    def unwrap(sub):
        sub.add_argument("--phase", required=True)
        sub.add_argument("--out", default="phase_unwrapped.npy")
    add("unwrap", "2-D phase unwrapping", "unwrap --phase phase.npy --out unwrapped.npy", cmd_unwrap, unwrap)

    def f2w(sub):
        sub.add_argument("--phase", required=True, help="unwrapped phase map in radians")
        sub.add_argument("--passes", type=int, default=2)
        sub.add_argument("--scheme", choices=Z.SCHEMES, default="fringe")
        sub.add_argument("--nterms", type=int, default=37)
        sub.add_argument("--out")
    add("fringe-to-wfe", "Phase map to wavefront error, with Zernike fit", "fringe-to-wfe --phase unwrapped.npy --passes 2 --nterms 37", cmd_fringe_to_wfe, f2w)

    def cavity(sub):
        sub.add_argument("--gap-mm", type=float, required=True)
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--tilt-arcsec", type=float)
        sub.add_argument("--linewidth-nm", type=float)
    add("cavity", "Fizeau/Twyman-Green cavity OPD, tilt fringes, coherence check", "cavity --gap-mm 5 --wavelength-um 0.6328 --tilt-arcsec 10 --linewidth-nm 0.001", cmd_cavity, cavity)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests, tighten the loose assertion, re-run**

Run: `uv run pytest tests/python/test_interfero.py -v`
Expected: PASS (7 tests). Then replace the `or True` assertion as noted and re-run: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/optical-design/scripts/interfero.py tests/python/test_interfero.py
git commit -m "feat(interfero): PSI, unwrap, fringe-to-wavefront, cavity checks"
```

---

### Task 10: `compare.py`

**Files:**
- Create: `skills/optical-design/scripts/compare.py`
- Test: `tests/python/test_compare.py`

**Interfaces:**
- Produces: `compare.main(argv)`; `flatten(d: dict, prefix="") -> dict[str, float]` (numeric leaves only, keys joined with `.`); exit 0 when all within tolerance, exit 1 otherwise (documented as "comparison failed", distinct from the 2/3/4 codes).

- [ ] **Step 1: Write the failing tests**

```python
import json
import pytest
import compare


def _write(tmp_path, name, results):
    p = tmp_path / name
    p.write_text(json.dumps({"schema": "1", "tool": "t", "subcommand": "s", "tier": 0, "inputs": {},
                             "results": results, "units": {}, "method": "", "warnings": []}))
    return str(p)


def test_flatten_numeric_leaves():
    flat = compare.flatten({"a": 1, "b": {"c": 2.5, "d": "x"}, "e": [1, 2]})
    assert flat == {"a": 1.0, "b.c": 2.5, "e.0": 1.0, "e.1": 2.0}


def test_within_tolerance_exits_0(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.80, "rms": 0.07})
    b = _write(tmp_path, "b.json", {"strehl": 0.805, "rms": 0.0701})
    code, out, _ = run(compare.main, [a, b, "--rtol", "0.01", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["results"]["all_within_tolerance"] is True
    assert data["results"]["diffs"]["results.strehl"]["rel"] == pytest.approx(0.00625)


def test_outside_tolerance_exits_1_and_lists(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.80})
    b = _write(tmp_path, "b.json", {"strehl": 0.70})
    code, out, _ = run(compare.main, [a, b, "--rtol", "0.05", "--json"])
    assert code == 1
    assert "results.strehl" in json.loads(out)["results"]["exceeded"]


def test_missing_keys_are_reported(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.80, "only_a": 1})
    b = _write(tmp_path, "b.json", {"strehl": 0.80, "only_b": 2})
    code, out, _ = run(compare.main, [a, b, "--json"])
    data = json.loads(out)
    assert set(data["results"]["only_in_a"]) == {"results.only_a"} and set(data["results"]["only_in_b"]) == {"results.only_b"}
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/python/test_compare.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write `compare.py`**

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare two JSON envelopes (tier vs tier, before vs after) with tolerances (Tier 0).

Exit 0 when every shared numeric value is within tolerance, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402

TOOL = "compare"


def flatten(d, prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}{k}."))
    elif isinstance(d, (list, tuple)):
        for i, v in enumerate(d):
            out.update(flatten(v, f"{prefix}{i}."))
    elif isinstance(d, bool):
        return out
    elif isinstance(d, (int, float)):
        out[prefix[:-1]] = float(d)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compare.py", description=__doc__, parents=[cli.common_parser()],
                                     epilog="example: uv run compare.py before.json after.json --rtol 0.02")
    parser.add_argument("a")
    parser.add_argument("b")
    parser.add_argument("--rtol", type=float, default=0.01)
    parser.add_argument("--atol", type=float, default=0.0)
    parser.add_argument("--section", default="results", help="top-level key to compare (default results; use '' for all)")
    args = parser.parse_args(argv)

    da = json.loads(Path(args.a).read_text(encoding="utf-8"))
    db = json.loads(Path(args.b).read_text(encoding="utf-8"))
    if args.section:
        da, db = {args.section: da.get(args.section, {})}, {args.section: db.get(args.section, {})}
    fa, fb = flatten(da), flatten(db)
    shared = sorted(set(fa) & set(fb))
    diffs, exceeded = {}, []
    for k in shared:
        x, y = fa[k], fb[k]
        absd = abs(x - y)
        rel = absd / abs(x) if x != 0 else (0.0 if absd == 0 else float("inf"))
        ok = absd <= args.atol + args.rtol * abs(x)
        diffs[k] = {"a": x, "b": y, "abs": absd, "rel": rel, "ok": ok}
        if not ok:
            exceeded.append(k)
    env = cli.Envelope(TOOL, "compare", 0,
                       inputs={"a": args.a, "b": args.b, "rtol": args.rtol, "atol": args.atol, "section": args.section},
                       results={"all_within_tolerance": not exceeded, "exceeded": exceeded, "diffs": diffs,
                                "only_in_a": sorted(set(fa) - set(fb)), "only_in_b": sorted(set(fb) - set(fa))},
                       units={}, method="|a−b| ≤ atol + rtol·|a| per shared numeric leaf",
                       warnings=[f"{len(exceeded)} value(s) exceed tolerance"] if exceeded else [])
    cli.emit(env, as_json=args.json)
    return 0 if not exceeded else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/python/test_compare.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add skills/optical-design/scripts/compare.py tests/python/test_compare.py
git commit -m "feat(compare): tolerance diff of result envelopes"
```

---

### Task 11: SKILL.md draft, frontmatter test, tier and install docs

**Files:**
- Create/replace: `skills/optical-design/SKILL.md`, `docs/tiers.md`, `docs/install.md`, `docs/compatibility.md`
- Test: `tests/node/frontmatter.test.ts`

**Interfaces:**
- Produces: the SKILL.md that plan 6 finalizes; the script index that plans 3–5 extend.

- [ ] **Step 1: Write the failing frontmatter test**

`tests/node/frontmatter.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import matter from "gray-matter";
import fs from "node:fs";
import path from "node:path";

const skillDir = path.resolve(__dirname, "..", "..", "skills", "optical-design");
const raw = fs.readFileSync(path.join(skillDir, "SKILL.md"), "utf8");
const parsed = matter(raw);
const allowed = ["name", "description", "license", "compatibility", "metadata"];

describe("SKILL.md frontmatter (Agent Skills spec)", () => {
  it("uses only portable fields", () => {
    for (const key of Object.keys(parsed.data)) expect(allowed, `field ${key}`).toContain(key);
  });
  it("name matches the directory and description is within limits", () => {
    expect(parsed.data.name).toBe("optical-design");
    expect(typeof parsed.data.description).toBe("string");
    expect(parsed.data.description.length).toBeGreaterThan(100);
    expect(parsed.data.description.length).toBeLessThanOrEqual(1024);
    expect(parsed.data.compatibility.length).toBeLessThanOrEqual(500);
    expect(parsed.data.license).toBe("MIT");
    expect(parsed.data.metadata.version).toBe(JSON.parse(fs.readFileSync(path.resolve(skillDir, "..", "..", "package.json"), "utf8")).version);
  });
  it("body stays under 400 lines and references shipped scripts only", () => {
    const lines = parsed.content.split("\n");
    expect(lines.length).toBeLessThan(400);
    const scripts = fs.readdirSync(path.join(skillDir, "scripts")).filter(f => f.endsWith(".py"));
    for (const m of parsed.content.matchAll(/scripts\/([a-z_]+\.py)/gu)) expect(scripts, m[1]).toContain(m[1]);
  });
});
```

- [ ] **Step 2: Run to verify failure**

Run: `npm test`
Expected: FAIL on the placeholder SKILL.md (description too short).

- [ ] **Step 3: Write SKILL.md**

```markdown
---
name: optical-design
description: >
  Optical design review, analysis and optimization: resolution limits, PSF/MTF, wavefront
  error, Zernike and Seidel aberrations, Strehl, depth of focus, Gaussian beams, tolerancing,
  merit-function design, and design guidance (audit a lens, flag its limitations, suggest and
  apply corrections, find comparable published or stock designs). Use when the user asks
  about lens or imaging system performance, wants a design reviewed or improved, works with
  OCT/microscopy/interferometer optics, Zemax OpticStudio files (.zmx) or ZOS-API, or wants
  numbers checked against diffraction limits — even if they do not name a tool.
license: MIT
compatibility: Requires Python 3.11+ and uv (scripts install their own dependencies on first run). Tier 1 needs optiland; Tier 2 needs Windows with Ansys Zemax OpticStudio Professional/Premium (ZOS-API).
metadata:
  author: Eric Tang
  repo: https://github.com/tangericm/optical-design
  version: "0.1.0-dev.0"
---

# optical-design

Act as a senior optical designer reviewing a colleague's system. Numbers come from the
scripts, never from memory. Every formula you quote names its source.

## Not for

Non-sequential or illumination design, stray light, thin-film coatings, opto-mechanics,
thermal analysis, and physics homework with no system behind it. Say so and stop.

## Modes

State the mode before answering.

| Mode | Use when | Output |
|---|---|---|
| Ask | conceptual or single-number question | formula, source, computed value |
| Analyze | a prescription or wavefront exists | performance table vs diffraction limit and vs spec |
| Audit | user wants review | ranked limitation flags with evidence |
| Improve | audit flags exist | ranked corrections with expected gain/cost, applied and re-verified |
| Research | user needs starting points or comparables | shortlist of designs with citations, imported and analyzed |

This release ships Tier 0 only (closed-form and wavefront math). Prescription analysis
(Tier 1), OpticStudio (Tier 2), audit/improve scripts and references arrive in later releases;
in Audit/Improve/Research modes use Tier 0 scripts for every number and state what could not
be computed.

## Preflight

1. `uv --version`. If missing, tell the user to install uv; do not pip-install into their environment.
2. Run scripts as `uv run <skill-dir>/scripts/<name>.py <subcommand> ... --json`. First run downloads dependencies.
3. Exit code 2 = usage (read `--help`), 3 = missing tier dependency (report the hint verbatim), 4 = analysis failed.

## Conventions

- Lengths in mm, wavelengths in µm (`--wavelength-um`), wavefront in waves at the stated wavelength.
- Zernike coefficients always carry a scheme: `fringe` (Zemax Fringe, unnormalized), `noll`
  (Zemax Standard, RMS-normalized), `ansi` (OSA/ANSI Z80.28, 0-based). Never mix schemes
  without `scripts/zernike.py convert`.
- NA ↔ F/#: paraxial `NA = 1/(2 F#)`. Say "paraxial" when you use it above NA ≈ 0.3.
- Report: quantity, value, unit, method/tier, and the limit it is compared to.

## Sanity rules

- Strehl and RMS wavefront error must agree with Maréchal (`S ≈ 1 − (2πσ)²`) when σ ≤ 0.1 waves. If not, the scheme or normalization radius is wrong.
- No MTF value exceeds the diffraction-limited curve. `wavefront.py mtf` overlays it.
- PSF and detector sampling: `Q = λF#/p`; Q < 2 aliases. Run `wavefront.py sample-check`.
- When geometric and diffraction numbers disagree, report both and say which governs.
- Diffraction limit is a floor, not a target: a design at the floor with no margin fails tolerancing.

## Scripts

| Script | Subcommands | Use for |
|---|---|---|
| `scripts/resolve.py` | airy, rayleigh, dof, gaussian, oct-axial, oct-lateral, micro, telescope | closed-form limits |
| `scripts/zernike.py` | convert, rms, strehl, seidel-from-zernike, fit | coefficient math |
| `scripts/wavefront.py` | psf, mtf, sample-check | diffraction from a wavefront |
| `scripts/interfero.py` | psi, unwrap, fringe-to-wfe, cavity | interferometer data |
| `scripts/compare.py` | (two JSON files) | before/after and cross-engine checks |

`--help` on any subcommand prints an example.

## Worked pattern

User: "Is my 0.8 NA objective at 520 nm sampled properly on a 6.5 µm camera at 40×?"

1. Mode: Ask. `resolve.py micro --wavelength-um 0.52 --na 0.8 --magnification 40 --pixel-um 6.5 --json`
2. Read `nyquist_pixel_um` and `sampling_ratio`; report Abbe/Rayleigh values with the method string.
3. If `warnings` lists "undersampled", say by how much and what magnification fixes it.

## Red flags

- "The diffraction limit is close enough" → run the script; quote the number and the margin.
- "The Zernike convention doesn't matter here" → it changes the value by up to √(2(n+1)); convert.
- "I'll estimate the PSF" → `wavefront.py psf`.
- "OpticStudio said so" → OpticStudio output still gets checked against `resolve.py` limits.
```

- [ ] **Step 4: Write the docs**

`docs/tiers.md`:
```markdown
# Compute tiers

| Tier | Needs | Scripts | Status |
|---|---|---|---|
| 0 | Python 3.11+, uv (numpy/scipy/scikit-image auto-installed) | resolve, zernike, wavefront, interfero, compare | shipped |
| 1 | optiland (auto-installed on first run) | trace | planned |
| 2 | Windows, Ansys Zemax OpticStudio Professional/Premium, ZOSPy | zos | planned |

## Script contract

- `uv run scripts/<name>.py <subcommand> [args] [--json]`
- JSON envelope: `{schema, tool, subcommand, tier, inputs, results, units, method, warnings}`
- Exit codes: 0 ok, 1 comparison failed (`compare.py` only), 2 usage, 3 missing tier dependency, 4 analysis failed
- No network calls at runtime; dependency download happens through uv on first run.
```

`docs/install.md`:
```markdown
# Install

Prerequisite for the scripts: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

| Client | Command or path |
|---|---|
| Any Agent Skills client | `npx skills add tangericm/optical-design` |
| Claude Code | `claude plugin marketplace add tangericm/optical-design` then `claude plugin install optical-design@optical-design` |
| Codex | copy `skills/optical-design` into `.agents/skills/` (project) or `~/.agents/skills/` |
| Cursor | copy into `.cursor/skills/` or install as a local plugin from `plugin.json` |
| Hermes | copy into `.hermes/skills/` or `~/.hermes/skills/` |
| OpenCode | copy into `.opencode/skills/` |
| npm | `npm install optical-design`; skill lives at `node_modules/optical-design/skills/optical-design` |

Verify: `uv run <skill-dir>/scripts/resolve.py airy --wavelength-um 0.55 --fnum 4`
```

`docs/compatibility.md`:
```markdown
# Compatibility

Claimed: any client that reads Agent Skills `SKILL.md` with the portable frontmatter fields.
Observed: none yet. Native install trials are recorded here per release, following the format
used by skillcrit (surface, evidence, boundary).

| Surface | Evidence | Boundary |
| --- | --- | --- |
| CI: Linux, macOS, Windows; Python 3.11 and 3.13 | pytest suites, `uv run` smoke test | Tests the scripts, not any agent client |
```

- [ ] **Step 5: Run tests**

Run: `npm test && npx skillcrit lint . --fail-on error`
Expected: vitest PASS (both files); skillcrit exits 0 or 1 (1 = warnings only; read them and fix anything at `error`).

- [ ] **Step 6: Commit**

```bash
git add skills/optical-design/SKILL.md docs tests/node/frontmatter.test.ts
git commit -m "docs: SKILL.md draft, tiers, install and compatibility docs"
```

---

### Task 12: CI workflow, PEP 723 smoke test, package verification, ruff

**Files:**
- Create: `.github/workflows/ci.yml`, `scripts/verify-package.mjs`, `tests/python/test_uv_scripts.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write the uv smoke test**

`tests/python/test_uv_scripts.py`:
```python
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
    result = subprocess.run(["uv", "run", str(SCRIPTS / script), *argv, "--json"], capture_output=True, text=True, timeout=600)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["schema"] == "1"


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
def test_usage_error_exits_2():
    result = subprocess.run(["uv", "run", str(SCRIPTS / "resolve.py"), "airy"], capture_output=True, text=True, timeout=600)
    assert result.returncode == 2
```

Run: `uv run pytest tests/python/test_uv_scripts.py -v`
Expected: PASS (5 tests; first run downloads numpy/scikit-image into uv's cache).

- [ ] **Step 2: Write `scripts/verify-package.mjs`**

```js
#!/usr/bin/env node
// Pack the tarball, install it into a throwaway consumer, assert the skill files arrive intact.
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const source = fileURLToPath(new URL("../", import.meta.url));
const npmCli = process.env.npm_execpath;
assert.ok(npmCli && fs.existsSync(npmCli), "Run with: npm run verify:package");
const root = fs.mkdtempSync(path.join(os.tmpdir(), "optical-design-package-"));
function run(cwd, args) {
  const r = spawnSync(process.execPath, args, { cwd, encoding: "utf8", timeout: 120_000 });
  assert.ifError(r.error);
  assert.equal(r.status, 0, r.stderr || r.stdout);
  return r.stdout;
}
try {
  const [pack] = JSON.parse(run(source, [npmCli, "pack", "--json", "--ignore-scripts", "--pack-destination", root]));
  const files = pack.files.map(f => f.path);
  for (const required of ["skills/optical-design/SKILL.md", "skills/optical-design/LICENSE",
    "skills/optical-design/scripts/_lib/cli.py", "skills/optical-design/scripts/resolve.py",
    "skills/optical-design/scripts/zernike.py", "skills/optical-design/scripts/wavefront.py",
    "skills/optical-design/scripts/interfero.py", "skills/optical-design/scripts/compare.py",
    "docs/tiers.md", "docs/install.md", "LICENSE", "README.md", "SECURITY.md"]) {
    assert.ok(files.includes(required), `Missing package file: ${required}`);
  }
  assert.ok(files.every(f => !/^(?:tests|node_modules|docs\/superpowers|docs\/research|\.github)\//u.test(f)), "Package contains local files");
  const consumer = path.join(root, "consumer");
  fs.mkdirSync(consumer);
  fs.writeFileSync(path.join(consumer, "package.json"), JSON.stringify({ name: "consumer", private: true }));
  run(consumer, [npmCli, "install", "--ignore-scripts", "--no-audit", "--no-fund", path.join(root, pack.filename)]);
  const skill = path.join(consumer, "node_modules", "optical-design", "skills", "optical-design", "SKILL.md");
  assert.ok(fs.readFileSync(skill, "utf8").startsWith("---\nname: optical-design"));
  console.log("verify-package: ok");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
```

Run: `npm run verify:package`
Expected: prints `verify-package: ok`.

- [ ] **Step 3: Write the CI workflow**

`.github/workflows/ci.yml`:
```yaml
name: ci

on:
  push:
    branches: [main, 'release/**']
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  python:
    name: python (${{ matrix.os }}, ${{ matrix.python }})
    runs-on: ${{ matrix.os }}
    timeout-minutes: 20
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.11", "3.13"]
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: ${{ matrix.python }}
      - run: uv sync
      - run: uv run ruff check skills tests
      - run: uv run pytest -m "not zos and not tier1" -q

  node:
    name: node packaging and skill lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: "22"
          cache: npm
      - run: npm ci
      - run: npm test
      - run: npm run verify:package
      - run: npx skillcrit lint . --fail-on error
```

- [ ] **Step 4: Run ruff locally and fix**

Run: `uv run ruff check skills tests`
Expected: clean. Fix any reported unused import or line-length issue in place.

- [ ] **Step 5: Update CHANGELOG and commit**

`CHANGELOG.md` → under Unreleased add `- CI on Linux/macOS/Windows, Python 3.11 and 3.13; npm package verification; skillcrit lint.`

```bash
git add .github scripts/verify-package.mjs tests/python/test_uv_scripts.py CHANGELOG.md
git commit -m "ci: python matrix, packaging verification, skill lint"
```

- [ ] **Step 6: Full local gate**

Run:
```bash
uv run pytest -q
npm test
npm run verify:package
npx skillcrit lint . --fail-on error
```
Expected: all green.

---

### Task 13: Publish the repository (requires user confirmation)

**Files:** none.

- [ ] **Step 1: Confirm with the user** that the repo may be created publicly on GitHub as `tangericm/optical-design` now (spec §1 names it; creating a public repo is outward-facing). Do not proceed without a yes.

- [ ] **Step 2: Create and push**

```bash
gh repo create tangericm/optical-design --public --source . --remote origin --description "Agent skill for optical design review, analysis and optimization, with Zemax OpticStudio interoperability." --push
```

- [ ] **Step 3: Verify CI**

Run: `gh run watch --exit-status` (or `gh run list --limit 1`)
Expected: `ci` workflow succeeds on all 7 jobs. If a matrix job fails, fix on `main` in a follow-up commit; do not disable the job.

---

## Self-review

**Spec coverage (phase 1 scope):** §4 layout → Tasks 1, 2, 11, 12. §5 frontmatter → Task 11 + frontmatter test. §6 SKILL.md sections 1–9 → Task 11 (draft; modes table present, script index limited to shipped scripts, red flags present). §8 contract, exit codes, PEP 723, `--help` examples → Tasks 2–10, 12 (uv smoke test). §8 Tier 0 script list: resolve (Tasks 3–4), zernike (6–7), wavefront (8), interfero (9), compare (10) — all subcommands from the spec table present. §10 tests: textbook pins (Airy 1.22λF#, Maréchal λ/14→0.80, Zernike round trips, RMS from coefficients, PSI recovers phase) → Tasks 3–9; node frontmatter/packaging tests → 1, 11; CI matrix → 12; `zos`/`tier1` markers defined → 2. §9 assets, §7 references, Tier 1/2, design.py, catalog.py, evals → later plans (roadmap README).

**Placeholder scan:** none; the one intentionally loose assertion in Task 9 has its exact replacement stated in the same task.

**Type consistency:** `Envelope(tool, subcommand, tier, inputs, results, units, method, warnings)` used identically in Tasks 3–10; `run_json(main, argv)` fixture appends `--json` and asserts exit 0 (compare.py's exit-1 case uses `run` instead); `coefficients_to_map`, `load_map`, `fit_map`, `rms_from_coeffs`, `_terms` defined in Task 6/7 and imported by Tasks 8/9 with the same names and signatures; `fourier.psf_from_wavefront` keys used in Task 8 match its definition.
