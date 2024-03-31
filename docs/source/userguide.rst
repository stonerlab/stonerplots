Stoner Plots User Guide
=======================

Although you can make use of the style sheets directly in matplotlib after impriting stonerplots, it is anticipated
that using the :doc:`stonerplots<api>` context managers will be the main way of using the package.

The look of the various stylesheets is demonstrated in the :doc:`style gallery<style-gallery>` page.

Context Managers Primer
-----------------------

In Python, a context manager is used in a `with ... :` statement. Its main advantage is that it ensures that
initialisiation and cleanup code are executed around the enclosed block of statements, no matter why the code block
exited (e.g. due to an Exception or due to normal termination). This is generally used to ensure resources, such as
open network conenctions, open files etc. are opened and cleaned up properly.

The other reason a context manager might be used, is to temporarily change something in the environment the code is
running in for the duration of the enclosed lines of code. Matplotlib offers context managers that operate in this way
to temporarily set default parameters (:py:func:`matplotlib.pyplot.rc_context`) or to temporarily apply stylesheets
(py:func:`matplotlib.style.context`).

.. currentmodule:: stonerplots.context

SavedFigure Context Manager
---------------------------

The  :py:class:`SavedFigure` is used to bpth apply style sheets and capture the current figure and save it to disk.
It applies stylesheets by wrapping a :py:func:`matplotlib.style.context` context manager. On entry, the context manager
will note the open matplotlib figures, and on exit it will compare the list of copen figures with those that existed at
entry, and save all the new figures. Therefore, it is very important that figure creation is done **inside** the
:py:class:`SavedFigure` context manager.

Simple Example
~~~~~~~~~~~~~~

In its simplest form, :py:class:`SavedFigure` just needs to know a filename to save the figure as::

    with SavedFigure("example.png"):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

In this case, the stylesheet is switched to the default "stoner" style, the format to save the file in is determined
from the filename to be a PNG file, and the open figure will be saved to the current working directory as
"example.png". The figure that was created will be left open at the end of the run.

If you don't specify a filename, then :py:class:`SavedFigure` will look for a label for your figures (set with
:py:meth:`matplotlib.figure.Figure.set_label`).

Applying Styles
~~~~~~~~~~~~~~~

To apply one or more stylesheets to the :py:class:`SavedFigure`, just pass them as the keyword parameter *stle*::

    with SavedFigure("example.png", style=["stoner","nature"]):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

Alternatively, if you want to stop :py:class:`SavedFigure` from messing with the existing style parameters, pass False to *style*::

    with SavedFigure("example.png", style=False):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

This will suppress the encapsulated :py:func:`matplotlib.style.context` context manager being used.

Automatically Closing the Plot Figures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have saved your figures to disk, you probably don't want to leave them open as eventually matplotlib will
complain about the number of open figures. :py:class:`SavedFigure` has an *autoclose* parameter that will close all the figures
that it has saved for you::

    with SavedFigure("example.png", autoclose=True):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

Setting the Format of the Saved Figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Matplotlib has the ability to save figures in a variety of different formats. For scientific writing, one often wants
to save in a vector format, such as encapsulated postscript (eps), scalable vector graphics (svg), or portable document
format (pdf). However, when the graphics are to be used in a PowerPoint presentation (or poster), a bitmapped image
format such as Portable Network Graphics (png) is easiest to work with.

.. warning::
    JPEG encoding is not a good choice to use due to the image artefacts it introduces. JPEG uses a wavelet encoding
    algorithm to achieve high levels of image compression. Whilst this often works well for photographs, it handles
    sharp changes in contrast rather poorly and produces often very visible artefacts at such features. Unfortunately,
    scientic plots have lots of such features - axes lines, data lins, axes labels etc. and as a result JPEG encoded
    plots do not reproduce well and should be avoided.

