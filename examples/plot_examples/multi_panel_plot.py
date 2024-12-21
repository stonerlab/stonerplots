# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and InsetPlot context manager."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import MultiPanel, SavedFigure

with SavedFigure(figures / "fig7c.png", style=["stoner", "iop"], autoclose=__name__ != "__main__"):
    fig = plt.figure()
    with MultiPanel((2, 2)) as axes:
        for ix, ax in enumerate(axes):
            for p in [10, 30, 100]:
                ax.plot(x, model(x, p + ix * 5), label=p + ix * 5, marker="")
            ax.legend(title="Order", loc="lower right")
            ax.set(**pparam)
