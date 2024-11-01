"""Run all the plot examples by importing the plot_examples package."""

import os
from pathlib import Path
import sys

pth = str(Path(__file__).parent)
if pth not in sys.path:
    sys.path.insert(0, pth)
pth = str(Path(__file__).parent.parent / "src")
if pth not in sys.path:
    sys.path.insert(0, pth)

os.chdir("plot_examples")

from plot_examples import *  # NOQA

os.chdir("..")
