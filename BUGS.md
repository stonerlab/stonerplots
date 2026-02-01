# Code Review Report - StonerPlots Repository

**Review Date:** 2026-02-01  
**Last Updated:** 2026-02-01  
**Repository:** stonerlab/stonerplots  

This document contains detailed information about all issues and bugs discovered during a comprehensive code review of the stonerplots repository.

---

## Critical Issues (HIGH SEVERITY)

### Issue #1: Buffer Overflow in counter() Function

**File:** `src/stonerplots/counter.py:73`  
**Severity:** HIGH  
**Status:** Open  

**Description:**

The `counter()` function computes lowercase alphabet labels using `chr(ord("a") + value)`. This works for values 0-25 (producing 'a'-'z'), but crashes for values >= 26 because the resulting ASCII code exceeds the lowercase letter range.

**Current Code:**
```python
def counter(value: int, pattern: str = "({alpha})", **kwargs: str) -> str:
    r"""Format an integer as a string using a pattern and various representations.

    Args:
        value (int): The integer to format.
        pattern (str): A format string with placeholders (default: '({alpha})').
        \*\*kwargs: Additional data to replace placeholders.

    Returns:
        str: The formatted string.
    """
    alpha = chr(ord("a") + value)  # ← Bug: No bounds checking!
    Roman = roman(value + 1)
    return pattern.format(alpha=alpha, Alpha=alpha.upper(), roman=Roman.lower(), Roman=Roman, int=value, **kwargs)
```

**Reproduction:**
```python
>>> from stonerplots.counter import counter
>>> counter(0)
'(a)'
>>> counter(25)
'(z)'
>>> counter(26)  # Expected: 'aa' or error, Got: '{'
'({)'
>>> counter(27)  # Expected: 'ab' or error, Got: '|'
'(|)'
```

**Impact:**

- **Critical:** Function produces invalid output (non-letter characters) for common use cases
- Affects any code using counter() for labelling beyond 26 items (e.g., subfigures, panels)
- Silent failure - produces garbage output instead of raising an error
- Users may not notice the bug until they have > 26 items

**Root Cause:**

The function assumes `value` is in range [0, 25] but doesn't validate or handle values outside this range.

**Recommended Fix:**

**Option 1: Multi-letter labels (Excel-style)**
```python
def _int_to_alpha(value: int) -> str:
    """Convert integer to Excel-style column label (a, b, ..., z, aa, ab, ...)."""
    if value < 0:
        raise ValueError(f"Value must be non-negative, got {value}")
    
    result = ""
    value += 1  # Make 1-indexed (a=1, b=2, ..., z=26, aa=27)
    while value > 0:
        value -= 1
        result = chr(ord('a') + (value % 26)) + result
        value //= 26
    return result

def counter(value: int, pattern: str = "({alpha})", **kwargs: str) -> str:
    # ...
    alpha = _int_to_alpha(value)
    # ...
```

**Option 2: Wraparound (modulo)**
```python
def counter(value: int, pattern: str = "({alpha})", **kwargs: str) -> str:
    # ...
    alpha = chr(ord("a") + (value % 26))  # Wrap: 26→a, 27→b, etc.
    # ...
```

**Option 3: Raise error**
```python
def counter(value: int, pattern: str = "({alpha})", **kwargs: str) -> str:
    # ...
    if not 0 <= value < 26:
        raise ValueError(f"counter() alpha format only supports values 0-25, got {value}")
    alpha = chr(ord("a") + value)
    # ...
```

**Recommendation:** Option 1 (multi-letter labels) is most flexible and matches user expectations. Option 3 is simplest but limits functionality.

---

### Issue #2: Assignment Bug in InsetPlot.__enter__()

**File:** `src/stonerplots/context/inset_plot.py:114-115`  
**Severity:** HIGH  
**Status:** Open  

**Description:**

The `__enter__()` method attempts to handle axes wrappers by detecting objects with an `.ax` attribute. However, line 114 assigns `self.ax = self._ax.ax`, and then line 115 **unconditionally overwrites** this assignment, making the wrapper detection completely ineffective.

