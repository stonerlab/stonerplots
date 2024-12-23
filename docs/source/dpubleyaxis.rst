DoubleYAxis Context Manager
----------------------------

.. currentmodule:: stonerplots.context

A double-y-axis plot is one where one dataset is plotted referenced to the y-axis on the left of the fram and a second
dataset is plotted against the y-axis on the right hand side of the frame. This works well when you want to show two
different parameters that are dependent on the same independent variable.

The :py:class:`DoubleYAxis` context manager adjust the current (or sepecified) set of axes and creates a second set
of axes that shares the same same x-axis. Be default it will also set the matplotlib current axes to be the new second
y-axis within the context manager and restore the original current axes on exit.

It offeres additional parameters to control the merging of legends between the two y-axes and to colour the y-axes
separately to help idenitfy which axis goes with whic data set.::

    with DoubleYAxis() as Y2:
        Y2.plot(...)

will create a new second y-axis on the right side of the current axes' plot frame, replacing the original axes
right ticks etc. After plotting using the `Y2` axes, the context manager will create a legend for both original and
second y-axis plots and look for the best place to put the combined legend.

Finally on exist, the original axes are set to be the current axes.

Legend Control
~~~~~~~~~~~~~~

There are two keyword parameters that affect the legend behaviour. `legend` is a boolea switch that if set to `False`
ensures the context manager takes no action over the legends. If set `True` then at exit, the context manager will
remove any existing legends from the two y-axes and create a new merged legend on the original (left) axes.

The location of the new legend can be controlled with the `loc` parameter. By default this has the value `"best"`. In
this case, a slightly modified version of the usual matplotlib automatic placement algorithm is run. The main
difference is that the contents of both sets of axes are considered in determining the best location.

Colouring the Axes
~~~~~~~~~~~~~~~~~~

The `colours` parameter is used to set the colour of the two y-axis spines, tick labels and axis labels. It can either
be a comma separated string of two named coours, or a 2 element list or tuple of colours for left and right axes. If
only element is supplied, is assumed to be the colour of the right hand axes. Values of `None` signal that the axis is
not to be coloured.

Other parameters
~~~~~~~~~~~~~~~~

The `ax` keyword parameter sets the parent axes to create the second y-axis on. The default `None` signals that the
current axes should be used.

The `switch_to_y2` parameter controls whether the current axes are set to the new second y-axis within the context
manager. The default, `True` switches the current axes cover for the duration of the context manager. This avoids the
need to explicitly use the context manager's variable.

Example
~~~~~~~

This illustrates the use of the :py:class:`DoubleYAxis` in conjunction with the :py:class:`SavedFigure` context
manager.::

    with SavedFigure("fig7d.png", style="stoner,med-res"):
        fig, ax = plt.subplots()

        # Do First (left hand y-axis) plot.
        for p in [10, 20, 50]:
            ax.plot(x, model(x, p), label=p, marker="")
        ax.legend(title="Order", fontsize=6, ncols=2)

        # Now do plotting of second (right) y axis.
        with DoubleYAxis(colours="central,piccadilly"):
            for p in [10, 20, 50]:
                plt.plot(x, np.abs(model(x, p) - 0.5), "--", label=f"$|{p}|$")
            plt.ylabel("2$^\\mathrm{nd}$ Harmonic")

.. image:: ../../examples/figures/fig7c.png
  :alt: 2x2 multi-panel plot.
  :align: center