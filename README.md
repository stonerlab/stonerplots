Stoner Plots
=============

Stoner Plots is a fork of Science Plots

*Matplotlib styles for physics figures*

This repo has Matplotlib styles to format your figures for scientific papers, presentations and theses with an
emphasisi on Condesed Matter Physics journals.

<p align="center">
<img src="https://github.com/gb119/StonerPlots/raw/master/examples/figures/fig01a.jpg" width="500">
</p>

You can find [the full gallery of included styles here](https://github.com/gb119/StonerPlots/wiki/Gallery).

Getting Started
---------------

The easiest way to install StonerPlots is by using `pip`:

```bash
# to install the lastest release (from PyPI)
pip install StonerPlots

# to install the lastest release (using Conda)
conda install -c phygbu stonerplots

# to install the latest commit (from GitHub)
pip install git+https://github.com/gb119/StonerPlots

# to clone and install from a local copy
git clone https://github.com/gb119/StonerPlots.git
cd StonerPlots
pip install -e .
```

**Notes:**
- StonerPlots requires Latex ([see Latex installation instructions](https://github.com/gb119/StonerPlots/wiki/FAQ#installing-latex)).

Using the Styles
----------------

``"science"`` is the primary style in this repo. Whenever you want to use it, simply add the following to the top of your python script:

```python
import matplotlib.pyplot as plt
import stonerplots

plt.style.use('science')
```

You can also combine multiple styles together by:

```python
plt.style.use(['science','ieee'])
```

In this case, the ``ieee`` style will override some of the parameters from the ``science`` style in order to configure the plot for IEEE papers (column width, fontsizes, etc.).

To use any of the styles temporarily, you can use:

```python
with plt.style.context('science'):
    plt.figure()
    plt.plot(x, y)
    plt.show()
```

Examples
--------

The basic ``science`` style is shown below:

<img src="https://github.com/gb119/StonerPlots/raw/master/examples/figures/fig01a.jpg" width="500">

It can be cascaded with other styles to fine-tune the appearance. For example, the ``science`` + ``notebook`` styles (intended for Jupyter notebooks):

<img src="https://github.com/gb119/StonerPlots/raw/master/examples/figures/fig10.jpg" width="500">

Please see [the project Wiki](https://github.com/gb119/StonerPlots/wiki/Gallery) for a full list of available styles.

Specific Styles for Academic Journals
-------------------------------------

The ``science`` + ``ieee`` styles for IEEE papers:

<img src="https://github.com/gb119/StonerPlots/raw/master/examples/figures/fig02a.jpg" width="500">

   - IEEE requires figures to be readable when printed in black and white. The ``ieee`` style also sets the figure width to fit within one column of an IEEE paper.

The ``science`` + ``nature`` styles for Nature articles:

<img src="https://github.com/gb119/StonerPlots/raw/master/examples/figures/fig02c.jpg" width="500">

   - Nature recommends sans-serif fonts.

Other color cycles
------------------

StonerPlots comes with a variety of different color cycles. For a full list, [see the project Wiki](https://github.com/gb119/StonerPlots/wiki/Gallery#color-cycles). Two examples are shown below.

The ``bright`` color cycle (color blind safe):

<img src="https://github.com/gb119/StonerPlots/raw/master/examples/figures/fig06.jpg" width="500">

The ``high-vis`` color cycle:

<img src="https://github.com/gb119/StonerPlots/raw/master/examples/figures/fig04.jpg" width="500">


Citing StonerPlots
-------------------

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