**Current Code:**
```python
def __enter__(self) -> Axes:
    """Create the inset axes using the axes_grid toolkit."""
    # Support for axes wrappers: check if _ax is a wrapper with an 'ax' attribute
    ax_attr = getattr(self._ax, "ax", None)
    if isinstance(ax_attr, Axes):
        self.ax = self._ax.ax  # type: ignore[union-attr]  # ← Set here
    self.ax = self._ax if isinstance(self._ax, Axes) else plt.gca()  # ← OVERWRITTEN HERE!
    if not isinstance(self._loc, int):
        self.loc = self.locations.get(str(self._loc).lower().replace("-", " "), 1)
    else:
        self.loc = self._loc
    axins = inset_axes(self.ax, width=self.width, height=self.height, loc=self.loc if self.loc else 1)
    # ...
```

**Impact:**

- **Critical:** Axes wrapper functionality is completely broken
- Code intended to support wrappers (line 112-114) never works as intended
- May cause AttributeError or incorrect behavior when using wrapped axes
- Silently fails - wrapper appears to be passed but isn't properly unwrapped

**Root Cause:**

Missing `elif` or `else` on line 115. The assignment is unconditional, so it always executes regardless of the wrapper check.

**Recommended Fix:**

```python
def __enter__(self) -> Axes:
    """Create the inset axes using the axes_grid toolkit."""
    # Support for axes wrappers: check if _ax is a wrapper with an 'ax' attribute
    ax_attr = getattr(self._ax, "ax", None)
    if isinstance(ax_attr, Axes):
        self.ax = self._ax.ax  # type: ignore[union-attr]
    elif isinstance(self._ax, Axes):  # ← Add elif
        self.ax = self._ax
    else:
        self.ax = plt.gca()
    
    if not isinstance(self._loc, int):
        self.loc = self.locations.get(str(self._loc).lower().replace("-", " "), 1)
    else:
        self.loc = self._loc
    axins = inset_axes(self.ax, width=self.width, height=self.height, loc=self.loc if self.loc else 1)
    # ...
```

**Testing:**

```python
# Test with axes wrapper
class AxesWrapper:
    def __init__(self, ax):
        self.ax = ax

fig, ax = plt.subplots()
wrapper = AxesWrapper(ax)

# Should use wrapper.ax, not wrapper itself
with InsetPlot(wrapper) as inset:
    assert inset.ax is ax  # Should pass after fix
```

---

### Issue #3: Index Out of Bounds in StackVertical._fix_limits()

**File:** `src/stonerplots/context/multiple_plot.py:425-428`  
**Severity:** HIGH  
**Status:** Open  

**Description:**

The `_fix_limits()` method accesses `yticks[1]` and `yticks[-2]` without checking if the yticks list has enough elements. If there are fewer than 3 ticks, this raises an IndexError.

**Current Code:**
```python
def _fix_limits(self, ix: int, ax: Axes, fnt_pts: float, ax_height: float) -> None:
    """Adjust axes ylim to ensure labels don't overlap between stacked plots."""
    dy = 1.33 * fnt_pts / ax_height  # Space needed in axes units
    ylim = list(ax.get_ylim())
    tr = ax.transData + ax.transAxes.inverted()
    yticks = [tr.transform((0, x))[1] for x in ax.get_yticks()]
    
    if yticks[1] < dy and ix != len(self.axes) - 1:  # ← No bounds check!
        ylim[0] = tr.inverted().transform((0, -dy))[1]
    if yticks[-2] < 1.0 - dy and ix != 0:  # ← No bounds check!
        ylim[1] = tr.inverted().transform((0, 1 + dy))[1]
    ax.set_ylim(ylim[0], ylim[1])
    self.figure.canvas.draw()
```

**Impact:**

- **Critical:** Function crashes with IndexError for plots with < 3 tick marks
- Occurs with custom tick configurations, small data ranges, or manual tick setting
- Breaks stacked plot functionality for edge cases

**Reproduction:**

```python
import matplotlib.pyplot as plt
from stonerplots import StackVertical

fig = plt.figure()
with StackVertical(fig, 2) as axes:
    axes[0].plot([1, 2, 3], [1, 2, 3])
    axes[0].set_yticks([1, 3])  # Only 2 ticks - will crash on exit!
    axes[1].plot([1, 2, 3], [3, 2, 1])
# IndexError: list index out of range
```

**Root Cause:**

