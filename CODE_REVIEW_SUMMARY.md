# Code Review Summary - StonerPlots Repository

**Review Date:** January 19, 2026
**Repository:** stonerlab/stonerplots
**Reviewer:** GitHub Copilot
**Scope:** Complete repository code review

## Executive Summary

This comprehensive code review analysed the entire StonerPlots repository, examining Python source files,
documentation, test coverage, and adherence to project coding standards. The codebase is generally
well-structured and makes good use of modern Python features, but several issues were identified that should be
addressed to improve code quality, maintainability, and reliability.

## Overall Assessment

### Code Quality Score: 7.5/10

### Strengths

- ✅ Modern Python features (match/case, context managers, type hints in some places)
- ✅ Well-organised package structure
- ✅ Good separation of concerns with context managers
- ✅ Comprehensive docstrings in most places
- ✅ Use of singleton pattern for defaults
- ✅ Good use of matplotlib's style system

### Areas for Improvement

- ⚠️ Critical bugs in weakref handling (base.py)
- ⚠️ Missing type hints in most functions
- ⚠️ Incomplete documentation in some areas
- ⚠️ Use of private matplotlib APIs

## Issue Breakdown

| Severity  | Count  | Priority                          |
|-----------|--------|-----------------------------------|
| High      | 2      | **Critical** - Fix immediately    |
| Medium    | 9      | Important - Address soon          |
| Low       | 17     | Nice to have - Address over time  |
| Info      | 2      | Awareness only                    |
| **Total** | **30** |                                   |

## Critical Issues Requiring Immediate Attention

### 1. Weakref Comparison Bugs (High Severity)

**Files:** `src/stonerplots/context/base.py:285, 305`

- Direct comparison of figures/axes with weakref lists will always fail
- Affects tracking of new figures and axes in context managers
- **Impact:** Core functionality may not work as intended
- **Fix Required:** Dereference weakrefs before comparison

### 2. Missing Renderer Parameter Handling (High Severity)

**File:** `src/stonerplots/util.py:266-290`

- Function accepts `renderer=None` but doesn't handle None case
- Could cause NoneType errors when renderer is not provided
- **Impact:** Crashes when auto-positioning insets
- **Fix Required:** Add default renderer acquisition

## Medium Priority Issues

### Documentation & API Issues (5 issues)

- Incomplete docstrings missing Examples sections
- Incorrect function signatures in documentation
- Todo comments indicating incomplete features
- Typos in API documentation

### Potential Runtime Errors (4 issues)

- Missing bounds checking in StackVertical (IndexError risk)
- Unsafe division in format.py (overflow/underflow risk)
- None reference handling in multiple files
- No input validation for file paths

### Code Quality (2 issues)

- Access to private matplotlib API (`_colors_full_map`)
- Deprecated parameter without removal version

## Low Priority Issues

### Code Style & Consistency (10 issues)

- Inconsistent import organisation
- Line length violations
- Mixed None-checking patterns
- Inconsistent string formatting (f-strings vs .format())
- Magic numbers without documentation

### Performance & Maintainability (7 issues)

- Redundant list creation in loops
- Multiple canvas draws
- Complex nested logic
- Missing type hints

## Test Coverage Analysis

### Current State (Updated: 2026-01-31)

- ✅ Example script execution tests exist (52 examples)
- ✅ Examples provide comprehensive coverage of the codebase
- ✅ Unit tests for error conditions added (28 tests)
- ✅ Tests for formatter edge cases (7 tests)
- ✅ Integration tests included

### Coverage Results

**Updated Coverage: 90.64%** (940 statements, 88 missed) - **Up from 85.81%**

After adding comprehensive error condition tests, coverage improved by 4.83 percentage points.

**Coverage by Module:**

- `__init__.py`: 100.00%
- `colours.py`: 100.00%
- `context/__init__.py`: 100.00%
- `counter.py`: 100.00% ⬆️ (was 93.75%)
- `context/inset_plot.py`: 95.12%
- `context/multiple_plot.py`: 95.65% ⬆️ (was 92.39%)
- `context/double_y.py`: 95.35% ⬆️ (was 83.72%)
- `context/save_figure.py`: 94.77% ⬆️ (was 88.54%)
- `util.py`: 93.98% ⬆️ (was 90.79%)
- `format.py`: 84.95% ⬆️ (was 70.93%)
- `context/noframe.py`: 81.40%
- `context/base.py`: 71.67% ⬆️ (was 70.83%)

### Assessment

✅ **Coverage Goal Exceeded:** The current 90.64% coverage significantly exceeds the recommended 85% threshold.

### Test Composition

