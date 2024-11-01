# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and InsetPlot context manager."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import InsetPlot, SavedFigure

with SavedFigure(figures / "fig07a.png", style=["stoner"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 10, 20, 38, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order", fontsize=7)
    ax.set(**pparam)
    with InsetPlot(loc="lower right") as inset:
        inset.plot(x[::10], model(x[::10], 200), linestyle="", marker=".")
