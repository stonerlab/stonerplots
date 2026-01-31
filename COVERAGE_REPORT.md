# Test Coverage Report

**Date:** 2026-01-31
**Repository:** stonerlab/stonerplots

## Executive Summary

The initial code review estimated test coverage at ~30%. However, this estimate was **incorrect**.

### Actual Coverage: 93.30%

After adding comprehensive error condition tests and tests for helper methods and optional parameters, coverage has
improved from 85.81% to **93.30%**.

This was verified by running pytest with coverage reporting:

```bash
pytest tests/ --cov=src/stonerplots --cov-report=term
```

## Coverage by Module

| Module                     | Statements | Missed | Coverage  | Change        |
|----------------------------|------------|--------|-----------|---------------|
| `__init__.py`              | 26         | 0      | 100.00%   | ➡️            |
| `colours.py`               | 6          | 0      | 100.00%   | ➡️            |
| `context/__init__.py`      | 6          | 0      | 100.00%   | ➡️            |
| `counter.py`               | 16         | 0      | 100.00%   | ⬆️ +6.25%     |
| `context/noframe.py`       | 43         | 0      | 100.00%   | ⬆️ +18.60%    |
| `context/inset_plot.py`    | 41         | 2      | 95.12%    | ➡️            |
| `context/multiple_plot.py` | 184        | 8      | 95.65%    | ⬆️ +3.26%     |
| `context/double_y.py`      | 86         | 4      | 95.35%    | ⬆️ +11.63%    |
| `context/save_figure.py`   | 153        | 8      | 94.77%    | ⬆️ +6.23%     |
| `util.py`                  | 166        | 10     | 93.98%    | ⬆️ +3.19%     |
| `format.py`                | 93         | 10     | 89.25%    | ⬆️ +18.27%    |
| `context/base.py`          | 120        | 21     | 82.50%    | ⬆️ +10.83%    |
| **TOTAL**                  | **940**    | **63** | **93.30%**| **⬆️ +7.49%** |

## Why the Initial Estimate Was Wrong

The initial review assumed that because only example execution tests exist (in `test_examples.py`), coverage
would be low. However:

1. **47 example scripts** are run as parametrised tests
2. These examples exercise nearly all code paths in the library
3. Examples demonstrate real-world usage patterns, providing comprehensive integration testing
4. The examples cover all major features and most edge cases

## Recent Improvements (2026-01-31)

### Phase 1: Error Condition Tests

Added comprehensive error condition tests (`test_error_conditions.py`) covering:

1. **counter.py**: ValueError validation for invalid roman numeral inputs
2. **format.py**: TypeError validation for invalid PlotLabeller parameters
3. **util.py**: TypeError validation for invalid _default class properties
4. **context/save_figure.py**: Multiple exception types for invalid parameters
5. **context/double_y.py**: ValueError/TypeError for invalid locations and colours
6. **context/multiple_plot.py**: TypeError for invalid figure and panels

This resulted in a **4.83% increase in coverage** (85.81% → 90.64%).

### Phase 2: Helper Methods and Optional Parameters

Added comprehensive tests (`test_coverage_improvements.py`) addressing the optional recommendations from the original
coverage report:

1. **format.py helper methods**: Tests for `format_data()` and `format_data_short()` methods in both TexFormatter and
   TexEngFormatter classes, bringing coverage from 84.95% to 89.25% (+4.30%)
2. **context/noframe.py optional parameters**: Tests for `__call__()` method with various parameter combinations
   including `x`, `y`, `include_open`, and `use` parameters, plus tests for axis limit adjustment edge cases, bringing
   coverage from 81.40% to 100.00% (+18.60%)
3. **context/base.py collection protocol**: Tests for tuple indexing in RavelList, `__contains__`, `__reversed__`,
   and `__iter__` methods in PlotContextSequence, bringing coverage from 71.67% to 82.50% (+10.83%)

This resulted in an additional **2.66% increase in coverage** (90.64% → 93.30%).

## Test Coverage Goals

✅ **Goal Exceeded:** The 93.30% coverage significantly exceeds the recommended 85% threshold.

## Areas with Lower Coverage

The modules with coverage below 95%:

1. **`format.py` (89.25%)**:
   - Missing: Exception handling paths (lines 55-56, 118-119) - exception handler bodies for extreme numerical values
   - Missing: Minor formatter/locator setting (lines 199, 203-207) - edge cases in locator setting
   - ✅ **Improved**: Helper methods `format_data()` and `format_data_short()` now tested

