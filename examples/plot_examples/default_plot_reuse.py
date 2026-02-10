# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import SavedFigure

with SavedFigure(figures / "fig01e_1.png", style=["stoner"], autoclose=False):
    fig, ax = plt.subplots()
    for p in [10, 15, 20]:
        ax.plot(x, model(x, p), label=p, marker="")

for p in [30, 50, 100]:
    name = figures / "fig01e_2.png" if p == 100 else False
    # This time we use SavedFigure inside a loop - but using *use* to always add to the same figure.
    with SavedFigure(name, style=["stoner"], autoclose=p == 100 and __name__ != "__main__", use=fig):
        ax = fig.gca()
        ax.plot(x, model(x, p), label=p, marker="")
        if p == 100:  # last time
            ax.legend(title="Order")
            ax.set(**pparam)
            ax.autoscale(tight=True)