The :py:class:`SavedFigure` context manager lets you specify the figure format(s) to use via the the *formats* parameter. This can
be either a single string representing the desired file extension, or a list of such file extensions.  In this latter
case, :py:class:`SavedFigure` will save multiple copies of the same figure in the different format. This can be helpful if, e.g.
you need eps formats for a LaTeX document, but also want png images to check the figures look ok.::

    with SavedFigure("example", formats=["png","pdf"]):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)


If you don't specify a format and the figure's filename has an extension, that is used for the format. Otherwise it
defaults to 'png'. If the figure filename has an extension *and* you sepcify a format, then the extension is strippled
and the correct extension for the format is used.

The choice of formats is determined by :py:func:`matplotlib.pyplot.savefig`.

Multiple Figures and SavedFigure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you create multiple figures within a :py:class:`SavedFigure` context manager, it will attempt to save all of yor figures. In
this case it is rpobably desirable to set how each figure should be named. You can do this by providing a pattern
within the figure filename. The number of the figure being saved is substituted into a placeholder in the filename
string like so::

    with SavedFigure("example_{int}", formats=["png","pdf"]):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)
       fig, ax = plt.subplots()
       ax.plot(x_data2, y_data2)

This will then result in example_0.png and example_1.png, with the "{int}" placeholder being replaced with 0,1,2...

As well as the `int` placehold you can also use:

    - `alpha` or `Alpha` for lower and upper case letters (starting from `a`|)
    - `roman` or `Roman` for lower or upper case Roman numberals (starting from 'i'!)

Including Already Open Figures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default :py:class:`SavedFigure` will ignore all already open figures. If you want to use the :py:class:`SavedFigure` machinery to save
figures with adjsuted filenames and in different formats, then you can pass it the *include_open* parameter set to True
and if will not ignore the already opened figures when saving. Note, however, it is **not** possible to retrospectively
style figures, so already open figures will be saved with their existing formatting.::

    with SavedFigure("Figure-{int}", formats=["eps","png"],
                                            include_open=True):
        pass

Will save all of your figures as Figure-0.eps, Figure-0.png, Figure-1.eps, Figure-1.png... in one go.


InsetPlot Context Manager
-------------------------

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


StackVertical Context Manager
-----------------------------

When comparing several quantities that have a common independent variable, using a sequence of vertically stacked plots
can be effective. Typically each sub-plot is positioned so that the top x-axis of one panel is the bottom x-axis of the
one above, and only the bottom x-axis of the whole stack is labelled and.

Although matplotlib's builtin features to make multiple plots on a grid have been improved in recent releases, it is
still quite complex and getting the plots to be adjacent, whilst also not having the labels etc clash is challenging.
:py:class:`StackVertical` is a context manager designed to make this a bit easier.::

    with StackVertical(3) as axes:
        for ax,y in zip(axes, [y_data1, y_data2, y_data3]):
            ax.plot(x, y)

The only required parameter to :py:class:`StackVertical` is the number of plots to stack vertically. It then returns a list of the
:py:class:`matplotlib.axes.Axes` for each subplot - the first set of axes being the top plot and the last being the
bottom.

When the context manager exits, it adjusts the y-axis limits to ensure the tick markers do not interfere and reduces
the spacing between the plots to zero so that they are adjacent.

Adjusting the Figure Size for the Stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BY default :py:class:`StackVertical` will look at the current figure to work out its dimensions and will then assume that this is
the correct size for a single plot. It will then adjust the figure height to accommodate the additional stacked plots.
The equation used for this is:

.. math::
   h_{new} = h_{old} (f h_{old} (N_{plots}-1)+1)

with :math:`f` being a fraction of the old plot size set by the *adjust_figsize* parameter to :py:class:`StackVertical`.
If this is left at the default value of `True`, then :math:`f` is set to 0.6 and to 0 if *adjust_figsize* is `False`.

Typically stacked plots have a bigger aspect ratio (width:height) than a single plot.::

    with StackVertical(3, adjust_figsize=0.5) as axes:
        for ax,y in zip(axes, [y_data1, y_data2, y_data3]):
            ax.plot(x, y)

