# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""

__all__ = ["SavedFigure", "InsetPlot", "DoubleYAxis", "StackVertical", "MultiPanel", "CentredAxes", "OffsetPlots"]

from .double_y import DoubleYAxis
from .inset_plot import InsetPlot
from .multiple_plot import MultiPanel, StackVertical
from .noframe import CentredAxes
from .offset import OffsetPlots
from .save_figure import SavedFigure
