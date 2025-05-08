SavedFigure Context Manager
============================

.. currentmodule:: stonerplots.context.save_figure

The :py:class:`SavedFigure` is used to apply stylesheets, capture the current figure, and save it to disk. It applies
stylesheets by wrapping a :py:func:`matplotlib.style.context` context manager around the code. On entry, the context
manager will note the open matplotlib figures, and on exit it will compare the list of open figures with those that
existed at entry, and save all the new figures. Therefore, it is very important that figure creation is done **inside**
the :py:class:`SavedFigure` context manager.

Simple Example
--------------

In its simplest form, :py:class:`SavedFigure` just needs to know a filename to save the figure as::

    with SavedFigure("example.png"):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

In this case, the stylesheet is switched to the default "stoner" style. The format to save the file is determined from
the filename, resulting in a PNG file. The open figure will then be saved to the current working directory as
"example.png". The figure that was created will be left open at the end of the run.

If you don't specify a filename, then :py:class:`SavedFigure` will look for a label for your figures (set with
:py:meth:`matplotlib.figure.Figure.set_label`).

Applying Styles
---------------

To apply one or more stylesheets to the :py:class:`SavedFigure`, just pass them as the keyword parameter *style*::

    with SavedFigure("example.png", style=["stoner", "nature"]):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

Multiple stylesheets may also be expressed as a single string containing comma separated values.::

    with SavedFigure("example.png", style="stoner,nature"):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

Alternatively, if you want to stop :py:class:`SavedFigure` from altering the existing style parameters, pass False to
*style*::

    with SavedFigure("example.png", style=False):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

This will suppress the encapsulated :py:func:`matplotlib.style.context` context manager from being used.

Automatically Closing the Plot Figures
--------------------------------------

Once you have saved your figures to disk, you may not want to leave them open, as eventually Matplotlib will complain
about the number of open figures. The :py:class:`SavedFigure` class has an *autoclose* parameter that will close all the
figures that it has saved for you::

    with SavedFigure("example.png", autoclose=True):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

Setting the Format of the Saved Figure
--------------------------------------

Matplotlib supports saving figures in a variety of formats. In scientific writing, vector formats are often preferred,
such as encapsulated postscript (eps), scalable vector graphics (svg), or portable document format (pdf). However, when
the graphics are to be used in a PowerPoint presentation (or poster), a bitmapped image format such as Portable Network
Graphics (png) is easiest to work with.

.. warning::
    JPEG encoding is not a good choice to use due to the image artefacts it introduces. JPEG uses wavelet encoding to
    achieve high compression levels. Whilst effective for photographs, it handles sharp changes in contrast poorly,
    often producing visible artefacts. Unfortunately, scientific plots have lots of such features - axes lines, data
    lines, axes labels etc. As a result, JPEG-encoded plots do not reproduce well and should therefore be avoided.

The :py:class:`SavedFigure` context manager lets you specify the figure format(s) to use via the *formats* parameter.
This can be either a single string representing the desired file extension, or a list of such file extensions. In this
latter case, :py:class:`SavedFigure` will save multiple copies of the same figure in the different formats. This can be
helpful if, e.g. you need eps formats for a LaTeX document, but also want png images to check the figures look ok::

    with SavedFigure("example", formats=["png", "pdf"]):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

As with stylesheets, multiple formats can be expressed as a single string of comma separated values:

    with SavedFigure("example", formats="png,pdf"):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

If you don't specify a format and the figure's filename has an extension, that is used for the format. Otherwise it
defaults to 'png'. If the figure filename has an extension *and* you specify a format, then the extension is stripped
and the correct extension for the format is used.

The choice of formats is determined by :py:func:`matplotlib.pyplot.savefig` - you can get a list of supported formats
by doing::

    supported_formats = plt.gcf().canvas.get_supported_filetypes()
    print(supported_formats)

Typically this gives:

- `eps`: Encapsulated Postscript,
- `jpg`: Joint Photographic Experts Group,
- `jpeg`: Joint Photographic Experts Group,
- `pdf`: Portable Document Format,
- `pgf`: PGF code for LaTeX,
- `png`: Portable Network Graphics,
- `ps`: Postscript,
- `raw`: Raw RGBA bitmap,
- `rgba`: Raw RGBA bitmap,
- `svg`: Scalable Vector Graphics,
- `svgz`: Scalable Vector Graphics,
- `tif`: Tagged Image File Format,
- `tiff`: Tagged Image File Format,
- `webp`: WebP Image Format

Not Saving the figure
---------------------

This might seem a little counter intuitive, but in some scenarios you might want to be able to apply the style sheets
but not immediately save the figure. By setting the filename arameter to *False* you can skip actually writing the file
to disk. This can be a useful option when you also want to contnue plotting and then saving a figure elsewhere and so
want to ensure the style is used consistently.  See the section `Adding to an already existing figure`.

Overriding individual settings
------------------------------

