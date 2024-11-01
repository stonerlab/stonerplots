# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and InsetPlot context manager."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import SavedFigure
from stonerplots import StackVertical

with SavedFigure(figures / "fig7b.png", style=["stoner"], autoclose=__name__ != "__main__"):
    fig = plt.figure()
    fig.set_figheight(fig.get_figheight() * 0.6)
    with StackVertical(3) as axes:
        for ix, ax in enumerate(axes):
            for p in [10, 30, 100]:
                ax.plot(x, model(x, p + ix * 5), label=p + ix * 5, marker="")
            ax.legend(title="Order", loc="lower right")
            ax.set(**pparam)
