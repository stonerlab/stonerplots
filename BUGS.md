# Code Review Report - StonerPlots Repository

This document contains issues and bugs discovered during a comprehensive code review of the stonerplots repository.

## Documentation Issues

### Issue 1: Typo in __init__.py Docstring
**File:** `src/stonerplots/__init__.py:8`
**Description:** The word "insance" should be "instance" in the Attributes section.
**Severity:** Low (typo)
**Fix:** Change "insance" to "instance"

### Issue 2: Incorrect reStructuredText Syntax in __init__.py
**File:** `src/stonerplots/__init__.py:3`
**Description:** The docstring uses `:py:module\`stonerplots\`` which has incorrect backtick syntax. Should use proper reStructuredText role syntax.
**Severity:** Low (documentation formatting)
**Fix:** Change to `:py:mod:`stonerplots``

### Issue 3: Inconsistent Docstring Style in format.py
**File:** `src/stonerplots/format.py:19-39`
**Description:** The `TexFormatter` class docstring uses British English ("Formatting is set...") but lacks proper structure according to the project's documented standards. Missing Examples section for a public class.
**Severity:** Medium (documentation completeness)
**Fix:** Add Examples section to demonstrate usage

### Issue 4: Missing Docstring for _round Function
**File:** `src/stonerplots/format.py:9-16`
**Description:** The `_round` function has a docstring but it's incomplete - missing Args and Returns sections according to project standards.
**Severity:** Low (private function, but called from multiple places)
**Fix:** Complete docstring with Args and Returns sections

### Issue 5: Incomplete Docstring in format.py
**File:** `src/stonerplots/format.py:132-133`
**Description:** The Todo section mentions "This needs proper handling of minor/major formatting" which suggests incomplete implementation.
**Severity:** Medium (potential functionality gap)
**Action:** Review if minor/major formatting is properly handled or if this is still pending

### Issue 6: Docstring has Non-British English Spelling
**File:** `src/stonerplots/context/multiple_plot.py:31`
**Description:** Throughout the codebase, check for American spellings like "color" vs "colour".
**Severity:** Low (consistency)
**Note:** The code uses "colours" parameter name (British) but matplotlib uses "color" (American) - this is intentional for API consistency.

### Issue 7: Incomplete Documentation in util.py
**File:** `src/stonerplots/util.py:267-290`
**Description:** The `find_best_position` docstring has incorrect parameter list - mentions `loc` and `padding` parameters that don't exist in the function signature.
**Severity:** Medium (documentation accuracy)
**Fix:** Update docstring to match actual function signature (ax, axins, renderer=None)

## Code Quality Issues

### Issue 8: Accessing Private matplotlib API
**File:** `src/stonerplots/__init__.py:15`
**Description:** Imports `_colors_full_map` from `matplotlib.colors` which is a private API (indicated by leading underscore).
**Severity:** Medium (potential breaking change in future matplotlib versions)
**Risk:** Private APIs can change without warning
**Recommendation:** Consider using public matplotlib colour registration methods if available

### Issue 9: Inconsistent Type Checking Pattern
**File:** `src/stonerplots/context/base.py:83-88`
**Description:** Uses `isinstance(index, tuple)` check, but could benefit from more consistent use of match/case statements used elsewhere in the codebase.
**Severity:** Low (code style consistency)

### Issue 10: Complex Nested Logic in util.py
**File:** `src/stonerplots/util.py:162-186`
**Description:** The `_process_artist` function has deeply nested match/case logic that could be simplified or split into smaller functions.
**Severity:** Low (maintainability)
**Recommendation:** Consider extracting some cases into separate handler functions

### Issue 11: Potential None Reference in double_y.py
**File:** `src/stonerplots/context/double_y.py:158-160`
**Description:** Complex nested getattr access `getattr(self._ax,"ax",None)` could fail if _ax is None.
**Severity:** Low (defensive programming)
**Context:** The code does handle this, but the pattern is repeated and could be extracted to a helper

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

### Issue 15: List Comparison in base.py
**File:** `src/stonerplots/context/base.py:285`
**Description:** Line checks `if fig in self._existing_open_figs:` but `_existing_open_figs` contains weakrefs, not direct figure references.
**Severity:** High (potential bug)
**Fix:** Should check `if weakref.ref(fig) in self._existing_open_figs:` or dereference the weakrefs for comparison

### Issue 16: Dictionary Key Check on List
**File:** `src/stonerplots/context/base.py:305`
**Description:** Similar issue - `if ax in self._existing_open_axes:` but `_existing_open_axes` is a dict of figure numbers to weakref lists.
**Severity:** High (potential bug)
**Fix:** Need to check against the actual weakrefs in the dict values

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

### Issue 21: Inconsistent Import Grouping
**File:** Multiple files
**Description:** Some files don't follow the documented import grouping standard (stdlib, well-known third-party, other third-party, local).
**Example:** `src/stonerplots/format.py` has imports not grouped according to standard
**Severity:** Low (code style)
**Fix:** Reorganise imports according to documented standard

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

**Total Issues Found: 32**
- High Severity: 2
- Medium Severity: 11
- Low Severity: 17
- Info: 2

**Priority Fixes:**
1. Issue #15 & #16: Fix weakref comparison bugs in base.py
2. Issue #18: Add renderer None handling in util.py
3. Issue #19: Add bounds checking in StackVertical
4. Issue #8: Review matplotlib private API usage
5. Issue #31: Improve test coverage

**Code Quality Score: 7.5/10**
The codebase is generally well-structured with good use of modern Python features (match/case, context managers). Main areas for improvement are documentation completeness, type hints, test coverage, and fixing the identified bugs.
