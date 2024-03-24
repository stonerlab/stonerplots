# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""
import weakref
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import stonerplots

__all__ = ["SavedFigure"]


class SavedFigure(object):

    """Context manager that applies a style and saves figures.

    Keyword Arguments:
        filename (str, Path, default=None):
            The filename to use for saving the figure created. If None then the figure's label is used as a
            filename.
        style (str, List[str], default is ['science','nature','vibrant']):
            The mnatplotlib syslesheet(s) to use for plotting.
        autoclose (bool, default=False):
            Automatically close figures after they are saved. This leaves open figures that were open before we
            started,

    This wraps the mpl.style.context() context manager and also determines what new figures have been created and
    saves them with a soecified filename.
    """

    def __init__(self, filename=None, style=None, autoclose=False):
        """Create the context manager.

        Keyword Arguments:
            filename (str, Path, default=None):
                The filename to use for saving the figure created. If None then the figure's label is used as a
                filename.
            style (str, List[str], default is ['science','nature','vibrant']):
                The mnatplotlib syslesheet(s) to use for plotting.
            autoclose (bool, default=False):
                Automatically close figures after they are saved. This leaves open figures that were open before we
                started,
        """
        self.filename = filename
        if style is None:
            self.style = ["science", "nature", "vibrant"]
        else:
            self.style = style
        self.autoclose = autoclose
        self.style_context = None
        self.open_figs = []

    def __enter__(self):
        """Record the open figures and start the style context manager.

        Creates a list of weak references to all the open figures. This is then used to detect whether an open figure
        has been created within the context manager or not. We use weak references to allow figures to be closed
        without blocking.
        """
        for num in plt.get_fignums():
            self.open_figs.append(weakref.ref(plt.figure(num)))
        self.style_context = mpl.style.context(self.style)
        self.style_context.__enter__()

    def __exit__(self, type, value, traceback):
        """Cleanup context manager and save figures created.

        First call the __exit__ of the style context manager to finish of plotting with the specified stylesheet, then
        cjeck all the open figures and if they were not in our list of figures open before, save them with a filename
        from the keyword parameter to __init__ or the plot label.
        """
        self.style_context.__exit__(type, value, traceback)
        self.open_figs = [x() for x in self.open_figs if x() is not None]
        processed = -1
        for num in plt.get_fignums():
            if (fig := plt.figure(num)) not in self.open_figs:  # new figure
                processed += 1
                title = self.filename if self.filename is not None else fig.get_label()
                title = str(title).format(fighum=num, ix=processed)
                fig.savefig(title)
                if self.autoclose:
                    plt.close(num)


if __name__ == "__main__":
    with SavedFigure("test-{ix}.pdf", autoclose=True):
        plt.figure()
        x = np.linspace(0, 6, 200)
        y = np.sinc(x) ** 2
        plt.plot(x, y, "+")
        plt.xlabel("Test")
        plt.figure()
        plt.plot(x, y**2, "+")
        plt.yscale("log")
        plt.ylim(1e-9, 1)
        plt.xlabel("Test")
