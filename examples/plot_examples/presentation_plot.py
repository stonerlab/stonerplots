# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and presentation format."""
import matplotlib.pyplot as plt

from stonerplots import SavedFigure

from common import x, model, pparam, figures

with SavedFigure(figures / "fig05c.png", style=["stoner", "presentation"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        line = ax.plot(x, model(x, p), label=p, marker="")
        ax.plot(x[::5], model(x[::5], p), label=None, c=line[0].get_color(), linestyle="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
