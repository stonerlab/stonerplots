"""Compare independent top x axes with independent top and right axes."""

import matplotlib.pyplot as plt
import numpy as np
from common import figures

from stonerplots import DoubleXAxis, DoubleXYAxis, SavedFigure


def main():
    """Save an illustration of both double-axis variants."""
    x = np.linspace(0, 4, 100)
    with SavedFigure(figures / "double_axes.png", style="stoner", autoclose=True):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="none")
        for parent, manager in zip(axes, (DoubleXAxis, DoubleXYAxis)):
            parent.plot(x, np.sin(x), color="central", label="Primary")
            parent.set(xlabel="Time (s)", ylabel="Signal (V)")
            with manager(ax=parent, colours=("central", "piccadilly"), loc="lower left") as secondary:
                y = np.cos(x) if manager is DoubleXAxis else 300 + 20 * np.cos(x)
                secondary.plot(10 + 5 * x, y, "--", color="piccadilly", label="Secondary")
                secondary.set_xlabel("Distance (mm)")
                if manager is DoubleXYAxis:
                    secondary.set_ylabel("Temperature (K)")
        fig.subplots_adjust(left=0.08, bottom=0.16, right=0.91, top=0.84, wspace=0.5)


main()
