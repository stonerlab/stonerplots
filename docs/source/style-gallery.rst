Stoner Plots Style Gallery
==========================

1. Default Styles
-----------------

Basic *stoner* style:
~~~~~~~~~~~~~~~~~~~~~

The basic stylesheet is the *stoner* stylesheet.::

    with SavedFigure(figures / "fig01a.png", style=["stoner"], autoclose=True):
        fig, ax = plt.subplots()
        for p in [10, 15, 20, 30, 50, 100]:
            ax.plot(x, model(x, p), label=p, marker="")
        ax.legend(title="Order")
        ax.autoscale(tight=True)
        ax.set(**pparam)


.. image:: ../../examples/figures/fig01a.png
  :alt: Example figure formatted with the 'stoner' style sheet.
  :align: center

LaTeX Rendering
~~~~~~~~~~~~~~~

The basic stoner style uses matplotlib's builtin emulation of LaTeX to render mathemtatical expressions. Use the
*latex* modier to turn on LaTeX rendering of text and maths.::


    with SavedFigure(figures / "fig01b.png", style=["stoner", "latex"], autoclose=True):
        fig, ax = plt.subplots()
        for p in [10, 15, 20, 30, 50, 100]:
            ax.plot(x, model(x, p), label=p, marker="")
        ax.legend(title="Order")
        ax.autoscale(tight=True)
        ax.set(**pparam)


.. image:: ../../examples/figures/fig01b.png
  :alt: Example figure formatted with the 'stoner' style sheet.
  :align: center

2. Journal Formats
------------------

There are specific stylesheets for producing plots at the correct size and style for some common Physics journals.

+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig02a.png        | .. image:: ../../examples/figures/fig02b.png      |
|    :alt: Example fogure in IEEE format              |    :alt: Example figure in APS Format             |
|    :align: center                                   |    :align: center                                 |
|                                                     |                                                   |
| Using styles ["stoner", "ieee"]                     | Using styles ["stoner", "aps"]                    |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig02c.png        | .. image:: ../../examples/figures/fig02d.png      |
|    :alt: Example fogure in AIP format               |    :alt: Example figure in IOP Format             |
|    :align: center                                   |    :align: center                                 |
|                                                     |                                                   |
| Using styles ["stoner", "aip"]                      | Using styles ["stoner", "iop"]                    |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig02e.png        |                                                   |
|    :alt: Example fogure in nature format            |                                                   |
|    :align: center                                   |                                                   |
|                                                     |                                                   |
| Using styles ["stoner", "nature"]                   |                                                   |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
|                                                                                                         |
| .. image:: ../../examples/figures/fig02f.png                                                            |
|    :alt: Example fogure in APS 1.5 Column format                                                        |
|    :align: center                                                                                       |
|                                                                                                         |
| Using styles ["stoner", "aps","aps1.5"]                                                                 |
|                                                                                                         |
+-----------------------------------------------------+---------------------------------------------------+
|                                                                                                         |
| .. image:: ../../examples/figures/fig02g.png                                                            |
|    :alt: Example fogure in APS 2 Column format                                                          |
|    :align: center                                                                                       |
|                                                                                                         |
| Using styles ["stoner", "aps","aps2"]                                                                   |
|                                                                                                         |
+-----------------------------------------------------+---------------------------------------------------+

3. Different Plot Types
-----------------------


4. Different Colour Schemes
---------------------------

+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig04a.png        | .. image:: ../../examples/figures/fig04b.png      |
|    :alt: Standard colours scheme                    |    :alt: Bright palette colour scheme             |
|    :align: center                                   |    :align: center                                 |
|                                                     |                                                   |
| Using styles ["stoner", "std-colours"]              | Using styles ["stoner", "bright"]                 |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig04c.png        | .. image:: ../../examples/figures/fig04d.png      |
|    :alt: High contrast palette colour scheme        |    :alt: High visibility palette colour scheme    |
|    :align: center                                   |    :align: center                                 |
|                                                     |                                                   |
| Using styles ["stoner", "high-contrast"]            | Using styles ["stoner", "high-vis"]               |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig04e.png        | .. image:: ../../examples/figures/fig04f.png      |
|    :alt: Light palette colour scheme                |    :alt: Muted palette colour scheme              |
|    :align: center                                   |    :align: center                                 |
|                                                     |                                                   |
| Using styles ["stoner", "light"]                    | Using styles ["stoner", "muted"]                  |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig04g.png        | .. image:: ../../examples/figures/fig04h.png      |
|    :alt: Retro palette colour scheme                |    :alt: Vibrant palette colour scheme            |
|    :align: center                                   |    :align: center                                 |
|                                                     |                                                   |
| Using styles ["stoner", "retro"]                    | Using styles ["stoner", "vibrant"]                |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
|                                                     |                                                   |
| .. image:: ../../examples/figures/fig04i.png        |                                                   |
|    :alt: Dark themed plot figure                    |                                                   |
|    :align: center                                   |                                                   |
|                                                     |                                                   |
| Using styles ["stoner", "stoner-dark"], in addition |                                                   |
| to the dark bakground, the tuve_colours50 palette   |                                                   |
| gives a reasonable constrast for the plot lines.    |                                                   |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+



5. Different Formats
--------------------


6. Miscellaneous Tweaks
-----------------------

The *grid* style adds an axes grid to the plot.

.. image:: ../../examples/fi

This was produced with the style ["stoner", "grid"]

7. Insets and Multi-panel plots
-------------------------------

Inset Plots
~~~~~~~~~~~

The :py:class@`InsetPlot` context manager can be used to add a new set of axes as an inset to a plot.

.. image::  ../../examples/figures/fig07a.png
   :alt: Plot with inset in lower right corner
   :align: center

Stacked Sub-plots
~~~~~~~~~~~~~~~~~

When you want to compare several variables against a common independent variable, stacking the plots can be useful.
The :py:class:`StackedPlots` context manager can be used for this.

.. image:: ../../examples/figures/fig07b.png
   :alt: 3-panel vertically stacked plot
   :align: center
