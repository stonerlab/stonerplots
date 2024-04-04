SavedFigure Context Manager
---------------------------

.. currentmodule:: stonerplots.context


The  :py:class:`SavedFigure` is used to both apply style sheets and capture the current figure and save it to disk.
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

Reusing the Context Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using the same settings in SavedFigure context managers over and over again, then you might want to reuse
the context manager.::

    cm=SavedFigure(figures/"fig_{label}.png", style=["stoner"])

    with cm: # first figure
        plt.figure("one")
        ...

    # figures/fig_one.png saved.
    with cm: # second figure
        plt.figure("two")
        ...

    # figures/fig_two.png saved

One trick being used here is to use a placeholder for the filename - 'fig_{label}.png' - when it comes time to save the
figure, the figure label is stored in the variable *label* (and the figure number is stored in *number*) and can then
be substituted into the filename. The other end of the process is that when we create the figure with `plt.figure()` we
give the figure a label or name.

Doin this allows you to change, for example, the style in one place and have all of your figures change over. The
downside is that once you set the context manager up, that's it. Exc ept, it isn't.... you can also call the context
manager to adjust the settings.::

    cm=SavedFigure(figures/"fig_{label}.png", style=["stoner"])

    with cm: # first figure
        plt.figure("one")
        ...
    # figures/fig_one.png saved.
    cm(filename=figures/"new_{label}", formats="pdf")
    with cm: # second figure
        plt.figure("two")
        ...
    # figures/new_two.pdf saved
