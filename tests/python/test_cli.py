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
