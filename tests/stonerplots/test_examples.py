# test_spam.py

import pathlib
import runpy
import shutil
import sys

import pytest

srcpath = pathlib.Path(__file__).parent.parent.parent / "src"
srcpath = str(srcpath.absolute())
if srcpath not in sys.path:
    sys.path.insert(0, srcpath)

import stonerplots

scriptpath = pathlib.Path(stonerplots.__file__).parent.parent.parent / "examples" / "plot_examples"
scripts = [str(x) for x in scriptpath.resolve().glob("*.py") if not x.stem.startswith("_")]

if str(scriptpath) not in sys.path:
    sys.path.insert(0, str(scriptpath))


def is_latex_available():
    """
    Check if LaTeX is installed and available.

    Returns:
        (bool): True if latex executable is found, False otherwise.
    """
    return shutil.which("latex") is not None


# Scripts that require LaTeX to run
LATEX_REQUIRED_SCRIPTS = ["default_plot_latex.py", "scatter_plot.py"]


@pytest.mark.parametrize("script", scripts)
def test_script_execution(script):
    script_name = pathlib.Path(script).name
    if script_name in LATEX_REQUIRED_SCRIPTS and not is_latex_available():
        pytest.skip("LaTeX is not installed")
    runpy.run_path(script)


if __name__ == "__main__":
    pytest.main(["--pdb", __file__])
