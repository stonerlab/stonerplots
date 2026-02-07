# GitHub Issues to Create from BUGS.md Review

This document contains all the issues from BUGS.md that still need to be created as GitHub issues.
The issues below are organized by priority. After creating the GitHub issues, this file can be deleted.

## Status Summary

Out of 16 issues originally listed in BUGS.md:

- **6 issues have been FIXED** and do not need GitHub issues
- **10 issues remain OPEN** and should be tracked as GitHub issues

---

## Medium Priority Issues

### Issue: Redundant type conversion in TexEngFormatter

**Labels:** `code-quality`, `good-first-issue`

**Description:**

In `src/stonerplots/format.py`, the variable `pre` is already converted to `int` on line 109:

```python
pre = int(np.ceil(power / 3.0) * 3)
```

However, line 124 redundantly converts it again:

```python
ret = f"${v}\\mathrm{{{self.prefix[int(pre)]} {self.unit}}}$"
```

This is not a bug but unnecessary code since `pre` is already an integer.

**Recommended Fix:**

Change line 124 from:

```python
ret = f"${v}\\mathrm{{{self.prefix[int(pre)]} {self.unit}}}$"
```

To:

```python
ret = f"${v}\\mathrm{{{self.prefix[pre]} {self.unit}}}$"
```

---

### Issue: Usage of private matplotlib API (_TransformedBoundsLocator)

**Labels:** `dependencies`, `technical-debt`

**Description:**

The code in `src/stonerplots/util.py:16` imports `_TransformedBoundsLocator` from matplotlib's private API:

```python
from matplotlib.axes._base import _TransformedBoundsLocator
```

While this is documented with a comment explaining there's no public alternative, it could break in future matplotlib versions.

**Impact:** Low risk - this class is used internally by matplotlib itself for the same purpose.

**Recommended Action:**

- Document the usage and rationale
- Monitor matplotlib releases for public alternative
- Consider creating a wrapper if matplotlib provides a public API

**Note:** The current implementation includes a comment acknowledging this limitation and explaining why it's necessary.

---

### Issue: Incorrect docstring reference to private matplotlib class

**Labels:** `documentation`, `good-first-issue`

**Description:**

The docstring in `src/stonerplots/context/double_y.py` (around line 165-167) references `matplotlib.axes._subplots.AxesSubplot` which is a private class.

**Recommended Fix:**

Update the docstring to reference the public API instead:

```python
def __enter__(self):
    """Handle context entry for managing temporary switchable axes in a Matplotlib figure.

    Returns:
        matplotlib.axes.Axes:  # Changed from matplotlib.axes._subplots.AxesSubplot
            The secondary Y-axis created through `twinx()`.
    """
```

---

## Low Priority Issues

### Issue: TODO comment for marker consideration in auto-positioning

**Labels:** `enhancement`, `help-wanted`

**Description:**

In `src/stonerplots/util.py:410`, there's a TODO comment:

```python
# XXX TODO: If markers are present, it would be good to take them
# into account when checking vertex overlaps in the next line.
```

This indicates that marker bounding boxes may not be considered when automatically positioning inset plots, which could lead to suboptimal placement when plots contain markers.

**Recommended Action:**

1. Investigate if this is still relevant
2. If relevant, implement marker consideration in auto-positioning logic
3. If not feasible, document as a known limitation
4. If already handled elsewhere, remove the comment

---

### Issue: Logic inconsistency in DoubleYAxis.good_colour()

**Labels:** `bug`, `needs-investigation`

**Description:**

In `src/stonerplots/context/double_y.py:157`, the `good_colour()` method has potentially incorrect logic when `self.colours` is a string:

```python
match self.colours:
    case list() if -len(self.colours) < axis < len(self.colours):
        return self.colours[axis] is not None
    case str() if -len(self.colours) < axis < len(self.colours):
        return True
    case _:
        return False
```

When `self.colours` is a string (e.g., `"red"`), `len(self.colours)` returns the string length (3 for "red"), not the number of colours (1). The condition `-len(self.colours) < axis < len(self.colours)` checks `-3 < axis < 3`, which may not be the intended behavior.

**Questions to Clarify:**

1. Should a string colour apply to all axes?
2. Should string length matter, or should it be treated as a single colour?
3. Is the string case meant to handle comma-separated colours?

**Suggested Fix (if string should apply to all axes):**

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

### Issue: Missing comprehensive type hints

**Labels:** `enhancement`, `code-quality`, `good-first-issue`

**Description:**

Most functions in the codebase lack comprehensive Python type annotations. While some functions have partial hints in docstrings, Python type annotations are missing.

**Impact:**

- Reduced IDE autocomplete and IntelliSense support
- Cannot use mypy for static type checking
- Harder for contributors to understand expected types
- More runtime type errors that could be caught statically

