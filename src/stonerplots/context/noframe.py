# -*- coding: utf-8 -*-
"""Context manager for central (i.e. non-framed) figures."""

from matplotlib import pyplot as plt

from .base import PreserveFigureMixin, TrackNewFiguresAndAxes

__all__ = ["CentredAxes"]


class CentredAxes(TrackNewFiguresAndAxes, PreserveFigureMixin):
    """Remove the plot frame from all enclosed figures and move the axes to specified x,y values.

    Keyword Args:
        x (float, default 0):
            x co-ordinate of the vertical (y) axis.
        y (float, default 0):
            y co-ordinate of the horizontal (x) axis.
        include_open (bool):
            If `True`, any figures opened before entering the context are included for adjusting. Default is `False`.
        use (Figure):
            If set, use this matplotlib figure in the context hander. This is useful in a situation where one partially
            plots a figure, then run some other code outside the context handler and finally return and finish plotting
            the figure.
    """

    def __init__(self, x=0.0, y=0.0, include_open=False, use=None):
        """Initialise context manager with default settings."""
        super().__init__(include_open=include_open)
        self.use = use
        self.x = x
        self.y = y

    def __call__(self, x=None, y=None, include_open=None, use=None):
        """Update settings dynamically and return self."""
        self.x = self.x if x is None else x
        self.y = self.y if y is None else y
        self.include_open = self.include_open if include_open is None else include_open
        self.use = self.use if use is None else use
        return self

    def __enter__(self):
        """Record existing open figures and enter style context (if any)."""
        super().__enter__()
        if self.use:  # Set the current figure to be that given by use.
            plt.figure(getattr(self.use, "number", None))

    def __exit__(self, exc_type, exc_value, traceback):
        """Adjust all the figure axes."""
        super().__exit__(exc_type, exc_value, traceback)
        for ax in self.new_axes:
            # Ensure (self.x,self.y) is inside the visible range
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            if not xlim[0] <= self.x <= xlim[1]:
                ax.set_xlim(min(xlim[0], self.x), max(xlim[1], self.x))
            if not ylim[0] <= self.y <= ylim[1]:
                ax.set_ylim(min(ylim[0], self.y), max(ylim[1], self.y))

            # Move spines to the origin
            ax.spines["left"].set_position(("data", self.x))
            ax.spines["bottom"].set_position(("data", self.y))

            # Hide the top and right spines (removes the "frame" look)
            ax.spines["right"].set_color("none")
            ax.spines["top"].set_color("none")

            # Put ticks/labels only on the axes that remain visible
            ax.xaxis.set_ticks_position("bottom")
            ax.yaxis.set_ticks_position("left")

            # Place axis labels below (x) and to the left (y)
            label = ax.xaxis.get_label()
            ax.set_xlabel(label.get_text(), loc="right")
            ax.xaxis.set_label_position("bottom")

            label = ax.yaxis.get_label()
            ax.set_ylabel(label.get_text(), loc="top")
            ax.yaxis.set_label_position("left")

            # Move tick labels slightly away from the origin for clarity
            ax.set_xticks([x for x in ax.get_xticks() if x != self.x])
            ax.set_yticks([y for y in ax.get_yticks() if y != self.y])

            ax.tick_params(axis="both", which="both", direction="out", pad=6)
