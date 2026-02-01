# -*- coding: utf-8 -*-
"""Additional matplotlib formatting classes."""

from typing import Any, Optional, Union
import numpy as np
from numpy.ma import MaskedArray
from matplotlib.ticker import EngFormatter, Formatter, Locator, NullFormatter

from .context.base import TrackNewFiguresAndAxes


def _round(value: float, offset: int = 2) -> float:
    """Round numbers for the TexFormatters to avoid crazy numbers of decimal places.

    Args:
        value (float): The numerical value to round.
        offset (int): Additional decimal places to consider in the rounding threshold.

    Returns:
        float: The rounded value.
    """
    for i in range(5):
        vt = np.round(value, i)
        if np.abs(value - vt) < 10 ** (-i - offset):
            value = vt
            break
    return value


class TexFormatter(Formatter):
    r"""An axis tick label formatter that emits Tex formula mode code.

    Formatting is set so that large numbers are registered as :math:`\times 10^{power}`
    rather than using E notation.

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from stonerplots.format import TexFormatter
        >>> fig, ax = plt.subplots()
        >>> ax.yaxis.set_major_formatter(TexFormatter())
        >>> ax.plot([0, 1e6, 2e6], [0, 1, 2])
        >>> plt.show()
    """

    def __call__(self, value: float, pos: Optional[int] = None) -> str:
        """Return the value in a suitable texable format."""
        if value is None or np.isnan(value):
            ret = ""
        elif value != 0.0:
            power = np.floor(np.log10(np.abs(value)))
            if np.abs(power) < 4:
                ret = f"${round(value)}$"
            else:
                try:
                    v = _round(value / (10**power))
                    ret = f"${v}\\times 10^{{{power:.0f}}}$"
                except (OverflowError, ZeroDivisionError, FloatingPointError):
                    ret = f"${value:g}$"
        else:
            ret = "$0.0$"
        return ret

    def format_data(self, value: float) -> str:
        """Return the full string representation of the value with the position unspecified."""
        return self.__call__(value)

    def format_data_short(self, value: Union[float, MaskedArray]) -> str:  # pylint: disable=r0201
        """Return a short string version of the tick value.

        Defaults to the position-independent long value.
        """
        return f"{value:g}"


class TexEngFormatter(EngFormatter):
    """An axis tick label formatter that emits Tex formula mode code.

    Formatting is set so that large numbers are registered as with SI prefixes
    rather than using E notation.
    """

    prefix: dict[int, str] = {
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

    def __call__(self, value: float, pos: Optional[int] = None) -> str:
        """Return the value in a suitable texable format."""
        if value is None or np.isnan(value):
            ret = ""
        elif value != 0.0:
            power = np.floor(np.log10(np.abs(value)))
            pre = np.ceil(power / 3.0) * 3
            if -1 <= power <= 3 or pre == 0:
                ret = f"${round(value, 4)}\\,\\mathrm{{{self.unit}}}$"
            else:
                power = power % 3
                try:
                    with np.errstate(over="raise", divide="raise", invalid="raise"):
                        v = _round(value / (10**pre), 4)
                        if np.abs(v) < 0.1:
                            v *= 1000
                            pre -= 3
                        elif np.abs(v) > 1000.0:
                            v /= 1000
                            pre += 3.0

                    ret = f"${v}\\mathrm{{{self.prefix[int(pre)]} {self.unit}}}$"
                except (OverflowError, ZeroDivisionError, FloatingPointError, KeyError):
                    ret = f"${value:g}\\,\\mathrm{{{self.unit}}}$"
        else:
            ret = "$0.0$"
        return ret

    def format_data(self, value: float) -> str:
        """Return the full string representation of the value with the position unspecified."""
        return self.__call__(value)

    def format_data_short(self, value: Union[float, MaskedArray]) -> str:  # pylint: disable=r0201
        """Return a short string version of the tick value.

        Defaults to the position-independent long value.
        """
        return f"{value:g}"


class PlotLabeller(TrackNewFiguresAndAxes):
    """Adjust the x and y axis tick formatters of plots created in the context handler.

    Keyword Arguments:
        x,y,z (Formatter,Locator or tuple or list of Formatter or Locator):
            Ticker formatter and locator classes or instances.

    Notes:
        The PlotLabeller Context handler will apply any given axis tick locators and formatters to
        any plots created inside the context handler. If Formatter/Locator classes are passed in, these
        are instantiated with default parameters.

        Both major and minor formatters/locators are handled: if a minor formatter/locator is already set
        (i.e., not NullFormatter), the same formatter/locator will be applied to it as well.

        The default is to not change the Locator and set the Formatters to use the TexEngFormatter that
        renders the labels with LaTeX codes to allow proper micro signs.

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from stonerplots.format import PlotLabeller, TexFormatter
        >>> with PlotLabeller(x=TexFormatter, y=TexFormatter):
        ...     fig, ax = plt.subplots()
        ...     ax.plot([1e6, 2e6, 3e6], [1, 2, 3])
        >>> plt.show()
    """

    def __init__(
        self,
        *args: Any,
        x: Union[type[Formatter], type[Locator], Formatter, Locator, list, tuple] = TexEngFormatter,
        y: Union[type[Formatter], type[Locator], Formatter, Locator, list, tuple] = TexEngFormatter,
        z: Union[type[Formatter], type[Locator], Formatter, Locator, list, tuple] = TexEngFormatter,
        **kargs: Any,
    ) -> None:
        """Store tick formatting classes."""
        self._initialize_axes("x", x)
        self._initialize_axes("y", y)
        self._initialize_axes("z", z)
        super().__init__(*args, **kargs)

    def _initialize_axes(
        self, label: str, axis: Union[type[Formatter], type[Locator], Formatter, Locator, list, tuple]
    ) -> None:
        """Initialize axis with given formatters or locators."""
        if not isinstance(axis, (list, tuple)):
            axis = [axis]
        formatted_axes: list[Union[Formatter, Locator]] = []
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

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_value: Optional[BaseException], traceback: Any
    ) -> None:
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
