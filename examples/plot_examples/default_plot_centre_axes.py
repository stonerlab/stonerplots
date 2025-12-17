# -*- coding: utf-8 -*-
"""Demonstrate the CentredAxes context manager for frameless plots with central axes."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import SavedFigure, CentredAxes

with SavedFigure(figures / "fig01g.png", style=["stoner"], autoclose=__name__ != "__main__"):
    with CentredAxes():
        fig, ax = plt.subplots()
        for p in [10, 15, 20, 30, 50, 100]:
            ax.plot(x-1, model(x, p)-0.6, label=p, marker="")
        ax.legend(title="Order", fontsize="small")
        ax.autoscale(tight=True)
        ax.set(**pparam)