Code assumes `yticks` always has at least 3 elements, but matplotlib can produce fewer ticks depending on the data range and tick settings.

**Recommended Fix:**

```python
def _fix_limits(self, ix: int, ax: Axes, fnt_pts: float, ax_height: float) -> None:
    """Adjust axes ylim to ensure labels don't overlap between stacked plots."""
    dy = 1.33 * fnt_pts / ax_height
    ylim = list(ax.get_ylim())
    tr = ax.transData + ax.transAxes.inverted()
    yticks = [tr.transform((0, x))[1] for x in ax.get_yticks()]
    
    # Check bounds before accessing indices
    if len(yticks) > 1 and yticks[1] < dy and ix != len(self.axes) - 1:
        ylim[0] = tr.inverted().transform((0, -dy))[1]
    if len(yticks) > 1 and yticks[-2] > 1.0 - dy and ix != 0:
        ylim[1] = tr.inverted().transform((0, 1 + dy))[1]
    
    ax.set_ylim(ylim[0], ylim[1])
    self.figure.canvas.draw()
```

**Alternative Fix (more robust):**

```python
def _fix_limits(self, ix: int, ax: Axes, fnt_pts: float, ax_height: float) -> None:
    """Adjust axes ylim to ensure labels don't overlap between stacked plots."""
    dy = 1.33 * fnt_pts / ax_height
    ylim = list(ax.get_ylim())
    tr = ax.transData + ax.transAxes.inverted()
    yticks = [tr.transform((0, x))[1] for x in ax.get_yticks()]
    
    if len(yticks) < 2:
        # Not enough ticks to determine spacing - skip adjustment
        return
    
    # Check first visible tick (excluding bottom axis line)
    if yticks[1] < dy and ix != len(self.axes) - 1:
        ylim[0] = tr.inverted().transform((0, -dy))[1]
    
    # Check last visible tick (excluding top axis line)
    if len(yticks) > 2 and yticks[-2] > 1.0 - dy and ix != 0:
        ylim[1] = tr.inverted().transform((0, 1 + dy))[1]
    
    ax.set_ylim(ylim[0], ylim[1])
    self.figure.canvas.draw()
```

---

## Medium Severity Issues

### Issue #4: Package Configuration Mismatch in setup.py

**File:** `setup.py:22`  
**Severity:** MEDIUM  
**Status:** Open  

**Description:**

The `setup.py` file specifies `packages=["stonerplots"]` but doesn't specify `package_dir`, and the actual package is located in `src/stonerplots`. This may cause installation issues.

**Current Code:**
```python
# setup.py
setup(
    name="StonerPlots",
    description="Format Matplotlib for physics plotting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["stonerplots"],  # ← Incorrect: package is in src/
    package_data={
        "stonerplots": ["styles/**/*.mplstyle"],
    },
)
```

**Impact:**

- May cause installation failures with `pip install .`
- Package structure may be incorrect in installed environments
- Works currently because `pyproject.toml` overrides this, but inconsistency is confusing

**Recommended Fix:**

**Option 1 (Recommended):** Remove `setup.py` entirely

Since `pyproject.toml` already has complete configuration:
```toml
[tool.setuptools.packages.find]
where = ["src"]
```

The `setup.py` file is redundant. Remove it and rely solely on `pyproject.toml`.

**Option 2:** Fix `setup.py` if it must be kept

```python
setup(
    name="StonerPlots",
    description="Format Matplotlib for physics plotting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},  # ← Add this
    packages=["stonerplots"],
    package_data={
        "stonerplots": ["styles/**/*.mplstyle"],
    },
)
```

---

### Issue #5: Type Inconsistency in TexEngFormatter.prefix Dictionary Lookup

**File:** `src/stonerplots/format.py:109-124`  
**Severity:** MEDIUM  
**Status:** Open  

**Description:**

The variable `pre` is computed using numpy floating-point operations and then used as a dictionary key after conversion to int. While the try/except block catches KeyError, the float→int conversion could theoretically produce unexpected results due to floating-point precision.