Setting Common (Shared) axes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default :py:class:`StackVertical` will set the x-axis to be shared between all the plots and the y-axis of each plot to be
independent. The *sharex* and *sharey* parameters control this. When the plots are adjacent it probably doesn't make
sense to not share the x-axis though!::

    with StackVertical(3, sharey=True) as axes:
        for ax,y in zip(axes, [y_data1, y_data2, y_data3]):
            ax.plot(x, y)

Labelling the Panels
~~~~~~~~~~~~~~~~~~~~

A common requirement of a multi-panel figure is to label the individual sets of axes (a), (b)... or similar. This is
supported by the *label_panels* parameter. If this takes the value `True` then each set of axes is labelled '(a)',
'(b)' and so on. For added control, the parameter can also take a string with a similar format to that used in
:py:class:`SavedFigure` above. Placeholders such as {Alpha} or {roman} can be used and will give the axes number.::

    with StackVertical(3, label_panels=True) as axes:
        for ax,y in zip(axes, [y_data1, y_data2, y_data3]):
            ax.plot(x, y)

Some journals, e.g. Science, also want the label to be in bold font, and :py:class:`StackVertical` supports passing the font...
jeyword arguments to control the font size and appearance.::

    with StackVertical(3, label_panels='{Alpha}', fontweight='bold') as axes:
        for ax,y in zip(axes, [y_data1, y_data2, y_data3]):
            ax.plot(x, y)


Specifying a Figure
~~~~~~~~~~~~~~~~~~~

The default is to use the current matplotlib figure, but by passing the *figure* parameter into the :py:class:`StackVertical`
context manager it will use that figure instead.::

    with StackVertical(3, figure=2) as axes:
        for ax,y in zip(axes, [y_data1, y_data2, y_data3]):
            ax.plot(x, y)

The *figure* parameter can be either a :py:class:`matplotlib.figure.Figure` or a figure number or figure label. Within
the context manager, the current figure is set to be figure specified by the *figure* parameter. The previously active
figure is reset as active when the context manager exits.

Not Joining the Plots
~~~~~~~~~~~~~~~~~~~~~

Although it is envisaged that the main use of the :py:class:`StackVertical` context manager is to make plots with shared x-axes and
sitting adjacent to each other, setting the *joined* parameter to `False` will stop the post-plotting re-sizing and
adjustment of the y-limits and therefore set the plots as separate enties.::

    with StackVertical(3, joined=False) as axes:
        for ax,y in zip(axes, [y_data1, y_data2, y_data3]):
            ax.plot(x, y)

MultiPanel Context Manager
--------------------------

Another common requirement when writing papers and theses is to create a figure with several distinct panels shwing
different (related) datasets. In this case, the :py:class:`MultiPanel` context manager works in a very analogous way to the
:py:class:`StackVertical` context manager.::

    with MultiPanel((2,2)) as axes:
    for ax,x,y in zip (axes,[x1,x2,x3,x4],[y1,y2,y3,y4]):
        ax.plot(x,y)

The only required parameter is the number of panels to show. This can be either a tuple of (n_rows,n_cols) or an
integer specifying a number of columns (number of rows is assumed to be one in this case.)

Optional Parameters
~~~~~~~~~~~~~~~~~~~

The *figure*, *sharex*, *sharey* and *label_panels* work exactly as for the :py:class:`StackVertical` Context manager
described above, except that the default is not to share any axes.

The *adjust_figsize* parameter lets you specify a tuple to give different expansion factors for width and height. The
default value is to expand the width by exactly the number of columns and the height by the height of one row + 80% of
additional rows. Since full-page width figures are more than double a single column, it may be useful to do something
like:

    with SavedFigure("example.png",stle=["stoner","aip","aip2"]):
        with MultiPanel((2,2),adjust_figsize=(0,0.12)) as axes:
            for ax,x,y in zip (axes,[x1,x2,x3,x4],[y1,y2,y3,y4]):
                ax.plot(x,y)

To make a genuinely full width x 2 single plots high figure.
