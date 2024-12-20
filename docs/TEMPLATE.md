# Documentation Template

This template defines the structure and style for functions, class and method documentation.
Docstrings should be written in ReStructured Text format.

## General Structure

1. **Short Summary**
    - A brief description of the class or method functionality.
    - This should include a one line summary written as an imperitive satement,
      followed by a longer summary of the purpose of the class, function or method.
    - The on line summary should start on the openning """" of the docstring.
2. **Args**
    - A section describing the positional parameters in order.
    - Each parameter should be described following the format:
      `parameter_name (type): Description of what the parameter represents.`
    - If the description takes more than the remainder of the line, it should
      form a short block.
3. **Keyword Parameters**
    - A section describing the keyword parameters.
    - Each keyword parameter should be described following the format:
    - `parameter_name (type): Description of what the parameter represents.`
       and the default value.`
3. **Attributes**
    - Provide brief explanations for key internal class attributes:
      `attribute_name (type): Description.`
4. **Raises**
    - Provide a list of any Exceptions that are eplicitly raised with a
      brief description of the circumstances in which they are raise.
5. **Returns**
    - Indicate the return type of the function or method.
    - Give a brief description of the return value.
6. **Notes**
    - Explain important implementation details, gotchas, or assumptions.
    - THis section may be omitted if there are no important details or gotchas.
5. **Examples**
    - Include real-world examples of how to use the functionality, both basic and advanced.
    - This section may be omitted for functions, methods and classes that are not intended
      for third parties to use - for example, base classes, internal or private functions or methods.

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
    >>> my_instance = MyClass(param1=value1)
    >>> result = my_instance.some_method()
    >>> print(result)
"""
```