"""Shared script contract (design spec section 8): every subcommand has --help with an example."""
import compare
import interfero
import pytest
import resolve
import wavefront
import zernike

SUBCOMMANDS = [
    (resolve, ["airy", "rayleigh", "dof", "telescope", "gaussian", "oct-axial", "oct-lateral", "micro"]),
    (zernike, ["convert", "rms", "strehl", "seidel-from-zernike", "fit"]),
    (wavefront, ["psf", "mtf", "sample-check"]),
    (interfero, ["psi", "unwrap", "fringe-to-wfe", "cavity"]),
]
CASES = [(module.main, [sub, "--help"], f"{module.TOOL}.py {sub}")
         for module, subs in SUBCOMMANDS for sub in subs]
CASES.append((compare.main, ["--help"], "compare.py"))


@pytest.mark.parametrize("main,argv", [(m, a) for m, a, _ in CASES], ids=[i for _, _, i in CASES])
def test_help_prints_an_example(run, main, argv):
    code, out, _ = run(main, argv)
    assert code == 0
    assert "example" in out.lower()
