# -*- coding: utf-8 -*-
"""SavedFigure context manager."""

from collections.abc import Iterable, Mapping
from contextlib import ExitStack
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from ..util import _default
from .base import PreserveFigureMixin, TrackNewFiguresAndAxes

default = _default()


def _make_path(output_file):
    """Ensure that output_file is going into a path that exists."""
    match output_file:
        case str():
            output_dir = Path(output_file).parent
        case Path():
            output_dir = output_file.parent
        case _:
            raise TypeError(f"output filename should be a string or pathlib.Path not a {type(output_file)}")
    output_dir.mkdir(parents=True, exist_ok=True)


class SavedFigure(TrackNewFiguresAndAxes, PreserveFigureMixin):
    """A context manager for applying plotting styles and saving matplotlib figures.

    This class simplifies the process of managing figure styling and saving multiple figures
    within a single context. It allows for automatic application of matplotlib stylesheets and
    handles the generation of unique filenames for figures, taking into account user-provided
    templates and output formats. SavedFigure can be reused across multiple `with` blocks,
    and its settings can dynamically be reconfigured by calling the instance with new parameters.

    Args:
        filename (str, Path, None):
            The base filename or target directory for saving figures.
            - If `filename` is a directory, the figure's label is used to generate the filename.
            - If `filename` includes placeholders (e.g., `{label}`, `{number}`), they will be replaced dynamically.
        style (list[str], str, None):
            One or more matplotlib stylesheets to apply. If a single string is provided, it is split by commas
            to form a list of styles. Defaults to ["stoner"].
        autoclose (bool):
            Determines whether figures should be closed automatically after being saved. Default is `False`.
        formats (str, list[str], None):
            The output file formats for saved figures (e.g., "png", "pdf"). Can be a comma-separated string,
            a list of strings, or `None` (default: ["png"]).
        extra (dict, None):
            Specific rcParams to override within the style sheet context manager. Defaults to {}
        include_open (bool):
            If `True`, any figures opened before entering the context are included for saving. Default is `False`.
        use (Figure):
            If set, use this matplotlib figure in the context hander. This is useful in a situation where one partially
            plots a figure, then run some other code outside the context handler and finally return and finish plotting
            the figure.

    Attributes:
        filename (Path):
            A property representing the base filename or directory for saving figures.
        formats (list[str]):
            A list of file formats to save the figures (e.g., ["png", "pdf"]).
        style (list[str]):
            A list of stylesheets to apply to the figures.
        autoclose (bool):
            Indicates whether figures are closed after being saved.
        include_open (bool):
            Determines whether figures already open before entering the context are saved.

    Notes:
        - `SavedFigure` can identify and save only the new figures created while inside its context, unless
          `include_open` is set to `True`.
        - `filename` and `formats` parameters support dynamic placeholders:
          - `{number}`: Figure number.
          - `{label}`: Figure label.
          - `{alpha}`, `{Alpha}`: Counter in lowercase or uppercase.
          - `{roman}`, `{Roman}`: Roman numeral (lowercase/uppercase).
        - Files are automatically numbered if placeholders are missing and multiple figures are created.

    Examples:
        Saving two figures in the same context:

        >>> cm = SavedFigure(filename="plots/figure_{label}.png", style="default", autoclose=True)
        >>> with cm:
        ...     plt.figure("plot1")
        ...     plt.plot([1, 2, 3], [4, 5, 6])
        ...     plt.show()
        ...     plt.figure("plot2")
        ...     plt.plot([7, 8, 9], [10, 11, 12])
        ...     plt.show()

        After exiting the context, SavedFigure will save:
        - plots/figure_plot1.png
        - plots/figure_plot2.png

        Dynamically updating SavedFigure settings during reuse:

        >>> with cm(formats=["pdf", "png"]):
        ...     plt.figure("plot3")
        ...     plt.plot([3, 4, 5], [9, 8, 7])
        ...     plt.show()

        This saves:
        - plots/figure_plot3.pdf
        - plots/figure_plot3.png
    """

    _keys = ["filename", "style", "autoclose", "formats", "include_open", "use", "extra"]

    def __init__(
        self, filename=None, style=None, autoclose=False, formats=None, extra=None, include_open=False, use=None
    ):
        """Initialize with default settings."""
        # Internal state initialization
        super().__init__(include_open=include_open)
        self._filename = None
        self._formats = []
        self._style = []
        self._extra = {}
        self._context_stack = None

        # Parameter assignment
        self.filename = filename
        self.style = style
        self.autoclose = autoclose
        self.formats = formats
        self.extra = extra
        self.use = use

    @property
    def filename(self):
        """Return filename as a Path object without extension.

        Returns:
            Path: The filename or directory path.

        Examples:
            >>> sf = SavedFigure(filename="plot.png")
            >>> sf.filename
            PosixPath('plot')
        """
        if self._filename is None:
            return default.filename
        return self._filename

    @filename.setter
    def filename(self, value):
        """Set filename and extract its extension if valid.

        Args:
            value (Union[str, Path]): The filename or directory path.

        Examples:
            >>> sf = SavedFigure()
            >>> sf.filename = "plot.png"
            >>> sf.filename
            PosixPath('plot')
        """
        match value:
            case None:  # use default filename
                value = default.filename
            case _ if not value:  # do not save the figure
                self._filename = None
            case str() | Path():
                value = Path(value)
                ext = value.suffix[1:]
                if ext and ext not in self.formats:
                    self.formats.append(ext)
                value = value.parent / value.stem
            case _:
                raise TypeError(f"Cannot interpet {value} as a filename.")
        self._filename = value

    @property
    def formats(self):
        """Return the output formats as a list of strings.

        Returns:
            list[str]: The list of output formats.

        Examples:
            >>> sf = SavedFigure(formats="png,pdf")
            >>> sf.formats
            ['png', 'pdf']
        """
        if not self._formats:
            return default.formats
        return self._formats

    @formats.setter
    def formats(self, value):
        """Ensure formats are stored as a list of strings.

        Args:
            value (Union[str, Iterable[str], None]): The formats to store.

        Raises:
            TypeError: If the value is not str, iterable, or None.

        Examples:
            >>> sf = SavedFigure()
            >>> sf.formats = "png,pdf"
            >>> sf.formats
            ['png', 'pdf']
        """
        match value:
            case str():
                self._formats = [x.strip() for x in value.split(",") if x.strip()]
            case Iterable() if all(isinstance(x, str) for x in value):
                self._formats = list(value)
            case None if not self._formats:  # Use default if formats aren't set
                self._formats = default.formats
            case _:
                raise TypeError(f"Invalid formats specified {value}. Expected str, iterable, or None.")

    @property
    def style(self):
        """Return the stylesheets as a list of strings.

        Returns:
            list[str]: The list of stylesheets.

        Examples:
            >>> sf = SavedFigure(style="default")
            >>> sf.style
            ['default']
        """
        return self._style

    @style.setter
    def style(self, value):
        """Ensure style is stored as a list of strings.

        Args:
            value (Union[str, Iterable[str], None]): The styles to store.

        Raises:
            TypeError: If the value is not str, iterable, or None.

        Examples:
            >>> sf = SavedFigure()
            >>> sf.style = "default,ggplot"
            >>> sf.style
            ['default', 'ggplot']
        """
        match value:
            case str():
                self._style = [x.strip() for x in value.split(",") if x.strip()]
            case Iterable() if all(isinstance(x, str) for x in value):
                self._style = list(value)
            case None:
                self._style = default.style
            case _:
                raise TypeError(f"Invalid style: {value}. Expected str, iterable, or None.")

    @property
    def extra(self):
        """Return the extra rcParams dictionary."""
        return self._extra

    @extra.setter
    def extra(self, value):
        """Ensure we set extra with valid rc_parameters."""
        match value:
            case None:
                self._extra = {}
            case Mapping() if len(value) == 0:
                self._extra = {}
            case Mapping():
                if bad := value.keys() - mpl.rcParams.keys():
                    raise KeyError(f"{','.join(bad)} are not valid Matplotlib rcParameters.")
                for param, val in value.items():
                    self._extra[param] = val

    def __call__(self, *args, **kwargs):
        """Update settings dynamically and return self."""
        settings = {key: kwargs[key] for key in self._keys if key in kwargs}
        match args:
            case (filename,) if isinstance(filename, (str, Path)):
                settings["filename"] = filename
            case tuple() if not len(args) and self.filename is not None:
                pass
            case _:
                raise ValueError("Only a single positional argument that is either a string or path is supported")
        for key, val in settings.items():
            setattr(self, key, val)
        return self

    def __enter__(self):
        """Record existing open figures and enter style context (if any)."""
        super().__enter__()
        if self.use:  # Set the current figure to be that given by use.
            plt.figure(getattr(self.use, "number", None))

        # Use ExitStack to manage multiple context managers cleanly
        self._context_stack = ExitStack()
        self._context_stack.__enter__()

        if self.style:
            self._context_stack.enter_context(mpl.style.context(self.style))
        if self.extra:
            self._context_stack.enter_context(mpl.rc_context(rc=self.extra))

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit style context, save new figures, and optionally close them."""
        # Exit all contexts managed by ExitStack
        if self._context_stack is not None:
            self._context_stack.__exit__(exc_type, exc_value, traceback)
            self._context_stack = None

        self._existing_open_figs = [ref() for ref in self._existing_open_figs if ref() is not None]
        new_file_counter = 0

        new_figures = list(self.new_figures)
        if self.use:
            new_figures += [self.use]

        for fig in new_figures:

            new_file_counter += 1
            label = fig.get_label()
            filename = self.generate_filename(label, new_file_counter)

            if filename:
                for fmt in self.formats:
                    output_file = f"{filename}.{fmt.lower()}"
                    _make_path(output_file)
                    fig.savefig(output_file)

            if self.autoclose:
                plt.close(fig)

        # Reset state
        super().__exit__(exc_type, exc_value, traceback)

    def generate_filename(self, label, counter):
        """Help generate filenames based on `filename` and placeholders.

        Supports placeholders like {label}, {number}, and appends
        a counter if multiple new figures are detected.

        Args:
            label (str): The figure label.
            counter (int): The figure counter.

        Returns:
            str: The generated filename.

        Examples:
            >>> sf = SavedFigure(filename="plot_{label}.png")
            >>> sf.generate_filename("test", 1)
            'plot_test.png'
        """
        if not self.filename:
            return None
        if self.filename.is_dir():
            filename: Path = self.filename / "{label}"
        else:
            filename: Path = self.filename if self.filename is not None else Path("{label}")

        filename = str(filename).format(label=label, number=counter)
        # Append counter if filename lacks placeholders and multiple files
        if "{label}" not in str(self.filename) and "{number}" not in str(self.filename) and counter > 1:
            parts = filename.rsplit(".", 1)
            filename = f"{parts[0]}-{counter}.{parts[1]}" if len(parts) > 1 else f"{filename}-{counter}"
        return filename
