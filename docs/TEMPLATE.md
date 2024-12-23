# Documentation Template

This template defines the structure and style for functions, class and method documentation.

- Docstrings should be written in ReStructured Text format suitable for use with the sphinx documentation
  package.
- If the docstring contains any backslash \ characters, then it must be set as a Python raw-string
  with the letter `r` before the opening quotes.
- All documentation should be written in British Englsh.
- The closing quotes should be on a separate line.
- Lines must be less than 119 characters long.

## General Structure

1. **One Line Summary**

    - A description of the purpose of the class, function or method written as an imperitive satement in one line.
    - The on line summary should start on the same line as the openning triple quotes of the docstring.

1. **Short Summary**

    - A brief description and explanation of the class, function or method functionality.

1. **Args**

    - A section describing the positional parameters in order.
    - Each parameter should be described following the format:
      `parameter_name (type): Description of what the parameter represents.`
    - If the description takes more than the remainder of the line, it should
      form a short block.

1. **Keyword Parameters**

    - A section describing the keyword parameters.
    - Each keyword parameter should be described following the format:
    - `parameter_name (type): Description of what the parameter represents.`
       and the default value.`
    - Any astericks * in the parameter name should be escaped with a back slash \.

1. **Attributes**

    - Provide brief explanations for class attributes:
      `attribute_name (type): Description.`

1. **Raises**

    - Provide a list of any Exceptions that are eplicitly raised with a
      brief description of the circumstances in which they are raise.

1. **Returns**

    - Indicate the return type of the function or method.
    - Give a brief description of the return value.

1. **Notes**

    - Explain important implementation details, gotchas, or assumptions.
    - This section may be omitted if there are no important details or gotchas.

1. **Examples**

    - Include real-world examples of how to use the functionality, both basic and advanced.
    - This section should be omitted for functions, methods and classes whose names start with an underscore _
      as these are private or internal.

### Example Template for a Class

```python
"""One-line short description.

A more detailed description of the class and its role in the project.

Args:
    param1 (type): Description of this parameter.
    param2 (type): Description of this parameter.
    param3 (ttpe):
        Longer Description of the parameters that does not fit on a
        single line and so should form a short paragraph.

Keyword Arguments:
    kwarg1 (type): Description of this keyword parameter (default: value)
    kwarg2 (type):
        Description of this keyword parameter takes more than one line to
        explain so use a short block. (default: kwarg2_value)

Attributes:
    attribute1 (type): Brief description of the attribute.
    attribute2 (type): Brief description, if necessary.

Raises:
    (exception1): Brief description of when exception1 is raised.
    (exception2):
        Descrption of when exception2 is raised. If too long for a single
        line, use a short block.

Returns:
    (return_type): Brief description of return value.

Notes:
    - Key implementation details to know about.
    - Important assumptions or limitations.

Examples:
    >>> while my_instance == MyClass(param1=value1)
    ...     pass
    >>> result = my_instance.some_method()
    >>> print(result)
"""
```