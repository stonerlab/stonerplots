# -*- coding: utf-8 -*-
"""Demonstrate using SavedFigure as a callable, re-usable context manager."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import SavedFigure

resumed_plotting = SavedFigure(False, formats="png", style="stoner", autoclose=False)

with resumed_plotting():
    fig, ax = plt.subplots()
    for p in [10, 15]:
        ax.plot(x, model(x, p), label=p, marker="")

# Do other stuff and then come back to the figure
...

with resumed_plotting(use=fig):
    for p in [20, 30]:
        ax.plot(x, model(x, p), label=p, marker="")

# Do other stuff and then come back to the figure
...

name = figures / "fig01f.png"
with resumed_plotting(name, autoclose=__name__ != "__main__"):
    for p in [50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.set(**pparam)
    ax.autoscale(tight=True)