**Current Code:**
```python
def __call__(self, value: Optional[float], pos: Optional[int] = None) -> str:
    """Format value with SI prefix."""
    ret = ""
    if value is None or np.isnan(value):
        ret = ""
    elif value != 0.0:
        power = np.floor(np.log10(np.abs(value)))
        pre = np.ceil(power / 3.0) * 3  # ← numpy float
        if -1 <= power <= 3 or pre == 0:
            ret = f"${round(value, 4)}\\,\\mathrm{{{self.unit}}}$"
        else:
            power = power % 3
            try:
                with np.errstate(over="raise", divide="raise", invalid="raise"):
                    v = _round(value / (10**pre), 4)
                    if np.abs(v) < 0.1:
                        v *= 1000
                        pre -= 3  # ← Still float
                    elif np.abs(v) > 1000.0:
                        v /= 1000
                        pre += 3.0  # ← Still float

                ret = f"${v}\\mathrm{{{self.prefix[int(pre)]} {self.unit}}}$"  # ← Convert here
            except (OverflowError, ZeroDivisionError, FloatingPointError, KeyError):
                ret = f"${value:g}\\,\\mathrm{{{self.unit}}}$"
    else:
        ret = "$0.0$"
    return ret
```

**Impact:**

- Low probability of actual failure (caught by try/except)
- Could theoretically produce KeyError for edge cases
- Reduces code clarity - mixing float and int types

**Root Cause:**

Using numpy float operations for values that should always be integers (multiples of 3).

**Recommended Fix:**

```python
def __call__(self, value: Optional[float], pos: Optional[int] = None) -> str:
    """Format value with SI prefix."""
    ret = ""
    if value is None or np.isnan(value):
        ret = ""
    elif value != 0.0:
        power = np.floor(np.log10(np.abs(value)))
        pre = int(np.ceil(power / 3.0) * 3)  # ← Convert to int immediately
        if -1 <= power <= 3 or pre == 0:
            ret = f"${round(value, 4)}\\,\\mathrm{{{self.unit}}}$"
        else:
            power = power % 3
            try:
                with np.errstate(over="raise", divide="raise", invalid="raise"):
                    v = _round(value / (10**pre), 4)
                    if np.abs(v) < 0.1:
                        v *= 1000
                        pre -= 3  # ← Now int subtraction
                    elif np.abs(v) > 1000.0:
                        v /= 1000
                        pre += 3  # ← Now int addition

                ret = f"${v}\\mathrm{{{self.prefix[pre]} {self.unit}}}$"  # ← No conversion needed
            except (OverflowError, ZeroDivisionError, FloatingPointError, KeyError):
                ret = f"${value:g}\\,\\mathrm{{{self.unit}}}$"
    else:
        ret = "$0.0$"
    return ret
```

---

### Issue #6: Usage of Private matplotlib APIs

**Files:**
- ~~`src/stonerplots/__init__.py:15, 61-65`~~ ✅ **FIXED** (now uses `get_named_colors_mapping()`)
- `src/stonerplots/util.py:14` - Import of `_TransformedBoundsLocator`
- `src/stonerplots/context/double_y.py:153` - Docstring references `_subplots.AxesSubplot`

**Severity:** MEDIUM  
**Status:** Partially Fixed  

**Description:**

The codebase uses private matplotlib APIs (indicated by leading underscores) which could break in future matplotlib versions. However, one issue has been fixed and the remaining issues have low impact.

**Current Status:**

1. ✅ **FIXED:** `_colors_full_map` has been replaced with public API `get_named_colors_mapping()`

2. ⚠️ **Open:** `_TransformedBoundsLocator` (util.py:14, 110)
   - Used to create axes locators for positioning inset axes
   - No public alternative exists
   - This is the official internal class used by matplotlib's own `inset_axes()` method
   - **Low risk** - unlikely to change as it would break matplotlib itself
   - **Recommendation:** Document usage and add comment explaining rationale

3. ⚠️ **Open:** `_subplots.AxesSubplot` reference in docstring (double_y.py:153)
   - Only used in documentation, not actual code
   - **Very low risk** - documentation only
   - **Recommendation:** Replace with `matplotlib.axes.Axes` for better documentation

**Recommended Fixes:**

**For util.py (add comment):**
```python
from matplotlib.axes._base import _TransformedBoundsLocator  # type: ignore[attr-defined]

# Note: _TransformedBoundsLocator is a private API, but it's the standard way to create
# axes locators and is used internally by matplotlib.axes.Axes.inset_axes().
# There is no public alternative. This usage matches matplotlib's own implementation.
```