2. **`context/base.py` (82.50%)**:
   - Missing: Axis selection helpers (lines 212-218, 222-225) - edge cases in save/restore operations without figures
   - Missing: WeakRef handling edge cases (lines 288-290, 320-327, 333) - dereferenced weak references
   - Missing: Edge case in `__len__` method (line 183)
   - ✅ **Improved**: Tuple indexing, `__contains__`, `__reversed__`, and `__iter__` now tested

## Recommendations

### Current Status: Excellent

The current test coverage is **excellent at 93.30%** and exceeds industry standards. The codebase is well-tested
with a combination of integration tests (examples), unit tests (error conditions), and targeted tests for helper methods
and optional parameters.

### Remaining Gaps Analysis

The uncovered code falls into these categories:

#### 1. Exception Handler Bodies (Low Priority)

Lines inside `except` blocks that handle edge cases like `OverflowError`, `ZeroDivisionError`, and `FloatingPointError`.
These are defensive programming patterns that are hard to trigger in normal usage.

**Affected modules:** `format.py`

**Testing approach:** Would require crafting extreme numerical values or conditions to trigger these specific errors.

#### 2. Helper Methods (Medium Priority)

Methods like `format_data()` and `format_data_short()` that wrap the main formatter logic.
These are typically called by matplotlib internals rather than user code.

**Affected modules:** `format.py`

**Testing approach:** Would require integration with matplotlib's ticker system directly.

✅ **Addressed**: Helper methods `format_data()` and `format_data_short()` now have comprehensive tests.

#### 3. Advanced Collection Protocol Methods (Low Priority)

Special methods like `__contains__`, complex tuple indexing, and reversed iteration that support
advanced Python collection protocols but aren't commonly used.

**Affected modules:** `context/base.py`

**Testing approach:** Would require tests explicitly exercising these protocols.

✅ **Addressed**: Collection protocol methods now have comprehensive tests covering tuple indexing, `__contains__`,
`__reversed__`, and `__iter__`.

#### 4. Optional Parameter Edge Cases (Medium Priority)

Code paths for optional parameters and edge conditions in context managers.

**Affected modules:** `context/noframe.py`, `context/base.py`

**Testing approach:** Would require tests with specific combinations of optional parameters.

✅ **Addressed**: Optional parameters in `context/noframe.py` now have comprehensive tests covering all parameter
combinations and edge cases.

#### 5. WeakRef Edge Cases (Low Priority)

Code handling dereferenced weak references and edge cases in figure/axes tracking.

**Affected modules:** `context/base.py`

**Testing approach:** Would require tests that explicitly cause garbage collection between operations.

### Recommended Actions

1. **No immediate action required** - Coverage at 93.30% is excellent
2. ✅ **Completed enhancements:**
   - ✅ Added tests for helper methods in `format.py` (improved from 84.95% to 89.25%)
   - ✅ Added tests for optional parameter combinations in `context/noframe.py` (improved from 81.40% to 100.00%)
   - ✅ Added tests for collection protocol methods in `context/base.py` (improved from 71.67% to 82.50%)

3. **Not recommended:**
   - Testing exception handler bodies for extreme numerical conditions (diminishing returns)
   - Testing weak reference edge cases (too fragile and environment-dependent)
   - Testing save/restore edge cases without figures (rare edge cases)

## Configuration Updates

To ensure accurate coverage reporting in the future, the following configurations have been added:

### `pyproject.toml`

```toml
[tool.coverage.run]
source = ["src/stonerplots"]
omit = [
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

### CI Workflow (`.github/workflows/pytest.yaml`)

Updated to include coverage reporting:

- Added `pytest-cov` to environment dependencies
- Added `--cov=src/stonerplots --cov-report=term --cov-report=html` to pytest arguments

## Conclusion

The test coverage for StonerPlots is **excellent at 93.30%**, a significant improvement from the initial 85.81%. The
addition of error condition tests and targeted tests for helper methods and optional parameters has substantially
improved coverage across all modules.

The example-based testing approach provides comprehensive coverage of real-world usage patterns, while the unit tests
ensure proper error handling, input validation, and edge case handling for helper methods and optional parameters.

**Status**: ✅ Coverage goal exceeded (93.30% >> 85%)

**Test composition:**

- 52 example execution tests (integration testing)
- 7 format edge case tests (formatter robustness)
- 28 error condition tests (input validation)
- 20 coverage improvement tests (helper methods and optional parameters)
- **Total: 107 tests** (100 passed, 2 skipped, 5 xfailed)
