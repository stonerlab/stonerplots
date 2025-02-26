# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""

__all__ = ["SavedFigure", "InsetPlot", "DoubleYAxis", "StackVertical", "MultiPanel"]

from .double_y import DoubleYAxis
from .inset_plot import InsetPlot
from .multiple_plot import MultiPanel, StackVertical
from .save_figure import SavedFigure