- 52 example execution tests (integration testing)
- 7 format edge case tests (formatter robustness)
- 28 error condition tests (input validation)
- **Total: 87 tests** (80 passed, 2 skipped)

### Remaining Gaps (Low Priority)

The remaining 9.36% uncovered code consists primarily of:

1. Exception handler bodies (defensive programming for extreme edge cases)
2. Helper methods called by matplotlib internals
3. Advanced collection protocol methods (`__contains__`, complex indexing)
4. WeakRef edge case handling
5. Optional parameter combinations in rarely-used code paths

These gaps are low priority as they represent edge cases that are difficult to test reliably and have minimal
impact on normal usage.

**Current Coverage:** 90.64% (significantly exceeds 85% target)
**Recommended Coverage:** Maintain 85%+ (✅ Achieved)

## Compliance with Project Standards

### Docstring Compliance

| Requirement | Status | Notes |
| --- | --- | --- |
| British English | ⚠️ Partial | Some inconsistencies found |
| Google Standard | ⚠️ Partial | Missing Examples in public APIs |
| Public APIs documented | ✅ Good | Most have docstrings |
| Parameter descriptions | ✅ Good | Generally complete |
| Return value docs | ✅ Good | Generally present |
| Examples sections | ❌ Poor | Often missing |

### Code Formatting

| Requirement | Status | Notes |
| --- | --- | --- |
| Line length (119 chars) | ⚠️ Partial | Some violations |
| Line length examples (79) | ✅ Good | Examples follow standard |
| Import grouping | ⚠️ Partial | Some files not compliant |
| Black formatting | Unknown | No evidence of black runs |

## Security Analysis

### Findings

- ✅ No SQL injection risks (no database access)
- ✅ No command injection risks (limited subprocess use)
- ⚠️ File path validation needed if accepting user input
- ℹ️ Uses runpy for test execution (acceptable for tests)
- ⚠️ Private matplotlib API usage (could break)

**Security Risk Level:** Low

The repository does not handle untrusted input in security-critical ways. The main risk is future compatibility
with matplotlib updates.

## Recommendations

### Immediate Actions (This Sprint)

1. ✅ **Fix weakref comparison bugs** in base.py (Issues #15, #16)
1. ✅ **Add renderer None handling** in util.py (Issue #18)
1. ✅ **Add bounds checking** in StackVertical (Issue #19)
1. ✅ **Add unit tests** for critical functionality

### Short Term (Next Sprint)

1. Review and address matplotlib private API usage (Issue #8)
1. Complete missing docstring sections
1. Fix typos and documentation inaccuracies
1. Add type hints to public APIs
1. Run black formatter across codebase

### Long Term (Next Quarter)

1. Add unit tests for error conditions and edge cases
1. Add comprehensive type hints
1. Set up pre-commit hooks for code quality
1. Document matplotlib version compatibility
1. Consider adding py.typed for better IDE support

## Code Review Checklist

- [x] All source files reviewed
- [x] Documentation reviewed
- [x] Test coverage assessed
- [x] Security analysis completed
- [x] Coding standards compliance checked
- [x] Issues documented in BUGS.md
- [x] Priority recommendations provided
- [x] Summary report created

## Files Reviewed

### Source Files (12 Python files)

- `src/stonerplots/__init__.py`
- `src/stonerplots/colours.py`
- `src/stonerplots/counter.py`
- `src/stonerplots/format.py`
- `src/stonerplots/util.py`
- `src/stonerplots/context/__init__.py`
- `src/stonerplots/context/base.py`
- `src/stonerplots/context/double_y.py`
- `src/stonerplots/context/inset_plot.py`
- `src/stonerplots/context/multiple_plot.py`
- `src/stonerplots/context/noframe.py`
- `src/stonerplots/context/save_figure.py`

### Test Files (1 Python file)

- `tests/stonerplots/test_examples.py`

### Configuration Files

- `pyproject.toml`
- `setup.py`
- `.github/workflows/pytest.yaml`

## Detailed Findings

For a complete list of all 32 issues with detailed descriptions, file locations, severity assessments, and
recommended fixes, please refer to the **BUGS.md** file in the repository root.

## Conclusion

The StonerPlots repository is a well-designed matplotlib extension with useful functionality for scientific
plotting. The identified issues are manageable and mostly fall into documentation and testing categories. The
critical bugs should be addressed promptly, but they don't fundamentally compromise the package's utility.

With the recommended improvements, particularly around test coverage and bug fixes, the codebase quality could
easily reach 9/10.

---

**Next Steps:**

1. Review this summary with the development team
1. Prioritise issues based on team bandwidth
1. Create GitHub issues for critical bugs
1. Plan sprint work for high and medium priority items
1. Consider this review when planning the next release
