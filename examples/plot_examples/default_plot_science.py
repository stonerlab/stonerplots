# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style in Nature format."""
import matplotlib.pyplot as plt

from stonerplots import SavedFigure

from common import x, model, pparam, figures

with SavedFigure(figures / "fig02i_1.png", style=["stoner", "aaas-science"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig02i_2.png", style=["stoner", "aaas-science", "science-2col"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig02i_3.png", style=["stoner", "aaas-science", "science-3col"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
