# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import SavedFigure, default

default.formats = "svg"
default.style = "stoner,med-res"
default.filename = figures / "defaults"

with SavedFigure(autoclose=__name__ != "__main__"):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
