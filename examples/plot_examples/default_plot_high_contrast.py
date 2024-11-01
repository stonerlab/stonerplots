# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style with high-contrast colour scheme."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import SavedFigure

with SavedFigure(figures / "fig04c.png", style=["stoner", "high-contrast"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p)
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
