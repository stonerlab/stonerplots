# -*- coding: utf-8 -*-
"""Demonstrate the PlotLabeller context manager and TexEngFormatter."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import PlotLabeller
from stonerplots import SavedFigure

with SavedFigure(figures / "fig01c.png", style=["stoner"], autoclose=__name__ != "__main__"), PlotLabeller():
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x * 1e5, model(x, p) * 1e-6, label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    pparam.update({"xlabel": "Voltage (V)", "ylabel": "Current (A)"})
    ax.set(**pparam)
