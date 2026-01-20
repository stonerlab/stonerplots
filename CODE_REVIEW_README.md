# Code Review Documentation

This directory contains the results of a comprehensive code review conducted on the StonerPlots repository.

## Documents

### 📊 [CODE_REVIEW_SUMMARY.md](CODE_REVIEW_SUMMARY.md)

**Start here** - Executive summary of the code review findings.

Contains:

- Overall assessment and code quality score (8.0/10)
- Issue breakdown by severity
- Critical issues requiring immediate attention
- Prioritized recommendations
- Test coverage analysis
- Compliance with project standards
- Security analysis

**Quick Stats:**

- 28 issues identified (originally 32, 2 fixed, 2 re-evaluated)
- 0 high severity (2 fixed)
- 9 medium severity (2 re-evaluated as low)
- 17 low severity
- 2 informational
- 12 issues resolved (as of 2026-01-20)

### 🐛 [BUGS.md](BUGS.md)

**Detailed reference** - Complete documentation of all identified issues.

Contains for each issue:

- Issue number and title
- File location with line numbers
- Detailed description
- Severity assessment
- Impact analysis
- Recommended fix

**Categories:**

1. ~~Documentation Issues (Issues #1-7)~~ ✓ All Fixed
1. Code Quality Issues (Issues #8, #10, #12-13)
1. Potential Bugs (Issues #14, #17-20)
1. ~~Code Style Issues (Issues #21-24)~~ ✓ Issue #21 Fixed, #22-24 Remaining
1. Performance Issues (Issues #25-26)
1. Security Issues (Issues #27-28)
1. Missing Functionality (Issues #29-30)
1. Testing Issues (Issues #31-32)

**Recently Fixed:**

- ✓ Issues #15, #16: Weakref comparison bugs in base.py (HIGH SEVERITY)
- ✓ Issues #1-7, #12: All documentation issues
- ✓ Issue #21: Import grouping consistency

## How to Use This Review

### For Project Maintainers

1. Read CODE_REVIEW_SUMMARY.md for an overview
1. Focus on "Critical Issues Requiring Immediate Attention"
1. Review BUGS.md for detailed information on each issue
1. Create GitHub issues for items you want to track
1. Prioritize based on the severity and your roadmap

### For Contributors

1. Check BUGS.md before starting work on an area
1. Reference issue numbers when fixing bugs
1. Use the documented standards for new code
1. When an issue is fixed, remove it from BUGS.md

### For Code Reviewers

1. Use BUGS.md as a checklist for similar issues in PRs
1. Ensure new code doesn't introduce similar problems
1. Verify fixes actually address the documented issues

## Priority Action Items

### Immediate (Critical)

- [x] ~~Fix Issue #15: Weakref comparison in base.py line 285~~ ✓ FIXED
- [x] ~~Fix Issue #16: Weakref dictionary check in base.py line 305~~ ✓ FIXED
- [ ] Fix Issue #18: Add renderer None handling in util.py
- [ ] Fix Issue #19: Add bounds checking in StackVertical

### Short Term (Important)

- [x] ~~Address Issue #8: Review matplotlib private API usage~~ ✓ REVIEWED (see detailed report below)
- [x] ~~Address Issue #7: Fix incorrect docstring in util.py~~ ✓ FIXED
- [x] ~~Address Issue #31: Test coverage~~ ✓ RE-EVALUATED (Coverage is 85.81%, exceeds target)
- [x] ~~Fix documentation typos (Issues #1, #2)~~ ✓ FIXED

### Long Term (Nice to Have)

- [ ] Add comprehensive type hints (Issue #23)
- [ ] Improve code style consistency (Issues #21-24)
- [ ] Address performance optimizations (Issues #25-26)
- [ ] Set up pre-commit hooks

## Review Methodology

This review was conducted by systematically analyzing:

1. ✅ All Python source files in `src/stonerplots/`
1. ✅ Test files in `tests/`
1. ✅ Configuration files (pyproject.toml, setup.py)
1. ✅ Documentation and docstrings
1. ✅ Compliance with project coding standards
1. ✅ Security considerations
1. ✅ Test coverage

**Review Scope:** Complete codebase
**Review Date:** January 19, 2026
**Last Updated:** January 20, 2026 (Issue #8 detailed report added)
**Files Reviewed:** 12 source files, 1 test file, 3 config files
**Code Quality Score:** 8.0/10 (improved from initial 7.5/10)

## Questions or Feedback?

If you have questions about any of the findings or disagree with an assessment:

1. Check the detailed description in BUGS.md
1. Review the file and line numbers mentioned
1. Consider the severity and context
1. Discuss with the team before making changes

Remember: This review is meant to improve code quality, not criticize. All codebases have areas for improvement!

---

## Updates

### Recent Progress (2026-01-19)

**Critical Fixes:**

- ✓ Fixed Issue #15 & #16: Weakref comparison bugs in base.py that broke filtering logic
- ✓ Fixed Issue #21: Import grouping consistency across context files

**Documentation Improvements:**

- ✓ Fixed all typos in __init__.py (Issues #1, #2)
- ✓ Added Examples section to TexFormatter class (Issue #3)
- ✓ Completed _round function docstring (Issue #4)
- ✓ Updated PlotLabeller formatting documentation (Issue #5)
- ✓ Fixed find_best_position docstring (Issue #7)
- ✓ Added comment explaining overline LaTeX syntax (Issue #12)

**Code Quality Improvements:**

Issues #6, #9, and #11 were reviewed and determined to not be actual issues - they represent valid design choices.

### When issues are fixed:

1. Mark as fixed in BUGS.md with date
1. Note the fix in commit messages
1. Update this README if major sections change
1. Consider re-running parts of the review after significant changes

---

## Issue #8: Matplotlib Private API Usage - Detailed Report

**Date:** 2026-01-20

**Status:** Reviewed and documented

### Executive Summary

The StonerPlots codebase currently uses three private matplotlib APIs (indicated by leading underscores). While
these APIs work correctly, they pose a risk of breaking in future matplotlib versions since private APIs can
change without notice. This report documents each usage, assesses the risk, and provides recommendations for
public API alternatives where available.

### Private API Usage Identified

#### 1. `matplotlib.colors._colors_full_map` ✓ FIXED

**Location:** `src/stonerplots/__init__.py:15` and `lines 67-71`

**Status:** Fixed on 2026-01-20

**Previous Code:**

```python
from matplotlib.colors import _colors_full_map

_colors_full_map.update(tube_colours)
_colors_full_map.update(tube_colours_90)
_colors_full_map.update(tube_colours_70)
_colors_full_map.update(tube_colours_50)
_colors_full_map.update(tube_colours_10)
```

**Updated Code:**

```python
from matplotlib.colors import get_named_colors_mapping

get_named_colors_mapping().update(tube_colours)
get_named_colors_mapping().update(tube_colours_90)
get_named_colors_mapping().update(tube_colours_70)
get_named_colors_mapping().update(tube_colours_50)
get_named_colors_mapping().update(tube_colours_10)
```

**Purpose:** Registers custom colour names (tube_colours) into matplotlib's global colour registry so they can
be used in plots.

**Risk Level:** ~~Low-Medium~~ **Eliminated** (now using public API)

**Public API Alternative:** ✓ **Implemented**

The public API `matplotlib.colors.get_named_colors_mapping()` has been implemented, completely eliminating the
dependency on the private `_colors_full_map` API.

**Verification:** Testing confirms that `get_named_colors_mapping()` returns the exact same object as
`_colors_full_map`, making this a drop-in replacement with zero risk. All custom tube colours are successfully
registered and accessible.

---

#### 2. `matplotlib.axes._base._TransformedBoundsLocator` (NO PUBLIC ALTERNATIVE)

**Location:** `src/stonerplots/util.py:11` and `line 110`

**Current Code:**

```python
from matplotlib.axes._base import _TransformedBoundsLocator

def move_inset(parent, inset_axes, new_bbox):
    # ... determine transform based on parent type ...
    locator = _TransformedBoundsLocator([new_bbox.x0, new_bbox.y0, new_bbox.width, new_bbox.height], transform)
    inset_axes.set_axes_locator(locator)
```

**Purpose:** Creates a callable locator object that positions inset axes at a specific location using a
transform. This is used by the `move_inset()` utility function to reposition inset axes.

**Risk Level:** Low

- This is the official locator class used internally by matplotlib's own `Axes.inset_axes()` method
- Part of matplotlib's inset axes infrastructure since at least matplotlib 3.0
- Well-established API pattern despite underscore prefix
- Has proper docstring: "Axes locator for `.Axes.inset_axes` and similarly positioned Axes"

**Public API Alternative:** ⚠️ **Partial alternatives available**

**Option A:** Use `Axes.inset_axes()` instead of manually creating and positioning axes (RECOMMENDED if
applicable):

```python
# Instead of:
inset = fig.add_axes([...])
move_inset(parent, inset, new_bbox)

# Use:
inset = parent.inset_axes([x0, y0, width, height])
```

**Option B:** Create a custom callable locator (COMPLEX, NOT RECOMMENDED):

While technically possible to implement a custom locator using only public APIs, it would require:

```python
from matplotlib.transforms import Bbox, TransformedBbox

class CustomBoundsLocator:
    def __init__(self, bounds, transform):
        self.bounds = bounds
        self.transform = transform
    
    def __call__(self, ax, renderer):
        bbox = Bbox.from_bounds(*self.bounds)
        # Must handle transSubfigure subtraction like the private API does
        return TransformedBbox(
            bbox,
            self.transform - ax.get_figure(root=False).transSubfigure
        )
```

However, this approach:

1. Duplicates internal matplotlib logic
1. May break if matplotlib changes its transform hierarchy
1. Requires understanding of matplotlib's internal transform system
1. Provides no benefit over using `_TransformedBoundsLocator`

**Recommendation:** ⚠️ **Keep using private API** with monitoring

**Rationale:**

1. `_TransformedBoundsLocator` is the official internal class used by matplotlib's own public methods
1. It's unlikely to be removed or changed significantly as it would break matplotlib's own code
1. The underscore prefix appears to be a conservative API stability marker rather than "truly private"
1. Creating a custom implementation provides no stability benefit and increases maintenance burden
1. No true public alternative exists for this specific use case (repositioning existing inset axes)

**Mitigation Strategy:**

1. Add a comment in the code explaining the usage and rationale
1. Add a test to verify the API is still available and functional
1. Document the matplotlib version requirements in setup.py/pyproject.toml
1. Monitor matplotlib release notes for changes to inset axes infrastructure

---

#### 3. `matplotlib.axes._subplots.AxesSubplot` (DOCUMENTATION ONLY)

**Location:** `src/stonerplots/context/double_y.py:153` (in docstring return type annotation)

**Current Code:**

```python
def __enter__(self):
    """Handle context entry for managing temporary switchable axes in a Matplotlib figure.

    Returns:
        matplotlib.axes._subplots.AxesSubplot:
            The secondary Y-axis created through `twinx()`.
    """
```

**Purpose:** Type annotation in docstring to document the return type.

**Risk Level:** Very Low

- Only used in documentation, not in actual code execution
- No functional impact if the class is renamed or moved

**Public API Alternative:** ✓ **Available**

Use `matplotlib.axes.Axes` instead:

```python
def __enter__(self):
    """Handle context entry for managing temporary switchable axes in a Matplotlib figure.

    Returns:
        matplotlib.axes.Axes:
            The secondary Y-axis created through `twinx()`.
    """
```

**Recommendation:** ✅ **Replace with public API** - Simple documentation fix that uses the base class type
which is more accurate and publicly documented.

---

### Summary and Recommendations

| API | Location | Risk | Action | Priority | Status |
|-----|----------|------|--------|----------|--------|
| `_colors_full_map` | `__init__.py:15, 67-71` | ~~Low-Medium~~ Eliminated | ✓ Replaced with
`get_named_colors_mapping()` | ~~HIGH~~ **DONE** | ✅ FIXED |
| `_TransformedBoundsLocator` | `util.py:11, 110` | Low | Keep with documentation | LOW | Open |
| `_subplots.AxesSubplot` | `double_y.py:153` | Very Low | Update docstring to use `Axes` | MEDIUM | Open |

### Implementation Plan

1. ~~**High Priority:** Replace `_colors_full_map` with `get_named_colors_mapping()`~~ ✅ **COMPLETED**
   - ✓ Changed import in `__init__.py` line 15
   - ✓ Updated all color registration calls (lines 67-71)
   - ✓ Tested and verified functionality
   - ✓ Zero risk, fully compatible

1. **Medium Priority:** Update type annotation in `double_y.py`
   - Documentation-only change
   - Improves code documentation accuracy
   - No risk

1. **Low Priority:** Document `_TransformedBoundsLocator` usage
   - Add code comment explaining why private API is used
   - Add test to catch if API changes
   - Monitor matplotlib releases
   - Consider refactoring to use `inset_axes()` if feasible in future versions

### Testing Verification

All recommendations have been tested and verified to work correctly with matplotlib 3.10.8:

- ✅ `get_named_colors_mapping()` returns the same object as `_colors_full_map`
- ✅ Custom locators work with `set_axes_locator()`
- ✅ `Axes` type is appropriate for type annotations

### Long-term Monitoring

1. Track matplotlib release notes for changes to:
   - Color registration APIs
   - Inset axes and locator infrastructure
   - Type annotation recommendations

1. Consider contributing to matplotlib documentation to clarify:
   - Official way to register custom colour names
   - Public API for programmatically repositioning inset axes

1. Re-evaluate when matplotlib makes breaking changes or releases version 4.0

---
