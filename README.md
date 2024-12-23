[![GitHub version](https://badge.fury.io/gh/stonerlab%2Fstonerplots.svg)](https://badge.fury.io/gh/stonerlab%2Fstonerplots)
[![pytest](https://github.com/stonerlab/stonerplots/actions/workflows/pytest.yaml/badge.svg)](https://github.com/stonerlab/stonerplots/actions/workflows/pytest.yaml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/bc7404ac3cbf432184a13b6c3cb88ea4)](https://app.codacy.com/gh/stonerlab/stonerplots/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![PyPI version](https://badge.fury.io/py/StonerPlots.svg)](https://badge.fury.io/py/StonerPlots)
[![Build Docs](https://github.com/stonerlab/stonerplots/actions/workflows/publish_sphinx.yaml/badge.svg)](https://stonerlab.github.io/stonerplots/)
[![Conda](https://github.com/stonerlab/stonerplots/actions/workflows/build_conda.yaml/badge.svg)](https://github.com/stonerlab/stonerplots/actions/workflows/build_conda.yaml)
[![Conda Version](https://anaconda.org/phygbu/stonerplots/badges/version.svg)](https://anaconda.org/phygbu/stonerplots)
![Not platform specific](https://anaconda.org/phygbu/stonerplots/badges/platforms.svg)
![MIT Licensed](https://anaconda.org/phygbu/stonerplots/badges/license.svg)
[![DOI](https://zenodo.org/badge/776970304.svg)](https://zenodo.org/doi/10.5281/zenodo.10905673)

# Stoner Plots

Stoner Plots is a fork of Science Plots with additional features to make plotting of scientific plots easier.

<img src="https://raw.githubusercontent.com/stonerlab/stonerplots/main/examples/figures/fig05a.png" width=640 alt="Presentation Style Image"/>

## Usage

Before using the new styles you need to import stonerplots - but you will most likely also want to make use of
one of the context managers - the `SavedFigure` class.

    from stonerplots import SavedFigure

    with SavedFigure("my_figure.pdf", style=["stoner","aps"]):
        plt.figure()
        plt.plot(x,y,label="Dataset")
        ...

There are three main parts to this package::

1. A set of matplotlib style sheets for making lots wih styles suitable for a variety of Physics related journals
   and formats such as presentations and posters as well as reports and theses.

1. A set of Python Content managers designed to help with the process of preparing production quality figures in
  matplotlib.

1. Soem defintitions of colours based on the Transport for London colour palette and inserted as named colours into
   the matplotlib colour tables.

The package is fully documented (see link below) and comes with a set of examples that also server as unit tests.

## Documentation

Documentation can be found on the [github pages for this repository](https://stonerlab.github.io/stonerplots/index.html).

## Available Styles

### Core Styles

- stoner - this is the base style sheet
- poster - makes everything bigger for printing on a poster
- notebook - makes things a little bigger for a Jupyter notebook - from the original scienceplots package
- presentation - a style suitable for the main graph on a powerpoint slide
- thesis - a style that tries to look like the CM Physics group LaTeX thesis template

### Journal Styles

- nature - for Nature group journals - from the original scienceplots package
- aaas-science - Science single columne style.
- ieee - for IEEE Transactions journals - from the original scienceplots package
- aps - for American Physical Society Journals (like Phys Rev Lett etc.)
- aip - for AIP journals such as Applied Physics Letters - labels in Serif Fonts
- iop - for Institute of Physics Journals.

### Modifiers

- aps1.5 - Switch to 1.5 column wide format
- aps2.0 - Switch to 2 column wide format
- aip2 - Switch to 2 column wide format for AIP journals
- stoner-dark - Switch to a dark background a lighter plotting colours.
- hi-res - Switches to 600dpi plotting (but using eps, pdf or svg is generally a better option)
- med-res - like hi-res, but switches to 300dpi plotting.
- presentation_sm - a style for making 1/2 width graphs.
- presentation_dark - tweak the weight of elements for dark presnetations.
- science-2col, science-3col - Science 2 and 3 column width figures
- thesis-sm - reduces the figure width to make the axes closer to 4/3 aspect ratio.

## Context Managers

The package is designed to work by using python context managers to aid plotting. These include:

- SavedFigure - apply style sheets and then save any resulting figures to disc in one or more formats
- StackVertical - make a multi-panel plot where the panels are arranged in a vertical stack and pushed together so that
  the top-x-axis on one frame is the bottom of the next.
- MultiPanel - a general; purpose miulti-panel plotting helper.
- InsetPlot - create an inset set of axes.
- DoubleYAxis - setup the righthand y axis for a second scale and optional colour the y-axes differently and merge
  the legend into a single legend.

## Colour Cycles

The default colour cycle is based on the London Underground map colour scheme (why not?) and goes

- Northern
- Central
- Picadily
- District
- Metropolitan
- Bakerloo
- Jubilee
- Overground
- Victoria
- Elizabeth
- Circle

## Reference

The package adds these as named colours in matplotlib, along with 90,50,70 and 10% shade variants of some of them. See
the [documentation page on colours](https://stonerlab.github.io/stonerplots/colours.html) for a full list.

This package draws heavily on [scienceplots](https://github.com/garrettj403/SciencePlots), so it
seems only fair to cite the original work....

    @software{john_garrett_2023_10206719,
      author       = {John Garrett and
                      Echedey Luis and
                      H.-H. Peng and
                      Tim Cera and
                      gobinathj and
                      Josh Borrow and
                      Mehmet Keçeci and
                      Splines and
                      Suraj Iyer and
                      Yuming Liu and
                      cjw and
                      Mikhail Gasanov},
      title        = {garrettj403/SciencePlots: 2.1.1},
      month        = nov,
      year         = 2023,
      publisher    = {Zenodo},
      version      = {2.1.1},
      doi          = {10.5281/zenodo.10206719},
      url          = {https://doi.org/10.5281/zenodo.10206719},
    }

The doi and BibTex reference for stonerplots is: https://doi.org/10.5281/zenodo.14026874

    @software{gavin_burnell_2024_14026874,
      author       = {Gavin Burnell},
      title        = {stonerlab/stonerplots},
      month        = nov,
      year         = 2024,
      publisher    = {Zenodo},
      version      = {v1.5.2},
      doi          = {10.5281/zenodo.14026874},
      url          = {https://doi.org/10.5281/zenodo.14026874},
}
