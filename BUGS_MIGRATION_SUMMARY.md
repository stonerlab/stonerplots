# BUGS.md Migration Summary

## Completed Tasks ✅

1. **Reviewed all issues in BUGS.md** - Verified the status of all 16 issues
   - Identified 6 issues that have been **FIXED**
   - Identified 10 issues that are still **OPEN**

2. **Removed BUGS.md** - The file has been deleted from the repository

3. **Updated copilot-instructions.md** - Changed instructions from writing to BUGS.md to creating GitHub issues with proper guidelines

4. **Created ISSUES_TO_CREATE.md** - Comprehensive document with all open issues ready to be converted to GitHub issues

## Issues Status Report

### Fixed Issues (No Action Needed) ✅

The following 6 issues have been **FIXED** and do not require GitHub issues:

1. **Counter buffer overflow** - Fixed with modulo 26 wraparound in `counter.py`
2. **InsetPlot assignment bug** - Fixed with proper elif/else in `inset_plot.py`
3. **StackVertical index bounds** - Fixed with len checks in `multiple_plot.py`
4. **setup.py configuration** - Fixed (file removed, using pyproject.toml only)
5. **_colors_full_map private API** - Fixed (now uses public `get_named_colors_mapping()`)
6. **Test security concern** - Not an issue (by design, tests run trusted code)

### Open Issues (Need GitHub Issues) 📝

The following 10 issues are still **OPEN** and need to be created as GitHub issues:

#### Medium Priority (3 issues)
1. Redundant type conversion in TexEngFormatter (code-quality)
2. Usage of private matplotlib API _TransformedBoundsLocator (technical-debt)
3. Incorrect docstring reference to private matplotlib class (documentation)

#### Low Priority (7 issues)
4. TODO comment for marker consideration in auto-positioning (enhancement)
5. Logic inconsistency in DoubleYAxis.good_colour() (bug)
6. Missing comprehensive type hints (code-quality)
7. Inconsistent None checking patterns (code-quality)
8. Line length violations (code-quality)
9. Inconsistent string formatting (code-quality)
10. Multiple canvas draws in loops (performance)

## Next Steps for Repository Maintainer

Since GitHub Copilot agents cannot directly create GitHub issues, the remaining open issues need to be created manually.

### Option 1: Manual Creation (Recommended)

Use the detailed information in `ISSUES_TO_CREATE.md` to create each issue. Each issue section includes:
- Suggested title
- Recommended labels
- Detailed description with file paths and line numbers
- Reproduction steps (where applicable)
- Recommended fixes with code examples

### Option 2: Automated Creation via Script

You could use the GitHub CLI or API to automate issue creation:

```bash
# Example using GitHub CLI
gh issue create --title "Redundant type conversion in TexEngFormatter" \
  --label "code-quality,good-first-issue" \
  --body-file issue_template_1.md
```

### After Creating Issues

1. Delete `ISSUES_TO_CREATE.md` from the repository
2. Delete this summary file (`BUGS_MIGRATION_SUMMARY.md`)
3. Verify the updated copilot instructions are working correctly

## Files Modified

- **Deleted:** `BUGS.md` (29,526 bytes)
- **Modified:** `.github/copilot-instructions.md` (updated issue tracking workflow)
- **Created:** `ISSUES_TO_CREATE.md` (temporary file with issue details)
- **Created:** `BUGS_MIGRATION_SUMMARY.md` (this file - temporary)

## Verification

To verify the migration was successful:

```bash
# Confirm BUGS.md is removed
ls BUGS.md  # Should show: No such file or directory

# Check updated copilot instructions
grep -A 10 "Issues and Bugs" .github/copilot-instructions.md

# Review issues to create
less ISSUES_TO_CREATE.md
```

---

**Date:** 2026-02-07  
**Branch:** copilot/verify-bugs-and-update-docs  
**Commit:** Remove BUGS.md and update copilot instructions to use GitHub issues
