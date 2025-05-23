# Changelog

## v1.7.1 Release

New feature

- Added the *use* parameter to SavedFigure to allow a fignure to be returned to in the same or different SavedFigure
  context manager.

## v1.7.0

New feature

- Added new keyword argument to SavedFigure to allow individual rcParam values to be overriden.

Other

- Split stonerplots.context into separate sub modules for easier maintainence.

## v1.6.1 Release

Minor feature release o implement fontsize for individual elements and also default settings.

## v1.6.0 Release

New features

- Added the inset autolocator code.
- Added a medium resolution style sheet.
- PlotLabeller context manager to apply axes formatting to new figures.
- Additional Formatting functions from the stoner Package.
- Added a DoubleYAxis context manager for helping with double-y axis plots.

## v1.5.2 Release

Further code cleanups following codacy code quality checks.

## v1.5.1 Release

Some refactoring of the context managers and other code cleanups. No intentional changes to the API.

## v1.5.0 Release

Iregular grids in MultuPanel now can also do different numbers of rows in each column with the *transpose* parameter.

## v1.4.0 Release

Iregullar grids in MultiPanel that support different numbers of plots in each row.

## v1.3.2 Release

Improve StackVertical to allow asymmetric stacked plots and make an example for plotting
GenX fits.

- Add AAAS-Science stylesheet with 2 and 3 column variants.
- Improve SavedFigure to make it reusable and also adjustable after creation via call method.
- Improvements to StackVertical and MultiPanel to do more calculations with plot transforms.

## v1.3.1 Thesis Style

Add a stylesheet that tries to match the CM Group's LaTeX thesis template.

## v1.3.0 New MultiPanel Context Manager

Add a context manager for making multipanel figures more easily.

- MultiPanel Context Manger
- Improve documentation some more

## v1.2.0 New StackVertical Context Manager

Add a context manager for producing vertically stacked plots in a constrained layout.

- StackVertical added
- Rework examples into separate scripts
- Add Sphinx docs

## v1.1.0 New Stylesheets

Add New stylesheets to the package

- Add IOP styles
- Get package building running

## v1.0.0 (developement)

Initial fork from scienceplots 2.1.1

- Add aps plot style
- Remove language styles
- Add SavedFigures context manager
- Use pathlib.Path and not os.path
