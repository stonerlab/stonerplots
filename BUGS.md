# Code Review Report - StonerPlots Repository

This document contains issues and bugs discovered during a comprehensive code review of the stonerplots repository.

## Fixed Issues

### Issue 15 & 16: Weakref Comparison Bugs (HIGH SEVERITY) ✓ FIXED

**Files:** `src/stonerplots/context/base.py:284` and `src/stonerplots/context/base.py:305`
**Description:** The code was comparing actual figure/axes objects directly against lists/dicts containing weakrefs, which would always return False. This broke the filtering logic in the `new_figures` and `new_axes` properties.
**Fix Applied:** Modified both properties to properly dereference weakrefs before comparison. Also handles the case where items might already be dereferenced (for reusable context managers).
**Date Fixed:** 2026-01-19

## Documentation Issues

All previously documented issues have been fixed as of 2026-01-19:

- ✓ Issue 1: Fixed typo "insance" → "instance" in `__init__.py`
- ✓ Issue 2: Fixed reStructuredText syntax in `__init__.py`
- ✓ Issue 3: Added Examples section to `TexFormatter` class
- ✓ Issue 4: Completed `_round` function docstring with Args and Returns sections
- ✓ Issue 5: Updated and clarified minor/major formatting documentation in `PlotLabeller`
- ✓ Issue 7: Fixed `find_best_position` docstring to match actual function signature
- ✓ Issue 12: Added comment explaining overline LaTeX syntax in `counter.py`

### Issue 6: Docstring has Non-British English Spelling

**Status:** Not an issue
**Note:** The code uses "colours" parameter name (British) but matplotlib uses "color" (American) - this is intentional for API consistency.

### Issue 9: Inconsistent Type Checking Pattern

**Status:** Not an issue
**Note:** The code uses `isinstance(index, tuple)` check in `base.py:83-88`. While the codebase also uses match/case statements elsewhere, both patterns are valid Python and serve different purposes. `isinstance()` is appropriate for simple type checks, while match/case is better for structural pattern matching. The general coding standards don't mandate one pattern over the other, and both coexist legitimately in the codebase.

### Issue 11: Potential None Reference in double_y.py

**Status:** Not an issue
**Note:** The code `getattr(self._ax,"ax",None)` in `double_y.py:158` is correctly implemented. Python's `getattr()` handles None as the first argument gracefully - it returns the default value (None in this case) without raising an AttributeError. The subsequent `isinstance()` check then correctly evaluates to False, so the code flow is safe.

## Code Quality Issues

### Issue 8: Accessing Private matplotlib API ✓ REVIEWED

**Status:** Comprehensive review completed on 2026-01-20

**Files:**
- `src/stonerplots/__init__.py:15, 67-71` - Uses `_colors_full_map`
- `src/stonerplots/util.py:11, 110` - Uses `_TransformedBoundsLocator`
- `src/stonerplots/context/double_y.py:153` - References `_subplots.AxesSubplot` in docstring

**Description:** The codebase uses three private matplotlib APIs (indicated by leading underscores).

**Severity:** Low-Medium (potential breaking change in future matplotlib versions)

