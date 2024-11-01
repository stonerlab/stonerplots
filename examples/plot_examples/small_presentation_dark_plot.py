# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and smaller size presentation format."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import SavedFigure

with SavedFigure(
    figures / "fig05e.png",
    style=["stoner", "stoner_dark", "presentation", "presentation_sm", "presentation_dark"],
    autoclose=True,
):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        line = ax.plot(x, model(x, p), label=p, marker="")
        ax.plot(x[::5], model(x[::5], p), label=None, c=line[0].get_color(), linestyle="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
