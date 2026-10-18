"""Offset paired measurements and fits on linear and logarithmic axes."""

import matplotlib.pyplot as plt
import numpy as np
from common import figures

from stonerplots import OffsetPlots, SavedFigure

x = np.linspace(-3, 3, 100)
sample = np.arange(0, len(x), 8)

with SavedFigure(figures / "offset_plots.png", style="stoner", autoclose=__name__ != "__main__"):
    with OffsetPlots(offset=1.5, factor=10):
        fig, (linear, logarithmic, errors) = plt.subplots(1, 3, figsize=(12, 4))
        logarithmic.set_yscale("log")
        for index, width in enumerate((0.7, 0.9, 1.1)):
            y = 0.1 + np.exp(-((x / width) ** 2))
            for ax in (linear, logarithmic):
                line = ax.plot(x, y, label=f"Dataset {index + 1}")[0]
                ax.scatter(x[sample], y[sample], s=8, color=line.get_color())
            errors.errorbar(x[sample], y[sample], yerr=0.08, fmt="o-", capsize=3, markersize=3)
        for ax in (linear, logarithmic, errors):
            ax.set_xlabel("x")
            ax.set_ylabel("Signal (offset)")
        linear.set_title("Additive offsets")
        logarithmic.set_title("Multiplicative offsets")
        errors.set_title("Complete error-bar plots")