**Detailed Report:** See [CODE_REVIEW_README.md - Issue #8 Detailed Report](#issue-8-matplotlib-private-api-usage---detailed-report) for comprehensive analysis.

**Key Findings:**

1. `_colors_full_map` - **Public alternative available:** Use `get_named_colors_mapping()` (HIGH priority)
1. `_TransformedBoundsLocator` - **No public alternative:** Used internally by matplotlib, low risk (LOW priority)
1. `_subplots.AxesSubplot` - **Documentation only:** Use `Axes` type instead (MEDIUM priority)

**Recommendations:**

1. Replace `_colors_full_map` with `matplotlib.colors.get_named_colors_mapping()` (verified functionally identical)
1. Update type annotation in `double_y.py` docstring to use `matplotlib.axes.Axes`
1. Keep `_TransformedBoundsLocator` but add documentation explaining the usage
1. Monitor matplotlib releases for any breaking changes

**Risk:** Low for `_TransformedBoundsLocator` (used by matplotlib internally), Low-Medium for `_colors_full_map` (but has public alternative)

### Issue 10: Complex Nested Logic in util.py

**File:** `src/stonerplots/util.py:162-186`
**Description:** The `_process_artist` function has deeply nested match/case logic that could be simplified or split into smaller functions.
**Severity:** Low (maintainability)
**Recommendation:** Consider extracting some cases into separate handler functions

### Issue 12: Magic Numbers in counter.py

**File:** `src/stonerplots/counter.py:6-32`
**Description:** Large dictionary `ROMAN_NUMERAL_MAP` has magic numbers without explanation for the overline LaTeX syntax.
**Severity:** Low (documentation)
**Fix:** Add comment explaining that overlines represent multiplication by 1000 in Roman numerals

### Issue 13: Deprecated Parameter Warning

**File:** `src/stonerplots/context/multiple_plot.py:124-129`
**Description:** The code warns about deprecated `nplots` parameter but doesn't specify a removal version.
**Severity:** Low (deprecation policy)
**Recommendation:** Add version number for when this will be removed

## Potential Bugs

### Issue 14: Inconsistent Attribute Access in save_figure.py

**File:** `src/stonerplots/context/save_figure.py:281-282`
**Description:** Uses `getattr(self.use,"number",None)` which could return None and plt.figure(None) has specific behaviour (gets current figure).
**Severity:** Low (edge case handling)
**Test:** Verify behaviour when use.number is None

### Issue 17: Unsafe Division in format.py

**File:** `src/stonerplots/format.py:91-92`
**Description:** Division operation `value / (10**pre)` could potentially overflow or underflow for extreme values.
**Severity:** Low (edge case)
**Recommendation:** Add bounds checking or try/except for numerical errors

### Issue 18: Missing Renderer Parameter Handling

**File:** `src/stonerplots/util.py:266-290`
**Description:** The `find_best_position` function has `renderer=None` parameter but doesn't handle None case before using it.
**Severity:** Medium (potential NoneType error)
**Fix:** Add default renderer acquisition if None: `renderer = renderer or ax.figure.canvas.get_renderer()`

### Issue 19: Potential Index Error in StackVertical

**File:** `src/stonerplots/context/multiple_plot.py:398`
**Description:** Accesses `ax.yaxis.get_ticklabels()[0]` without checking if the list is non-empty.
**Severity:** Medium (potential IndexError)
**Fix:** Add check: `if ticklabels := ax.yaxis.get_ticklabels(): fnt_pts = ticklabels[0].get_fontsize()`

### Issue 20: Hardcoded Axis Name String

**File:** `src/stonerplots/context/inset_plot.py:107-108`
**Description:** Uses `getattr(self._ax,"ax",None)` assuming an "ax" attribute exists. This pattern is repeated in multiple files.
**Severity:** Low (duck typing assumption)
**Recommendation:** Document the expected protocol or use ABC

## Code Style Issues

### Issue 21: Inconsistent Import Grouping ✓ FIXED

**Files:** `src/stonerplots/context/double_y.py`, `src/stonerplots/context/inset_plot.py`, `src/stonerplots/context/__init__.py`
**Description:** Some files didn't follow the documented import grouping standard (stdlib, well-known third-party, other third-party, local). Multiple imports from the same module were not combined into one statement, and imports were not sorted alphabetically within groups.
**Fix Applied:**

- Combined duplicate imports from `.base` module in `double_y.py` and `inset_plot.py`
- Sorted imports alphabetically in `context/__init__.py`
**Date Fixed:** 2026-01-19

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
**Description:** `self.axes.flatten()` is called repeatedly in `__len__`, `__contains__`, and `__iter__` methods. Could cache the result.
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
**Description:** The filename setter accepts any string/Path without validation for directory traversal or invalid characters.
**Severity:** Low (depends on usage context)
**Recommendation:** Add path validation if accepting user input.

### Issue 28: Arbitrary Code Execution in test_examples.py

**File:** `tests/stonerplots/test_examples.py:25`
**Description:** Uses `runpy.run_path(script)` to execute arbitrary Python files. This is appropriate for testing but ensure test files are from trusted sources only.
**Severity:** Info (by design for testing)
**Note:** Not a bug, just noting for security awareness

## Missing Functionality

### Issue 29: TODO in format.py

**File:** `src/stonerplots/format.py:132-133`
**Description:** Todo comment indicates incomplete implementation: "This needs proper handling of minor/major formatting."
**Severity:** Medium (feature gap)
**Action Required:** Investigate if this is still needed or can be removed

### Issue 30: Incomplete Error Messages

**File:** `src/stonerplots/context/multiple_plot.py:163`
**Description:** Error message has f-string with variable but uses .format() elsewhere. Inconsistent string formatting.
**Severity:** Low (code style)
**Fix:** Use consistent f-string formatting throughout

## Testing Issues

### Issue 31: Limited Test Coverage

**File:** `tests/stonerplots/test_examples.py`
**Description:** Only one test file exists that runs example scripts. No unit tests for individual functions/classes.
**Severity:** Medium (test coverage)
**Recommendation:** Add unit tests for:

- Format classes (TexFormatter, TexEngFormatter, PlotLabeller)
- Utility functions (calculate_position, new_bbox_for_loc, etc.)
- Context managers with various parameter combinations
- Edge cases and error conditions

### Issue 32: No Tests for Error Conditions

**File:** Test suite
**Description:** No tests verify that appropriate errors are raised for invalid inputs.
**Severity:** Medium (test coverage)
**Recommendation:** Add tests for ValueError, TypeError, etc.

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

**Total Issues Found: 28** (2 issues reclassified as "Not an Issue")

- High Severity: 0 (2 fixed)
- Medium Severity: 11
- Low Severity: 15
- Info: 2

**Priority Fixes:**

1. ~~Issue #15 & #16: Fix weakref comparison bugs in base.py~~ ✓ FIXED
1. Issue #18: Add renderer None handling in util.py
1. Issue #19: Add bounds checking in StackVertical
1. Issue #8: Review matplotlib private API usage
1. Issue #31: Improve test coverage

**Code Quality Score: 8.0/10**
The codebase is generally well-structured with good use of modern Python features (match/case, context managers). Main areas for improvement are documentation completeness, type hints, test coverage, and fixing the remaining identified bugs.
