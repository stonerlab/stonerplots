"""Install StonerPlots.

This script (setup.py) will install the StonerPlots package.
In order to expose .mplstyle files to matplotlib, "import stonerplots"
must be called before plt.style.use(...).
"""

import os
from setuptools import setup

# Get description from README
root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='StonerPlots',
    description="Format Matplotlib for physics plotting",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=["stonerplots"],
    package_data={
      'stonerplots': ['styles/**/*.mplstyle'],
    },

)
