# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style."""
from common import figures
from common import model
from common import pparam
from common import x
import matplotlib.pyplot as plt

from stonerplots import MultiPanel
from stonerplots import SavedFigure

with SavedFigure(figures / "fig02h_{int}", style="stoner,thesis", formats="pdf,png", autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)
    ax.set_box_aspect(0.75)
    fig = plt.figure()
    with MultiPanel(2, adjust_figsize=(0, -0.25)) as axes:
        for ix, ax in enumerate(axes):
            for p in [10, 15, 20, 30, 50, 100]:
                ax.plot(x, model(x, p + 2 * ix), label=p + 2 * ix, marker="")
            ax.legend(title="Order")
            ax.autoscale(tight=True)
            ax.set(**pparam)
