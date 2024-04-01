# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and InsetPlot context manager."""
import matplotlib.pyplot as plt

from stonerplots import SavedFigure, MultiPanel

from common import x, model, pparam, figures

with SavedFigure(figures / "fig7c.png", style=["stoner","iop"], autoclose=True):
    fig = plt.figure()
    with MultiPanel((2,2)) as axes:
        for ix, ax in enumerate(axes):
            for p in [10, 30, 100]:
                ax.plot(x, model(x, p + ix * 5), label=p + ix * 5, marker="")
            ax.legend(title="Order", loc="lower right")
            ax.set(**pparam)