**Recommended Implementation:**

1. Add type hints progressively, starting with public APIs
2. Add `py.typed` marker file for library type stub support
3. Enable mypy in CI pipeline
4. Configure mypy to gradually increase strictness

**Example:**

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

---

### Issue: Inconsistent None checking patterns

**Labels:** `code-quality`, `style`

**Description:**

The codebase uses different patterns for None checking:

- `if x is None:`
- `if not x:`
- `match x: case None:`

**Impact:**

- Reduced code consistency
- Potential subtle bugs (`if not x:` matches 0, empty list, etc., not just None)
- Makes code harder to review and understand

**Recommended Standard:**

- Use `is None` / `is not None` for explicit None checks
- Use `if not x:` only when you explicitly want falsy checking (0, empty containers, etc.)
- Document the standard in CONTRIBUTING.md

**Example:**

```python
# Pattern 1: Explicit None check (recommended)
if value is None:
    return default

# Pattern 2: Truthy check (use only when you want to check for any falsy value)
if not value:  # Matches None, 0, False, [], "", etc.
    return default
```

---

### Issue: Line length violations

**Labels:** `code-quality`, `style`, `good-first-issue`

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

**Additional Recommendation:**

Add pre-commit hooks to prevent future violations.

---

### Issue: Inconsistent string formatting

**Labels:** `code-quality`, `style`

**Description:**

Mix of f-strings and `.format()` methods for string formatting throughout the codebase.

**Examples:**

```python
# F-strings (modern, preferred)
message = f"Error: {value} is not valid"

# .format() method (older style)
message = "Error: {} is not valid".format(value)
```

**Recommendation:**

Standardize on f-strings (Python 3.6+ supports this) as they are:

- More readable
- Faster
- Less error-prone (syntax checked at compile time)
- The modern Python standard

---

### Issue: Redundant list creation in flatten() calls

**Labels:** `performance`, `code-quality`

**Description:**

In `src/stonerplots/context/base.py:178`, `self.axes.flatten()` is called repeatedly in `__len__`, `__contains__`, and `__iter__` methods, creating a new flattened list each time.

**Current Code:**

```python
def __len__(self) -> int:
    return len(self.axes.flatten())

def __contains__(self, item: Any) -> bool:
    return item in self.axes.flatten()

def __iter__(self) -> Iterator[Any]:
    return iter(self.axes.flatten())
```

**Impact:**

- Minimal for small numbers of axes
- Could matter for very large subplot arrays (unlikely use case)

**Status:** This is a premature optimization concern. The current implementation is clearer and more maintainable.

**Recommendation:** Only optimize if profiling shows this is a bottleneck.

---

### Issue: Multiple canvas draws in loops

**Labels:** `performance`, `enhancement`

**Description:**

In `src/stonerplots/context/multiple_plot.py:369-410`, multiple `figure.canvas.draw()` calls within loops could be expensive for complex figures.

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

**Important:** Verify this doesn't break intended behavior - some operations may require intermediate draws for measurements or layout calculations.

---

### Issue: Missing file path validation in save_figure.py

**Labels:** `security`, `enhancement`

**Description:**

The `filename` setter in `src/stonerplots/context/save_figure.py:158-161` accepts any string/Path without validating for:

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

**Note:** For internal use with trusted paths, current implementation is acceptable. Only add validation if user input is accepted.

---

## Issues Already Fixed ✅

The following issues from BUGS.md have been **FIXED** and do **NOT** need GitHub issues:

1. **Counter buffer overflow** - Fixed with modulo 26 wraparound (`src/stonerplots/counter.py:76`)
2. **InsetPlot.__enter__() assignment bug** - Fixed with proper elif/else structure (`src/stonerplots/context/inset_plot.py:112-117`)
3. **StackVertical._fix_limits() index bounds** - Fixed with len checks before accessing list elements (`src/stonerplots/context/multiple_plot.py:426-428`)
4. **setup.py package configuration mismatch** - Fixed (setup.py removed, using pyproject.toml exclusively)
5. **_colors_full_map private API usage** - Fixed (now uses public `get_named_colors_mapping()` API in `src/stonerplots/__init__.py:61-65`)
6. **Arbitrary code execution in test_examples.py** - Not an issue (by design, tests run trusted repository code)

---

## After Creating Issues

Once you've created the above GitHub issues, you can:

1. Delete this file (`ISSUES_TO_CREATE.md`)
2. Verify that `.github/copilot-instructions.md` has been updated to reference GitHub issues
3. Confirm that `BUGS.md` has been removed from the repository

The updated workflow for copilot agents will be to create GitHub issues instead of writing to BUGS.md.
