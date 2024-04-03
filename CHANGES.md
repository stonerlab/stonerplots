v1.3.2 Release
==============

- Improve StackVertical to allow asymmetric stacked plots and make an example for plotting
GenX fits.
- Add AAAS-Science stylesheet with 2 and 3 column variants.
- Improve SavedFigure to make it reusable and also adjustable after creation via call method.
- Improvements to StackVertical and MultiPanel to do more calculations with plot transforms.

v1.3.1 Thesis Style
===================

Add a stylesheet that tries to match the CM Group's LaTeX thesis template.

v1.3.0 New MultiPanel Context Manager
=====================================

Add a context manager for making multipanel figures more easily.
- MultiPanel Context Manger
- Improve documentation some more

v1.2.0 New StackVertical Context Manager
========================================

Add a context manager for producing vertically stacked plots in a constrained layout.
- StackVertical added
- Rework examples into separate scripts
- Add Sphinx docs

v1.1.0 New Stylesheets
======================

Add New stylesheets to the package
- Add IOP styles
- Get package building running

v1.0.0 (developement)
=====================

Initial fork from scienceplots 2.1.1
- Add aps plot style
- Remove language styles
- Add SavedFigures context manager
- Use pathlib.Path and not os.path
