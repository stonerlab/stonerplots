# Code Review Report - StonerPlots Repository

This document contains issues and bugs discovered during a comprehensive code review of the stonerplots repository.

## Code Quality Issues

### Issue 8: Accessing Private matplotlib API ✓ PARTIALLY FIXED

**Status:** Fix implemented on 2026-01-20

**Files:**

- ~~`src/stonerplots/__init__.py:15, 67-71` - Uses `_colors_full_map`~~ ✓ FIXED
- `src/stonerplots/util.py:11, 110` - Uses `_TransformedBoundsLocator`
- `src/stonerplots/context/double_y.py:153` - References `_subplots.AxesSubplot` in docstring

**Description:** The codebase uses three private matplotlib APIs (indicated by leading underscores).

**Severity:** Low-Medium (potential breaking change in future matplotlib versions)

**Detailed Report:** See CODE_REVIEW_README.md - Issue #8 Detailed Report
(<#issue-8-matplotlib-private-api-usage---detailed-report>) for comprehensive analysis.

**Key Findings:**

1. ~~`_colors_full_map`~~ ✓ **FIXED** - Replaced with `get_named_colors_mapping()`
1. `_TransformedBoundsLocator` - **No public alternative:** Used internally by matplotlib, low risk (LOW priority)
1. `_subplots.AxesSubplot` - **Documentation only:** Use `Axes` type instead (MEDIUM priority)

**Fix Applied:**

Replaced all uses of `_colors_full_map` with the public API `get_named_colors_mapping()` in `__init__.py`:

- Changed import from `from matplotlib.colors import _colors_full_map` to
  `from matplotlib.colors import get_named_colors_mapping`
- Updated color registration calls to use `get_named_colors_mapping().update(...)`

**Verification:** Testing confirms the public API works correctly and all custom tube colours are successfully
registered.

**Remaining Recommendations:**

1. Update type annotation in `double_y.py` docstring to use `matplotlib.axes.Axes`
1. Keep `_TransformedBoundsLocator` but add documentation explaining the usage
1. Monitor matplotlib releases for any breaking changes

**Risk:** Low for remaining private APIs

### Issue 10: Complex Nested Logic in util.py

**File:** `src/stonerplots/util.py:162-186`
**Description:** The `_process_artist` function has deeply nested match/case logic that could be simplified or
split into smaller functions.
**Severity:** Low (maintainability)
**Recommendation:** Consider extracting some cases into separate handler functions

### Issue 13: Deprecated Parameter Warning

**File:** `src/stonerplots/context/multiple_plot.py:124-129`
**Description:** The code warns about deprecated `nplots` parameter but doesn't specify a removal version.
**Severity:** Low (deprecation policy)
**Recommendation:** Add version number for when this will be removed

## Potential Bugs

### Issue 14: Inconsistent Attribute Access in save_figure.py

**File:** `src/stonerplots/context/save_figure.py:281-282`
**Description:** Uses `getattr(self.use,"number",None)` which could return None and plt.figure(None) has specific
behaviour (gets current figure).
**Severity:** Low (edge case handling)
**Test:** Verify behaviour when use.number is None

### Issue 17: Unsafe Division in format.py

**File:** `src/stonerplots/format.py:91-92`
**Description:** Division operation `value / (10**pre)` could potentially overflow or underflow for extreme values.
**Severity:** Low (edge case)
**Recommendation:** Add bounds checking or try/except for numerical errors

### Issue 18: Missing Renderer Parameter Handling

**File:** `src/stonerplots/util.py:266-290`
**Description:** The `find_best_position` function has `renderer=None` parameter but doesn't handle None case
before using it.
**Severity:** Medium (potential NoneType error)
**Fix:** Add default renderer acquisition if None: `renderer = renderer or ax.figure.canvas.get_renderer()`

### Issue 19: Potential Index Error in StackVertical

**File:** `src/stonerplots/context/multiple_plot.py:398`
**Description:** Accesses `ax.yaxis.get_ticklabels()[0]` without checking if the list is non-empty.
**Severity:** Medium (potential IndexError)
**Fix:** Add check: `if ticklabels := ax.yaxis.get_ticklabels(): fnt_pts = ticklabels[0].get_fontsize()`

### Issue 20: Hardcoded Axis Name String

**File:** `src/stonerplots/context/inset_plot.py:107-108`
**Description:** Uses `getattr(self._ax,"ax",None)` assuming an "ax" attribute exists. This pattern is repeated in
multiple files.
**Severity:** Low (duck typing assumption)
**Recommendation:** Document the expected protocol or use ABC

## Code Style Issues

### Issue 22: Line Length Exceeds Standards

**File:** `src/stonerplots/util.py:155-156`
**Description:** Some lines exceed the 119 character limit for non-example code.
**Severity:** Low (formatting)
**Tool:** Run black formatter to fix

### Issue 23: Missing Type Hints

**File:** Multiple files
**Description:** Most functions lack type hints, which would improve IDE support and catch type-related bugs early.
**Severity:** Medium (maintainability and tooling)
**Recommendation:** Add type hints progressively, starting with public APIs

### Issue 24: Inconsistent None Checking

**File:** Multiple files
**Description:** Mix of `if x is None:`, `if not x:`, and `match x: case None:` patterns.
**Severity:** Low (consistency)
**Recommendation:** Establish and document preferred pattern

## Performance Issues

### Issue 25: Redundant List Creation in base.py

**File:** `src/stonerplots/context/base.py:178`
**Description:** `self.axes.flatten()` is called repeatedly in `__len__`, `__contains__`, and `__iter__` methods.
Could cache the result.
**Severity:** Low (micro-optimization)
**Impact:** Only matters for large numbers of axes

### Issue 26: Multiple Canvas Draws

**File:** `src/stonerplots/context/multiple_plot.py:369-410`
**Description:** Multiple `figure.canvas.draw()` calls in loops could be expensive for complex figures.
**Severity:** Low (performance)
**Recommendation:** Consider batching drawing operations

## Security Issues

### Issue 27: No Input Validation for File Paths

**File:** `src/stonerplots/context/save_figure.py:136-161`
**Description:** The filename setter accepts any string/Path without validation for directory traversal or invalid
characters.
**Severity:** Low (depends on usage context)
**Recommendation:** Add path validation if accepting user input.

### Issue 28: Arbitrary Code Execution in test_examples.py

**File:** `tests/stonerplots/test_examples.py:25`
**Description:** Uses `runpy.run_path(script)` to execute arbitrary Python files. This is appropriate for testing
but ensure test files are from trusted sources only.
**Severity:** Info (by design for testing)
**Note:** Not a bug, just noting for security awareness

## Missing Functionality

### Issue 29: TODO in format.py

**File:** `src/stonerplots/format.py:132-133`
**Description:** Todo comment indicates incomplete implementation: "This needs proper handling of minor/major
formatting."
**Severity:** Medium (feature gap)
**Action Required:** Investigate if this is still needed or can be removed

### Issue 30: Incomplete Error Messages

**File:** `src/stonerplots/context/multiple_plot.py:163`
**Description:** Error message has f-string with variable but uses .format() elsewhere. Inconsistent string
formatting.
**Severity:** Low (code style)
**Fix:** Use consistent f-string formatting throughout

## Testing Issues

### Issue 32: No Tests for Error Conditions

**File:** Test suite
**Description:** No tests verify that appropriate errors are raised for invalid inputs.
**Severity:** Low (given good overall coverage)
**Recommendation:** Consider adding tests for ValueError, TypeError, etc. in future iterations

## Recommendations

### Recommendation 1: Add Type Stubs

Consider adding a py.typed marker and type stubs (.pyi files) for better IDE support and type checking.

### Recommendation 2: Add Pre-commit Hooks

Set up pre-commit hooks for:

- black (code formatting)
- isort (import sorting)
- flake8 or ruff (linting)
- mypy (type checking)

### Recommendation 3: Improve Documentation

- Add more examples to docstrings
- Create a CONTRIBUTING.md with coding standards
- Document the expected protocols for custom axes-like objects

### Recommendation 4: Version Documentation

Document which matplotlib versions are supported and test against multiple versions.

### Recommendation 5: Add Logging

Consider adding logging (using Python's logging module) instead of or in addition to warnings for better debugging.

---

## Summary

**Total Issues Found: 18** (excluding fixed issues and items reclassified as "Not an Issue")

- High Severity: 0
- Medium Severity: 3
- Low Severity: 13
- Info: 2

**Priority Fixes:**

1. Issue #18: Add renderer None handling in util.py
1. Issue #19: Add bounds checking in StackVertical
1. Issue #8: Review matplotlib private API usage

**Code Quality Score: 8.0/10**
The codebase is generally well-structured with good use of modern Python features (match/case, context managers).
Main areas for improvement are documentation completeness, type hints, and fixing the remaining identified bugs.
