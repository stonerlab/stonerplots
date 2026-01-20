# Copilot general instructions

## Docstring Formatting

All docstrings for python functions, classes, methods should confirm to the following:

- Generally the format is based on Google stadnard
- Written in British English
- There is a one line suymmary that starts on the same line as the opening quotes and terminated with a period.
- All public classes, methods and functions should conform to the following:

  - The position areguments are described in an Args: section, the keyword parameters in a "Keyword Parameters:" section.
  - Parameters are listed as "name (type):" then a newline and indent with the descritpion.
  - Return values are in a "Returns:" section. For single return values the format is "(type):" newline and indent and then description. Tuples (multiple return values) are given a sequyence of single value blocks.
  - Exceptions that are specifically raised are in a "Raises:" section.
  - Class atributes are in a "Attributes:" section and follow a similar structure to parameters.
  - Any details of the algorithm etc are in a "Notes:" section.
  - Public methods and functions should have examples of usage in an "Examples:" section
  - The Class constructor should be documented in the class docstring rather than the __init__ method's docstring.

- Private mthods, functions should conform to the following:

  - If the function or method is called outside of the same scope (e.g. in an inherited class or different module) then it should be documented as a publuc method or function
  - Otherwise, only the summary needs to be probided and other sections are optional.

## Code formatting

For user examples, the line length is 79 characters, for all other code use 119 characters.
Otherwise folow black coding standards.
Group ipmorts as follows:

- standard library imports
- well known third party packages such as numpy, matplotlib, scipy, pandas
- other third party packages
- imports from within this package, including relative imports

Within each group, sort imports alphabetically. Where possible combine imports from the same module into one statement.

## Issues and Bugs discovered during copilot operations

If a new issue or bug is discovered during editing or creating other features, place a descritpion of the issue in BUGS.md. Describe the ussye/bug in a way that will make it most easy for a future copilot session to correct the problem.

If an issue or bug in BUGS.md is fixed, remove the issue report from the BUGS.md file.

## Markdown Formatting

### Blank Lines

- Ensure that lists are surrounded by a single blank line
- Ensure a single blank line between headings at different levels and between headings and the following text.
- Enumerated lists should always use 1. for each item marker.

## Line length

- Keep the lines to 119 characters
