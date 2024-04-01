# -*- coding: utf-8 -*-
"""Demonstrate the SavedFigure context manager and Scatter Plot settings."""
import matplotlib.pyplot as plt
import numpy as np

from stonerplots import SavedFigure

from common import figures

with SavedFigure(figures / "fig03.png", style=["stoner", "scatter", "latex"], autoclose=True):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.plot([-2, 2], [-2, 2], "k--")
    ax.fill_between([-2, 2], [-2.2, 1.8], [-1.8, 2.2], color="dodgerblue", alpha=0.2, lw=0)
    for i in range(7):
        x1 = np.random.normal(0, 0.5, 10)
        y1 = x1 + np.random.normal(0, 0.2, 10)
        ax.plot(x1, y1, label=r"$^\#${}".format(i + 1))
    lgd = r"$\mathring{P}=\begin{cases}1 \mathrm{if \nu\geq0}\\0 \mathrm{if \nu<0}\end{cases}$"
    ax.legend(title=lgd, loc=2, ncol=2)
    xlbl = r"$\log_{10}\left(\frac{L_\mathrm{IR}}{\mathrm{L}_\odot}\right)$"
    ylbl = r"$\log_{10}\left(\frac{L_\ast}{\mathrm{L}_\odot}\right)$"
    ax.set_xlabel(xlbl)
    ax.set_ylabel(ylbl)
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
