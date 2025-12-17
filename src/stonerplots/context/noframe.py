# -*- coding: utf-8 -*-
"""Context manager for central (i.e. non-framed) figures."""
from .base import PreserveFigureMixin, TrackNewFiguresAndAxes

__all__=["CentredAxes"]

class CentredAxes(TrackNewFiguresAndAxes,PreserveFigureMixin):

    """Remove the plot frame from all enclosed figures and move the axes to specified x,y values.

    Keyword Args:
        x (float, default 0):
            x co-ordinate of the vertical (y) axis.
        y (float, default 0):
            y co=ordinate of the horizontal (x) axis.
        include_open (bool):
            If `True`, any figures opened before entering the context are included for adjusting. Default is `False`.
        use (Figure):
            If set, use this matplotlib figure in the context hander. This is useful in a situation where one partially
            plots a figure, then run some other code outside the context handler and finally return and finish plotting
            the figure.
        """

    def __init__(self,x=0., y=0., include_open=False,use=None):
        """Initialise context manager with default settings."""
        super().__init__(include_open=include_open)
        self.use = use
        self.x=x
        self.y=y

    # __enter__ is entirely inherited

    def __exit__(self, exc_type, exc_value, traceback):
        """Adjust allt he figure axes."""
        for ax in self.axes():

            # Ensure (self.x,self.y) is inside the visible range
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            if not xlim[0] <= self.x <= xlim[1]:
                ax.set_xlim(min(xlim[0], self.x), max(xlim[1], self.x))
            if not ylim[0] <= self.y <= ylim[1]:
                ax.set_ylim(min(ylim[0], self.y), max(ylim[1], self.y))

            # Move spines to the origin
            ax.spines['left'].set_position(('data', self.x))
            ax.spines['bottom'].set_position(('data', self.y))

            # Hide the top and right spines (removes the "frame" look)
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')

            # Put ticks/labels only on the axes that remain visible
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

            # Place axis labels below (x) and to the left (y)
            ax.xaxis.set_label_position('bottom')
            ax.yaxis.set_label_position('left')

            # Move tick labels slightly away from the origin for clarity
            ax.tick_params(axis='both', which='both', direction='out', pad=6)

            # Use annotations to add arrows to the axes.
            arrowprops={"arrowstyle":'->', "color":ax.spines['bottom'].get_edgecolor()}
            ax.annotate('', xy=(self.x, ax.get_ylim()[1]), xytext=(self.x, ax.get_ylim()[0]),
                        arrowprops=arrowprops)
            arrowprops={"arrowstyle":'->', "color":ax.spines['left'].get_edgecolor()}
            ax.annotate('', xy=(ax.get_xlim()[1], self.y), xytext=(ax.get_xlim()[0], self.y),
                        arrowprops=arrowprops)
