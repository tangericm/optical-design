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
