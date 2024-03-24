Stoner Plots
=============

Stoner Plots is a fork of Science Plots

*Matplotlib styles for physics figures*

Usage
-----

Before using the new styles you need to import stonerplots - but it's ok to just import e.g. the SavedFigure context
manager:

    from stonerplots import SavedFigure

    with SavedFigure("my_figure.pdf", style=["science","aps"]):
        plt.figure()
        plt.plot(x,y,label="Dataset")
        ...

Available Styles
----------------

 * science - this is the base style sheet

Journal Styles
~~~~~~~~~~~~~~

 * nature - for Nature group journals
 * ieee - for IEEE Transactions journals
 * aps - for American Physical Society Journals (like Phys Rev Lett etc.)

Modifiers
~~~~~~~~~

 * aps1.5 - Switch to 1.5 column format
 * aps2.0 - Switch to 2 column format


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
