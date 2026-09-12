import argparse
import io
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


def test_fail_writes_error_and_exits_with_the_given_code(capsys):
    with pytest.raises(SystemExit) as e:
        cli.fail("map has no valid samples", cli.EXIT_ANALYSIS)
    assert e.value.code == cli.EXIT_ANALYSIS
    err = capsys.readouterr().err
    assert err.startswith("error:") and "map has no valid samples" in err


def test_require_returns_module():
    assert cli.require("json", "") is json


def test_human_output_survives_cp1252_stream():
    raw = io.BytesIO()
    out = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    env = cli.Envelope(tool="demo", subcommand="x", tier=0, inputs={}, results={"r": 1.0},
                       units={"r": "waves"}, method="λ ≈ √2 − π")
    cli.emit(env, as_json=False, out=out)
    out.flush()
    text = raw.getvalue().decode("cp1252")
    assert "method:" in text and "r" in text and "waves" in text


def test_emit_refuses_non_finite_numbers():
    env = cli.Envelope(tool="demo", subcommand="x", tier=0, inputs={},
                       results={"r": float("inf")}, units={}, method="test")
    with pytest.raises(ValueError):
        cli.emit(env, as_json=True, out=io.StringIO())


def test_run_maps_a_non_finite_result_to_exit_4_not_2(run):
    """A ValueError from json.dumps(allow_nan=False) inside emit() is an analysis failure
    (the arguments were fine, the computed result wasn't), not a usage error."""
    def build_parser():
        common = cli.common_parser()
        parser = argparse.ArgumentParser(prog="demo")
        subs = parser.add_subparsers(dest="subcommand", required=True)
        sub = subs.add_parser("go", parents=[common])

        def cmd(_sub, _args):
            return cli.Envelope(tool="demo", subcommand="go", tier=0, inputs={},
                                results={"r": float("inf")}, units={}, method="test")

        sub.set_defaults(func=cmd, sub=sub)
        return parser

    def main(argv):
        return cli.run(build_parser, argv)

    code, _out, err = run(main, ["go", "--json"])
    assert code == cli.EXIT_ANALYSIS
    assert err.startswith("error:")
