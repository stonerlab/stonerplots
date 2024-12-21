# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style."""
import matplotlib.pyplot as plt
from common import figures, model, pparam, x

from stonerplots import MultiPanel, SavedFigure

with SavedFigure(
    figures / "fig02h_{number}", style="stoner,thesis", formats="pdf,png", autoclose=__name__ != "__main__"
):
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
