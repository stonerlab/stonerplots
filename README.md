[![GitHub version](https://badge.fury.io/gh/stonerlab%2Fstonerplots.svg)](https://badge.fury.io/gh/stonerlab%2Fstonerplots)
[![PyPI version](https://badge.fury.io/py/StonerPlots.svg)](https://badge.fury.io/py/StonerPlots)
[![Build Docs](https://github.com/stonerlab/stonerplots/actions/workflows/publish_sphinx.yaml/badge.svg)](https://stonerlab.github.io/stonerplots/)
[![Conda](https://github.com/stonerlab/stonerplots/actions/workflows/build_conda.yaml/badge.svg?branch=main)](https://github.com/stonerlab/stonerplots/actions/workflows/build_conda.yaml)
![Conda Version](https://anaconda.org/phygbu/stonerplots/badges/version.svg)
![Not platform specific](https://anaconda.org/phygbu/stonerplots/badges/platforms.svg)
![MIT Licensed](https://anaconda.org/phygbu/stonerplots/badges/license.svg)


Stoner Plots
=============

Stoner Plots is a fork of Science Plots

<img src="https://raw.githubusercontent.com/stonerlab/stonerplots/main/examples/figures/fig05a.png" width=640 alt="Presentation Style Image"/>

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


Documentation
-------------

Documentation can be found on the [github pages for this repository](https://stonerlab.github.io/stonerplots/index.html).

Available Styles
----------------

 * stoner - this is the base style sheet
 * poster - makes everything bigger for printing on a poster
 * notebook - makes things a little bigger for a Jupyter notebook - from the original scienceplots package
 * presentation - a style suitable for the main graph on a powerpoint slide

Journal Styles
--------------

 * nature - for Nature group journals - from the original scienceplots package
 * ieee - for IEEE Transactions journals - from the original scienceplots package
 * aps - for American Physical Society Journals (like Phys Rev Lett etc.)
 * aip - for AIP journals such as Applied Physics Letters - labels in Serif Fonts
 * iop - for Institute of Physics Journals.

Modifiers
---------

 * aps1.5 - Switch to 1.5 column wide format
 * aps2.0 - Switch to 2 column wide format
 * aip2 - Switch to 2 column wide format for AIP journals
 * stoner-dark - Switch to a dark background a lighter plotting colours.
 * hi-res - Switches to 600dpi plotting (but using eps, pdf or svg is generally a better option)
 * presentation_sm - a style for making 1/2 width graphs.
 * presentation_dark - tweak the weight of elements for dark presnetations.

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

The package adds these as named colours in matplotlib, along with 90,50,70 and 10% shade variants of some of them. See
the [documentation page on colours](https://stonerlab.github.io/stonerplots/colours.html) for a full list.

This package draws heavily on [scienceplots](https://github.com/garrettj403/SciencePlots), so it seems only fair to cite the original work....

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
