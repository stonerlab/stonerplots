InsetPlot Context Manager
-------------------------

.. currentmodule:: stonerplots.context


Inset plots, where a second set of axes are included within the main axes of a figure, are often used to show either a
detail of the main figure, or possibly an overview or a related dataset. Unfortunately, generating insets with
matplotlib can be a little tricky as the stadnard tools to setup and position the inset plot can need a bit of work to
avoid the inset axes clashing with the primary axes.

Stonerplot's :py:class:`InsetPlot` context manager is designed to make this easier by tweakign the placement of the
inset. It is a wrapper around :py:func:`mpl_toolkits.axes_grid1.inset_locator.inset_axes` with additional logic to
adjust the position of the inset.::

    with InsetPlot() as inset:
        inset.plot(x, y)

will create an inset that is placed int he upper-left corner of te current axes and occupies 25% of the axes
horizontally and vertically. By default the context manager also manipulates the :py:mod:`matplotlib.pyplot`'s
current axes so that inside the context manager the current axes are the inset plot and afterwards they are restored to
the originally active axes.

Controlling Inset Location
~~~~~~~~~~~~~~~~~~~~~~~~~~

The context anager takes a *loc* parameter that defines the location of the inset. These take the same value as for
:py:func:`matplotlib.pyplot.legend` - except there is no 'auto' setting. (For convenience any hyphens in the location
string are replaced with spaces and everything is lower-cased).::

    with InsetPlot(loc="lower right") as inset:
        inset.plot(x, y)

Setting the Inset Size
~~~~~~~~~~~~~~~~~~~~~~

The *width*, *height* and *dimension* parameters control the size of the inset axes (not this does not include any axes
labels, tick markers etc.). *width* and *height* are floating point numbers, if *dimension* is "fraction" (the default)
then these floating point numbers represent the fraction of the parent axes size to take up with the inset axes. Thus,
the default values are 0.25, or 25%.  If *dimension* is not "fraction" then the units for *width* and *height* are
inches.::

    with InsetPlot(width=1.1, height=0.7, dimension="inches") as inset:
        inset.plot(x, y)


Control of Axes
~~~~~~~~~~~~~~~

By default, the parent axes are taken to be the current axes from the current figure, but the *ax* parameter to the
Context Manager can override this.::

    with InsetPlot(ax=plt.foigure(2).gca()) as inset:
        inset.plot(x, y)

As noted above, be default the context manager switches the current axes around so that pyplot functions will work on
the inset inside the context manager.::

    plt.plot(x_main,y_main)
    with InsetPlot():  # Ignore the context manager's return value
        plt.plot(x_inset,y_inset)  # On the inset axes
    plt.xlabel("Main X") # Back on the main axes again
    plt.ylabel("Main Y")
