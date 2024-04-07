# -*- coding: utf-8 -*-
"""Use stonerplots to create a 3 panel; (1+2) plot."""

import matplotlib.pyplot as plt
import numpy as np
from stonerplots import SavedFigure, MultiPanel
from common import x, figures, model, pparam

with SavedFigure(figures / "trriplot.png", style="stoner,thesis", autoclose=True):
    fig = plt.figure("tri-plot")
    with MultiPanel((2, 2), nplots=[2, 1], adjust_figsize=False) as axes:
        for ix, ax in enumerate(axes):
            for p in [10, 30, 100]:
                plt.plot(x, model(x, p + 5 * ix), label=p + 5 * ix, marker="")
            plt.legend(title="Order")
            ax.set(**pparam)
