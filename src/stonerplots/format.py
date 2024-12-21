# -*- coding: utf-8 -*-
"""Additional matplotlib formatting classes."""
import numpy as np
from matplotlib.ticker import EngFormatter, Formatter, Locator, NullFormatter

from .context import _TrackNewFiguresAndAxes


def _round(value, offset=2):
    """Round numbers for the TexFormatters to avoid crazy numbers of decimal places."""
    for i in range(5):
        vt = np.round(value, i)
        if np.abs(value - vt) < 10 ** (-i - offset):
            value = vt
            break
    return value


class TexFormatter(Formatter):
    r"""An axis tick label formatter that emits Tex formula mode code.

    Formatting is set so that large numbers are registered as :math`\times 10^{power}`
    rather than using E notation.
    """

    def __call__(self, value, pos=None):
        """Return the value ina  suitable texable format."""
        if value is None or np.isnan(value):
            ret = ""
        elif value != 0.0:
            power = np.floor(np.log10(np.abs(value)))
            if np.abs(power) < 4:
                ret = f"${round(value)}$"
            else:
                v = _round(value / (10**power))
                ret = f"${v}\\times 10^{{{power:.0f}}}$"
        else:
            ret = "$0.0$"
        return ret

    def format_data(self, value):
        """Return the full string representation of the value with the position unspecified."""
        return self.__call__(value)

    def format_data_short(self, value):  # pylint: disable=r0201
        """Return a short string version of the tick value.

        Defaults to the position-independent long value.
        """
        return f"{value:g}"


class TexEngFormatter(EngFormatter):
    """An axis tick label formatter that emits Tex formula mode code.

    Formatting is set so that large numbers are registered as with SI prefixes
    rather than using E notation.
    """

    prefix = {
        0: "",
        3: "k",
        6: "M",
        9: "G",
        12: "T",
        15: "P",
        18: "E",
        21: "Z",
        24: "Y",
        -3: "m",
        -6: "\\mu",
        -9: "n",
        -12: "p",
        -15: "f",
        -18: "a",
        -21: "z",
        -24: "y",
    }

    def __call__(self, value, pos=None):
        """Return the value ina  suitable texable format."""
        if value is None or np.isnan(value):
            ret = ""
        elif value != 0.0:
            power = np.floor(np.log10(np.abs(value)))
            pre = np.ceil(power / 3.0) * 3
            if -1 <= power <= 3 or pre == 0:
                ret = f"${round(value, 4)}\\,\\mathrm{{{self.unit}}}$"
            else:
                power = power % 3
                v = _round(value / (10**pre), 4)
                if np.abs(v) < 0.1:
                    v *= 1000
                    pre -= 3
                elif np.abs(v) > 1000.0:
                    v /= 1000
                    pre += 3.0

                ret = f"${v}\\mathrm{{{self.prefix[int(pre)]} {self.unit}}}$"
        else:
            ret = "$0.0$"
        return ret

    def format_data(self, value):
        """Return the full string representation of the value with the position unspecified."""
        return self.__call__(value)

    def format_data_short(self, value):  # pylint: disable=r0201
        """Return a short string version of the tick value.

        Defaults to the position-independent long value.
        """
        return f"{value:g}"


class PlotLabeller(_TrackNewFiguresAndAxes):
    """Adjust the x and y axis tick formatters of plots created in the context handler.

    Keyword Arguments:
        x,y,z (Formatter,Locator or tuple or list of Formatter or Locator):
            Ticker formatter and locator classes or isntances.

    Notes:
        The PlotLabeller Context handerl will apply any given axis tick locators and formatters to
        any plots created inside the context handler. If Formatter/Locator classes are passed in, these
        are instantiated with default parameters. If the minor formatter/locator is set, the same locator and
        formatter are applied as for the major formatter/locator.

        The default is to not change the Locator and set the Formatters to use the TexEngFormatter that
        renders the labels with LaTeX codes to allow proper micro signs.

    Todo:
        This needs proper handling of minor/major fomatting.



    """

    def __init__(self, *args, x=TexEngFormatter, y=TexEngFormatter, z=TexEngFormatter, **kargs):
        """Store tick formatting classes."""
        self._initialize_axes("x", x)
        self._initialize_axes("y", y)
        self._initialize_axes("z", z)
        super().__init__(*args, **kargs)

    def _initialize_axes(self, label, axis):
        """Initialize axis with given formatters or locators."""
        if not isinstance(axis, (list, tuple)):
            axis = [axis]
        formatted_axes = []
        for elem in axis:
            if isinstance(elem, type):
                elem = elem()
            if not isinstance(elem, (Locator, Formatter)):
                raise TypeError(
                    f"{label} should only contain matplotlib.ticker.Formatter subclasses "
                    "or instances of matplotlib.ticker.Locator"
                )
            formatted_axes.append(elem)
        setattr(self, f"{label}axis", formatted_axes)

    def __exit__(self, exc_type, exc_value, traceback):
        """Apply the ticker formatter to all the opened axes."""
        for ax in self.new_axes:
            for name in ("xaxis", "yaxis", "zaxis"):
                axis = getattr(ax, name, None)
                if not axis:
                    continue
                for elem in getattr(self, name):
                    if isinstance(elem, type):
                        elem = elem()
                    if isinstance(elem, Formatter):
                        axis.set_major_formatter(elem)
                        if not isinstance(axis.get_minor_formatter(), NullFormatter):
                            axis.set_minor_formatter(elem)
                    elif isinstance(elem, Locator):
                        axis.set_major_locator(elem)
                        if not isinstance(axis.get_minor_locator(), NullFormatter):
                            axis.set_minor_locator(elem)
        super().__exit__(exc_type, exc_value, traceback)
