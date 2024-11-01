# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and InsetPlot context manager."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import InsetPlot
from stonerplots import SavedFigure

with SavedFigure(figures / "fig07a.png", style=["stoner"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 10, 20, 38, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order", fontsize=7)
    ax.set(**pparam)
    with InsetPlot(loc="lower right") as inset:
        inset.plot(x[::10], model(x[::10], 200), linestyle="", marker=".")
