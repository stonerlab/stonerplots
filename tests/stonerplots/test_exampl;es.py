# test_spam.py

import pathlib
import runpy
import pytest
import sys

srcpath = pathlib.Path(__file__).parent.parent.parent / "src"
srcpath = str(srcpath.absolute())
if srcpath not in sys.path:
    sys.path.insert(0, srcpath)

import stonerplots

scriptpath = pathlib.Path(stonerplots.__file__).parent.parent.parent / "examples" / "plot_examples"
scripts = [str(x) for x in scriptpath.resolve().glob("*.py") if not x.stem.startswith("_")]

if str(scriptpath) not in sys.path:
    sys.path.insert(0, str(scriptpath))


@pytest.mark.parametrize("script", scripts)
def test_script_execution(script):
    runpy.run_path(script)


if __name__ == "__main__":
    pytest.main(["--pdb", __file__])
