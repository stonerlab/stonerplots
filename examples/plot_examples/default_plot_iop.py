# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style in IOP format."""
import matplotlib.pyplot as plt

from stonerplots import SavedFigure

from common import x, model, pparam, figures

with SavedFigure(figures / "fig02d.png", style=["stoner", "iop"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
