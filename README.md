[![GitHub version](https://badge.fury.io/gh/stonerlab%2Fstonerplots.svg)](https://badge.fury.io/gh/stonerlab%2Fstonerplots)
[![PyPI version](https://badge.fury.io/py/StonerPlots.svg)](https://badge.fury.io/py/StonerPlots)
![Conda Version](https://anaconda.org/phygbu/stonerplots/badges/version.svg)
![Not platform specific](https://anaconda.org/phygbu/stonerplots/badges/platforms.svg)
![MIT Licensed](https://anaconda.org/phygbu/stonerplots/badges/license.svg)


Stoner Plots
=============

Stoner Plots is a fork of Science Plots

<img src="https://raw.githubusercontent.com/stonerlab/stonerplots/main/examples/figures/fig15.png" width=640 alt="Presentation Style Image"/>

Usage
-----

Before using the new styles you need to import stonerplots - but it's ok to just import e.g. the SavedFigure context
manager:

    from stonerplots import SavedFigure

    with SavedFigure("my_figure.pdf", style=["stoner","aps"]):
        plt.figure()
        plt.plot(x,y,label="Dataset")
        ...

The SavedFigure context manager will handle the call to the matplotlib style context manager and will also save any
figures opened within the context manager. If the filename for the figure has an embedded place holder for {ix}, then
multiple figures can be saved without clobbering the filename.

There is also an InsetPlot context manager that can help you get insets placed correctly so that axes
labels don't escape over the edge of the surrounding figure.

    with SavedFigure("my_figure.pdf", style=["stoner","aps"]):
        plt.figure()
        plt.plot(x,y,label="Dataset")
        ...
        with InsetPlot(loc="lower right", width=0.25, height=0.25, padding=0.05) as inset:
            inset.plot(x, model(x, 200), linestyle="--")


Available Styles
----------------

 * stoner - this is the base style sheet
 * poster - makes everything bigger for printing on a poster
 * notebook - makes things a little bigger for a Jupyter notebook - from the original scienceplots package
 * presentation - a style suitable for the main graph on a powerpoint slide
 * presentation_sm - a style for making 1/2 width graphs.

Journal Styles
--------------

 * nature - for Nature group journals - from the original scienceplots package
 * ieee - for IEEE Transactions journals - from the original scienceplots package
 * aps - for American Physical Society Journals (like Phys Rev Lett etc.)
 * aip - for AIP journals such as Applied Physics Letters - labels in Serif Fonts

Modifiers
---------

 * aps1.5 - Switch to 1.5 column format
 * aps2.0 - Switch to 2 column format
 * hi-res - Switches to 600dpi plotting (but using eps, pdf or svg is generally a better option)

Colour Cycles
-------------

The default colour cycle is based on the London Underground map colour scheme (why not?) and goes

 * Northern
 * Central
 * Picadily
 * District
 * Metropolitan
 * Bakerloo
 * Jubilee
 * Overground
 * Victoria
 * Elizabeth
 * Circle


This package draws heavily on scienceplots, so it seems only fair to cite the original work....

    @article{StonerPlots,
      author       = {John D. Garrett},
      title        = {{garrettj403/SciencePlots}},
      month        = sep,
      year         = 2021,
      publisher    = {Zenodo},
      version      = {1.0.9},
      doi          = {10.5281/zenodo.4106649},
      url          = {http://doi.org/10.5281/zenodo.4106649}
    }
