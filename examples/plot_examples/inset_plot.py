# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and InsetPlot context manager."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import InsetPlot
from stonerplots import SavedFigure

with SavedFigure(figures / "fig07a.png", style="stoner, thesis", autoclose=__name__ != "__main__"):
    fig, ax = plt.subplots()
    for p in [5, 10, 20, 38, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.set(**pparam)
    ax.legend(title="Order", fontsize=7)
    with InsetPlot(loc="best", height=0.4, padding=(0.02, 0.01)) as inset:
        inset.scatter(x[::8], model(x[::8], 200), c="district")
        plt.xlabel("Time")
        plt.ylabel("Signal")
    with InsetPlot(loc="best") as inset:
        inset.scatter(x[::10], model(x[::10], 300), c="district")
        inset.set_label("Inset 2")
