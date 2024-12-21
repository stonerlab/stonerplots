# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and notebook format."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import SavedFigure

with SavedFigure(figures / "fig05a.png", style=["stoner", "notebook"], autoclose=__name__ != "__main__"):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
