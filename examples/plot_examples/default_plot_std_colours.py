# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style with standard colours."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import SavedFigure

with SavedFigure(figures / "fig04a.png", style=["stoner", "std-colours"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p)
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
