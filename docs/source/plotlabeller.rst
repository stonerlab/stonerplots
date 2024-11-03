PlotLabeller Context Manager
============================

.. currentmodule:: stonerplots.format

The purpose of :py:class:`PlotLabeller` is to assist with setting tick label locators and formatters consistently for
multiple plots. This helps to ensure that your lots maintain a common formatting look and in conjunction with the
Loy:class:`TexEngFormatter` class, that axes tick labels do not have excessive digits for lare or small numbers.

In its simplest form, :py:class:`PlotLabeller` will simply apply the :py:class:`TexEngFormatter` tick label formatter
to all the axes of any plots created within the context manager. If the minor tick formatter is set to NullFormatter,
this is respected and the minor tick labels are left unset.

You can pass optional parameters *x*,*y* and *z* to the :py:class:`PlotLabeller` which contain either:

    * A subclass of :py:class:`matplotlib.ticker.Formatter` or :py:class:`matplotlib.ticker.Locator`
    * An instance of either :py:class:`matplotlib.ticker.Formatter` or :py:class:`matplotlib.ticker.Locator`
    * A list or tuple of either of the above. This allows both a locator and a formatter to be specified for
      the corresponding axes within one :py:class:`PlotLabeller` context manager.

To use :py:class:`PlotLabeller`, you would typically just stack it with SavedFigure.::

    with (SavedFigure(figures / "fig01c.png", style=["stoner"], autoclose=__name__!="__main__"),
          PlotLabeller()):
        fig, ax = plt.subplots()
        for p in [10, 15, 20, 30, 50, 100]:
            ax.plot(x*1E5, model(x, p)*1E-6, label=p, marker="")
        ax.legend(title="Order")
        ax.autoscale(tight=True)
        ax.set(**pparam)

This will give a plot somewhat like:

.. image:: ../../examples/figures/fig01c.png
  :alt: A plot with the x and y tick labels formatted in engineering style with si prefixes.
  :align: center