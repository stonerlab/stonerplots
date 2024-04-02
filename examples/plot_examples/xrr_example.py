# -*- coding: utf-8 -*-
"""Setting up a StackVertical Context Manager for GenX."""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from stonerplots import SavedFigure, StackVertical

from common import figures  # Just for the figures path

# Prepare data assuming a GenX data export format of x,I_s,I_m,e
data = np.genfromtxt(Path(__file__).parent.parent / "data" / "xrr.dat")
x = data[:, 0]
simulated = data[:, 1]
measured = data[:, 2]
fom = np.log10(measured) - np.log10(simulated)

# Set up the scales, labels etc for the two panels.
main_props = {"ylabel": "Counts", "yscale": "log","ylim":(10,5E6)}
residual_poprs = {"xlabel": r"2$\theta (^\circ)$", "ylabel": "FOM"}

# This is stonerplots context managers at work
with SavedFigure(figures / "genx_plot.png", style=["stoner", "presentation"], autoclose=True):
    plt.figure()
    with StackVertical(2, adjust_figsize=False, height_ratios=[3, 1]) as axes:
        main, residual = axes
        main.plot(x, measured, linestyle="", marker=".", label="Data", c="victoria")
        main.plot(x, simulated, marker="", label="Fit", c="central")
        main.set(**main_props)
        main.legend()
        residual.plot(x, fom, marker="", c="central")
        residual.set(**residual_poprs)
