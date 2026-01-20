# Test Coverage Report

**Date:** 2026-01-20
**Repository:** stonerlab/stonerplots

## Executive Summary

The initial code review estimated test coverage at ~30%. However, this estimate was **incorrect**.

### Actual Coverage: 85.81%

This was verified by running pytest with coverage reporting:

```bash
pytest tests/ --cov=src/stonerplots --cov-report=term
```

## Coverage by Module

| Module                     | Statements | Missed | Coverage  |
|----------------------------|------------|--------|-----------|
| `__init__.py`              | 26         | 0      | 100.00%   |
| `colours.py`               | 6          | 0      | 100.00%   |
| `context/__init__.py`      | 6          | 0      | 100.00%   |
| `context/inset_plot.py`    | 41         | 2      | 95.12%    |
| `counter.py`               | 16         | 1      | 93.75%    |
| `context/multiple_plot.py` | 184        | 14     | 92.39%    |
| `util.py`                  | 152        | 14     | 90.79%    |
| `context/save_figure.py`   | 157        | 18     | 88.54%    |
| `context/double_y.py`      | 86         | 14     | 83.72%    |
| `context/noframe.py`       | 43         | 8      | 81.40%    |
| `format.py`                | 86         | 25     | 70.93%    |
| `context/base.py`          | 120        | 35     | 70.83%    |
| **TOTAL**                  | **923**    | **131**| **85.81%**|

## Why the Initial Estimate Was Wrong

The initial review assumed that because only example execution tests exist (in `test_examples.py`), coverage
would be low. However:

1. **47 example scripts** are run as parametrised tests
1. These examples exercise nearly all code paths in the library
1. Examples demonstrate real-world usage patterns, providing comprehensive integration testing
1. The examples cover all major features and most edge cases

## Test Coverage Goals

✅ **Goal Met:** The 85.81% coverage exceeds the recommended 85% threshold.

## Areas with Lower Coverage

The modules with coverage below 85%:

1. **`format.py` (70.93%)**: Missing coverage primarily in error handling and edge cases
1. **`context/base.py` (70.83%)**: Some error paths and less common configuration options not exercised
1. **`context/noframe.py` (81.40%)**: Minor gaps in edge case handling

## Recommendations

### Current Status: Satisfactory

The current test coverage is **adequate and exceeds industry standards**. No immediate action is required to
improve coverage.

### Optional Future Improvements

If resources permit, the following would further improve test quality:

1. **Error condition tests**: Add tests that verify appropriate exceptions are raised for invalid inputs
1. **Edge case tests**: Add unit tests for boundary conditions in format classes
1. **Explicit unit tests**: While examples provide good integration testing, explicit unit tests can make
   expected behaviour more clear

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

The test coverage for StonerPlots is **excellent at 85.81%**, significantly better than initially estimated. The
example-based testing approach provides comprehensive coverage of real-world usage patterns. The code review
documentation has been updated to reflect these accurate findings.

**Status**: ✅ Coverage goal achieved (85.81% ≥ 85%)
