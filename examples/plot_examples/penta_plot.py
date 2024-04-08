# -*- coding: utf-8 -*-
"""Use stonerplots to create a 3 panel; (1+2) plot."""

import matplotlib.pyplot as plt
import numpy as np
from stonerplots import SavedFigure, MultiPanel
from common import x, figures, model, pparam

autoclose=__name__!="__main__"

with SavedFigure(figures / "pentaplot.png", style="stoner,aaas-science", autoclose=autoclose):
    fig = plt.figure("penta-plot")
    with MultiPanel([2, 3], adjust_figsize=True) as axes:
        for ix, ax in enumerate(axes):
            for p in [10, 30, 100]:
                plt.plot(x, model(x, p + 5 * ix), label=p + 5 * ix, marker="")
            plt.legend(title="Order", loc="lower right")
            ax.set(**pparam)
