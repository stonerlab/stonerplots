# -*- coding: utf-8 -*-
"""Functions that can count in a variety of formats."""

__all__ = ["counter"]

# Roman numeral map for converting integers to Roman numerals.
# The overline (\overline{}) in LaTeX represents multiplication by 1,000 in Roman numerals,
# allowing representation of numbers >= 4,000 (e.g., \overline{V} = 5,000).
ROMAN_NUMERAL_MAP = {
    1_000_000: "$\\overline{\\mathrm{M}}$",
    900_000: "$\\overline{\\mathrm{CM}}$",
    500_000: "$\\overline{\\mathrm{D}}$",
    400_000: "$\\overline{\\mathrm{CD}}$",
    100_000: "$\\overline{\\mathrm{C}}$",
    90_000: "$\\overline{\\mathrm{XC}}$",
    50_000: "$\\overline{\\mathrm{L}}$",
    40_000: "$\\overline{\\mathrm{XL}}$",
    10_000: "$\\overline{\\mathrm{X}}$",
    9_000: "$\\overline{\\mathrm{IX}}$",
    5_000: "$\\overline{\\mathrm{V}}$",
    4_000: "$\\overline{\\mathrm{IV}}$",
    1_000: "M",
    900: "CM",
    500: "D",
    400: "CD",
    100: "C",
    90: "XC",
    50: "L",
    40: "XL",
    10: "X",
    9: "IX",
    5: "V",
    4: "IV",
    1: "I",
}


def roman(number: int) -> str:
    """Convert a positive integer to Roman numeral representation.

    Args:
        number (int): A positive integer.

    Returns:
        str: The number represented as an upper-case Roman numeral string.

    Raises:
        ValueError: If the input is not a positive integer.
    """
    if not isinstance(number, int) or number <= 0:
        raise ValueError("Only positive integers can be represented as Roman numerals.")

    result = ""
    for value, numeral in ROMAN_NUMERAL_MAP.items():
        count = number // value
        if count:
            result += numeral * count
            number -= count * value
    return result


def counter(value: int, pattern: str = "({alpha})", **kwargs: str) -> str:
    r"""Format an integer as a string using a pattern and various representations.

    Args:
        value (int): The integer to format.
        pattern (str): A format string with placeholders (default: '({alpha})').
        \*\*kwargs: Additional data to replace placeholders.

    Returns:
        str: The formatted string.
    """
    alpha = chr(ord("a") + value)  # Lowercase alphabet representation
    Roman = roman(value + 1)  # Uppercase Roman numeral
    return pattern.format(alpha=alpha, Alpha=alpha.upper(), roman=Roman.lower(), Roman=Roman, int=value, **kwargs)