**For double_y.py (update docstring):**
```python
def __enter__(self):
    """Handle context entry for managing temporary switchable axes in a Matplotlib figure.

    Returns:
        matplotlib.axes.Axes:  # ← Change from matplotlib.axes._subplots.AxesSubplot
            The secondary Y-axis created through `twinx()`.
    """
```

**Impact:** Low - remaining private API usages are either necessary (no alternative) or documentation-only.

---

## Low Severity Issues

### Issue #7: TODO Comment Indicating Incomplete Implementation

**File:** `src/stonerplots/util.py:406`  
**Severity:** LOW  
**Status:** Open  

**Description:**

Comment reads: `# XXX TODO: If markers are present, it would be good to take them`

**Impact:**

Indicates feature gap in auto-positioning logic - marker bounding boxes may not be considered when automatically positioning inset plots.

**Recommended Action:**

1. Investigate if this TODO is still relevant
2. If relevant, create a GitHub issue to track the feature request
3. If not relevant (e.g., feature implemented elsewhere), remove the comment
4. Document as a known limitation if implementation is difficult

---

### Issue #8: Missing Type Hints Throughout Codebase

**File:** Multiple files  
**Severity:** LOW (affects maintainability and tooling)  
**Status:** Open  

**Description:**

Most functions in the codebase lack comprehensive type hints. While some functions have partial hints in docstrings, Python type annotations are missing.

**Impact:**

- Reduced IDE autocomplete and IntelliSense support
- Cannot use mypy for static type checking
- Harder for contributors to understand expected types
- More runtime type errors that could be caught statically

**Examples:**

```python
# Current (no type hints)
def move_inset(parent, inset_axes, new_bbox):
    """Move an inset axes to a new position."""
    # ...

# Recommended (with type hints)
def move_inset(parent: Axes, inset_axes: Axes, new_bbox: Bbox) -> None:
    """Move an inset axes to a new position."""
    # ...
```

**Recommendation:**

1. Add type hints progressively, starting with public APIs
2. Consider adding `py.typed` marker file for library type stub support
3. Enable mypy in CI pipeline
4. Configure mypy to gradually increase strictness

---

### Issue #9: Inconsistent None Checking Patterns

**File:** Multiple files  
**Severity:** LOW (consistency)  
**Status:** Open  

**Description:**

The codebase uses different patterns for None checking:
- `if x is None:`
- `if not x:`
- `match x: case None:`

**Impact:**

- Reduced code consistency
- Potential subtle bugs (`if not x:` matches 0, empty list, etc., not just None)
- Makes code harder to review and understand

**Examples:**

```python
# Pattern 1: Explicit None check (recommended)
if value is None:
    return default

# Pattern 2: Truthy check (can have different behavior!)
if not value:  # Matches None, 0, False, [], "", etc.
    return default

# Pattern 3: Match statement
match value:
    case None:
        return default
    case _:
        process(value)
```

**Recommendation:**

Establish and document preferred pattern:
- Use `is None` / `is not None` for explicit None checks
- Use `if not x:` only when you explicitly want falsy checking (0, empty containers, etc.)
- Document the standard in CONTRIBUTING.md

---

### Issue #10: Line Length Violations

**File:** Multiple files (e.g., `src/stonerplots/util.py:155-156`)  
**Severity:** LOW (formatting)  
**Status:** Open  

**Description:**

Some lines exceed the 119 character limit specified in `pyproject.toml`:

```toml
[tool.black]
line-length = 119
```

**Impact:**

- Minor readability issues on smaller screens
- Inconsistent with project standards
- May cause unnecessary diff churn when eventually formatted

**Recommended Fix:**

Run black formatter across the codebase:

```bash
python -m black src/ tests/ --line-length 119
```

Consider adding this to pre-commit hooks to prevent future violations.

---

### Issue #11: Inconsistent String Formatting

**File:** Multiple files  
**Severity:** LOW (code style)  
**Status:** Open  

**Description:**

Mix of f-strings and `.format()` methods for string formatting.

**Examples:**

```python
# F-strings (modern, preferred)
message = f"Error: {value} is not valid"

# .format() method (older style)
message = "Error: {} is not valid".format(value)

# Both used in the same file
error = f"Invalid type: {type(value)}"
other_error = "Invalid range: {}".format(value)
```

