InsetPlot Context Manager
-------------------------

.. currentmodule:: stonerplots.context

Inset plots, where a second set of axes are included within the main axes of a figure, are often used to show either a
detail of the main figure, or possibly an overview or a related dataset. Unfortunately, generating insets with
matplotlib can be somewhat tricky, as the standard tools to set up and position the inset plot often require additional work to
avoid the inset axes clashing with the main axes.


StonerPlot's `InsetPlot` context manager is designed to make this easier by tweaking the placement of the
inset. It is a wrapper around :py:func:`axes.Axes.inset_axes` with additional logic to
adjust the position of the inset.::

    with InsetPlot() as inset:
        inset.plot(x, y)

will create an inset that is then automatically placed in the best location within the current axes and occupies
33% of the axes horizontally and vertically. By default the context manager also manipulates the
the `matplotlib.pyplot`'s current axes, so that inside the context manager, the current axes are the inset plot
and afterwards, they are restored to the original active axes.

Controlling the Inset Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The context manager takes a *loc* parameter that defines the location of the inset. These take the same value as for
`matplotlib.pyplot.legend` (For convenience, any hyphens in the location string are replaced with spaces, and
everything is lower-cased).::

    with InsetPlot(loc="lower right") as inset:
        inset.plot(x, y)

Adjusting the Inset Size
~~~~~~~~~~~~~~~~~~~~~~~~

The *width*, *height* and *dimension* parameters control the size of the inset axes (not this does not include any axes
labels, tick markers, etc.). *width* and *height* are floating-point numbers. If *dimension* is "fraction" (the default),
then these floating-point numbers represent the fraction of the parent axes' size occupied by the inset axes. Thus,
the default values are 0.33, or 33%. If *dimension* is not "fraction," then the units for *width* and *height* are

    with InsetPlot(width=1.1, height=0.7, dimension="inches") as inset:
        inset.plot(x, y)


Control of Axes and Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the parent axes are considered the current axes from the current figure, but the *ax* parameter to the

    with InsetPlot(ax=plt.figure(2).gca()) as inset:
        inset.plot(x, y)

As noted above, by default the context manager switches the current axes around so that Pyplot functions will work on

the inset inside the context manager.::

    plt.plot(x_main,y_main)
    with InsetPlot():  # Ignore the context manager's return value
        plt.plot(x_inset,y_inset)  # On the inset axes
    plt.xlabel("Main X") # Back on the main axes again
    plt.ylabel("Main Y")

Multiple Insets
~~~~~~~~~~~~~~~

The automatic placement of insets considers both the main axes' legend and other insets, and it will attempt to locate
the second inset in the best remaining location.::

    plt.plot(x_main,y_main)
    with InsetPlot() as inset_1:
        inset_1.plot(x_inset_1,y_inset_1)
    with InsetPlot() as inset_2:
        inset_2.plot(x_inset_2,y_inset_2)



