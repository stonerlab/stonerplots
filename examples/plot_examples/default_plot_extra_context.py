# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x
from matplotlib.style import context

from stonerplots import SavedFigure

with SavedFigure(figures / "fig01a.png", style=["stoner"], autoclose=__name__ != "__main__"):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    with context({"font.size": 8}):
        ax.text(1.0, 0.3, "Annotation")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