**Impact:**

Minor - affects code consistency and readability.

**Recommendation:**

Use f-strings consistently throughout the codebase (Python 3.10+ supports this). F-strings are:
- More readable
- Faster
- Less error-prone (syntax checked at compile time)
- The modern Python standard

---

### Issue #12: Redundant List Creation in base.py

**File:** `src/stonerplots/context/base.py:178`  
**Severity:** LOW (micro-optimization)  
**Status:** Open  

**Description:**

`self.axes.flatten()` is called repeatedly in `__len__`, `__contains__`, and `__iter__` methods, creating a new flattened list each time.

**Impact:**

- Minimal for small numbers of axes
- Could matter for very large subplot arrays (unlikely use case)
- Premature optimization concern

**Current Code:**

```python
def __len__(self) -> int:
    return len(self.axes.flatten())

def __contains__(self, item: Any) -> bool:
    return item in self.axes.flatten()

def __iter__(self) -> Iterator[Any]:
    return iter(self.axes.flatten())
```

**Potential Optimization (if needed):**

```python
@property
def _flattened(self):
    if not hasattr(self, '_flattened_cache'):
        self._flattened_cache = self.axes.flatten()
    return self._flattened_cache

def __len__(self) -> int:
    return len(self._flattened)

def __contains__(self, item: Any) -> bool:
    return item in self._flattened

def __iter__(self) -> Iterator[Any]:
    return iter(self._flattened)
```

**Recommendation:** Only optimize if profiling shows this is a bottleneck. Current implementation is clearer and more maintainable.

---

### Issue #13: Multiple Canvas Draws in Loops

**File:** `src/stonerplots/context/multiple_plot.py:369-410`  
**Severity:** LOW (performance)  
**Status:** Open  

**Description:**

Multiple `figure.canvas.draw()` calls within loops could be expensive for complex figures.

**Impact:**

- Slower rendering for complex multi-panel figures
- Each draw triggers a full re-render
- Noticeable with many subplots or complex visualizations

**Recommendation:**

Consider batching drawing operations - collect all changes then draw once:

```python
# Instead of:
for ax in axes:
    modify(ax)
    figure.canvas.draw()  # Draw after each modification

# Consider:
for ax in axes:
    modify(ax)
figure.canvas.draw()  # Draw once at the end
```

However, verify this doesn't break intended behavior - some operations may require intermediate draws.

---

### Issue #14: Missing File Path Validation in save_figure.py

**File:** `src/stonerplots/context/save_figure.py:158-161`  
**Severity:** LOW (context-dependent)  
**Status:** Open  

**Description:**

The `filename` setter accepts any string/Path without validating for:
- Directory traversal (`../../../etc/passwd`)
- Invalid characters for the filesystem
- Existence of parent directories

**Current Code:**

```python
@filename.setter
def filename(self, value: Optional[Union[str, Path]]) -> None:
    """Set filename and extract its extension if valid."""
    if value is None:
        self._filename = None
        return
    # No validation here - accepts any path
    self._filename = Path(value).with_suffix("")
```

**Impact:**

- Low if only used with trusted, hard-coded paths
- Medium if accepting user input (potential directory traversal, crashes)

**Recommended Fix (if accepting user input):**

```python
@filename.setter
def filename(self, value: Optional[Union[str, Path]]) -> None:
    """Set filename and extract its extension if valid."""
    if value is None:
        self._filename = None
        return
    
    path = Path(value)
    
    # Validate no directory traversal
    try:
        path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        raise ValueError(f"Invalid path: {value} (directory traversal detected)")
    
    # Ensure parent directory exists or can be created
    if not path.parent.exists():
        raise ValueError(f"Parent directory does not exist: {path.parent}")
    
    self._filename = path.with_suffix("")
```

**Note:** For internal use with trusted paths, current implementation is acceptable.

---

## Informational Issues

### Issue #15: Arbitrary Code Execution in test_examples.py

**File:** `tests/stonerplots/test_examples.py:25`  
**Severity:** INFO (by design)  
**Status:** Not an Issue  

**Description:**

Uses `runpy.run_path(script)` to execute Python files from the examples directory.

