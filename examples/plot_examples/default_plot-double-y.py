# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and default Stoner plot style."""
import matplotlib.pyplot as plt
import numpy as np
from common import figures, model, pparam, x

from stonerplots import SavedFigure, DoubleYAxis

with SavedFigure(figures / "fig7d.png", style="stoner,med-res", autoclose=__name__ != "__main__"):
    fig, ax = plt.subplots()

    # Do First (left hand y-axis) plot.
    for p in [10, 20, 50]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order", fontsize=6, ncols=2)

    # Now do plotting of second (right) y axis.
    with DoubleYAxis(colours="central,piccadilly") as ax2:
        for p in [10, 20, 50]:
            plt.plot(x, np.abs(model(x, p) - 0.5), "--", label=f"$|{p}|$")
        plt.ylabel("2$^\\mathrm{nd}$ Harmonic")
        ax2.autoscale(tight=True)
    ax.autoscale(tight=True)
    ax.set(**pparam)
