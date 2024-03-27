"""Plot examples of SciencePlot styles."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from stonerplots import SavedFigure, InsetPlot

from pathlib import Path

figures = Path(__file__).parent / "figures"


def model(x, p):
    """Make some nice data."""
    return x ** (2 * p + 1) / (1 + x ** (2 * p))


pparam = dict(xlabel="Voltage (mV)", ylabel=r"Current ($\mu$A)")

x = np.linspace(0.75, 1.25, 201)

with SavedFigure(figures / "fig01a.png", style=["stoner"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig01b.png", style=["stoner", "no-latex"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig02a.png", style=["stoner", "ieee"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 20, 40, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig02b.png", style=["stoner", "std-colours"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig02c.png", style=["stoner", "aps"], autoclose=True, formats=["png", "pdf"]):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)


with SavedFigure(figures / "fig02d.png", style=["stoner", "aps", "aps1.5"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig02e.png", style=["stoner", "aps", "aps2"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

    ax.set(**pparam)


with SavedFigure(figures / "fig02f.png", style=["stoner", "nature"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig02g.png", style=["stoner", "poster"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        line = ax.plot(x, model(x, p), label=p, marker="")
        ax.plot(x[::5], model(x[::5], p), label=None, c=line[0].get_color(), linestyle="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)


with SavedFigure(figures / "fig02h.png", style=["stoner", "aip", "hi-res"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)


with SavedFigure(figures / "fig03.png", style=["stoner", "scatter", "latex"], autoclose=True):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.plot([-2, 2], [-2, 2], "k--")
    ax.fill_between([-2, 2], [-2.2, 1.8], [-1.8, 2.2], color="dodgerblue", alpha=0.2, lw=0)
    for i in range(7):
        x1 = np.random.normal(0, 0.5, 10)
        y1 = x1 + np.random.normal(0, 0.2, 10)
        ax.plot(x1, y1, label=r"$^\#${}".format(i + 1))
    lgd = r"$\mathring{P}=\begin{cases}1 \mathrm{if \nu\geq0}\\0 \mathrm{if \nu<0}\end{cases}$"
    ax.legend(title=lgd, loc=2, ncol=2)
    xlbl = r"$\log_{10}\left(\frac{L_\mathrm{IR}}{\mathrm{L}_\odot}\right)$"
    ylbl = r"$\log_{10}\left(\frac{L_\ast}{\mathrm{L}_\odot}\right)$"
    ax.set_xlabel(xlbl)
    ax.set_ylabel(ylbl)
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])

with SavedFigure(figures / "fig04.png", style=["stoner", "high-vis"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p)
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig05.png", style=["dark_background", "stoner", "high-vis"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

# Plot different color cycles

with SavedFigure(figures / "fig06.png", style=["stoner", "bright"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig07.png", style=["stoner", "vibrant"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig08.png", style=["stoner", "muted"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 7, 10, 15, 20, 30, 38, 50, 100, 500]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order", fontsize=7)
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig09.png", style=["stoner", "retro"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig10.png", style=["stoner", "notebook"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig11.png", style=["stoner", "grid"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig12.png", style=["stoner", "high-contrast"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 20, 50]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig13.png", style=["stoner", "light"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 7, 10, 15, 20, 30, 38, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order", fontsize=7)
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig14.png", style=["stoner"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 10, 20, 38, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order", fontsize=7)
    ax.autoscale(tight=True)
    ax.set(**pparam)
    with InsetPlot(loc="lower right") as inset:
        inset.plot(x, model(x, 200), linestyle="--")


with SavedFigure(figures / "fig15.png", style=["stoner", "presentation"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [10, 15, 20, 30, 50, 100]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order")
    ax.autoscale(tight=True)
    ax.set(**pparam)

with SavedFigure(figures / "fig16.png", style=["stoner", "presentation", "presentation_sm"], autoclose=True):
    fig, ax = plt.subplots()
    for p in [5, 6, 8, 10, 15, 20, 30, 50, 100, 150]:
        ax.plot(x, model(x, p), label=p, marker="")
    ax.legend(title="Order", labelspacing = 0.2)
    ax.autoscale(tight=True)
    ax.set(**pparam)
    ax.set_title("Dataet 1")