Sometimes you might want to tweak a style sheet setting or other Matplotlib rcParams value for a single plot. The
keyword *extra* argument to :py:class:`SavedFigure` lets you do this. It takes a dictionary of rcParam name and value
pairs and embeds a call to :py:func:`matplotlib.rc_context` into the :py:class:`SavedFigure` call.::

    with SavedFigure(
        figures / "fig01d.png",
        style=["stoner"],
        extra={"lines.linestyle": "--"}
    ):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)

A KeyError exception will be raised if any of the supplied keys to the *extra* dictionary are not valid Matplotlib
rcParam names.

Multiple Figures and SavedFigure
--------------------------------

If you create multiple figures within a :py:class:`SavedFigure` context manager, it will attempt to save all of your
figures. In this case, it may be desirable to set how each figure should be named. You can do this by providing a
pattern within the figure filename. The number of the figure being saved is substituted into a placeholder in the
filename string like so::

    with SavedFigure("example_{int}", formats=["png", "pdf"]):
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)
        fig, ax = plt.subplots()
        ax.plot(x_data2, y_data2)

This will then result in example_0.png and example_1.png, with the "{int}" placeholder being replaced with 0, 1, 2...

As well as the `int` placeholder you can also use:

- `alpha` or `Alpha` for lower and upper case letters (starting from `a`)
- `roman` or `Roman` for lower or upper case Roman numerals (starting from 'i')

Including Already Open Figures
------------------------------

By default :py:class:`SavedFigure` will ignore all already open figures. If you want to use the :py:class:`SavedFigure`
machinery to save figures with adjusted filenames and in different formats, then you can pass it the *include_open*
parameter set to True and it will not ignore the already opened figures when saving. Note, however, it is **not**
possible to retrospectively style figures, so already open figures will be saved with their existing formatting::

    with SavedFigure("Figure-{int}", formats=["eps", "png"], include_open=True):
        pass

This will save all of your figures as Figure-0.eps, Figure-0.png, Figure-1.eps, Figure-1.png... in one go.

Adding to an already existing figure
-------------------------------------

If you have already started a figure and want to be able to add to it and then save the figure, you can do this by
using the *use* parameter. This is particularly useful in conjunction with providing *False* to the filename.::

    with SavedFigure(False,style="stoner", autoclose=False):
        fig,ax = plt.subplot()
        ... # plot stuff with fig

    # Do other stuff and then come back to the figure

    with SavedFigure("figure.png",style="stoner", use=fig)
        ... # more plotting

    #fig now saved here.

An evemt more compact form can be used by utilising the re-use of the context manager like so::

    resumed_plotting = SavedFigure(False,format="png", style="stoner", autoclose=False)

    with resumed_plotting():
        fig,ax=plt.subplot()
        ... # plotting

    # Do other stuff and then come back to the figure

    with resumed_plotting(use=fig):
        ... # Do more plotting

    # Do other stuff and then come back to the figure

    with resumed_plotting("figure", autoclose=True):
        ... # Final plotting and then save

This approach has the advantage that the format and style are setup just once and so are consistent between
reinvocations of the context manager.

Setting Default Values
----------------------

If you are making a lot of figures with similar stylesheet, formats and filename patterns, it can be tedious to keep
on typing them for each :py:class:`SavedFigure`. One option is to set default values once and have
:py:class:`SavedFigure` use them each time. You can do this using the :py:attr:`stonerplots.default` settings.::

    from stonerplots import SavedFigure, default

    default.style="stoner, med-res"
    default.formats="svg"
    default.filename="default"

    with SavedFigure():
        ...

:py:attr:`stonerplots.default` is a global setting so once set it will apply to all future instances of SavedFigure -
not just the ones in the current function or module. If you need to keep settings, but with more control over the
scaope, then the reuse of the :py:class:`SavedFigure` is going to be the better option.

Reusing the Context Manager
---------------------------

If you are using the same settings in SavedFigure context managers over and over again, but setting a global default
is not useful, then you might want to reuse the context manager::

    cm = SavedFigure(figures / "fig_{label}.png", style=["stoner"])

    with cm:  # first figure
        plt.figure("one")
        ...

    # figures/fig_one.png saved.
    with cm:  # second figure
        plt.figure("two")
        ...

    # figures/fig_two.png saved.

One trick being used here is to use a placeholder for the filename - 'fig_{label}.png' - when it comes time to save the
figure, the figure label is stored in the variable *label* (and the figure number is stored in *number*) and can then
be substituted into the filename. The other end of the process is that when we create the figure with `plt.figure()` we
give the figure a label or name.

Doing this allows you to change, for example, the style in one place and have all of your figures change over. The
downside is that once you set the context manager up, that's it. Except, it isn't... you can also call the context
manager to adjust the settings::

    cm = SavedFigure(figures / "fig_{label}.png", style=["stoner"])

    with cm:  # first figure
        plt.figure("one")
        ...
    # figures/fig_one.png saved.
    cm(filename=figures / "new_{label}", formats="pdf")
    with cm:  # second figure
        plt.figure("two")
        ...
    # figures/new_two.pdf saved