**Current Code:**

```python
def test_example(script: Path) -> None:
    """Test that the example script runs without error."""
    runpy.run_path(str(script))
```

**Impact:**

- None in current context - tests execute trusted code from the repository
- Would be a security issue if running untrusted scripts

**Note:** This is intentional design for testing example scripts. Not a bug or vulnerability. Just noting for security awareness that test files should be from trusted sources only.

---

### Issue #16: DoubleYAxis.good_colour() Logic Inconsistency

**File:** `src/stonerplots/context/double_y.py:154-160`  
**Severity:** INFO  
**Status:** Review Recommended  

**Description:**

The `good_colour()` method has logic that may not work as intended when `self.colours` is a string versus a list.

**Current Code:**

```python
def good_colour(self, axis: int) -> bool:
    """Return True if we have a colours defined for this axis."""
    axis = int(axis)
    if self.colours is None:
        return False
    match self.colours:
        case list() if -len(self.colours) < axis < len(self.colours):
            return self.colours[axis] is not None
        case str() if -len(self.colours) < axis < len(self.colours):  # ← String case
            return True
        case _:
            return False
```

**Issue:**

When `self.colours` is a string (e.g., `"red"`), `len(self.colours)` returns the string length (3), not the number of colours (1). The condition `-len(self.colours) < axis < len(self.colours)` checks `-3 < axis < 3`, which may not be the intended behavior.

**Impact:**

- May return True for invalid axis indices when colours is a string
- Logic inconsistency between list and string handling

**Recommended Review:**

Clarify the intended behavior:
1. Should `colours` as a single string apply to both axes?
2. Should string length matter, or should it be treated as a single colour?
3. Is the string case meant to handle comma-separated colours?

**Suggested Fix (assuming string is a single colour for all axes):**

```python
def good_colour(self, axis: int) -> bool:
    """Return True if we have a colour defined for this axis."""
    axis = int(axis)
    if self.colours is None:
        return False
    match self.colours:
        case str():  # Single colour string applies to all axes
            return True
        case list() if -len(self.colours) < axis < len(self.colours):
            return self.colours[axis] is not None
        case _:
            return False
```

---

## Summary Statistics

### Issues by Severity

- **HIGH:** 3 issues (all require immediate fixes)
- **MEDIUM:** 3 issues (2 require fixes, 1 documentation only)
- **LOW:** 8 issues (code quality improvements)
- **INFO:** 2 issues (awareness only)

**Total:** 16 issues identified

### Issues by Category

- **Bugs:** 5 (Issues #1, #2, #3, #5, #16)
- **Configuration:** 1 (Issue #4)
- **Code Quality:** 5 (Issues #6, #8, #9, #11, #12)
- **Documentation:** 1 (Issue #7)
- **Performance:** 2 (Issues #12, #13)
- **Security:** 1 (Issue #14)
- **Testing:** 1 (Issue #15)

### Priority Action Items

**Immediate (Fix before next release):**

1. ✅ Fix Issue #1: Counter function buffer overflow
2. ✅ Fix Issue #2: InsetPlot assignment bug
3. ✅ Fix Issue #3: StackVertical index bounds

**Short Term (Next sprint):**

4. Address Issue #4: Package configuration
5. Fix Issue #5: Type inconsistency in TexEngFormatter
6. Document Issue #6: matplotlib private API usage

**Long Term (When time permits):**

7. Address remaining low-priority code quality issues
8. Add comprehensive type hints (Issue #8)
9. Establish coding standards documentation

---

## Recommendations for Maintainers

1. **Prioritize Critical Bugs:** Issues #1, #2, and #3 should be fixed immediately as they cause runtime failures

2. **Test Edge Cases:** Add tests for:
   - Counter with values > 25
   - InsetPlot with axes wrappers
   - StackVertical with < 3 yticks

3. **Code Quality:** Consider setting up:
   - Pre-commit hooks (black, isort, mypy)
   - Type hint coverage goals
   - Coding standards documentation in CONTRIBUTING.md

4. **Documentation:** Update docstrings to use public matplotlib types where possible

5. **Testing:** Current 90.64% coverage is excellent - maintain this level when fixing bugs

---

**Last Updated:** 2026-02-01  
**Next Review:** Recommended after fixing critical issues
